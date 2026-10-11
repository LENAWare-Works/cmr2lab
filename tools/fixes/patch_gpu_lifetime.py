#!/usr/bin/env python3
"""patch_gpu_lifetime.py -- stop the RHI from freeing GPU memory that is still
being read, and stop it re-recording and re-submitting the *frame's* command
buffer from inside a texture upload.

WHY (measured, not theorised)
-----------------------------
The kernel log on this Deck says the game hangs the graphics ring and the kernel
then resets the whole GPU. Every timeout today is `Process cmr2`:

    Oct 10 22:50:51  ring gfx_0.0.0 timeout   Process cmr2 pid 411232
    Oct 10 22:54:05  ring gfx_0.0.0 timeout   Process cmr2 pid 412359
    Oct 10 22:55:02  ring gfx_0.0.0 timeout   Process cmr2 pid 413883
    Oct 10 22:55:09  ring gfx_0.0.0 timeout   Process cmr2 pid 413902
    Oct 10 22:58:14  ring gfx_0.0.0 timeout   Process cmr2 pid 414530
    Oct 10 22:58:44  ring gfx_0.0.0 timeout   Process cmr2 pid 414663
    Oct 10 22:59:48  ring gfx_0.0.0 timeout   Process cmr2 pid 414842
    Oct 10 23:01:43  ring gfx_0.0.0 timeout   Process cmr2 pid 415245
    Oct 10 23:05:44  ring gfx_0.0.0 timeout   Process cmr2 pid 417432
    Oct 10 23:07:10  ring gfx_0.0.0 timeout   Process cmr2 pid 417699

and the page faults that precede them name the texture fetch as the reader:

    [gfxhub] page fault (src_id:0 ring:24 vmid:4 pasid:14191)
     Process cmr2 pid 415245
      in page starting at address 0x0000800100882000 from client 0x1b (UTCL2)
    GCVM_L2_PROTECTION_FAULT_STATUS:0x00401031
       Faulty UTCL2 client ID: TCP (0x8)      <- the texture cache
       RW: 0x0                                <- a READ

A shader reading a VA that is not mapped does not finish: the CS never
completes, the ring times out, the kernel resets the GPU (MODE2 reset), and the
game dies with `context lost`. That is why every run of this port ends after
~20-30 s, whatever else is true about it -- and a GPU reset also takes the
desktop's compositor down. It is not a UBSan panic and it is not the other
worker's pkill; it leaves no line in the game's own log.

Two places in `a7_vk32.c` cause it, and both are lifetime bugs:

1. `a7_upload_texture()` destroys the texture's previous image and frees its
   memory with NO wait for the GPU:

       if (t->img) { vkDestroyImageView(...); vkDestroyImage(...); vkFreeMemory(...); }

   A frame submitted 1-2 frames ago (A7VK_FRAMES_IN_FLIGHT == 2) can still be
   executing and can still have that imageView bound in its descriptor set, so
   the fragment shader fetches from memory that has just been freed. That is the
   TCP read fault above. Nothing in the port calls SetTexture with a dirty
   surface only at load time -- a re-upload is exactly what a reused surface is.

2. The same function records and submits its upload copy command into
   `p->cmd[0]` -- THE FRAME'S OWN COMMAND BUFFER for frame slot 0:

       VkCommandBuffer cb = p->cmd[0];
       vkResetCommandBuffer(cb,0);

   `p->cmd[0]` is in flight whenever `p->frame % 2 == 0`. Resetting and
   re-recording a command buffer that the queue is still executing is undefined
   behaviour; it is a documented way to corrupt a command stream. The upload
   path gets its own buffer here, and so does `a7_capture()` (which had the same
   reuse, and destroyed and recreated the depth image one line before the
   vkDeviceWaitIdle that would have made it safe).

THE FIX
-------
* one extra command buffer, `p->upCmd`, allocated from the same pool, used by
  uploads and by captures, so the per-frame buffers are never touched by either;
* `vkDeviceWaitIdle()` before the old texture image is freed -- only on the
  re-upload path, so a first-time upload pays nothing;
* `vkDeviceWaitIdle()` moved above the depth/offscreen teardown in a7_capture.

No pipeline, no draw path, no state mapping is touched.

Usage:  python3 patch_gpu_lifetime.py [--apply]     (dry run without --apply)
"""
import shutil
import sys
import time

P = "/home/deck/lena/.lena_cmr2/port/rhi/a7_vk32.c"
STAMP = time.strftime("%Y%m%d-%H%M%S")

EDITS = []

# 1. the struct: an upload/capture command buffer of its own
EDITS.append((
    """    VkCommandPool   cmdPool;
    VkCommandBuffer cmd[A7VK_FRAMES_IN_FLIGHT];""",
    """    VkCommandPool   cmdPool;
    VkCommandBuffer cmd[A7VK_FRAMES_IN_FLIGHT];
    /* NOT one of the frame slots. Uploads and captures used to borrow cmd[0],
     * which is in flight on every even frame: resetting a command buffer the
     * queue is still executing is UB, and it is one of the two lifetime bugs
     * this file was fixed for (see work/RACE/GPU-RESET-FINDING.md). */
    VkCommandBuffer upCmd;""",
))

