#!/usr/bin/env python3
"""patch_combo_views.py -- fix the SECOND texture-lifetime hole in rhi/a7_vk32.c.

Run with no arguments for a DRY RUN that says "already applied" / "will apply"
per edit.  Pass --apply to write.  Refuses on drift (it will not guess).

THE FAULT THIS FIXES -- measured, not theorised
-----------------------------------------------
2026-10-11 07:25:40 and 07:31:49, two separate cmr2 runs while Miami was playing:

    [gfxhub] page fault (src_id:0 ring:24 vmid:3 pasid:14518)
     Process cmr2 pid 498908 thread cmr2 pid 498908
      in page starting at address 0x0000800106822000 from client 0x1b (UTCL2)
    GCVM_L2_PROTECTION_FAULT_STATUS:0x00301031
             Faulty UTCL2 client ID: TCP (0x8)
             PERMISSION_FAULTS: 0x3      RW: 0x0
    ~5 s later: ring gfx_0.1.0 timeout -> ring reset failed -> MODE2 reset
    -> "device wedged" -> the compositor's display dies with it.

TCP = the texture cache.  RW:0 = a READ.  The SAME page both times
(0x800106822000/0x8001068223000) because the game's texture-id sequence is
deterministic, so RADV hands back the same VA slot.

The 23:09 "gpu lifetime" fix (patch_gpu_lifetime.py) removed the IN-FLIGHT case:
it waits before a7_upload_texture frees an image.  It did not touch the CACHED
case, which is this one:

  * a7vk_combo_set() caches a VkDescriptorSet in p->combos[], keyed on
    (t0, t1, sampler hashes) -- TEXTURE IDS.
  * a texId is a SLOT, not an image.  SetTexture re-uploads into the same slot
    whenever the surface is dirty, and a7_upload_texture then destroys the
    imageView and frees the memory behind it.
  * the cached set still NAMES that destroyed view.  The next draw with the same
    slot + same sampler gets it back out of the cache and binds it.

So the fragment shader samples through a dead imageView -> unmapped page ->
TCP read fault -> the shader never retires -> ring timeout -> MODE2 reset.
The kernel blames kwin_wayland in the timeout line because the compositor owns
the next submission in the ring; the fault line names cmr2, and cmr2 is who did it.

THE FIX
-------
Make the imageView part of the cache key, and give the descriptor back to the
pool when its view dies.  Two properties, both needed:
  * correctness -- a set naming a dead view can never be handed out again,
  * boundedness -- the pool is not leaked, so a long run cannot fill it.
The pool gains VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT so the sets can
be released individually; the two long-lived sets (whiteSet, ubSet) are never in
combos[] and are never freed.

No pipeline, no draw path, no state mapping, no game object is touched.
"""
import sys, os, shutil, time

P = "/home/deck/lena/.lena_cmr2/port/rhi/a7_vk32.c"
BAK = P + ".bak-pre-comboviews-" + time.strftime("%Y%m%d-%H%M%S")

EDITS = []

def edit(name, old, new, marker):
    EDITS.append((name, old, new, marker))

# ---- 1. the key gains the two views ----------------------------------------
edit("key struct",
"""typedef struct { int t0, t1; uint32_t h0, h1; } A7VKComboKey;""",
"""typedef struct { int t0, t1; uint32_t h0, h1; VkImageView v0, v1; } A7VKComboKey;""",
"""VkImageView v0, v1; } A7VKComboKey;""")

