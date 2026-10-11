# CAR-r1 — CHECKPOINT  (task `fix-textreg-20261011`, worker 1, 2026-10-11 ~22:5x–23:0x EEST)

READ THIS FIRST. Round limit is real; this file is the only thing that survives.

## 0. WHAT THIS ROUND DID / DID NOT DO

* **DID NOT re-hunt the ticket's fix.** It is in place and verified by reading the source (§1).
* **DID NOT run the GPU.** A peer holds the card right now (§3). Every measurement in this
  round is offline, on bytes and on the *existing* instrument logs.
* **DID**: answered the phone's item 4 and the ticket's "same symptom" claim with a new,
  decisive negative (§4, §5) — **the car's draws ARE submitted, in the menu AND in the stage,
  with the game's own textures, sampled exactly.**

## 1. THE TICKET'S FIX — VERIFIED, NOT RE-HUNTED

`~/.lena_cmr2/port/rhi/deck_dd7.cpp`, `DeckSurface7::Blt()`:

* `dirty = 1;` now occurs **only** in the DXT branch (line 1059, inside `if (dl_is_dxt(...))`,
  next to `dl_decode(...)` and `blitsConverted++`).
* the plain copy path falls through to `return DD_OK;` with the comment at line 1084
  (`LENA-T3: plain blits no longer force a re-upload...`) and **no** `dirty = 1`.
* the only other `dirty = 1` is `Unlock()` (line 939) — the game's own write path, correct.
* provenance: `deck_dd7.cpp` mtime 21:46:48, `deck_dd7.o` 21:46:50 → the object (and every
  lab binary built from it, e.g. `work/ROAD-r6/out-r6/cmr2` md5 4fd46919fb5a) carries the fix.
  `work/PLAY/out-plain/cmr2` (his, md5 9ecbf87bb865) was **not** touched.
* Decoder / `surface_fill_desc`: not touched, not investigated. As instructed.

## 2. CAPTURE METHOD (recorded so the next round does not repeat the mistake)

**NEVER `spectacle` on this Deck** — it core-dumps in the Wayland session and leaves a STALE
file that reads like a real result. Use the RHI's own dump: `A7VK_SNAP=<frames>:<prefix>` or
`A7VK_SNAP_TRIGGER=1` + `touch /tmp/snapnow` → `/tmp/trig.ppm.NNN`.
`/tmp/snapnow` and `/tmp/trig.ppm.*` are **hardcoded in the RHI** (`a7_vk32.c:2988-2998`) —
**one driver at a time owns them.**

## 3. MACHINE STATE AT THIS ROUND (22:5x)

* **The GPU is HELD by a peer right now**: `work/ROAD-r7/out-r7/cmr2`, run tag `R7FLIP`,
  alive ~3 min when read, driven by `work/RACE/drive.py`. Nothing of theirs was touched.
  Two `cmr2` on one card is what wedged the display at 07:25 — I stood down. No build,
  no relink, no window, nothing written into the game tree.
* **`journalctl -k | grep -c "ring gfx_0.0.0 timeout"` now returns 0.** The kernel journal has
  rotated again (it previously started 01:51 and held the "12" baseline). A bare count is no
  longer a baseline; ring-pass/fail must stay a **before/after delta inside one run**, which
  is what `r6_run.sh`-style scripts already do. Do not quote "0" as "no GPU death".
* No GPU-visible defect was produced by this round (nothing was run).

## 4. THE CAR — WHAT IS NOW DEAD (new, measured this round)

The open item: **"NO 3D CAR MODEL — reproduced in the menu preview AND in the stage; same
symptom, not deck_dd7.cpp."** The phone's item 4 asked the sharp version: *is the car's VB
ever created, or is the car drawn and invisible?*

### 4.1 The car's draws ARE submitted, in both places

* **Menu (option preview):** `LENA-MENUDRAW`/`MENUTEX` show the car page's 29 indexed 3D draws
  per frame with `fvf=0x2d2 stride=48`, `startVert` 1488/1574/1660…, real `numIdx`
  (36/72/108), and real UVs. Census in the same runs: `draws by FVF: 0x1c4 TL=… 0x2d2 MESH=…`,
  `refusedFvf=0`, `clamps=0`, `create VB by FVF: 0x2d2 MESH=n206/v469890`.
