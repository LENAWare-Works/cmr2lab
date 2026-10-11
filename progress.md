# progress.md — Lena on the Deck, reporting to Lena on the phone

**Rewritten whole, 2026-10-11 11:1x EEST.** This file is not appended to: each round
replaces it, so a stale claim cannot sit above a fresh one. The old append-log — every
dated block from 2026-10-10 up to 10:28 today, including the ones that turned out to be
wrong — is kept verbatim in [`docs/progress-archive.md`](docs/progress-archive.md).

Every number below names the log, binary or command that produced it. Where a number
came from another lane's run rather than mine, it says so.

---

## 1. RIGHT NOW

**The play binary on his icon is NOT the one this section used to name. Relinked at 12:04:43;
the bytes he drove two stages on at ~11:20 are preserved, and both pass the drive gate.**
(corrected 2026-10-11 15:1x, §1 was written 11:1x and went stale four minutes after the clock moved)

| | |
|---|---|
| binary ON DISK NOW | `work/PLAY/out-plain/cmr2`, md5 **`9ecbf87bb8650a3883b188f4e77890e4`**, 17,714,716 bytes, mtime **2026-10-11 12:04:43** |
| the bytes he actually drove (11:02 link) | md5 `80d927b54f597dbb2ad7590ddb6875e7`, 17,703,640 bytes — preserved at `out-plain/cmr2.bak-pre-pause-unlatch-20261011`, byte-identical to `work/HUD-2D/out3/cmr2` (two lanes, same tree, same bytes, 10:45) |
| does each drive? | yes, both — `cmr2_drives` returns **0** on `9ecbf87b…` *and* on the `80d927…` backup (`tools/drivecheck.sh`, re-run 15:14 on these exact files) |
| what the 12:04 relink changed | two things, by `nm -S` symbol diff: **GameInfo** (pause-unlatch, `GameInfo.cpp`) and **rhi/a7_vk32.o** — `build-play-lre.sh` links the *shared* RHI object, so `9ecbf87b…` is the first binary in the workspace carrying the peer's 11:36–11:47 near-plane work (21 new symbols, `g_nearclip`, `g_nearw`, `ap_update`, …) |
| his own launches, from the launcher's log | the whole ledger is **three lines, all `80d927b54f59`**, last one `2026-10-11 11:06:05  LAUNCH  …/out-plain/cmr2  md5=80d927b54f59  skipped-dead: none` (re-read 15:1x). **Nothing after 11:06:05** — so a run he made after 12:04 did *not* come through the gated launcher, and which bytes he was looking at then is not provable from this log either way |
| and it is alive | a `cmr2` process was running while this was written — but it is the **menu-car lane's** build (`MENU-CAR-FLATTENED/out-md9/cmr2`, pid 277263, started 15:03), not his play binary. The GPU is not free |

**The deadness window, and why it matters more than any single number here:** from
**08:39:06 to 11:02 today** no binary in this workspace could move a car. Our own
instrumentation had deleted two statements of game code (a `str.replace` anchor that
was the code itself — §2.4). Anything measured in that window that assumed a car could
be driven, steered, or that the physics stepped, was measured in a **frozen world**,
including the session he played at 10:03. That window is closed, and the fix is a gate
rather than an order, so it cannot reopen silently.

**The GPU no longer dies.** The kernel ledger, read with `journalctl -k` just now:

```
ring gfx_0.0.0 timeout   12      (-1 in the last 12 hours)
ring gfx_0.1.0 timeout    3
MODE2 reset              14
Faulty UTCL2 client ID: TCP   3
last GPU fault in the log: 2026-10-11 07:31:55
```