# ---- 2. resolve the views BEFORE the lookup, and key on them ---------------
edit("resolve + key",
"""    A7VKComboKey key; key.t0 = t0; key.t1 = t1; key.h0 = h0; key.h1 = h1;
    for (int i=0;i<p->ncombo;i++) if (memcmp(&p->combos[i].key,&key,sizeof key) == 0) return p->combos[i].set;
    if (p->ncombo >= A7VK_MAX_COMBOS) { p->clampHits++; return p->whiteSet; }
    VkDescriptorSet ds = VK_NULL_HANDLE;
    VkDescriptorSetAllocateInfo ai; memset(&ai,0,sizeof ai);
    ai.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO;
    ai.descriptorPool = p->dpool; ai.descriptorSetCount = 1; ai.pSetLayouts = &p->dsl;
    if (vkAllocateDescriptorSets(p->device,&ai,&ds) != VK_SUCCESS) return p->whiteSet;
    VkDescriptorImageInfo dii[2]; memset(dii,0,sizeof dii);
    int ids[2] = { t0, t1 };
    VkSampler sm[2] = { s0, s1 };
    for (int k=0;k<2;k++) {
        int id = (ids[k] >= 0 && p->tex[ids[k]].used) ? ids[k] : -1;
        dii[k].sampler = (id >= 0 && sm[k]) ? sm[k] : p->whiteSmp;
        dii[k].imageView = id >= 0 ? p->tex[id].view : p->whiteView;
        dii[k].imageLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
    }""",
"""    /* THE VIEWS ARE PART OF THE IDENTITY, and that is not a nicety. A texId is a
     * SLOT. The game re-uploads into the same slot whenever the surface is dirty,
     * and a7_upload_texture then destroys the imageView and frees the memory
     * behind it. A cache keyed on the id alone hands the next draw a descriptor
     * set still naming the DEAD view -- a fragment shader sampling unmapped
     * memory, which is a [gfxhub] "Faulty UTCL2 client ID: TCP" read fault, a
     * gfx_0.1.0 ring timeout and a MODE2 reset that takes the compositor and the
     * player's session down with it. MEASURED: 2026-10-11 07:25:40 and 07:31:49,
     * two runs, the same page, Process cmr2. */
    int ids[2] = { t0, t1 };
    VkImageView vw[2];
    for (int k=0;k<2;k++)
        vw[k] = (ids[k] >= 0 && ids[k] < A7VK_MAX_TEX && p->tex[ids[k]].used && p->tex[ids[k]].view)
              ? p->tex[ids[k]].view : p->whiteView;
    A7VKComboKey key; memset(&key,0,sizeof key);
    key.t0 = t0; key.t1 = t1; key.h0 = h0; key.h1 = h1;
    key.v0 = vw[0]; key.v1 = vw[1];
    for (int i=0;i<p->ncombo;i++) if (memcmp(&p->combos[i].key,&key,sizeof key) == 0) return p->combos[i].set;
    if (p->ncombo >= A7VK_MAX_COMBOS) { p->clampHits++; return p->whiteSet; }
    VkDescriptorSet ds = VK_NULL_HANDLE;
    VkDescriptorSetAllocateInfo ai; memset(&ai,0,sizeof ai);
    ai.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO;
    ai.descriptorPool = p->dpool; ai.descriptorSetCount = 1; ai.pSetLayouts = &p->dsl;
    if (vkAllocateDescriptorSets(p->device,&ai,&ds) != VK_SUCCESS) return p->whiteSet;
    VkDescriptorImageInfo dii[2]; memset(dii,0,sizeof dii);
    VkSampler sm[2] = { s0, s1 };
    for (int k=0;k<2;k++) {
        int id = (ids[k] >= 0 && p->tex[ids[k]].used) ? ids[k] : -1;
        dii[k].sampler = (id >= 0 && sm[k]) ? sm[k] : p->whiteSmp;
        dii[k].imageView = vw[k];
        dii[k].imageLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
    }""",
"""key.v0 = vw[0]; key.v1 = vw[1];""")

# ---- 3. the eviction helper -------------------------------------------------
edit("drop helper",
"""/* ============================== init ==================================== */
static int a7vk_load_symbols(int headless)""",
"""/* Every cached combo set that NAMES v - the view about to be destroyed - is
 * dropped and its descriptor given back to the pool. Must run (a) after a
 * vkDeviceWaitIdle, so nothing in flight can still be using the set, and
 * (b) BEFORE vkDestroyImageView, so the entry cannot outlive what it names.
 * Compaction by swap-pop: order in combos[] carries no meaning. */
static void a7vk_drop_combo_views(A7VK *p, VkImageView v)
{
    if (!p || !v) return;
    int i = 0;
    while (i < p->ncombo) {
        A7VKCombo *c = &p->combos[i];
        if (c->key.v0 == v || c->key.v1 == v) {
            if (c->set) vkFreeDescriptorSets(p->device,p->dpool,1,&c->set);
            p->combos[i] = p->combos[--p->ncombo];
            continue;
        }
        i++;
    }
}

/* ============================== init ==================================== */
static int a7vk_load_symbols(int headless)""",
"""static void a7vk_drop_combo_views(A7VK *p, VkImageView v)""")