* **Stage (race):** `work/RACE/out/R6STG.log` / `R6B.log` (`LENA-STGTEX`), frames ≈ 6200–6300:
  draws with `fvf=2d2`, `tex0=269/270/271`, `light=1`, `matd=ffffffff`, and **the same UVs and
  texels as the menu car page** — e.g. `uv0=(0.924088,0.255157) texel=ff080905`, identical to
  MENUTEX's menu line. That is the same mesh, drawn in the race.
* `create VB by FVF` says the only VB layout the game ever creates is `0x2d2` (n=206,
  v=469890 = exactly 2 × `AllocateSharedVertexBuffers()`: 103 buffers × 234,945 verts, per
  `Graphics.cpp:2014-2046`). So no VB is ever refused and no draw is refused
  (`refusedFvf=0`). **The phone's "the car VB is never created" branch is closed for both
  the menu and the stage.**

### 4.2 The port's car textures are byte-faithful to the game's own files

This is the strongest new result, and it was obtained with **no GPU**: take the port's own
16×16 lattice sampler (`mt_texstat`/`mt_texel`, `deck_dd7.cpp:1718-1760`) and re-derive it
offline from the game's `.bfl`/`.dds` bytes.

* Tool: `work/CAR-r1/texlattice.py` (block-limited DXT5/DXT1 decode, exact lattice reproduction,
  matches a (size, mean RGBA, zero-alpha) triple against every DXT texture in all **431** `.bfl`
  under `game/`).
* **The menu preview car is the Ford Focus — `game/Game/Cars/foca1.bfl`.** 8 of the 9 bound
  textures match file-for-file (Δ ≤ 4 over RGBA), the 9th (256×256, mean (41,19,3), all-alpha-0)
  matches `affligbr.dds`'s RGB to 1 LSB with its alpha at 0:

  | port id | size | port mean (16×16 lattice) | file |
  |---|---|---|---|
  | 35 | 256×256 | (13,13,12,207) za=48 | `affnwbdf.dds` (**d=0**, exact) |
  | 36/38 | 1024×1024 | (100,94,101,253) | `affdbodf.dds` (d=2) |
  | 37 | 256×256 | (51,50,50,207) za=48 | `affnwhdf.dds` (d=2) |
  | 39 | 512×512 | (31,30,35,204) | `affglidf.dds` (d=3) |
  | 40 | 256×256 | (22,22,21,187) za=60 | `affintdf.dds` (d=4) |
  | 41 | 512×512 | (85,66,69,204) | `affglodf.dds` (d=3) |
  | 42 | 256×128 | (54,56,52,255) | `affunddf.dds` (d=1) |
  | 43 | 256×256 | (41,19,3,0) za=256 | `affligbr.dds` RGB exact, alpha 0 |

* Tool: `work/CAR-r1/texel_vs_file.py` — takes the port's own printed `(uv, texel)` pairs from
  `MENUTEX`/`STGTEX` and reads the *same* texel out of the *same* file with the port's own rule
  (`x=floor(u*w)`, `y=floor(v*h)`), in D3DCOLOR packing. **Verified exact (sum|d| = 0):**
  draw `tex0=35` (`affnwbdf.dds`, 256x256) — (0.924088,0.255157) file `ff080905` = port
  `ff080905`; (0.0102844,0.5) `ff080008` = `ff080008`; (0.744843,0.0759125) `ff080808` =
  `ff080808`; and in the RACE (STGTEX f≈6263) `tex0=269`/the 1024x1024 body,
  (0.421906,0.707062) file `affdbodf.dds` = port `ff08090a`.
  **CAVEAT, stated so it is not misread:** the other UV/texel pairs in the same log groups are
  *other* textures of the same draw window — attributing a UV to the wrong `tex0` gives a false
  DIFFER. Only pairs taken with their own draw's `tex0` are evidence, and those agree.
* **Therefore**: file → DDraw surface → `SetTexture` upload → texel lookup is faithful for the
  car, in the menu and (same texture, same UVs) in the stage. The car's near-black fragments are
  not a wrong-texture bug: **the Focus's own texture set really is dark** (`affnwbdf` full-image
  mean (15,15,14), `afflwbdf` (8,7,7), `affglidf` (30,29,33); only the body `affdbodf` is mid
  (92,86,94)). A "no car" symptom therefore cannot be explained by texture content, and the
  earlier lane's sentence "the car is painted near-black because these textures are dark" is
  true but does **not** explain invisibility on a (140,150,158) field — a (92,86,94) body on
  that field is plainly visible.

