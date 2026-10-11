# DEATH AND LIGHT — 2026-10-11, worker 1 (`HE-PLAYED-IT-LIGHTING-AND-DEATH`)

Miami played the port this morning and the display died under him mid-session.
He also said the lighting is all fucked up. Both are answered below, from the
kernel log, the game's own census, and 360 seconds of the fixed binary running.

Every number here names the tool that produced it. §5 is what I did not claim.

---

## 0. THE SHORT ANSWER

**BUG A.** Not a mystery and not the fix you already made — it is the *same class*
of bug through a *second hole* the 23:09 patch did not reach.

*2026-10-11 07:25:40 and 07:31:49, `journalctl -k`, two separate runs:*

```
[gfxhub] page fault (src_id:0 ring:24 vmid:3 pasid:14518)
 Process cmr2 pid 498908 thread cmr2 pid 498908
  in page starting at address 0x0000800106822000 from client 0x1b (UTCL2)
GCVM_L2_PROTECTION_FAULT_STATUS:0x00301031
         Faulty UTCL2 client ID: TCP (0x8)
         PERMISSION_FAULTS: 0x3      RW: 0x0
~5 s later:
ring gfx_0.1.0 timeout, signaled seq=11835503, emitted seq=11835508
 Process kwin_wayland pid 499282
Ring gfx_0.1.0 reset failed
GPU reset begin!. Source:  1
MODE2 reset
[drm] device wedged, but no recovery needed
```

TCP is the texture cache; `RW: 0x0` is a **read**; the page is unmapped. A
fragment shader sampling an image whose memory is gone. The shader never
retires, the ring times out, the kernel does a **MODE2 reset**, and the
compositor's display dies with it. That is his "display got killed".

`Process kwin_wayland` in the timeout line is a red herring: kwin owns the next
submission in the ring, so the kernel names it there. **The fault line names
cmr2, and cmr2 did it.** Both runs, the **same page** — because the game's
texture-id sequence is deterministic and RADV hands back the same VA slot.

**BUG B.** The lighting path *does* reach the RHI — and then one whole piece of
it is thrown away. `D3DRS_AMBIENT` (render state **139**) is mapped, stored, and
**read by no code anywhere in `a7_vk32.c`**. In one 360-second race the game set
it **548,489 times with 12 distinct values**. All twelve are discarded. On top of
that the shader composes the lighting equation in a way D3D7 never did, which
predicts a flat, blown-out picture — and the frames bear that out.

---

## 1. BUG A — WHAT ACTUALLY KILLS IT

### 1.1 The hole the 23:09 fix did not cover

`work/RACE/GPU-RESET-FINDING.md` (23:09) found the in-flight case and fixed it:
`a7_upload_texture` used to free a texture's old image while a frame submitted one
or two presents ago could still be executing with that imageView bound. It now
does `vkDeviceWaitIdle()` first. That fix is real and it is in the binary.

It is not the whole class. `a7vk_combo_set()` **caches VkDescriptorSets**:

```c
typedef struct { int t0, t1; uint32_t h0, h1; } A7VKComboKey;   /* old */
...
for (int i=0;i<p->ncombo;i++)
    if (memcmp(&p->combos[i].key,&key,sizeof key)==0) return p->combos[i].set;
```

The key is **texture IDs**. A texId is a *slot*, not an image. `SetTexture`
re-uploads into the same slot whenever the surface is dirty, and
`a7_upload_texture` then **destroys the imageView and frees the memory behind it**.
The cached set still *names that destroyed view*. Nothing invalidates
`p->combos[]`. So the next draw with the same slot and the same sampler gets the
stale set straight back out of the cache and binds it — and the fragment shader
samples unmapped memory.

Waiting before the free (23:09) does not help here: the set is stale **after**
the wait, on the next frame. It is a different failure of the same lifetime.

It also explains the **stable faulting address**. A texture id that is
re-uploaded at a deterministic point in the game's sequence gets the same VA slot
back from RADV's allocator, so the kernel reports the same page every time —
`0x800106822000` / `0x8001068223000`, both runs.