# 2. allocate it, from the same pool
EDITS.append((
    """        cai.commandBufferCount = A7VK_FRAMES_IN_FLIGHT;
        vkAllocateCommandBuffers(p->device,&cai,p->cmd);""",
    """        cai.commandBufferCount = A7VK_FRAMES_IN_FLIGHT + 1;
        {
            VkCommandBuffer cbs[A7VK_FRAMES_IN_FLIGHT + 1];
            memset(cbs,0,sizeof cbs);
            vkAllocateCommandBuffers(p->device,&cai,cbs);
            for (int i=0;i<A7VK_FRAMES_IN_FLIGHT;i++) p->cmd[i] = cbs[i];
            p->upCmd = cbs[A7VK_FRAMES_IN_FLIGHT];
        }""",
))

# 3. a re-upload must not free memory a submitted frame can still read
EDITS.append((
    """    A7VKTex *t = &p->tex[texId];
    if (t->img) { vkDestroyImageView(p->device,t->view,NULL); vkDestroyImage(p->device,t->img,NULL);
                  vkFreeMemory(p->device,t->mem,NULL); t->img = VK_NULL_HANDLE; t->view = VK_NULL_HANDLE; }""",
    """    A7VKTex *t = &p->tex[texId];
    if (t->img) {
        /* WAIT. A frame submitted up to A7VK_FRAMES_IN_FLIGHT-1 frames ago can
         * still be executing with this imageView bound, and the fragment shader
         * would then fetch from memory freed here. On this Deck that is a
         * [gfxhub] page fault with "Faulty UTCL2 client ID: TCP" -- the texture
         * cache -- which never resolves, so the CS never completes, the ring
         * times out and the kernel resets the GPU. It is why no run of this
         * port survives ~30 s. Only the re-upload path pays for this wait. */
        vkDeviceWaitIdle(p->device);
        vkDestroyImageView(p->device,t->view,NULL); vkDestroyImage(p->device,t->img,NULL);
        vkFreeMemory(p->device,t->mem,NULL); t->img = VK_NULL_HANDLE; t->view = VK_NULL_HANDLE; }""",
))

# 4. the upload's own copy command: its own buffer, not the frame's
EDITS.append((
    """    VkCommandBuffer cb = p->cmd[0];
    vkResetCommandBuffer(cb,0);
    VkCommandBufferBeginInfo bi; memset(&bi,0,sizeof bi);
    bi.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cb,&bi);
    VkImageMemoryBarrier ib; memset(&ib,0,sizeof ib);""",
    """    VkCommandBuffer cb = p->upCmd;      /* NOT p->cmd[0]: see the struct note */
    vkResetCommandBuffer(cb,0);
    VkCommandBufferBeginInfo bi; memset(&bi,0,sizeof bi);
    bi.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cb,&bi);
    VkImageMemoryBarrier ib; memset(&ib,0,sizeof ib);""",
))

# 5. a7_capture: the depth/offscreen teardown came BEFORE the device wait
EDITS.append((
    """    uint32_t W = p->extent.width, H = p->extent.height;
    if (p->depthView) { vkDestroyImageView(p->device,p->depthView,NULL); p->depthView = VK_NULL_HANDLE; }""",
    """    uint32_t W = p->extent.width, H = p->extent.height;
    /* the frame just presented may still be executing and still reference these
     * two images; the wait used to be 30 lines below, after they were freed. */
    vkDeviceWaitIdle(p->device);
    if (p->depthView) { vkDestroyImageView(p->device,p->depthView,NULL); p->depthView = VK_NULL_HANDLE; }""",
))

# 6. a7_capture records into the upload buffer too
EDITS.append((
    """    vkDeviceWaitIdle(p->device);
    VkCommandBuffer cb = p->cmd[0];
    vkResetCommandBuffer(cb,0);
    VkCommandBufferBeginInfo bi; memset(&bi,0,sizeof bi);
    bi.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cb,&bi);
    a7vk_record(p,cb,p->offFb,p->rpOff,W,H);""",
    """    vkDeviceWaitIdle(p->device);
    VkCommandBuffer cb = p->upCmd;      /* NOT p->cmd[0] */
    vkResetCommandBuffer(cb,0);
    VkCommandBufferBeginInfo bi; memset(&bi,0,sizeof bi);
    bi.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cb,&bi);
    a7vk_record(p,cb,p->offFb,p->rpOff,W,H);""",
))


def main():
    apply = "--apply" in sys.argv
    src = open(P).read()
    n = 0
    for old, new in EDITS:
        # CHECK new FIRST. For edit 1 the new text has the old text as a prefix
        # (the declaration is inserted after it), so testing `old` first reports
        # "still pending" forever -- and a second --apply would then insert
        # `upCmd` twice and the tree would not compile. That was a real footgun
        # at 23:24; this is the fix.
        if src.count(new):
            print(f"  already applied ({new.strip().splitlines()[0][:60]})")
            continue
        c = src.count(old)
        if c != 1:
            print(f"  REFUSING: anchor found {c} times, need exactly 1:\n"
                  f"    {old.splitlines()[0][:80]}")
            return 2
        src = src.replace(old, new)
        n += 1
    print(f"  {n} edits to make, {len(EDITS)} anchors checked")
    if n == 0:
        print("  nothing to do")
        return 0
    if not apply:
        print("  dry run -- pass --apply to write")
        return 0
    bak = f"{P}.bak-pre-gpulifetime-{STAMP}"
    shutil.copy2(P, bak)
    open(P, "w").write(src)
    print(f"  written; backup {bak}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