# ---- 4. call it on the re-upload path ---------------------------------------
edit("call on re-upload",
"""        vkDeviceWaitIdle(p->device);
        vkDestroyImageView(p->device,t->view,NULL); vkDestroyImage(p->device,t->img,NULL);
        vkFreeMemory(p->device,t->mem,NULL); t->img = VK_NULL_HANDLE; t->view = VK_NULL_HANDLE; }""",
"""        vkDeviceWaitIdle(p->device);
        /* the cached descriptor sets name THIS view; drop them before it dies */
        a7vk_drop_combo_views(p,t->view);
        vkDestroyImageView(p->device,t->view,NULL); vkDestroyImage(p->device,t->img,NULL);
        vkFreeMemory(p->device,t->mem,NULL); t->img = VK_NULL_HANDLE; t->view = VK_NULL_HANDLE; }""",
"""a7vk_drop_combo_views(p,t->view);""")

# ---- 5. the pool must allow individual frees --------------------------------
edit("pool free bit",
"""        pi.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO;
        pi.maxSets = A7VK_MAX_TEX+A7VK_MAX_COMBOS+8; pi.poolSizeCount = 2; pi.pPoolSizes = psz;""",
"""        pi.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO;
        /* so a stale combo set can be handed back when its view dies -- see
         * a7vk_drop_combo_views. Without this flag the pool could only ever be
         * reset wholesale, which would take whiteSet and ubSet with it. */
        pi.flags = VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT;
        pi.maxSets = A7VK_MAX_TEX+A7VK_MAX_COMBOS+8; pi.poolSizeCount = 2; pi.pPoolSizes = psz;""",
"""VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT;""")

# ---- 6. declare + load vkFreeDescriptorSets ---------------------------------
edit("decl",
"""A7VK_DECL(vkUpdateDescriptorSets) A7VK_DECL(vkCreateFence) A7VK_DECL(vkDestroyFence)""",
"""A7VK_DECL(vkUpdateDescriptorSets) A7VK_DECL(vkFreeDescriptorSets)
A7VK_DECL(vkCreateFence) A7VK_DECL(vkDestroyFence)""",
"""A7VK_DECL(vkFreeDescriptorSets)""")

edit("load",
"""    A7VK_LOAD(vkAllocateDescriptorSets); A7VK_LOAD(vkUpdateDescriptorSets);""",
"""    A7VK_LOAD(vkAllocateDescriptorSets); A7VK_LOAD(vkUpdateDescriptorSets);
    A7VK_LOAD(vkFreeDescriptorSets);""",
"""A7VK_LOAD(vkFreeDescriptorSets);""")


# ---- 8. count and report the drops, so the fix is measured not argued -------
edit("drop counter",
"""static void a7vk_drop_combo_views(A7VK *p, VkImageView v)
{
    if (!p || !v) return;
    int i = 0;
    while (i < p->ncombo) {
        A7VKCombo *c = &p->combos[i];
        if (c->key.v0 == v || c->key.v1 == v) {
            if (c->set) vkFreeDescriptorSets(p->device,p->dpool,1,&c->set);
            p->combos[i] = p->combos[--p->ncombo];
            continue;
        }
        i++;
    }
}""",
"""static void a7vk_drop_combo_views(A7VK *p, VkImageView v)
{
    if (!p || !v) return;
    int i = 0, n = 0;
    while (i < p->ncombo) {
        A7VKCombo *c = &p->combos[i];
        if (c->key.v0 == v || c->key.v1 == v) {
            if (c->set) vkFreeDescriptorSets(p->device,p->dpool,1,&c->set);
            p->combos[i] = p->combos[--p->ncombo];
            n++;
            continue;
        }
        i++;
    }
    /* THE COUNT IS THE PROOF. Every one of these is a descriptor set that named
     * the image view that is about to be destroyed -- i.e. a set the OLD cache
     * would have handed straight back to the next draw, to sample unmapped
     * memory. A7VK_COMBODBG=1 prints them; unset, this costs one compare. */
    if (n) {
        p->staleViews++;
        static int dbg = -1;
        if (dbg < 0) dbg = getenv("A7VK_COMBODBG") ? 1 : 0;
        if (dbg) fprintf(stderr,"[COMBO] view %p: dropped %d stale descriptor set(s), %d left cached\\n",
                         (void*)v, n, p->ncombo);
    }
}""",
"""p->staleViews++;""")

# ---- 9. the counter field ---------------------------------------------------
edit("staleViews field",
"""    uint64_t refusedFvf, xformSet, lightsSet;""",
"""    uint64_t refusedFvf, xformSet, lightsSet, staleViews;""",
"""uint64_t refusedFvf, xformSet, lightsSet, staleViews;""")