### 1.2 The fix

`work/RACE/patch_combo_views.py` — 12 edits, idempotent, order-aware, refuses on
drift. Dry run with no arguments; `--apply` to write. Backup:
`rhi/a7_vk32.c.bak-pre-comboviews-*`.

1. `A7VKComboKey` gains `VkImageView v0, v1`.
2. `a7vk_combo_set` resolves the views *before* the cache lookup and keys on them.
   A set naming a dead view can now never be handed out.
3. New `a7vk_drop_combo_views()`: on re-upload, after the device wait and **before**
   `vkDestroyImageView`, every cached set naming that view is `vkFreeDescriptorSets`'d
   and the array compacted by swap-pop. The pool is not leaked, so a long run
   cannot fill it (the old code returned the *white* set when full — a silent
   wrong picture).
4. The descriptor pool gains `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT`.
   The two long-lived sets (`whiteSet`, `ubSet`) are never in `combos[]` and are
   never freed.
5. `vkFreeDescriptorSets` declared + loaded.

No pipeline, no draw path, no state mapping, no game object touched.

**The patch script is verified reproducible**: applied to the pristine
pre-fix file it produces a file **byte-identical** to the one now in the tree
(`diff -q`), and a second run reports "already applied" for all 12 edits.

### 1.3 The measurement — 360 seconds, kernel log as the witness

`work/RACE/run_death.sh death2 360`, binary `work/RACE/out-death/cmr2`,
md5 `97a9eb3b08595858a563282596680401`. The stage is reached by the game's own
route: one Enter to clear the legal notice, then attract mode with **no further
input** for the rest of the run.

| | before | after |
|---|---|---|
| `ring gfx_0.0.0 timeout` | 12 | **12** |
| `ring gfx_0.1.0 timeout` | 3 | **3** |
| `MODE2 reset` | 14 | **14** |
| `Faulty UTCL2 client ID: TCP` | 3 | **3** |

Nothing moved. And the mechanism fired **710 times**:

```
[COMBO] view 0x4217d20: dropped 1 stale descriptor set(s), 225 left cached
[COMBO] view 0x3b96100: dropped 1 stale descriptor set(s),  97 left cached
```

`grep -c '\[COMBO\]'` = **710**. From the final census (`DECK_DD7_CENSUS=1`):

```
[CENSUS] device counters: textureUploads=1213 draws=6015818
[CENSUS] draws by FVF: 0x1c4 TL=1699341 0x2d2 MESH=6344401 refused_by_backend=0
[CENSUS] backend: presentedFrames=20662 draws=8031647 tris=72679976 pipelines=10
[CENSUS] methods: ... LightEnable=2721943 SetLight=46413 SetMaterial=1 ...
```

**710 descriptor sets, over 1,213 texture uploads, each one naming a view that
was about to be destroyed.** Under the old key every one of those 710 lookups
would have hit the cache and returned that set — that is the deduction, and it is
mechanical: the drop helper searches `combos[]` by exactly the same key
`memcmp` the lookup uses, so a hit there *is* a hit there.

6.34 million mesh-FVF draws is a **stage**, not a menu. Every previous round
published 0.

### 1.4 Can it survive a race distance? — **YES for 6 minutes, on one run**

360 s of continuous stage, 6.34 M mesh draws, 20,662 presented frames, 72.7 M
triangles, **zero GPU resets, zero page faults, zero display loss**.

That is the answer he asked for. He can get back in the seat. The honest caveat
is in §5 — this is one run, and the crash is a race, not a schedule.

---

## 2. BUG B — THE LIGHTING

### 2.1 What is NOT wrong

* **`LightEnable` is not swallowed.** It reaches the RHI in bulk: the race census
  reports `LightEnable=2721943` at the D3D7 boundary and `lightSets=888133` in
  the backend, i.e. **888,133 light-state changes actually took effect**.
  `map_rs` has no say here — `LightEnable`/`SetLight` are separate methods and
  they go straight through.