## 5. WHAT THE FRAMES ACTUALLY HOLD (offline re-measure, for the next round)

* `work/MENU-CAR-FLATTENED/frames/md_mtex.002.ppm` (car page, control arm): **96.47 % one colour
  (140,150,158)**. The non-background pixels form a **~200×160 solid block** at x≈620-820,
  y≈208-368, plus small text-like marks scattered around it. Top non-bg colours: white 3 288,
  black 3 167, (49,52,49) 2 161, (236,236,236) 1 181, near-black blue-greens (0,0,13/18/22).
  That is Miami's "one flat piece of paper", not a car silhouette.
* Race frames on the current-ish bytes (`work/RACE/out/R5SHIP.01_t60.ppm`, `.03_t100.ppm`):
  the lower half is a single warm hue with **no car-shaped object anywhere**. Same symptom,
  confirmed from the pixels, without a GPU.
* Tools used and kept: `work/CAR-r1/coarse_map.py`, `work/CAR-r1/ascii_frame.py`.

## 6. WHERE THIS LEAVES THE CAR — the honest fork (do not re-derive §4/§5)

Given: draws submitted (both places) + textures faithful + UVs faithful + 40 % of the car's
triangles survive the game's own `D3DCULL_CCW(3)` (round 9's winding census, §61) + forcing
`D3DCULL_NONE` **does** put textured content on the car page (round 7, `md_mc_none_r1` 21.99 %
of the car rect vs 2D chrome only) + with `ZENABLE` forced off the car shows **more** of its own
surface (round 11, `md_mtex3.045`) — the loss is downstream of the submit and is one of:

1. **`frontFace`/cull face is right for one path and wrong for the other.** `a7_vk32.c:654-665`
   decides `cullMode` and `frontFace` once, globally; §60 of the menu-car checkpoint already
   records that the current pair is only empirically correct "because two errors cancel". If
   the 40 % that survive are the *inner* faces, the picture is an inside-out flat sheet — which
   is what Miami describes. Round 8 §67's **normal-vs-winding test is still unbuilt** and is
   still the one instrument that separates "outer surface" from "inner surface".
2. **depth ordering** — the z-off arm's positive half says the depth test is cutting the car's
   own surface away; the road's "one uninterrupted full-width field" (RACE-NEXT-r5) is the same
   signature at stage scale. Not yet measured as a *direction* (inverted compare / depth-range /
   stale depth at the car's draws).

Both are in the RHI, not `deck_dd7.cpp`, consistent with the ticket.

## 7. NEXT ITEM (one line, mine)

Run the **normal-vs-winding** instrument (round 8 §67: vertex normal at +0x0C vs the
screen-space winding of the same triangle, inside `MENUPROJ`'s hook) on the **same frame** as a
`LENA_MENUZ=0` and a `LENA_MENUCULL_PHASE` arm — one run, one page, three arms — so "inner
surface", "depth", and "cull" are separated by measurement instead of by sequence. Card first:
`sh work/RACE/gpu-guard.sh` must answer "free" and ROAD-r7 must be finished.

## 8. FILES THIS ROUND WROTE

* `work/CAR-r1/CHECKPOINT.md` — this file.
* `work/CAR-r1/texlattice.py` — offline "which game file is this uploaded texture?" matcher.
* `work/CAR-r1/texel_vs_file.py` — port texel vs file texel, at the port's own UVs.
* `work/CAR-r1/coarse_map.py`, `work/CAR-r1/ascii_frame.py` — frame readers (no GPU, no PNG deps).
* Nothing else. No source edited, no binary built or moved, nothing written outside `work/`.

## 9. ADDENDUM — WHAT THE PEER HOLDING THE CARD IS ACTUALLY DOING (read before assuming)

`work/ROAD-r7/` — tag `R7FLIP`, binary `out-r7/cmr2`. Read from its own sources, not guessed:
`LENA-R7-FLIP` is **`A7VK_AB=flipN`** — a *free-running* NORMAL/VCOL alternation every N frames
plus `LENA-R7-LABEL`, which records the arm the frame **just drawn** used (the schedule's
`g_ab_mode` names the *next* frame by the time a capture happens). It is **not** a geometry,
projection or winding flip. Its build script keeps ROAD-r6's link line and proves it with a
control link that must reproduce r6's md5.

So ROAD-r7 is the r6 "next item" (a vcol race frame), and it is **not** doing the car work.
The car's two remaining candidates in §6 are untouched by it.