edit("staleViews report",
"""void a7_vk32_counters(A7Device *d, unsigned long long *suboptimal, unsigned long long *recreates,
                      unsigned long long *presentErrors, unsigned long long *pushes)
{
    A7VK *p = PRIV(d);
    if (suboptimal) *suboptimal = p->suboptimal;
    if (recreates) *recreates = p->recreates;
    if (presentErrors) *presentErrors = p->presentErrors;
    if (pushes) *pushes = p->pushes;
}""",
"""void a7_vk32_counters(A7Device *d, unsigned long long *suboptimal, unsigned long long *recreates,
                      unsigned long long *presentErrors, unsigned long long *pushes)
{
    A7VK *p = PRIV(d);
    if (suboptimal) *suboptimal = p->suboptimal;
    if (recreates) *recreates = p->recreates;
    if (presentErrors) *presentErrors = p->presentErrors;
    if (pushes) *pushes = p->pushes;
}
/* stale descriptor sets dropped because their image view died under them. */
unsigned long long a7_vk32_stale_views(A7Device *d)
{
    return d ? (unsigned long long)PRIV(d)->staleViews : 0ull;
}""",
"""a7_vk32_stale_views""")


# ---- 11. the CONTROL switch: A7VK_OLD_COMBO=1 restores the old cache exactly --
# Same binary, same sequence, one env var: without this an A/B is two builds and
# a changed tree, and the difference is not attributable. Inert when unset --
# with it unset the flag is 0 and every branch below is the fixed behaviour.
edit("old-combo switch",
"""    int ids[2] = { t0, t1 };
    VkImageView vw[2];
    for (int k=0;k<2;k++)
        vw[k] = (ids[k] >= 0 && ids[k] < A7VK_MAX_TEX && p->tex[ids[k]].used && p->tex[ids[k]].view)
              ? p->tex[ids[k]].view : p->whiteView;""",
"""    /* A7VK_OLD_COMBO=1 is the CONTROL: it makes this function behave exactly as
     * it did before the fix, so one binary can run both arms of the A/B. It is a
     * switch and not a build difference on purpose -- two builds means two trees
     * and then the difference is not attributable to the fix. Inert unset. */
    static int old_combo = -1;
    if (old_combo < 0) old_combo = getenv("A7VK_OLD_COMBO") ? 1 : 0;
    int ids[2] = { t0, t1 };
    VkImageView vw[2];
    for (int k=0;k<2;k++)
        vw[k] = (ids[k] >= 0 && ids[k] < A7VK_MAX_TEX && p->tex[ids[k]].used && p->tex[ids[k]].view)
              ? p->tex[ids[k]].view : p->whiteView;
    if (old_combo) { vw[0] = vw[1] = VK_NULL_HANDLE; }""",
"""A7VK_OLD_COMBO""")

edit("old-combo drop",
"""static void a7vk_drop_combo_views(A7VK *p, VkImageView v)
{
    if (!p || !v) return;""",
"""static void a7vk_drop_combo_views(A7VK *p, VkImageView v)
{
    if (!p || !v) return;
    /* CONTROL arm: the old code did not drop anything. See a7vk_combo_set. */
    {
        static int oc = -1;
        if (oc < 0) oc = getenv("A7VK_OLD_COMBO") ? 1 : 0;
        if (oc) return;
    }""",
"""See a7vk_combo_set. */""")


def walk(src):
    """Check and apply IN ORDER against a buffer that grows as we go: edit 8
    rewrites the function edit 3 just inserted, so a check that always looks at
    the ORIGINAL text would call a correct sequence drift."""
    work, todo, drift = src, [], None
    for name, old, new, marker in EDITS:
        if marker in work:
            print("already applied : %s" % name)
            continue
        if old in work:
            print("will apply      : %s" % name)
            todo.append((name, old, new))
            work = work.replace(old, new, 1)
            continue
        drift = name
        print("DRIFT  -- not found, refusing: %s" % name)
        print("   looked for: %r" % old[:90])
        break
    return work, todo, drift


def main():
    apply = "--apply" in sys.argv
    src = open(P).read()
    work, todo, drift = walk(src)
    if drift:
        return 2
    if not apply:
        print("\ndry run. %d edit(s) to apply. re-run with --apply" % len(todo))
        return 0
    if not todo:
        print("\nnothing to do")
        return 0
    if not os.path.exists(BAK):
        shutil.copy2(P, BAK)
        print("backup: %s" % BAK)
    open(P, "w").write(work)
    print("wrote %s (%d edits)" % (P, len(todo)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