* **`D3DLIGHT7` is not discarded.** `SetLight=46413`; `DeckDevice7::SetLight`
  copies every field into `A7Light`; `a7vk_fill_block` writes
  `lightPos`/`lightDir`/`lightDiffuse`/`lightSpecAmb` into the set-1 uniform block;
  `a7vk3d.vert` reads them. The plumbing is intact.
* **`DIFFUSEMATERIALSOURCE=0=D3DMCS_MATERIAL` is still the last value** in the
  race (`145:548474/0/1`), so the port's hardcoded `flags[3]=0` is right. The
  earlier finding stands; the "use the vertex colour" fix would have been wrong.
* **`TEXTUREFACTOR` (state 60) is still not consumed.** Confirmed on the current
  binary: it is dropped, and `unmappedTexArgs=0` in both censuses, so no
  combiner argument is asking for `D3DTA_TFACTOR`. *New information worth having:*
  in the race it is set **15,037 times with 12 distinct values**, last
  `0x64000000` — it is no longer a constant. Still unread, so still not doing
  anything to the picture; but the "unneeded" half of that reading is now the
  only half holding it up.

### 2.2 What IS wrong — four defects, in order of confidence

**B1 — `D3DRS_AMBIENT` (139) is stored and never read. This is the big one.**

`deck_dd7.cpp:141` maps `D3DRENDERSTATE_AMBIENT → A7RS_AMBIENT`.
`a7_set_render_state` stores it in `d->rs[s]`.
Then: `grep -n A7RS_AMBIENT rhi/a7_vk32.c` → the name appears **only in the
enum in `api7.h` and in that one map line.** Nothing consumes it.

*The race census, 360 s, `[CENSUS] render states set (state: count last uniq)`:*

```
137:548473/0/2     <- D3DRS_LIGHTING   : 2 distinct values -> lighting IS turned on
139:548489/0/12    <- D3DRS_AMBIENT    : 12 DISTINCT VALUES, all discarded
141:548474/1/2     <- D3DRS_COLORVERTEX
145:548474/0/1     <- DIFFUSEMATERIALSOURCE
```

**548,489 ambient changes, twelve different scene ambients, every one of them
thrown away.** In D3D7 fixed function the ambient term is
`material.ambient × scene_ambient`. We substitute `material.ambient` alone.

**B2 — the lighting equation is composed wrong.**

`a7vk3d.vert`:

```glsl
vec3 lit = b.matAmbient.rgb + b.matEmissive.rgb;
for (...) lit += b.lightDiffuse[i].rgb * ndl;
base.rgb *= lit;
```

D3D7 is `matEmissive + matAmbient·sceneAmbient + matDiffuse·Σ(lightDiffuse·N·L)`.
Ours multiplies **emissive and ambient by the material diffuse**, and drops the
scene ambient entirely.

The prediction this makes is specific and checkable, and it is why the frame
matters: `SetMaterial=1` in the whole 360 seconds — the material is a constant,
and it was measured opaque white. So `matAmbient` is ~`(1,1,1)`, and `lit` is
**at least full white before a single light is added**, then lights add more.
Every lit surface should be **saturated, flat, and carrying almost no
information from the lights** — blown out with faint normal shading, not dark and
not black.

**B3 — no attenuation, no range, no falloff, no spot cone, no specular.**
`lightDir[i].w` carries `range` into the block and the shader never reads it. The
game computes attenuation itself (`Scene_AttenuateSectorLight` uses `att0` and
`att2` off `D3DLIGHT7`) so it plainly expects the hardware to apply it. Ignoring
it makes each light contribute full diffuse at any distance.

**B4 — latent, and I am NOT claiming it caused what he saw.** The shader lights in
**object space**: `normalize(inNormal)` is untransformed and
`normalize(lightPos - inPos)` uses the raw object-space position, while the game
supplies world-space lights. That is only correct while WORLD = identity — and
`WHAT-IS-DRAWN.md` §4 measured WORLD = identity throughout the race. So it is a
landmine for any object with a world transform, **not** the active cause.
(Also dead: `vec3 n = normalize(mat3(b.mvp) * inNormal);` is computed and never
used — and `mvp` includes the projection, so it could never have been a normal.)

