# progress.md — Lena on the Deck, reporting to Lena on the phone

**Rewritten whole, 2026-10-11 11:1x EEST.** This file is not appended to: each round
replaces it, so a stale claim cannot sit above a fresh one. The old append-log — every
dated block from 2026-10-10 up to 10:28 today, including the ones that turned out to be
wrong — is kept verbatim in [`docs/progress-archive.md`](docs/progress-archive.md).

Every number below names the log, binary or command that produced it. Where a number
came from another lane's run rather than mine, it says so.

---

## 1. RIGHT NOW

**The binary Miami plays can drive a car again, and he launched it himself at 11:06:05.**

| | |
|---|---|
| binary | `work/PLAY/out-plain/cmr2`, md5 `80d927b54f597dbb2ad7590ddb6875e7`, 17,703,640 bytes, linked **11:02 today** |
| does it drive? | yes — `cmr2_drives` returns 0 (`tools/drivecheck.sh`, run just now on this file) |
| how it got there | `build-play-lre.sh` recompiled 9 stale TUs and linked; the result is **byte-identical** to `work/HUD-2D/out3/cmr2`, which another lane built independently at 10:45 — two lanes, same tree, same bytes |
| his own launch, from the launcher's log | `2026-07-11 11:06:05  LAUNCH  …/out-plain/cmr2  md5=80d927b54f59  skipped-dead: none` — quoted verbatim, including the launcher's own month bug (`07` for `10`; the system clock reads 2026-10-11 and `journalctl` agrees) |
| and it is alive | a `cmr2` process on that path was running while this was written (PID 3787186, 6 min 28 s of uptime, RSS 128 MB, argv = the full path to that binary) |

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

**Also in flight right now, with no result to quote yet:** the sky/Finland lane
(worker 2, started 11:07) and the HUD-2D lane's round on the in-race HUD.

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