Thirteen kernel resets between 22:50 and 23:14 last night were ours (that document's count, `docs/GPU-LIFETIME-FIX.md` §1); the two this
morning (07:25, 07:31 — the ones that took his display down mid-session) were a second
hole in the same class of bug, closed at 08:06 (§2.2). Nothing since.

**What is owed, and it is one run.** The static gate says the play binary drives; a
peer ran these exact bytes 10:51–10:59 (11,753 frames, 0 panics) but without the drive
trace switched on, so **the car-moves proof on the shipped bytes has not been taken**.
It is cheap: `DECK_RACE_TRACE=1` is already compiled into that binary, and one
`drive.py` run turns "the gate says it can" into "it did". Until that exists, this file
says *drivable*, not *driven*.

**The skybox signature the phone asked about (15:0x):** "game UI present, no 3D stage content"
is a **different signature from the 10:06 state** (skybox and no UI at all), and he finished two
full stages at ~11:20 — so stage loading works and this is an intermittent, not a wall. The one
fact that matters for it is the md5 row above: the binary changed under him at 12:04:43.

**Also in flight right now, with no result to quote yet:** the sky/Finland lane
(worker 2, started 11:07), the HUD-2D lane's round on the in-race HUD, and the menu-car lane
(`out-md9`, running on the GPU as this was written).

---

## 2. DONE — finished and verified

### 2.1 The stage's textures were never decoded (DXT5) — the biggest single find of this project

The port was copying the **compressed block stream** of a DXT5 surface into a 32-bit
texture surface as if the bytes were pixels. Every road, verge, terrain, grass, tree
and building texture in the game went through that copy.

* The chain, joined at the copy: `CGraphics::LoadDDSTexture` → `DeckSurface7::Blt`,
  with the source surface created as `FOURCC=0x35545844` (DXT5) and the first bytes
  read out of it being `a0=0x64, a1=0x65` then six index bytes — a DXT5 block.
  The game never decodes DXT itself; it hands the blocks to a blit and expects the
  driver to convert. **The port implemented the decoder the frontend needs (TGA) and
  not the one the stage needs.** (`docs/DXT-COPY-PATH.md` §1)
* **Every DDS texture in the retail install is DXT5.** I swept all 582 `.bfl`
  containers on disk today with the repo's own reader: 581 readable, 26,132 entries,
  **7,804 DDS entries, fourCC histogram `{DXT5: 7804}`** — not one of anything else.
  In the run's own log, the stage's texture loads are `181 DXT5`, zero other.
  (My sweep, 11:1x today; `tools/bfl-read.py`.)
* **The fix** (`tools/fixes/patch_dxt_blt.py`, `patch_dxt_exact.py`): `Blt` decodes
  DXT1/DXT5 when the source surface is compressed; `surface_fill_desc` reports a
  compressed surface as compressed (`DDPF_FOURCC` + `DDSD_LINEARSIZE`), which is the
  branch the game already has for it; and `Blt` marks its destination dirty. The
  decoder agrees with `ffmpeg` on alpha (4096/4096 texels) and to 1 LSB on RGB.
* **Measured, before → after:** the ground band's mean colour was `(142, 171, 159)` —
  chromatic noise. It is now `(115, 90, 15)`, against the terrain texture's own mean
  of `(116, 89, 17)`. Frame-wide distinct sampled colours went 268,522/385,323 →
  22,187/589,792: *fewer* colours, because it stopped being noise. `rd_ga.dds` and
  `ter_kn4a.dds` both decode to alpha 255 everywhere.

### 2.2 The GPU lifetime bugs — the thing that was killing every run at ~30 s

Two holes, same class: memory or a handle freed while a frame in flight could still be
reading it. Both were found in the kernel log, not the game's log — the game's log just
stops.

* **Hole 1, fixed 23:09** (`tools/fixes/patch_gpu_lifetime.py`, 6 edits):
  `a7_upload_texture` destroyed an image and freed its memory with no wait while a
  frame submitted one or two presents ago could still have it bound in a descriptor
  set; and the upload path reset and re-recorded **the frame's own command buffer**
  (`p->cmd[0]`) while the queue was still executing it. The kernel names the fault
  exactly: `Faulty UTCL2 client ID: TCP` (the texture cache pipe), `RW: 0x0` (a read),
  from an unmapped page. The shader never retires, the ring times out, the kernel
  resets the GPU, and the desktop's compositor goes down with it.
  **Measured:** before — every run died at ~30–40 s, 13 kernel resets in 24 minutes,
  including one run with no instruments attached at all (so it was never our harness).
  After — 3 runs, **ring-timeout delta 0**, one of them **165 s / 8,124 frames /
  1,475,544 draws / 3,299,876 triangles**. (`docs/GPU-LIFETIME-FIX.md` §3–§4)
* **Hole 2, fixed 08:06** (`tools/fixes/patch_combo_views.py`, 12 edits): the
  descriptor-set cache was keyed on the texture **id**, so a draw could be handed a set
  naming an image view that had been destroyed seconds earlier. The fix keys on the
  **view** and frees stale sets.
  **Measured:** the mechanism fired **710 times** in one 360 s run; that run submitted
  **6,344,401 mesh-FVF draws**, 72.7 M triangles, 20,662 frames, **0 GPU resets, 0 page
  faults, no display loss**. Every previous round of this project published **0** mesh
  draws. (`docs/DEATH-AND-LIGHT.md` §1.3–§1.4)
* **What this means for the wall:** the order of the problem was wrong in every plan we
  had. It was not `frontend → state fidelity → crash → race`. It was
  **`ring timeout (every run, ±30 s)` → fixed → the game reaches its own frontend and
  drives its own 3D path**. (`docs/GPU-LIFETIME-FIX.md` §7)

### 2.3 The vertex-base double-subtract — the road was drawn from the wrong vertices

`DeckDevice7::DrawIndexedPrimitiveVB` shifted the vertex base by `startVert` **and**
subtracted `startVert` from every index. The two cancel, so `startVert` was lost, and
every triangle of a part whose base was not 0 was addressed outside the window it was
handed. The game's own loader had already re-based those indices
(`Mesh_BuildParts`: `pData[k] -= minIndex`) and draws them with
`startVert = vertexOffset + minIndex` — the port re-based them a second time.

* **Measured** (`DECK_IDXTRACE=1`, one ~90 s run): of **404,000** indexed draws with a
  non-zero base, **404,000 (100.00 %)** fit the game's convention (`relOk`) and
  **0** fit the port's (`absOk=0`). Of 15,969,393 indices, 100 % are inside
  `[0, numVerts)` as the game wrote them, and 2.19 % are after the subtraction.
* **The fix** (`tools/fixes/patch_idxfix.py`): the re-base is off by default;
  `A7VK_IDXBASE=sub` restores the old behaviour for an A/B in one binary.
* **Measured, before → after:** road texture `RD_GA` / id 102 went from **0.0** screens
  of coverage (2,000 draws) to **347,599.57** — the largest single coverage in the
  frame. `MRG_KN1` 0.0 → 237,993.76; `MOU_TER4A` 0.0 → 210,545.06. The frame at t=78:
  clear-colour pixels 57.9 % → **0.0 %**, distinct sampled colours 817 → **2,535**.
  (`docs/ROAD-TEXTURE-OWNER.md` §6–§7)
* **And the previous claim was withdrawn in public.** "Every `RD_*` has cov=0.0,
  draws=0" was an artefact of the instrument twice over: it printed only the top ten by
  coverage, and it selected ids by `cov > 0.0` so a texture with 2,000 draws and no
  area was never printed. The corrected instrument prints every id and selects by draws
  **or** coverage. (`docs/ROAD-TEXTURE-OWNER.md` §3)

### 2.4 The drive loop, deleted by our own tool, and restored

**This is the one we did to ourselves, and it goes in the open.**

On 2026-10-11 at **08:39:06** the round-2 instrumentation
(`work/RACE/patch_racetrace.py`) used two real statements of game code as its
`str.replace` **anchor**:

```c
    Physics_UpdateRateHold();
    g_unk0x00538124 = Car_UpdateEngineNoteFalloff(&g_unk0x00537f60);
```

— and its replacement block did not contain them. So applying the patch **deleted
them**. The second one assigns the bound of the per-car drive loop, so with it gone
the loop never ran one iteration, no car was ever given an input, the physics never
stepped, and every car sat frozen — **in a binary that still booted, still presented
frames, and still looked like a game.**

* **The window is 08:39:06 → 11:02.** Four binaries were in that state, including
  `work/PLAY/out-plain/cmr2` — **the one Miami plays** — and the Desktop icon was
  still launching it. The session he clicked into at 10:03 was a frozen world.
* **It was never missing from the port.** The statements are in the tree at
  08:38:50 (`md5 ae4a118c0b8f0fe9c7c499d696ec98bb`), in the upstream decompilation, and
  in every tree backup from 2026-10-09 23:33 onward. The tool's own two backups prove
  the deletion: they are the same file, byte for byte, taken either side of the patch.
  (`docs/DRIVE-LOOP-REGRESSION.md` §1)
* **Restored and measured** (220 s attract run, pure idle, no input): the loop iterates
  **3,650** times (`f24` = 3,650 = 3507·1 + 51·2 + 12·3 + 1·5, the loop's own counter
  agreeing with its bound), the physics steps at **~24 Hz**, car 0 accelerates to speed
  **101,958** and travels x 28,472,962 → 45,951,805. Before the restore: `steps=0`,
  car 0 speed 0, every frame. (`docs/DRIVE-LOOP-REGRESSION.md` §3)
* **And the honest part of the measurement:** that same run shows the car driving fast
  for ~1,600 frames, then **grinding in place with the throttle on for ~36 seconds**
  (0.08 world units of net travel), then the demo ending and another starting. Miami's
  *"she can't drive for shit"* is not a crash loop — it is a car that stops making
  progress. Whether that is scenery or an AI with nowhere to go is **open**, and it is
  the next question for that lane, not a finding. (`docs/DRIVE-LOOP-REGRESSION.md` §5)
* **So it cannot recur silently:** `tools/drivecheck.sh` asks the *file* whether it can
  drive (`cmr2_drives <bin>`); `tools/loopcheck.sh` asks it of every binary in the
  workspace; `build-play-lre.sh` refuses to install a build that fails the check;
  and the Desktop icon now launches the first candidate that **passes** it, refuses to
  start anything if none does, and logs every launch with its md5. A hardcoded order
  would have rotted within the hour — in this workspace a binary *path* is a name, not
  a build. (`docs/LAUNCHER-DEAD-BUILD.md` §1–§3)

### 2.5 The crash at 16 seconds, and the crash at 16 seconds after that

* **Before the GPU work there was a panic**, not a hang: `index 6484 out of bounds for
  type 'BYTE[6464]'` in `Profile_AssignAvailableCategory`, every run, ~16 s in. Cause:
  `zig cc` at `-O0` is Zig's **Debug** mode, so clang's `-fsanitize=array-bounds` is on
  and the Zig ubsan runtime **panics** instead of printing. The decompiled source forms
  pointers past the end of arrays on purpose, because that is what MSVC6 emitted.
  Measured on this toolchain: `G + 5` traps, `(char*)G + 5` does not, so only the
  subscript form is instrumented. **Seven sentinel sites in three files** were respelled
  as casts; no loop bound, iteration count or write offset changed.
  (`docs/PLAY-CHECKPOINT.md` §1–§2.)
* A **second** fatal trip found the next day was a misaligned `int *` load in
  `OptionMenu_LoadRallyRecords` — i.e. the fatal set is *"any UB the original binary was
  allowed to rely on"*, which is unbounded in decompiled code. Chasing it site by site
  is a treadmill, so the answer is **two builds on purpose**: `out-plain` (the
  launcher's default) with UBSan **off** for the decompiled game objects, and the
  checked build kept for finding defects. The platform layer stays checked in both,
  because it is hand-written and a misalignment there is a real bug.
  (`docs/PLAY-CHECKPOINT.md` §8.)

### 2.6 The black background — one line in our own renderer

The frontend's own backdrop colour `0x9cb4ac` never reached the swapchain, because
`CGraphics::ClearTarget()` clears `D3DCLEAR_TARGET` and then `ClearZBuffer()` clears
`D3DCLEAR_ZBUFFER` with colour `0xff000000`, and the RHI stored the colour on *any*
clear — so the Z clear, the last one every frame, won. Fixed: only a clear carrying
`D3DCLEAR_TARGET` owns the colour. **Verified per-pixel on the binary the launcher
runs:** legal notice 94.8–95.9 % exactly `0x9cb4ac`, 0.0 % exactly black; menu at
t=79 s 60.5 % clear colour, 0.0 % black.
The Bink theory for the black screen was wrong and is dead: the stub intro movie is
why the notice waits for a keypress, and it has nothing to do with the backdrop.
(`docs/GPU-LIFETIME-FIX.md` §6)

### 2.7 The data tools, which is the half of this repo you can use today

* **581 / 581 containers round-trip byte-identical** — re-ran it myself just now:
  `./cmr2lab repack <install>` → `repack VERIFY: 581/581 byte-identical (skipped 1
  non-container)`, 8.4 s wall, exit 0. A modified container is therefore structurally
  indistinguishable from one the game shipped.
* **259 / 259 car `.c3d` close exactly** on
  `48 + Σ(count×stride) + TEXCOUNT×24 + TEXCOUNT×260 == filesize` (3,803 texture
  references, zero mismatches, 2026-10-10; `tools/c3d.py`).
* **The format census, measured today:** in the 206 track containers, 220 car
  containers and 5 frontend containers, every DDS entry is DXT5 — 7,804 of them in the
  whole install, zero of any other DDS format. The stage's road textures are the same
  format the decoder now handles.
* **33 of 66 translation units compile on `x86_64-linux-gnu`; 66 of 66 on i386**
  (the second only with `-Wno-c++11-narrowing`), with the i386 build kept deliberately
  as a diagnostic oracle. All 33 x86_64 failures pass on i386, i.e. they are blocked by
  pointer width and nothing else. **These are compile-level numbers** — ASAN does not
  build on this toolchain, so there is no runtime evidence about the port's
  correctness, and this file will not imply there is.
  (`docs/P3-P1-REPORT.md`)

---

## 3. IN PROGRESS — with honest fractions

**The lighting. Fixes landed: 0 of 4. The defects are enumerated and measured.** Miami
said the lighting is all fucked up (2026-10-11), and the answer is four defects, in
order of confidence, none of them fixed yet:

1. **`D3DRS_AMBIENT` (state 139) is stored and read by nothing.** In one 360 s race the
   game set it **548,489 times with 12 distinct scene ambients** — all twelve
   discarded. In D3D7 fixed function the ambient term is `material.ambient ×
   scene_ambient`; we substitute `material.ambient` alone.
2. **The shader composes the equation wrong:** `base.rgb *= (matAmbient + matEmissive)`,
   then adds light diffuse — D3D7 is `matEmissive + matAmbient·sceneAmbient +
   matDiffuse·Σ(lightDiffuse·N·L)`. With `SetMaterial=1` in the whole run (the material
   is constant opaque white), the prediction is a **blown-out, flat** picture, and the
   frames bear that out.
3. **No attenuation, range, falloff, spot cone or specular** — `lightDir[i].w` carries
   the range into the block and the shader never reads it.
4. **Latent, not claimed as the cause:** the shader lights in *object* space while the
   game supplies world-space lights. Correct only while WORLD = identity, which it was
   for the whole race — a landmine, not the active bug.

Not wrong, and measured so nobody "fixes" them: `LightEnable` reaches the RHI (888,133
light-state changes took effect); `SetLight`/`D3DLIGHT7` are plumbed through to the
shader; `DIFFUSEMATERIALSOURCE = D3DMCS_MATERIAL` is still the last value, so the
port's hardcoded material-source is right and the "use the vertex colour" fix would
have been **wrong**. (`docs/DEATH-AND-LIGHT.md` §2)

**The collapsed car on the setup screen. Measured fraction: 0 — no cause has been shown to
be the cause.** What has moved is the list of what it is **not**, and two of those closed by
measurement since the last rewrite (mine, `work/MENU-CAR-FLATTENED/`, run 11:0x–11:2x):

* **The index base is not it — and the ticket's hypothesis is backwards.** Measured on the car
  page itself, both arms, same binary, one env var apart (`out/md_car_raw.log` vs
  `out/md_car_sub2.log`, `A7VK_IDXBASE=sub`):

  | | default | `sub` (the old re-base) |
  |---|---|---|
  | indexed draws parsed | 3,012 | 3,036 |
  | indices out of range as received | **0** | **2,778 (91.5 %)** — `65506, 65505, …` = −30, −31 |
  | mesh NDC box (GEOTRACE) | x=[−0.811 0.741] y=[−0.422 0.460] | **x=[−76577.33 3.60] y=[−92242.79 20664.31]** |
  | owner-map coverage on that page | 463–658 cells, 2,073 tris (18–25 %) | 21 cells, 48 tris (0.8 %) |

  *"All mangled and jungled up into one flat piece of paper"* is what the **old** setting
  produces, in the numbers. Reverting the fix to "un-break" the menu would create it.
  Also dead: the format/stride theory (float48, part-sized, `idxInRange` yes on the default).
* **The capture that this section used to call the missing piece now exists.**
  `frames/md_car_raw.000.ppm` is run frame **8517** with **1,377 car draws in flight** — and it
  is **96.417 % one colour (140,150,158), 232 distinct colours**. The car's own owner cells
  (rows r14–r27, cols c8–c53 of the 64×40 map = **x 160–1080, y 280–560 px**) are empty in it.
  So on the default arm the car is **submitted, textured, correctly transformed and invisible**;
  one capture in 41 landing inside its window was the binding constraint, and it is now closed
  for this page (`docs/MENU-CAR_car-frame.md`, PNG in `frames/`). All three of today's runs
  agree: no capture anywhere, pre-fix or post-fix, has a car in it.
* Same run, same frames, GEOTRACE (`[GEO] f=8460/8520/8580`): obj box
  `x=[-2.1 2.1] y=[-0.5 0.7] z=[-0.9 0.9]` (a car), `w=[4.076 6.158]`, `ndc
  x=[-0.811 0.741] y=[-0.422 0.460]`, `behind=0 nonfinite=0 draw_behind=0 draw_alloff=0`,
  `tex=1377 notex=0`, and the render-state line is **identical** to the frames with no 3D at
  all. Everything the software can see is right, which is why the answer is now narrowed to:
  **the fragments are discarded after submission (alpha test, cull/winding, or a dead texture
  binding) or written in the backdrop colour.** Next instrument: `A7VK_TEXDUMP` on the car's
  own texIds (37/39/40/41/44) to read their alpha, or one run with alpha test forced off.
* **One number in the previous rewrite is corrected here:** *"the option screen's 3D submits
  9,628 draws and rasterises zero triangles"* is an artefact of reading a **cumulative** census
  counter as a per-frame one. That screen draws ~675 parts/frame between frames ~2400–3600 (and
  the car page 1,377–1,620 draws/frame at 8460–8580) and then the game stops calling
  `DrawIndexedPrimitiveVB` on it altogether. The peer's 40-of-41-captures-outside-their-window
  finding is real and is the reason the earlier frames could not settle it — but it is a
  capture-latency fact, not a rasterisation one.

* **The car page's own textures, read one at a time, and the alpha question turned into a list.
  Measured fraction: still 0 — no cause shown to be the cause.** Round 6 of
  `work/MENU-CAR-FLATTENED/` (12:19–12:4x EEST, four guarded runs) joined three traces that had
  never been joined (`join_ids.py`): the game's own load (`[TEX] TGA <file> WxH surf=<p>`), the
  port's id (`[TEXREQ] DD7 NEWID surf=<p> -> texId=<n>`, `deck_dd7.cpp:1349`) and the bytes the
  GPU actually received (`[TEXDUMP] id=<n> … meanRGBA=… zeroAlpha=`, `a7_vk32.c:1589`).

  The car page's draws (`md_texcar2`, frames 4075–4200, option camera `eye=(0.14 -0.09 -5.00)`)
  bind **9 textures and 2,624 triangles, 419→601 owner cells (16.4→23.5 % of the frame)**:

  | texId | size | alpha in the uploaded bytes | tris |
  |---|---|---|---|
  | **47** (the body) | 1024x1024 | meanRGBA=(115 115 122 **254**) zeroAlpha=0.2 % | 1,175 |
  | 50 | 512x512 | (62 74 76 199) 3.6 % | 207 |
  | 46 | 256x256 | (67 67 66 200) 21.5 % | 424 |
  | 48 | 512x512 | (17 29 30 208) 0.0 % | 116 |
  | 49 | 256x256 | (46 45 44 173) 31.8 % | 148 |
  | 45 | 1024x1024 | (115 115 122 254) 0.2 % | 280 |
  | 51 | 256x128 | (59 53 50 255) 0.0 % | 80 |
  | **52** | 256x256 | (48 20 8 **0**) zeroAlpha=**100 %** | 58 |

  **The body's texture arrives with alpha 254, so "its texture is transparent" is dead for the
  body** — and so is the tidiest form of the 24-bit theory. What survives is the *computed*
  alpha (`a7vk3d.frag`: `c.a = combine(alphaOp, alphaArg1, alphaArg2, t0, vDiffuse)`), i.e. the
  vertex/material diffuse alpha, which nothing prints yet.

* **Five captures inside the car's window, and the frame does not change.** `md_texcar2`'s
  captures `.001…005` are frames **4078–4179** — five frames *inside* the car's own draw window,
  522–1,653 `MENUDRAW` lines in flight — and they are **byte-identical**
  (md5 `5b179735cafb5f48e45d6a79fed05d5d`): `distinct=3915`, dominant `(140,150,158)` **96.040 %**,
  non-dominant 3.96 % in bbox `x[0..926] y[209..438]`, and the 64x40 grid shows only UI. The
  2,624 submitted car triangles rasterise nothing, five times over. This closes the "one capture
  cannot separate…" caveat by showing that *several* captures cannot either.

* **A real port bug, found in the source, that is NOT the car's cause — but sits on the same
  page.** `DeckDevice7::EnumTextureFormats` (`deck_dd7.cpp:1162-1179`) offers **one** format,
  32-bit A8R8G8B8 *with* an alpha mask, on purpose. Real devices also offer a no-alpha 32-bit
  format and the game is written for it (`Graphics.cpp:1982`: if no 24-bit format was enumerated,
  substitute the 32-bit one). Then `CGraphics::LoadTGATexture`'s two branches disagree about the
  same case — 16-bit dest writes `a = 0xff` for a 24-bit source, **32-bit dest writes `a = 0`** —
  so with the port's 32-bit surfaces **every texel of every 24-bit TGA is written alpha 0**.
  TexId **52** above is that, measured: real RGB `(48 20 8)`, alpha 0 on 100 % of texels. It is a
  58-triangle part on this page and a defect in its own right (fix shape: offer the no-alpha
  format *and* sample no-alpha textures as alpha 1.0, as a driver does) — not the ticket's answer.

* **And the ready-made A/B cannot be aimed at this page.** `A7VK_AB=0:opaque` (blend off + alpha
  test off for every draw) is the obvious experiment, and it was run this round **on a card that
  was verified free** (`ps` empty, `gpu-guard.sh --list` empty, GPU 0 %): the run stayed at
  `frontend resource mode -1 -> 0` and **never reached the menu**, exactly as the two 11:2x runs
  did. That retires the "a peer held the card" explanation and leaves the mode harness itself as
  the suspect. The instrument that replaced it is 3D-only: `LENA_MENUOPAQUE=1` in
  `deck_dd7.cpp` builds `out-md3/cmr2`, which forces `ALPHABLENDENABLE=0`/`ALPHATESTENABLE=0`
  **around indexed 3D draws only** and restores them after, plus `LENA_MENUDRAW_ALPHA=1`, which
  prints each draw's atest/aref/afunc, blend src/dst, stage-0 alpha op/args and the first
  vertex's own diffuse/specular dwords. Both inert when unset.

* **The alpha inputs of the car's own draws, printed for the first time — and the arm that
  removes them still does not put the car on screen.** `LENA_MENUDRAW_ALPHA=1` (new, in
  `deck_dd7.cpp`, inert when unset) prints what the shader is built with:

  ```
  [ALPHADRAW] #1 fvf=0x2d2 stride=48 atest=1 aref=1 afunc=7 blend=1 src=5 dst=6
              aop=4 aa1=2 aa2=0 v0_off24=ffffffff (a=255) v0_off28=ff000000
  ```

  alpha test **on**, ref 1/255, func GREATEREQUAL; blending **on**, SRCALPHA/INVSRCALPHA;
  stage-0 alpha op MODULATE of (DIFFUSE × TEXTURE); the first vertex's own diffuse dword is
  opaque white. With the body texture at alpha 254 that computes `c.a ≈ 0.996` — a draw that
  should paint. Then `LENA_MENUOPAQUE=1` (also new: `ALPHABLENDENABLE=0` and
  `ALPHATESTENABLE=0` around **indexed 3D draws only**, restored after each) was run on the car
  page (`md_opq3`, f3650+, 587 cells / 2,747 tris): **the car is still not there.** Its cells
  hold 1.60 % non-dominant pixels against the default arm's 11.01 % — and every one of those
  11.01 % is 2D chrome. So the fragments are not being discarded by alpha test and are not being
  blended away: **alpha is now excluded by measurement**, and the fork is down to the vertex the
  GPU reads (the port's CPU-side view of the same buffer is car-shaped — `[GEO]` obj box
  `x=[-2.1 2.1] y=[-0.5 0.7] z=[-0.9 0.9]`, `behind=0 nonfinite=0`) or the fragment never being
  written at all. Caveat kept: the two frames above come from two runs, so this is "no car with
  alpha off on that page", not a same-frame A/B — the same-frame A/B is what `LENA_MENUOPAQUE`
  now makes possible for the next round (`A7VK_AB` cannot be aimed at this page at all, above).

  PNGs, with the full table: `frames/opt-preview-car_20261011-1235_CAR-PAGE_default-arm.png`,
  `frames/opt-preview-car_20261011-1237_CAR-PAGE_alpha-off-arm.png`,
  `docs/MENU-CAR_car-page-round6.md`.


**"A legible stage." Honest fraction: no measurable fraction on the picture — but the
inputs to it are now correct.** The road textures draw (347,599 screens of `RD_GA`),
the terrain draws in its own colour, and the transform is the game's own — the port's
projection reproduces `CGraphics::SetProjection` + `View_SetPlayerProjection` to four
decimals, aspect **1.600** exactly. What is *not* claimed: a road with verges, a car, a
HUD, a timer. The leading candidate for what the picture still is: **near-plane
blow-up** — in a static-camera shot the geometry spans clip `w ∈ [-89.3, +121.5]`
against a near plane of **5.86**, with NDC `x` reaching **-2.8 × 10⁷** — i.e.
screen-spanning triangles with a near-flat texture gradient. That is a hypothesis with
a measurement behind it, not a diagnosis. (`docs/CAMERA-AND-NEAR-PLANE.md`, `docs/FRAMING.md`)

**The in-race HUD. Question answered; the render is not.** All in-race HUD drawing is
on the transformed-lit 2D path (`Font_DrawChar`/`Sprite_Queue`/`Quad2D_QueueFixedTriangle`
→ FVF `0x1c4`), and the port is **not** refusing 2D draws — `Sprite_Queue` ==
`Sprite_DrawLayer` to within 176 draws out of 1,452,997 over a run. The "336/frame
frontend → 5/frame race" collapse is the **game never asking** in that state; in a
player race the same binary carries the whole HUD (66–70 sprite draws/frame, ~63 of
them glyphs). Whether it lands correctly on the swapchain is the next measurement, and
the instrument for it (`work/HUD-2D/patch_hudtrace.py` — 17 insertion sites, 8 files, `--revert` provided) is built and inert.
(`docs/HUD-2D.md`, 11:0x today)

**The car actually moving, on the bytes he plays. Fraction: 1 run owed of 1.** See §1.
The gate says the binary can; the trace that would say it *did* is compiled in and has
not been switched on for that build.

**Analog input reaches the car. Delivered: yes. Consumed: 0 of 1.** The port drives the
real pad and the axes land in the game's own units (`lY = -59965` at full stick, full
scale `0x10000` is the game's own `DIPROP_RANGE`), and the port bug that made analog
impossible (`prop_id()` returning an object address, so every `RANGE` call returned
`DIERR_UNSUPPORTED`) is fixed. But the engine's throttle/brake axis is **axis 1** and
the port maps L2→axis 2, R2→axis 5 — so the pedal axis is fed by nothing. The fix is
port-layer (`axis1 = R2 − L2`) and is **not written**. Pad → frontend: **6 of 22**
tested inputs register above the measured bar; **4 of 22 are clean negatives and
explained** (X/Y/L1/R1 map to keys `ReadKeyboardDevice` has no menu bit for — a design
decision, not a bug).

**The last 33 translation units. Fraction: mechanical, not begun.** Every remaining
x86_64 error is one class — a pointer cast into a smaller integer type — at **1,377
distinct sites**, plus 7 size asserts (56 sites). One of those is a real bug worth
naming: `typedef long LONG` is 8 bytes on LP64 and Win32 `LONG` is always 4, which
compiles fine and silently corrupts every struct holding a `POINT`/`RECT`/`SIZE`.
Waiting on it: an ASAN build (`docs/PORT-PLAN.md` §6) — there is still **no runtime
evidence** about the port's correctness, only compile-level and run-level counts.

### and what is deliberately not claimed

* **A stage that looks right.** No legible road, no car on it, no HUD, no timer.
* **That the car can be driven in a race by a human, on today's bytes.** The gate says
  yes and a peer ran those bytes clean, but the trace has not been switched on.
* **Anything about driving quality.** The loop runs; whether the AI is any good is an
  open question with a measurement pointing at it (§2.4).
* **That the lighting is merely "a bit off".** It is four specific defects, one of
  which throws away 548,489 values per run.
* **Any number here about the port's correctness at runtime beyond what the logs say.**
  ASAN does not build; compile-level counts are labelled as such.

### 2.6 HIS REVIEW, AND IT IS THE ONE THAT COUNTS — "textures were overall better"

**Miami played the demo on the Deck at 2026-10-11 ~07:4x and said, in his own words:**
*"the demo also worked here with Ford Focus and Kenya rally untill it didn't and froze
which was coool / again super janky and white box under the car, textures were overall
better tho"*.

That is a **person who drives the game** reporting that the DXT5 decode fix (§2.1) is
visible on real hardware, unprompted and without being shown a texel count. It is the
only review that counts, and it is reported here **as his observation, not as a
number** — the texel-level evidence stays in §2.1 and the two must not be conflated.

Two further readings of the same sentence, both measured, are in the round-7 note for
this ticket:

* he reached a race **with a car he selected** (Ford Focus, not the default) — the
  car-select path and the per-car model + livery load work well enough to be driven,
  so do not "fix" that path on the strength of the white box;
* the freeze he hit at 07:25/07:31 on 2026-10-11 is **not** the same kernel event as
  the 2026-10-10 cluster: no ring timeout was recorded, and the reset was triggered by
  **an amdgpu page fault raised by the `cmr2` process itself** at address
  `0x8010682_000` (see the round-7 note). Same symptom, different mechanism.

*(appended by the WHITE-BOX-UNDER-CAR ticket, round 7. If this paragraph is missing on
re-read, a concurrent writer rewrote the file — the copy is kept at
`work/WHITE-BOX-UNDER-CAR/progress.md.before-r7`.)*

### the setup-menu car, round 7 — the index fix is not what hides it; CULLING is

The car in the pre-race setup menu is still not right, but this round moved the
needle for the first time in four rounds, and it moved off the theory you sent.

**Your index-base hypothesis is dead, and it stays dead.** It was already
measured dead twice (the car's own indices are relative and in range; under
`A7VK_IDXBASE=sub` the car's vertices come out spread over ±76,000 in NDC — the
old path IS the mangled flat sheet). Round 7 added no scoping and reverted
nothing, because nothing needs scoping.

**What round 7 found instead, in two steps.**

1. **The port's backface culling was eating the car.** The owner map that said
   "the car is on screen, 648 cells, 2,073 triangles" is a *backface-agnostic*
   software rasteriser: it counts every triangle with a positive w and never
   tests facing. So a car that is 100 % culled still produces that map, and the
   screen still shows nothing. The port maps `D3DCULL_CCW` to Vulkan's
   `CULL_MODE_FRONT` + `FRONT_FACE_COUNTER_CLOCKWISE` once, globally, for the
   race and the menu alike.
   **Forcing the cull mode off for indexed 3D draws only, on that page:**

   | capture, same page, same camera, car's draws in flight | distinct colours | content in the car's own cells |
   |---|---|---|
   | `frames/opt-preview-car_20261011-1350_CULL-ON_control.png` | 1,205 | 10.0 % (2D chrome only) |
   | `frames/opt-preview-car_20261011-1346_CULL-OFF_car-visible.png` | **14,159** | **22.0 %** |

   The cull-off frame has a textured **1081 × 258 px band centred on (670, 332)** —
   wide and low, exactly where the car's cells are — and the control frame has
   chrome alone. Same binary, same route, one forced state apart.

2. **The menu car's draws are the first thing in the frame, and 375 2D draws
   follow them** (`[MENUORDER] draws=407 3d=29 first3d=4 last3d=32`), so an
   overpainting 2D quad is now a named, still-open second suspect — the
   instrument that would name it is built and running.

**What this does NOT yet claim:** that the hidden object is a *car* rather than a
shape in the car's place (I measure pixels, I can't look), and the two arms are
two runs, not two frames of one run. The next step is a same-run, frame-scheduled
cull switch, and then the real fix — decide the winding per triangle from the
transform, the way D3D does, instead of trusting one global convention.

**And one warning that matters for every measurement on this box.** Round 7 spent
40 minutes of its own time proving why five route attempts in a row never got
past the boot screen: **the game received no keys at all.** The harness's
keyboard injector creates a synthetic evdev device that this machine will not let
the game read (`[KB] evdev: /dev/input/event11: Permission denied` — no `uaccess`
ACL for a device created outside a login session), and the game's own intake
would refuse it even with access (it scores such a device -2 and only takes
devices at +3). Keys reach the game only when they are sent **straight to its
window** (`xdotool key --window`), which is what round 7 switched to. The runs
that DID progress earlier today must therefore have been taking input from
*somewhere else* — another lane's injector — which is the same contamination
`work/DEMO-DRIVE-CRASH` reported at 12:02 from the other side. Anything measured
on this box through a scripted route carries that caveat, this round included.

### the setup-menu car, round 8 — the same-run cull A/B was run, and it comes back NEGATIVE

Round 7 ended with a lead and a promise: forcing `D3DCULL_NONE` around the option page's indexed
3D draws had put content into the car's own cells, so culling looked like the mechanism — but
the two arms were two *runs*, so the page could have differed. This round ran the same-run,
adjacent-frame version of it (a new env-gated instrument, `LENA_MENUCULL_PHASE=<frames>`, which
alternates the forced cull between `D3DCULL_NONE` and the game's own value every N frames and
logs every change with the frame number, so each capture carries its own arm from the port's
own log).

**On one page, in one process, 204 captures inside the 3D window, 102 under each arm: the two
arms are indistinguishable.** Mean car-cell content 11.65 % (NONE) vs 11.64 % (PASS); median
3,003 distinct colours both ways; and the cleanest case is exact — frame 3639 (`PASS`) and frame
3641 (`NONE`) are **the same 1,024,000 pixels**, md5 `f4eda0d799ecf08e94cf51efce221563`, both
pushed to `frames/opt-preview-car_20261011-1420_*`. **Culling is not what hides the car on this
page**, and round 7's lead is downgraded from "the mechanism" to "a variable that changes
nothing here". Two caveats, both measured and both in `work/MENU-CAR-FLATTENED/ROUND8-CULL-AB.md`:
the game presents each rendered frame twice, so a capture can repeat a frame rather than redraw
it; and the `[GEO]` state snapshot restores the game's cull after every draw, so it cannot
confirm the forced arm reached the pipeline — a submit-time state readout is the follow-up.

**What the tracing DID settle about the car, on the page itself** (`LENA_MENUPROJ`, 3,000 traced
draws, every one logged): the game asks for `D3DCULL_CCW` on the preview car itself
(`gameCull=0x3` on every line — it is the game's own state, not the port's); the transform is
never mirrored or degenerate (`det_raw = +3.19935`, `det_flip = −3.19935`, identical on all
3,000; 0 vertices behind the camera, 0 non-finite); and over the 3D window's **96,655 triangles,
40.7 % are wound the way `D3DCULL_CCW` KEEPS and 59.3 % the way it CULLS, with none degenerate**
— which is what a closed mesh looks like from outside, and which therefore also kills the strong
form of "the car is culled to nothing". The index-base fix is not re-based differently here than
on the race path, so it is not this bug either — re-confirmed on the page the ticket was written
about, not just at the call sites. **No render-path code was changed this round**: the binary
differs from the shipped one only by two env-gated instruments, so nothing can have been
re-broken, and the race path was not touched.

The one instrument this page still needs is specced in the same file and is arithmetic on bytes
the port already reads: compare each triangle's **screen-space winding with the direction of its
own vertex normal** (offset 12 of the same 48-byte vertex). A mesh whose outward faces come back
screen-CCW is wound the other way round from the port's global rule — which draws a car
inside-out, and "inside-out" is what "all mangled and jungled up into one flat piece of paper"
describes. No picture and no second run needed.

---

## setup-menu car r9 (2026-10-11 14:2x–14:4x EEST): the frame measured against the port's OWN rasteriser of its own draws — the car page's cells are 70–78 % background, in either y orientation

`work/MENU-CAR-FLATTENED/ROUND9-ENGINE-VS-SCREEN.md`, `cmp9.py`, `fit9.py`, `flip9.py`, `map9.py`.
No GPU run this round (the card was a peer's for the whole round: `work/RACE/out-rt10/cmr2`,
guard-verified) and no render-path code was changed.

`[OWNER]` is the RHI's own CPU-side rasteriser of the same triangles the draws submit, loaded with
the same 48-byte stride and multiplied by `b->mvp` — **the very block that goes to the GPU**
(`a7_vk32.c:2637` hands `&b->blk` to `ow_note`, and `b->blk.mvp` is what `a7vk_fill_block` negates
and memcpy's at `:2735`). Nobody had compared that prediction against a capture of the same frame.
This round did, cell by cell, at the owner map's own 20 px grid.

**What the engine says it drew on this page:** frames 3650…4000 of `md_proj9b` all report **438 of
2560 cells owned, 2747 triangles**, by 8 textures — `tex=36` 255 cells (the body), `tex=37` 89 cells
in two wheel-shaped blobs, `tex=38` 75 cells (the cabin), `tex=40` 19 cells. Rows 14–27, cols 7–52
= **x 140–1050, y 280–560 px**. It is a car, it is static, and it is what the port thinks it drew.

**What the frame shows, 8 frames of the same run:**

| `[OWNER]` frame | capture | engine cells | screen cells | both | engine-only | screen-only |
|---|---|---|---|---|---|---|
| 3650 | 3649 | 438 | 217 | 130 | **308** | 87 |
| 3700 / 3750 | 3699 / 3749 | 438 | 168 | 97 | **341** | 71 |
| 3800 / 3850 | 3799 / 3849 | 438 | 217 | 130 | **308** | 87 |
| 3900 / 3950 | 3899 / 3949 | 438 | 168 | 97 | **341** | 71 |
| 4000 | 3999 | 438 | 217 | 130 | **308** | 87 |

**70–78 % of the car's own cells are plain background colour on the frame**, and 40 % of the
screen's own non-background cells lie *outside* the car's footprint. It is not an orientation
error — the `[OWNER]` map's own y convention is ambiguous by construction (it maps ndc y=+1 to row
0 while the block it reads has had the y column negated for Vulkan), so **both** orientations were
tested: IoU **0.248** as printed, **0.287** flipped vertically, and **0.435** for the best of 4,000
scale × flip × offset candidates (a 2:1 shrink *and* a 180° rotation — the fit finding chrome, not
a viewport transform).

**Round 7's positive is retired on its own frames.** The PNG it shipped as "the cull arm shows the
car" (`frames/opt-preview-car_20261011-1346_CULL-OFF_car-visible.png`, md5 `4fe6c651bdc26e45d8e8e9d0811a0c0b`)
is byte-identical, at every sampled byte, to `md_mc_none_r1.043…046` — capture frames **4464, 4471,
4488, 4490**, four consecutive captures of one unchanging image — and against that run's own
`[OWNER]` car map it scores IoU **0.310** upright / **0.338** flipped. The arm that forces
`D3DCULL_NONE` on every indexed 3D draw of the car page does not put the engine's car on the screen
either.

**And the `853x533` that `MENUPROJ` prints is identified:** it is the frontend **render target's**
size (`DeckD3D7::CreateDevice`, `deck_dd7.cpp:1274-1284`, stores `d->viewport` = the render target
size; `[WIN]`/`[A7VK]` say the display and swapchain are 1280x800). The game does call
`SetViewport` (1200 times in 600 frames; `Game.cpp:2667` with a caller rect, `Game.cpp:2774` with
`(0,0,resX,resY)`, `Graphics.cpp:2995` for the shadow cube faces) — **and the port stores every one
of them and applies none**: `a7vk_record` sets the Vulkan viewport, the scissor and the shader's
own pixel mapping `pc.vp = (W/2, H/2)` from the **swapchain extent**, once per frame
(`a7_vk32.c:2782-2795`, `:2847`). Not the flat-car cause (it mis-scales, it does not flatten), but
a named port defect on exactly this page, and it is the reason the `[OWNER]` map *is* a fair
prediction of the frame.

**What did not move: no coherent car has been seen and none is claimed.** The question the round
sharpens: the port's own rasteriser of the port's own draws puts a car on 438 cells, and the GPU's
frame does not show it — in either y orientation, with culling forced off, and with alpha test and
blending forced off (checkpoint §44). Either the car page these runs reach is **not** the sub-page
Miami is looking at (a fork open since round 5, never closed), or the car's batches are dropped or
overwritten between the batch and the rasteriser in a way independent of every state the draws
carry. The next instrument is unchanged and still unbuilt: the normal-vs-winding test (vertex
normal at offset 12 vs screen-space winding, in `MENUPROJ`'s own hook), a submit-time cull readout,
and the `A7VK_SNAP` four-consecutive-frame fence.

Frames pushed with this block: `frames/opt-preview-car_20261011-1440_f3639_ENGINE-SAYS-438-cells.png`
(md5 `9b9f142d9b002852f442a138f622d427`) and
`frames/opt-preview-car_20261011-1440_f3639_CAR-REGION-2x.png` (md5 `24e329061cd9f34fd21005de841e0a3c`),
both from `md_proj9b` capture 002 = frame 3639, the frame whose engine prediction is the first row
of the table above. `git push origin HEAD` still fails (no credential helper on this box).

## setup-menu car r10 (2026-10-11 14:4x–15:0x EEST): the per-frame draw ORDER at last, and 96.4 % of that frame is the option menu's own CLEAR COLOUR

`work/MENU-CAR-FLATTENED`, run **`md_cov7`**, card taken at 14:46:02 through the standing guard,
binary `out-md7/cmr2` md5 `b051924366847f8226094d4dc26e3810`, with the round-7 instruments
**`LENA_MENUORDER=1 LENA_MENUCOVER=1 LENA_MENUCOVER2=1`** — which no run had ever carried onto
the option page's 3D window (round 7 built them, ran them on `out-md5` whose MENUCOVER output is
silently suppressed, and gave up when `md_cov6` never drew the car; every run since used `out-md7`
and never turned them on).

**What the page does, per frame, measured:**

```
[MENUORDER]  draws=406 3d=29 first3d=4 last3d=32 2d_after_last3d=374
[MENUCOVER2] 3d_first=4 3d_last=32 2d_after3d=374 cover2d_after_3d=2
             first  =(33 [56.0 46.0 987.5 653.5] ffb8b8b8)
             topmost=(34 [179.0 352.0 1223.5 683.5] ffb8b8b8)
```

* The car is **29 indexed 3D draws, 4th to 32nd of every frame**, and it is submitted
  continuously (the `[MENUORDER]` 400-frame budget all fired with `3d=29`).
* **374 2D draws come after it**, and the first two are big opaque quads covering its whole
  footprint. Their vertex colour fades per frame (cc→b8→b2→ab→d9→ee→f6→fe…→ff): a page fade.
* **And the frame they are drawn on is 96.38 % ONE colour: (140,150,158).** That colour is the
  **option menu's own clear colour** — `GameInfo.cpp:1788` `SetClearColour(1, 0x8d, 0x97, 0x9f)`
  = (141,151,159), one code off (measured on the pixel). The only other content inside the car's
  own rect x160..1080 y280..560 is **9.85 %** of pixels, and its two commonest colours are pure
  white (255,255,255) and pure black (0,0,0) — **menu text**, on a panel so flat that the mean
  horizontal gradient there is **0.00** (against 22.28 inside the text). **The page is almost
  entirely UNPAINTED: the car's 29 draws, and everything else that should fill that screen, leave
  no marks on it.**

**So the r7 question — "who paints over the car" — was asked properly and answered NO.**
`LENA_MENUSKIP2D` (new, `patch_menuskip.py`, built into `out-md8/cmr2` md5
`fe0c82daa709e6fa5486f9c230c15df3`) drops every 2D/TL draw whose bbox contains (640,420) while
`/tmp/skipnow` exists, in frames that have already submitted a 3D draw. Run `md_skip` took the
card at 14:55:35 and did it as a triggered same-run A/B: 10 s control → `touch /tmp/skipnow`
14 s → remove 8 s, captures every 0.4 s throughout. The port's own log names what it dropped:
`count=72 quads=18` per frame, twice per frame, `sz0=0.0000 rhw0=0.0000`. **The frames before,
during and after are the same file: md5 `40fd7369f33caaa7a303b1d5f7c24748`** — and that is also
the md5 of `md_cov7`'s captures from 10 onward, a different binary in a different run. Dropping
the covering draws changes **nothing**; the car is not hidden by 2D chrome.

**Frames pushed with this block.**
`frames/opt-preview-page_20261011-1500_r10_car-submitted-29-draws_INVISIBLE.png` (md5
`03ac7eca08fbe2d32ddf94abd27f7c52`) — the whole option frame with the car's 29 draws in flight:
menu text on the clear colour, no car. `frames/opt-preview-page_20261011-1500_r10_CAR-RECT_what-is-really-there.png`
(md5 `bcfaf0ee568973804674a9038b3ecfbc`) — the car's own owner rect x160..1080 y280..560 cut out
and shown on its own, so the absence is visible without hunting for it.

**What did NOT move: the car is still not on that frame and no fix is claimed.** Three mechanisms
are now excluded by measurement *on this page*: the index base (r5), culling (r8), alpha (r6),
the 2D draw order (r10). What r10 adds is the reason the previous rounds kept disagreeing with
themselves — **the frame is not a wrong picture of the car, it is an EMPTY one: the car's draws,
and the page's own fill, are not reaching the rasteriser at all.** The next instrument is
therefore not another state readout but a *drop test on the 3D path* (submit none of the 29 draws
and compare the frame: if it is byte-identical, the car's draws contribute zero pixels on this
page and the fault is in the 3D submit/raster path, not in composition) — `LENA_MENUSKIP2D`'s
twin, ten lines away in the same file. `git push origin HEAD` still fails on this box (no
credential helper); the commit is local.

### setup-menu car r10, addendum 15:2x — **THE CAR'S 29 DRAWS DO PAINT. THEY PAINT A FLAT SLAB OF ONE COLOUR OVER THE MENU.**

`LENA_MENUSKIP2D`'s twin, `LENA_MENUSKIP3D` (drops every indexed 3D draw while `/tmp/skip3d`
exists), built into `out-md9/cmr2`. First attempt (`md_skip3`) did nothing and **its own log said
why**: `grep -c MENUSKIP3D` = 0 — no init line — while the same log had 8,688 `MENUORDER` lines
with `3d=29`, i.e. the gate was in `DrawPrimitiveVB` (which this page never calls) instead of
`DrawIndexedPrimitiveVB` (the call the car's 29 draws actually use). Moved, rebuilt
(`out-md9/cmr2` md5 `d3e90a99dd83bda86f1d180e9c82e52a`), re-run as **`md_skip3b` 15:09–15:2x**:
this time the log carries `[MENUSKIP3D] on:` and `[MENUSKIP3D] frame end: skipped=29 skip3d=1`
for every frame of the treatment.

**The A/B, same page, same process, adjacent frames, one file apart — and it MOVES:**

| | frame 0040 arm A (car submitted) | frame 0072 arm B (car's 29 draws dropped) |
|---|---|---|
| dominant colour | (140,149,158) **96.48 %** | (140,149,158) **86.31 %** |
| distinct colours | 826 | 254 |
| car rect x160..1080 y280..560 non-background | **9.57 %** | **26.33 %** |

**Pixdiff of the two frames: 175,878 pixels differ, bbox `x[0..1223] y[46..733]`, and the
colours are unambiguous:**

* in arm A those pixels are **(140,149,158)** — 140,044 of them, one flat colour;
* in arm B the same pixels are **(231,235,198)** (56,113), (79,79,79) (19,618), (201,214,216)
  (17,346), (199,199,212) (13,050), white (7,123) — **the menu's real content and its text**
  (LightYellow backdrop, icons, glyphs).

**So the car's 3D draws are rasterising and filling a ~140,000-pixel region — bigger than their own
rect — with a single flat colour**, and what we have been calling "the clear colour everywhere" is
in large part *the car itself, drawn flat*. Drop the car and the menu's real content appears.
Put it back and the car is a flat one-colour sheet lying over the menu. **That is Miami's
sentence, measured: "flattens into one place on the menu … one flat piece of paper."**

**The frames pushed for this:** `frames/opt-preview_20261011-1520_r10_A_car-3D-submitted_FLAT-SLAB.png`
(md5 `152a9fafb033f2de7f591f73cd1ad2cb`) and
`frames/opt-preview_20261011-1520_r10_B_car-3D-dropped_MENU-REVEALED.png`
(md5 `f5916050713b556e38a201e9aa2167a3`) — look at them side by side: A is what he sees, B is the
same frame with only those 29 draws removed.

**What the next instrument must name: where the flat colour comes from.** It is a *fragment*
value, not a geometry or a depth or a cull or an ordering value — all of which are now excluded on
this page. The three candidates are (i) the texture bound at those draws (a blank/never-uploaded
texture, or the wrong one), (ii) the texture-stage 0 combine (the census logs
`s0/t11`, `s0/t18`, `s0/t20`, `s0/t24` set 2,112 times and "texture-stage OPs set: 1:1200
4:4224"), and (iii) the material (`flags.w` source=material vs vertex). One line added to
`MENUDRAW` — the two bound texture handles and the material diffuse of the car's own draws, plus
an arm that forces texturing off — separates them, and it needs no new run machinery: the same
`md_skip3b` route, the same trigger file.

---

## setup-menu car r11 (2026-10-11 15:1x–15:3x EEST) — the car's FRAGMENT inputs measured for the first time, and the first A/B in this ticket that MOVES **and comes back byte-identical**

r10 named the next instrument and stopped one line short of it: *"where the flat colour comes from
— the bound texture, the stage-0 combine, or the material."* r11 built it, ran it, and got a result
that is stronger than a null: **three arms on the same page in the same process, each one changing
the frame, with the frame returning to the control's md5 byte for byte after each arm.**

### The instrument (`LENA_MENUTEX` + `LENA_MENUUNLIT`)

`patch_menutex.py` adds three things to `deck_dd7.cpp`, all inert unless the env var is set:

* per-indexed-3D-draw print: the two **bound texture ids**, the stage-0/1 ops and args, the lighting
  flag, and — for three of that draw's own vertices — the texel the shader *would* fetch, the vertex
  diffuse, and **the fragment colour the port's own combiner predicts** (`a7_eval_texop` on the real
  inputs, `a7_vk32.c:297`). A prediction is testable against the framebuffer; a list of inputs is not;
* a **CPU snapshot of every uploaded texture** taken at `a7_upload_texture` call time — the exact
  bytes the GPU was handed, so "the texture is flat" and "the sampling is wrong" are two lines;
* `LENA_MENUUNLIT`: two file-triggered forced-input arms applied to indexed 3D draws only and
  restored by a C++ scope guard, so no arm can leak into the 374 2D chrome draws after the car:
  `/tmp/mtA` = stage0 `SELECTARG1(TEXTURE)` (texture only), `/tmp/mtB` = stage0
  `SELECTARG2(DIFFUSE)` (vertex/material colour only).

`out-md10/cmr2` md5 `8be469d8545f9252e5c27f44c5ca6499`. Build notes worth keeping: three of the
four iterations were *compiler-caught* format/type errors in my own print (and `A7Material.diffuse`
is an `A7ColorValue` of floats, not a `D3DCOLOR`) — the last build has **zero warnings from the new
block**, and the first cut's budget was wrong in a way that would have printed the menu chrome and
never the car, which is why `MENUTEX` now rides `MENUDRAW`'s burst window.

### The run, and the route defect that cost the first 3 minutes of it

`md_mtex`, card taken 15:21:03 (guard empty, no peer touched). **The first launch had no X-key
driver and never left the boot screen** — `[MENUTEX]`/`[MENUDRAW]` = 0 lines for three minutes,
because `md_drive_car.py` injects through `inject-key.py`, whose uinput device cannot be taken on
this box (r7 measured it: score −2, or `Permission denied` on the evdev node). `kb_mt.sh`
(`drive_cov.sh`'s phases 1–2 with the exit condition moved to my own first line) reached the option
page **80 s after the keys actually arrived**. Every earlier round's route was driven by exactly
this xdotool path.

### What the car's draws actually bind (402 draw lines, 402 texture pairs, 1,206 vertex samples)

* **Eight real textures**, ids 35,36,37,38,39,40,41,42 — 256×256, 512×512, 1024×1024, means
  (13,13,12,207), (100,94,101,253), (51,50,50,207), (31,30,35,204), (22,22,21,187), (85,66,69,204)…
* **No stage-1 texture at any of them** (`tex1=-1`), so the 3D fragment shader's stage-1 branch is off.
* Stage-0 op at every draw: `MODULATE(TEXTURE, DIFFUSE)`; lighting on at 389/402.
* The car carries **38 distinct vertex diffuse colours** (white, greys, 0xff926c6c, 0xffb3b34c,
  0xff5f5f9f …) — real per-part colours, not a placeholder record.
* The combiner's **prediction is near-black** (`ff000000`, `ff08090a`, `ff080905`, `ff080008`…), and
  the framebuffer in the car's own region holds exactly that: `(0,0,0)` 3,344 px, `(49,52,49)`
  2,162, `(0,0,13)` 991, `(8,0,8)` 969. **The car is not missing and not mis-indexed — it is painted
  near-black, and the port's own arithmetic says so before the pixels do.**

### The A/B — control, texture-only, diffuse-only, with recoveries in between

| window | frames | md5 | distinct colours | car region |
|---|---|---|---|---|
| CONTROL 002–014 | 13 | `1b2bce5343` | 4,248 | dark: (0,0,0), (49,52,49), (0,0,13), (8,0,8) |
| **mtA** texture-only 015–031 | 17 | `15525ebc90` | 3,730 | dark + greys (161,160,161), (150,150,150) |
| recovery 032–042 | 11 | `1b2bce5343` | 4,248 | identical to control |
| **mtB** diffuse-only 043–059 | 17 | `1ce176a776` | 155 | **34,233 px of PURE WHITE** |
| recovery 060–071 | 12 | `1b2bce5343` | 4,248 | identical to control |

Both arms fired (`[MENUUNLIT] arm 1 ACTIVE (draw 1)`, `arm 2 … draw 958`), both changed the frame,
and **both recoveries returned it to the control md5**. Full pixdiff control→mtB is 32,092 pixels,
**98.4 % of them pure white in mtB** — so the car's own silhouette is `bbox x[87..891] y[215..378]`,
and with the texture removed from the chain that silhouette goes white: **the visible car in the
control is the texture, modulated by a white diffuse.**

### The one number r11 will NOT ship, and why it is the most interesting one

The UV column printed `uv0=(3.3609e-309, 2.122e-314)` — **a double, in a column that reads a
32-bit float** (smallest subnormal float is 1.4e-45). So the formatting is wrong and the *magnitude*
cannot be quoted. What is quotable is the **constancy**: all 1,206 printed UV strings are identical.

If that constancy is real it is the whole bug — every fragment of the car would sample ONE texel,
which is "flattens into one flat piece of paper" literally, in the fragment shader. So it was
checked against the file: the `.c3d`'s own 48-byte records (dumped offline this round from
`game/Game/Cars/205a1N.c3d`, located by their unit-length normals, 1,140/1,268 gaps = 48) carry
**real UVs** — `uv0=(0.5000,0.5000)`, `(0.9897,0.5000)`, `(0.9241,0.2552)` … at exactly the offsets
the port reads. **File has UVs; the runtime read says one repeated value; and the column that says
it is the one column I just caught being formatted wrong.** So `MENUTEX`'s UV column was rebuilt as
**hex** (`out-md11/cmr2`, md5 `629228b9c3211556157004feddcb4987`) and re-measured in run 2
(`md_mtex3`, launched 15:29), together with the depth question below. r11 does not get to claim it
yet, and says so here rather than in a footnote.

### Also in run 2, and it is a fork r10's numbers opened

r10's drop test showed the car's presence costs the *page* ~140,000 pixels of its own content, and
the car is drawn 4th–32nd of the frame — **before** the 374 2D chrome draws, so it cannot be
painting over them. Depth is the obvious candidate (the car writes z, the TL chrome depth-tests
against it): run 2 runs the same page with the existing `LENA_MENUZ=0` instrument, which forces
`D3DRS_ZENABLE=0` around indexed 3D draws only and restores the game's value right after. The option
page is deterministic (r10 measured byte-identical captures across frames, binaries and runs), so
the cross-run md5 comparison is a valid A/B.

**Frames pushed:** `frames/opt-preview_20261011-1524_r11_CONTROL_car-pixels-dark.png`
(`658c57ddcfe2c1aa43fe0791d0ecf286`) — the page as he sees it; the same frame with the car's
fragments forced to vertex/material colour,
`frames/opt-preview_20261011-1524_r11_mtB_diffuse-only_car-WHITE.png`
(`2f15d58f811c41facc922da90efa5caa`); and 880×300 crops of the car's own region from each
(`eb121df8c6e058a004fc7e4babc4a7c0`, `f3677e42cb067fd19eaeaffa5500aac3`).

Held for the next round: whether the runtime UVs are really one repeated value (run 2, hex), whether
depth is what costs the menu its own content (run 2), and — if the UV constancy holds — **where the
UV field is lost**, since the file has it and the port's record offsets are demonstrably right for
position (offset 0), normal (12) and diffuse (24, written by the game's own `Mesh.cpp:95`).

---

## installer + public face (2026-10-11 15:0x–15:2x EEST) — the shipped installer could not have worked, the pair did not compose, and the repo's face was not this game

**The bug, reproduced on his own tree** (isolated `HOME`, nothing written to his
applications): `find_game('…/.lena_cmr2/game')` → `…/game/Game`, which holds `Bigfiles
Cars Tracks DemoRuns Info` and no executable, so the launcher carried
`Exec=…/game/Game` — a **directory**. v0.2.0's root-vs-content split fixes it:
root `…/.lena_cmr2/game`, content `…/game/Game` (220 cars, 212 tracks), exe `CMR2.exe`.

**Four defects in v0.2.0 were already measured and fixed here** (`work/CMR2LAB-v020/REPORT.md`,
v0.2.2, md5 `135559b49804f6733b1d808f9f4cd477`): the `Cars/ + Tracks/` test badged
**Automobilista 2's audio folder** as `✓ <== INSTALL` (0 cars, 0 tracks, exit 0);
`~/.lena_cmr2` is a dead path on this box; a failing `--path` still fell back; and the
bounded walk could not reach a Proton prefix, which — once fixed — found **a second real
install**: his GOG copy at `compatdata/3646996028/pfx/drive_c/Program Files (x86)/Codemasters/Colin McRae Rally 2`, 220/212. Whole search: 0.17 s. v0.2.2 re-verified here:
no-arg `where` now picks the dev copy, AMS2 is refused *with the reason*, a nonexistent
`--path` hard-stops, `--all` lists both installs.

**The defect I found in the pair (fixed in this commit).** `cmr2install` unpacked
`lab.locate()` as a 2-tuple; v0.2.2 returns 4 → `/api/scan` raised
`ValueError: too many values to unpack` inside the request handler, so **tier 1/2 of the
browser installer returned an empty reply**. Fixed with a shape-tolerant `_locate()` that
accepts both versions, and used `everything=True` so tier 1 now lists **both** installs
instead of AMS2. Re-verified with the old lab and the new one.

**The browser installer, verified independently through HTTP** (not the CLI), on
fixtures: A auto → Wine/GOG prefix → `Exec=…/CMR2.exe` `exists:true runnable:true`;
B `--native` where a port exists → `cmr2-native`; C `--native` with no port → refuses,
**no file written**; D nonexistent folder → refuses with the reason, **no file written**.
4/4, and `ls` of the output dir afterwards shows exactly `A.desktop` and `B.desktop`.

**The public face.** The old `docs/social-preview.png` (`e692c642…`) measures **0 gold**
pixels and, under the rule `r≥95, g≤65, b≤65`, exactly **5,666** "red" — the phone's
number, reproduced; exact `#8b0000` is **9**. Its palette is 50,520 shades of generic dark
UI. Replaced with art regenerated from the game's own `FrontEnd/res1024.bfl`: **19,838**
gold and **231,183** red at 1280×640, wordmark band 19.97:1 against its plate and 19.77:1
measured **on the 128 px icon**, i.e. still legible where the old art had nothing to read.
Old file kept at `docs/art/old-social-preview-e692c642.png`. **The GitHub social-preview
upload is web-UI only** — the file is in place, the setting needs a human at a browser.

**And one honest correction to the art's own provenance:** `build_art.py` says every
colour is "sampled from the game files". Audited against all 72 textures: red `#8b0000`
(6,953 px), dirt `#744032` (5,342 px) and sky `#dae8ec` (6,020 px) are real; `#fff300` gold
appears **0 times** (the game's gold is `#fff100`, 2,641 px in `bgre.tga`) and bone
`#dcd3b1` appears **0 times** anywhere. The art is fine; the claim is two entries short of
true. `docs/ART-PROVENANCE.md` has the table and the two ways to settle it.

**§1 was also corrected**: it still named `80d927…` (11:02) as "RIGHT NOW" while the play
binary has been **`9ecbf87bb8650a3883b188f4e77890e4`** since **12:04:43** — the question the
phone opened with.

New in the repo: `cmr2install` (v0.2.1, md5 `0a68aedac4ad46afd7a54029614870f4`), `cmr2lab`
v0.2.2, `tools/build_art.py`, `docs/art/`, `docs/INSTALLER.md`, `docs/ART-PROVENANCE.md`.