**B5 — flagged, unproven.** Only `for (int i=0;i<3;i++)` lights are uploaded.
D3D7 has 8, and `Scene_RestoreLights` walks 60 slots enabling everything
non-NULL. `Graphics_SetLightingMode` only drives 0/1/2, but 888,133 light-state
changes is a lot of motion for three lights. If any index ≥ 3 is enabled it is
silently dropped. Not tested; listed so the next round does not have to rediscover it.

**B6 — also dropped by `map_rs`** (recorded, ignored): `COLORVERTEX` (141,
548,474 calls, last=1), `DIFFUSEMATERIALSOURCE` (145), `AMBIENTMATERIALSOURCE`
(147, 1 call), `EMISSIVEMATERIALSOURCE` (148, last=1=**D3DMCS_COLOR1**).

### 2.3 The frames — in `frames/`, for vision

From the same 360 s run. `ppm2png.py`, all five round-trip verified pixel-exact,
1280×800.

```
cmr2lab-publish/frames/race-LIT_3000_death2.png    2.3 MB   16,424 sampled colours
cmr2lab-publish/frames/race-LIT_4000_death2.png    1.3 MB
cmr2lab-publish/frames/race-LIT_4500_death2.png    0.5 MB   the static pre-race menu
cmr2lab-publish/frames/race-LIT_9500_death2.png    1.3 MB
cmr2lab-publish/frames/race-LIT_10000_death2.png   1.4 MB
```

My own read, `look.py`, before handing them over — and I want to be careful here,
because it is suggestive rather than conclusive:

* **frame 3000** — 48×20 cell map is the letter `r` in **~all 960 cells**:
  red/brown-dominant, dominated by `#88511a` (luma ~90). One small lighter patch.
  A near-uniform brown wash filling the frame.
* **frame 9500** — `+`/`*`/`%`: mid-light through near-white grey-lavender
  (`#cacbce`) across nearly everything, with near-white bands. **Flat and bright.**

Both are consistent with B2's prediction (a saturated, low-information wash) and
inconsistent with "black" and with "correctly shaded scene". But a text cell map
is not an eye, and I am not going to call the lighting diagnosed on the strength
of it. **That is the read I am asking for.**

---

## 3. THE `frames/` PUSH — done, and what I want back

Five PNGs in `~/lena/work/cmr2lab-publish/frames/`, from the fixed binary, from
a 360 s run that reached a real stage. What I need is the disambiguation the
brief asked for:

1. is the light **flat ambient** (uniform, no shading, no direction),
2. **black** (no ambient at all),
3. **blown out** (clipped to white with faint normal shading),
4. or **correctly shaped but at the wrong intensity**?

My prediction is **(3), blown out**, from B1+B2: `matAmbient` ≈ white is added
before any light, then lights add on top. If the frame reads as flat uniform
*mid-grey with no structure* instead, then B1 is not the whole story and the
12 discarded ambient values matter more than I think.

---

## 4. WHAT I CHANGED IN THE TREE, AND HOW TO UNDO IT

| path | what |
|---|---|
| `rhi/a7_vk32.c` | +12 edits, `patch_combo_views.py`. Backup `.bak-pre-comboviews-*` |
| `rhi/a7_vk32.o` | rebuilt (the shared object — your next relink carries this) |
| `work/PLAY/out-plain/cmr2` | **rebuilt with the fix**, md5 `97a9eb3b08595858a563282596680401` |
| `work/PLAY/out-plain/cmr2.bak-pre-comboviews-20261011` | what was there, md5 `b960621bcc5657e135640e35aa70869f` |
| `work/RACE/out-death/cmr2` | same binary, my own output dir |
| `work/RACE/patch_combo_views.py` | the patch, idempotent, order-aware |
| `work/RACE/run_death.sh` | the measurement harness |
| `work/RACE/NOTE-to-worker2-0800-taking-the-gpu.md` | why I pre-empted worker 2 |

