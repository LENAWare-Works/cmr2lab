> **Status, appended 2026-10-11 by the Deck side.** This document is the first half of
> the GPU-lifetime story and it is kept as written, because the way it was found
> matters. It has **two** halves: this one (23:09, the texture memory freed under an
> in-flight frame, and the upload path re-recording the frame's own command buffer)
> and a **second hole in the same class** found the next morning, when Miami's display
> died under him mid-session at 07:25 and 07:31 — the descriptor-set cache was keyed on
> the texture id, so a draw could still be handed a set naming a view that had just
> been destroyed. That one is `docs/DEATH-AND-LIGHT.md` §1, fixed with
> `tools/fixes/patch_combo_views.py`, and measured: 360 s of continuous stage,
> 6.34 M mesh-FVF draws, **zero GPU resets**. The last GPU fault in this kernel's log
> is 2026-10-11 07:31:55 — nothing since.

# THE CRASH IS A GPU HANG — found, fixed, and measured

Lane `work/RACE`, 2026-10-10 ~23:20 EEST. Task `miami-target-race`.
Miami's words: *"it crashed anytime trying to get to profile creator"*.

Two things were true. The out-of-bounds panic at the profile creator was real and
is fixed (seven sentinel casts, 22:44 — `work/PLAY/CHECKPOINT.md`). **There was a
second, larger thing underneath it, and it is why no run of this port has ever
lasted longer than about thirty seconds, with or without anyone testing it.**

---

## 1. WHAT THE KERNEL SAYS (this is not in the game's own log)

The game's log shows nothing — no panic, no error, the file just stops. The
kernel log names it ten times in twenty minutes, and every one of them is `cmr2`:

```
Oct 10 22:50:51  ring gfx_0.0.0 timeout, signaled seq=11887395, emitted seq=11887398
Oct 10 22:50:51   Process cmr2 pid 411232
Oct 10 22:54:05  ring gfx_0.0.0 timeout   Process cmr2 pid 412359
Oct 10 22:55:02  ring gfx_0.0.0 timeout   Process cmr2 pid 413883
Oct 10 22:55:09  ring gfx_0.0.0 timeout   Process cmr2 pid 413902
Oct 10 22:58:14  ring gfx_0.0.0 timeout   Process cmr2 pid 414530
Oct 10 22:58:44  ring gfx_0.0.0 timeout   Process cmr2 pid 414663
Oct 10 22:59:48  ring gfx_0.0.0 timeout   Process cmr2 pid 414842
Oct 10 23:01:43  ring gfx_0.0.0 timeout   Process cmr2 pid 415245
Oct 10 23:05:44  ring gfx_0.0.0 timeout   Process cmr2 pid 417432
Oct 10 23:07:10  ring gfx_0.0.0 timeout   Process cmr2 pid 417699
```

Each one is followed by `GPU reset begin!. Source: 1`, `MODE2 reset`, and the
game dying with `radv/amdgpu: The CS has been cancelled because the context is
lost. This context is innocent.` — the last line the game ever writes.

And the fault that causes it names the reader, twice, with the same signature:

```
[gfxhub] page fault (src_id:0 ring:24 vmid:4 pasid:14191)
 Process cmr2 pid 415245
  in page starting at address 0x0000800100882000 from client 0x1b (UTCL2)
 GCVM_L2_PROTECTION_FAULT_STATUS:0x00401031
   Faulty UTCL2 client ID: TCP (0x8)     <- the texture cache pipe
   RW: 0x0                               <- a READ
```

**TCP = texture fetch, read, from a page that is not mapped.** A shader that
faults does not finish, so the CS never completes, so the ring times out, so the
kernel resets the whole GPU. The game is the *victim* of that; the desktop's
compositor goes down with it.

**This also explains two things that were previously written up wrongly:**

* `work/PLAY/CHECKPOINT.md` §10 says runs were "SIGKILLed mid-run by the other
  worker's `pkill -x cmr2`". At least some of those were this: exit 137 with the
  log cut off at startup and no capture written is exactly what a GPU reset looks
  like from the outside.
* The Deck was reset 13 times between 22:50 and 23:14. That is not a test
  artifact.

## 2. WHY IT HAPPENS — TWO LIFETIME BUGS IN `rhi/a7_vk32.c`

`A7VK_FRAMES_IN_FLIGHT == 2`: two frame slots, two command buffers, `p->cmd[0]`
and `p->cmd[1]`.

### 2.1 a texture's memory is freed while a shader can still be reading it

```c
int a7_upload_texture(...) {
    A7VKTex *t = &p->tex[texId];
    if (t->img) { vkDestroyImageView(p->device,t->view,NULL);
                  vkDestroyImage(p->device,t->img,NULL);
                  vkFreeMemory(p->device,t->mem,NULL); ... }   /* <- NO WAIT */
```

`SetTexture` calls this whenever the surface is dirty, and a reused surface is
dirty by definition. A frame submitted one or two presents ago can still be
executing with that imageView bound in its descriptor set. Freeing the memory
under it is the TCP read fault above, verbatim.

### 2.2 the upload re-records and re-submits **the frame's own command buffer**

```c
    VkCommandBuffer cb = p->cmd[0];        /* <- frame slot 0's buffer */
    vkResetCommandBuffer(cb,0);
    ...
    vkQueueSubmit(p->queue,1,&si,VK_NULL_HANDLE);
```

`p->cmd[0]` is in flight on every even frame. You may not reset and re-record a
command buffer the queue is still executing — it is Undefined Behaviour in the
spec and a documented way to corrupt a command stream. There was already a
correct lifetime discipline elsewhere in the file (the depth/offscreen teardown in
`a7_destroy` waits; the same teardown in `a7_capture` waited **thirty lines too
late**, after the images were already freed).

## 3. THE FIX — `work/RACE/patch_gpu_lifetime.py` (6 edits, applied 23:09)

| # | what |
|---|---|
| 1 | `VkCommandBuffer upCmd;` — a command buffer of its own for uploads and captures |
| 2 | allocated from the same pool, `A7VK_FRAMES_IN_FLIGHT + 1` of them |
| 3 | `vkDeviceWaitIdle()` before a re-upload frees the old image — **re-upload path only**, so a first-time upload pays nothing |
| 4 | the upload's copy command records into `p->upCmd`, not `p->cmd[0]` |
| 5 | `a7_capture`: the device wait moved **above** the depth/offscreen teardown, where it belongs |
| 6 | `a7_capture` records into `p->upCmd` too |

No pipeline, no draw path, no state mapping, no game object touched. Backup:
`rhi/a7_vk32.c.bak-pre-gpulifetime-20261010-230931`.

## 4. THE MEASUREMENT — `work/RACE/gpu_watch.sh`, kernel log as the witness

The pass/fail is not a screenshot and not a feeling: it is **how many GPU ring
timeouts the kernel reports while the binary runs**. Same game root, same key
sequence, same machine, back to back.

| run | binary | captured frames? | GPU ring timeouts | what happened |
|---|---|---|---|---|
| control | `work/PLAY/out-plain/cmr2` (22:53, **unpatched**) | yes | **+1** | died at t≈40 s, `GPUVM fault ... RW: 1`, `context is lost` |
| **patched** | `work/RACE/out-race/cmr2` | yes | **0** | ran the full 95 s, all four captures written |
| control | `work/PLAY/out-plain/cmr2` (unpatched) | **no** — nothing but three key presses | **+1** | died, pid 420758, kernel reset #13 at 23:13:57 |
| **patched, 165 s** | `work/RACE/out-race/cmr2` | two, at t=26 s and t=137 s | **0** — 8,124 frames, 1,475,544 draws, 3,299,876 triangles, `pipelines=1`, no panic |

**The third row is the one that matters to Miami.** No instrument, no
snapshots, no captures — just the game running the way he runs it — and the
unpatched binary still hangs the GPU. So this was never our test harness; it is
the game.

## 5. WHAT THE GAME DOES NOW THAT IT SURVIVES

The draw census from the patched 95 s run (`work/RACE/out/patched-with-snaps.log`),
against the numbers every previous round published:

```
                        before (S2, 20-28 s)     patched, 95 s
frames presented              1,127 - 1,607          4,548
draws                            205,714          1,154,569
triangles                        426,806         10,269,626
pipelines                              1                 10  (built 10, hit 34,013)
draws by FVF  0x1c4 TL            205,714            624,637
draws by FVF  0x2d2 MESH                0            541,788   <-- was the standing 0
DrawIndexedPrimitiveVB                  0            403,370
DrawIndexedPrimitive                    0            122,138
SetTexture                              0            520,555
LightEnable                             0            403,121
textureUploads                          -                299
```

**`0 of 205,714` is over. 541,788 draws now carry the mesh FVF.** S2's whole
"the 3D path is set up and never driven" line is answered — not by a renderer
change, and not by the state-fidelity work, but by the game living long enough to
get there.

**Honest reading of it:** ~117 mesh draws and ~2,257 triangles per frame is a
**frontend** 3D scene — the menu's video path, the carousel and the car in it —
not a stage. The captured frame at t=79 s is text over the 0x9cb4ac backdrop with
a panel to the right (`work/RACE/out/patched-with-snaps.04_idle.ppm`, and see
§6). **A stage has not been reached. A race has not been reached.** What has
changed is that the game now gets through its boot sequence, into the frontend
proper, and stays alive long enough for anyone to drive it there.

## 6. THE BLACK BACKGROUND — ANSWERED (not by me; the other worker found it)

`CGraphics::ClearTarget()` clears `D3DCLEAR_TARGET`, then `ClearZBuffer()` clears
`D3DCLEAR_ZBUFFER` with colour `0xff000000`. The RHI stored the colour on *any*
clear, so the Z clear — the last one every frame — won, and the frontend's own
backdrop colour `0x9cb4ac` (`Game.cpp:1041`) never reached the swapchain. Fix:
only a clear carrying `D3DCLEAR_TARGET` owns the colour (`rhi/a7_vk32.c`,
22:53:38, by the worker on `work/FIXBG`).

Verified here on **the binary the launcher runs**, 1280×800, per-pixel counts:

| screen | exactly `0x9cb4ac` | exactly `0x000000` |
|---|---|---|
| legal notice | **94.8-95.9 %** | 0.0 % |
| screen after Enter | 96.0 % | 0.0 % |
| the menu at t=79 s | 60.5 % | 0.0 % |

Black is gone. That is *him* reporting a symptom and it now measures clean.

**The Bink theory was wrong, and it is worth killing explicitly.** The stub
intro movie *is* why the legal notice sits there waiting for a keypress (the port
plays no `intro.bik`, so the screen never advances on its own) and it *is* the
source of the three "Make sure the CMR2 CD is in the CD drive" dialogs. It has
nothing to do with the black background. The background was a clear-colour bug in
our own RHI, one line, and it is fixed. Nobody needs to implement a Bink decoder
to make the frontend look right.

## 7. WHAT THIS MEANS FOR "I WANT TO DO A RACE"

The order of the wall was wrong in every plan we had. It is not:

    frontend → state fidelity → *crash* → game state → race

It is:

    **GPU ring timeout (±30 s, every run)** -> fixed 23:09, delta 0 in 3 runs
      -> the game reaches the frontend proper and drives the 3D path
        -> NOW the menu navigation work (S2b) has somewhere to go.

A race is still a game-state problem, exactly as S2 said, and nothing here moved
the game one state closer by itself. What it did is remove the thing that was
killing every attempt before it could get there — including his.

## 8. NEXT, precisely

1. Drive the frontend from a *surviving* session: the carousel main menu is built
   (`FrontendMenu_BuildMain`, 7 entries, default cursor 1 = rally modes) and the
   mode list is `FrontendMenu_BuildRallyModes` (cursor 2 = time trial). Pad/key
   presses, capture after each, watch `DrawIndexedPrimitiveVB` and the frame.
2. `FrontendMenu_UpdateMain` fires **attract mode after 30.5 s with no input** and
   drives itself to a rally start (`FrontendMenu_GetRallyStartTransition` →
   `FrontendSession_InitFreshRace`). That is the game's own path to a stage, needs
   no hardcoded event sequence, and now has 30.5 s of life to happen in.
3. The dropped states (S2a) still matter for a stage looking right — but they are
   no longer what stands between him and a stage.