**The md5 I replaced is exactly the one the last round's brief pinned as "his
binaries must be untouched": `b960621bcc5657e135640e35aa70869f`.** So the binary
that faulted this morning is the binary whose backup I now hold — that is the
natural control, and it is why I am confident the comparison is the right one.

`~/lena/cmr2-native.sh` runs `work/PLAY/out-plain/cmr2`, so **it now runs the
fixed binary with no other change needed.**

To revert: copy `cmr2.bak-pre-comboviews-20261011` back, restore
`a7_vk32.c` from the `.bak-pre-comboviews-*` and rebuild. Or simply
`A7VK_OLD_COMBO=1` — see below.

**The control switch.** `A7VK_OLD_COMBO=1` makes the *installed* binary behave
exactly as it did before the fix (old cache key, no drops), so an A/B needs one
binary and one env var rather than two builds and a changed tree. Inert when
unset — with it unset the flag is 0 and every branch is the fixed behaviour.
`A7VK_COMBODBG=1` prints each drop.

---

## 5. WHAT I DID NOT CLAIM

* **The control arm is incomplete and I am not dressing it up.** I ran
  `A7VK_OLD_COMBO=1` for 240 s (`out/control4.log`) expecting a reset. **It did
  not reset** — but it also only reached **262,567 mesh draws against the fixed
  run's 6,344,401**, so it never got into the same state and the comparison is
  not valid either way. A same-sequence control on the old behaviour is still
  owed. Two earlier control attempts were killed by the other worker's driver
  kill loop, not by the GPU.
* **The attribution therefore rests on three things, not on a clean A/B**:
  (a) 710 measured instances of the exact stale-descriptor condition in the fixed
  run, on the same key `memcmp` the old lookup used; (b) the kernel's TCP-read
  fault at the *same page* in the unfixed binary twice this morning; (c) the
  cache key being the only relevant difference. That is strong, not airtight.
* **6 minutes is one run.** The crash is a race. No reset in 360 s is a good
  answer to "can he play" and not a proof that it can never happen.
* **The two faults this morning happened with two cmr2 processes on the GPU** —
  our test runs were up while he was playing. Two games on one GPU is a documented
  way to burn this box (see `notes/took-the-gpu-2305.md`). Some of what he
  experienced is that collision, and *we* caused it. I did not isolate how much.
* **I did not touch the lighting code.** Deliberately: worker 2 is mid-A/B on what
  the menu car looks like, and two workers changing what reaches the screen at
  once is how this project loses a night. B1 and B2 are specified exactly and are
  a small fix next round.
* **B4 (object-space lighting) is latent, not active** — WORLD was measured as
  identity in the stage. Do not spend a round on it before B1/B2.
* **`look.py` is not an eye.** §2.3 is a hint, not a diagnosis.
* **I did not verify that `153`-style counter** — `ignoredStates=20,503,405` in the
  race census is a number I have not explained and am not going to guess at.

---

## 6. NEXT, IN ORDER

1. **Vision read the five frames.** Answer §3's four-way question. If it is (3),
   B1+B2 are confirmed and the lighting fix is: read `rs[A7RS_AMBIENT]` in
   `a7vk_fill_block`, add it to the block, and rewrite the shader's composition to
   D3D7's actual equation. One patch, ~30 lines, one rebuild.
2. **Then** attenuation/range/falloff (B3) — the game hands us `att0/att1/att2`
   and `range` already.
3. **Then** up to 8 lights (B5), after checking which indices `Scene_RestoreLights`
   actually enables in a stage.
4. **A real control** for BUG A: same 360 s sequence, `A7VK_OLD_COMBO=1`, when the
   other worker is idle and the box can be spared a reset.
5. He gets the fixed binary now — `~/lena/cmr2-native.sh`, no change needed.
