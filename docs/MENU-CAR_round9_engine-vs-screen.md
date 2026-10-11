# round 9: the frame, measured against the RHI's OWN rasteriser of the same draws

`work/MENU-CAR-FLATTENED/`, 2026-10-11 14:2x–14:4x EEST. No GPU run this round: the card was
held by a peer (`work/RACE/out-rt10/cmr2`, guard-verified `--foreign` = `251349`) for the whole
round, so every number below comes out of logs and frames that already existed. Nothing was
built, nothing was relinked, no render-path code was touched.

## 0. the instrument that was already there and had never been aimed at a capture

`[OWNER]` is the RHI's own **CPU-side rasteriser**: it walks the same triangles the draw submits,
loads vertices with the same 48-byte stride, multiplies by `b->mvp` — **the very block that goes
to the GPU** (`a7_vk32.c:2637`, `ow_note(..., &b->blk)`, and `b->blk.mvp` is what
`a7vk_fill_block` negates and memcpy's at `:2735`) — clips, and paints a 64x40 cell map with the
owning texture id per cell. It is a prediction of the frame, made from the same input the GPU
gets, on the CPU.

Nobody had compared that prediction to a capture of the same frame. This round did, cell by cell,
on both runs that carry an `[OWNER]` dump: **`md_proj9b` (the round-8 A/B run, 204 captures inside
the 3D window) and `md_mc_none_r1` (round 7's cull-forced-NONE run)**.

## 1. the car as the ENGINE says it is — this is what the port thinks it drew

`md_proj9b` frame 3650 (`[OWNER]` prints every 25 frames):

```
cam eye=(0.14 -0.09 -5.00) fwd=(0.000 0.000 1.000) up=(0.000 1.000 0.000)
proj znear=1.0000 zfar=250.00 | xscale=1.5185 yscale=2.0985
     geomAspect=yscale/xscale=1.3820 viewportAspect=1.6000
owner map THIS FRAME: 438/2560 cells owned (17.1% of the frame) by 8 textures | 2747 tris drawn
  A tex=36  cells=255  10.0%  dw=5.02  wmin=4.121  draws=11  tris=1310
  B tex=37  cells= 89   3.5%  dw=5.00  wmin=4.119  draws= 4  tris= 424
  C tex=38  cells= 75   2.9%  dw=4.99  wmin=4.213  draws= 2  tris= 164
  D tex=40  cells= 19   0.7%  dw=5.01  wmin=4.213  draws= 4  tris= 358
```

and its own map (rows 14–27 of 40, cols 7–52 of 64 = **x 140–1050, y 280–560 px**):

```
r14 |           BBBBB                          BBBBB                 |
r16 |         ABBBBBBBBAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBAAAA           |
r20 |        AAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBAAAAAA            |
r23 |         AAAAAAAAAAAAACCCCCCCCCCCCCCCCCCC                       |
r26 |            DACCCCDCCCCCCCDDDDCCCC                              |
```

Two wheel-shaped `tex=37` blobs at the two ends, the long body `A`, a cabin `C`/`D` — **the
engine's own picture of the car is a car**, and it is *static*: 438 cells and 2747 triangles,
identical at frames 3650, 3700, 3750, 3800, 3850, 3900, 3950, 4000 of that run and at 4450–4700 of
`md_mc_none_r1`. This is the strongest statement of "the port thinks it drew a car, here" that
exists in this task, and it is the yardstick the rest of this file uses.

## 2. the screen, cell by cell, against that map — 8 frames of one run

`cmp9.py LOG FRAME PPM` (new, in this directory): engine-owned cells vs cells that are not the
frame's dominant colour, at the owner map's own 20 px grid, 5 % threshold.

| `[OWNER]` frame | capture | engine cells | screen cells | both | engine-only | screen-only |
|---|---|---|---|---|---|---|
| 3650 | 3649 | 438 | 217 | 130 | **308** | 87 |
| 3700 | 3699 | 438 | 168 | 97 | **341** | 71 |
| 3750 | 3749 | 438 | 168 | 97 | **341** | 71 |
| 3800 | 3799 | 438 | 217 | 130 | **308** | 87 |
| 3850 | 3849 | 438 | 217 | 130 | **308** | 87 |
| 3900 | 3899 | 438 | 168 | 97 | **341** | 71 |
| 3950 | 3949 | 438 | 168 | 97 | **341** | 71 |
| 4000 | 3999 | 438 | 217 | 130 | **308** | 87 |

**70–78 % of the car's own cells — the cells the port's own rasteriser of its own draws says the
car occupies — are plain background colour on the captured frame**, and the screen's own content
is not the car: **40 % of it (71–87 cells) is outside the car's footprint altogether**, and the
434 cells of the car's footprint that matter are not filled in. The two screen states that
alternate (217 and 168 cells) are the page's two content states, and they alternate under both
cull arms — the round-8 finding — so what is moving in those cells is not the car.

## 3. orientation: it is not a flip, and it is not a scale either

`ow_dump` maps **ndc y=+1 to row 0 (top)** (`a7_vk32.c:2347`: `r0 = (int)((1.0 - y1) * 0.5 * OW_R)`),
while the block it reads has had the y column negated for Vulkan (`:2733`) — with that matrix the
top of the frame is ndc y = **-1**. So the map's orientation relative to the real frame is
ambiguous *by construction*, and this round tested both. It also tested the transforms a wrong
viewport would produce (`fit9.py`: scale about the centre, x/y flips, ±4-cell offsets):

| frame 3650 vs capture 3649 | IoU |
|---|---|
| engine map, as printed | **0.248** |
| engine map flipped vertically (UD) | **0.287** |
| best of 4,000 (scale × flip × offset) candidates | **0.435** (sx=2.0, sy=1.0, x-flip, y-flip) |

A car drawn *anywhere* at *any* of those scales or orientations would beat these numbers. The best
candidate is a 2:1 shrink **and** a 180° rotation — which is not a viewport transform and not a
flip bug, it is the fit finding chrome.

**So: at cell resolution, in either orientation, the frame does not contain the car the engine
says it drew.** This is measured against the port's own prediction of its own draws, not against
an expectation of what a car should look like.

## 4. round 7's positive is retired — with the engine's own map this time

Round 7 shipped `frames/opt-preview-car_20261011-1346_CULL-OFF_car-visible.png`
(md5 `4fe6c651bdc26e45d8e8e9d0811a0c0b`) as the frame where forcing `D3DCULL_NONE` "shows the
car". Two things about that frame, both measured here:

1. **it is a static screen, not a cull result.** Its pixels are byte-identical (every sampled
   byte, 1 in 3001) to `frames/md_mc_none_r1.043.ppm` … `.046.ppm` — capture frames **4464, 4471,
   4488, 4490** of that same run, four consecutive captures of one unchanging image.
2. **it does not contain the engine's car either.** Against the `[OWNER]` map of that run's car
   page (438 cells, 2747 tris, frames 4425–4700): the pushed frame has 306 non-background cells,
   IoU **0.310** upright / **0.338** flipped.

Its own run's earlier captures (frames 4438, 4440, `.037`/`.038`) come out at 222 cells, IoU
**0.255** / **0.294**. So **the arm that forces `D3DCULL_NONE` on every indexed 3D draw of the car
page also does not put the engine's car on the screen** — the same conclusion round 8 reached from
the frame-scheduled A/B, now reached from the cull-off arm's own frames compared against the
engine's own rasteriser. Round 7's "the cull arm shows the car" is downgraded from "two runs whose
pages differed" to "a frame that is a static chrome image".

## 5. what the port does with the game's viewport — a real defect, named, on this page

Chasing the `vp=853x533` that `MENUPROJ` prints (round 8 flagged it as "`a7_get_viewport` is not
returning the game's viewport"):

* `DeckD3D7::CreateDevice` (`deck_dd7.cpp:1274-1284`) sets the RHI up at the **render target's**
  size — `853x533` on this page — and stores that in `d->viewport`. `[WIN]` says the display is
  **1280x800**, and `[A7VK]` says the swapchain is **1280x800**. So the game's frontend backbuffer
  is 853x533 (2/3 of the panel) and the panel is 1280x800.
* The game does call `SetViewport` (1200 times in 600 frames; three call sites: `Game.cpp:2667`
  with a caller-supplied rect, `Game.cpp:2774` with `(0,0,resX,resY)`, `Graphics.cpp:2995` for the
  cube-map shadow faces). **The port stores all of them and applies none.**
* `a7vk_record` (`a7_vk32.c:2782-2795`) sets the Vulkan viewport and scissor **once per frame from
  the swapchain extent**, and the shader's own pixel mapping is `pc.vp[0] = W*0.5, pc.vp[1] = H*0.5`
  from the same extent (`:2847`).

Consequence for this bug: the 3D path is **always full-frame 1280x800**, the game's own viewport is
ignored, and — because the shader and the `[OWNER]` overlay both use the swapchain size — the owner
map *is* a fair prediction of the frame (which is what makes §2 valid). The 2D/TL path is
consistent too (a 853x533-authored UI scaled 1.5x onto 1280x800 keeps its 1.6 aspect, so the menu
looks right and hides it). **This is not the flat-car cause** — it would mis-scale, not flatten —
but it is a named port defect on exactly this page, and it means *no* frontend viewport ever
reaches the GPU.

## 6. what moved, and what did not

**Moved.**
* The frame is now measured against the RHI's **own rasteriser of the same draws** — 8 frames of
  one run, plus the other arm's run. 70–78 % of the car's own cells are background, in either
  orientation, under every transform tested. That is a hard, first-hand yardstick where rounds 5–8
  had colour counts and shapes.
* **Round 7's cull lead is retired on its own frames**, and the frame it shipped as "the car" is
  identified as a static chrome image (byte-identical to four consecutive captures of that run).
* The `853x533` is identified: the frontend **render target's** size, and the game's `SetViewport`
  calls are stored but never applied by the RHI (`a7vk_record` uses the swapchain extent for both
  the Vulkan viewport and the shader's pixel mapping).
* New tools in this directory, all read-only over existing artefacts: `cmp9.py` (engine vs screen,
  cell by cell), `fit9.py` (transform search), `flip9.py` (orientation + IoU), `map9.py` (a frame
  as ASCII).

**Did not move.**
* **No coherent car has been seen, and this round does not claim one. No render-path code was
  changed and no run was made** (the card was a peer's for the whole round).
* The question this round *sharpens* rather than answers: the port's own rasteriser of its own
  draws puts a car on 438 cells, and the GPU's frame does not show it, in either y orientation,
  under culling forced off, and with alpha test and blending forced off (§44 of the checkpoint).
  Either (a) the car page these runs reach is **not the sub-page Miami is looking at** — a fork
  that has been open since round 5 and has never been closed — or (b) the car's batches are
  dropped or overwritten **between the batch and the rasteriser** in a way that is independent of
  every state the draws carry. (b) is the one that fits "changing the state changes nothing".
* The next instrument is unchanged and still unbuilt: **the normal-vs-winding test** (normals at
  vertex offset 12 vs the screen-space winding, in the same hook `MENUPROJ` already uses), plus a
  **submit-time cull readout** to close §62's caveat (ii), plus the **`A7VK_SNAP` four-consecutive-
  frame fence** for caveat (i).

## 7. the frames pushed with this file

| PNG | what it is |
|---|---|
| `frames/opt-preview-car_20261011-1440_f3639_ENGINE-SAYS-438-cells.png` | the full frame of `md_proj9b` capture 002 (frame 3639), the frame whose `[OWNER]` prediction is §2's first row |
| `frames/opt-preview-car_20261011-1440_f3639_CAR-REGION-2x.png` | the engine's own car rectangle (x 160–1080, y 280–560) cropped out and doubled — what is actually in the car's cells |

Both come from `md_proj9b` (binary `out-md7/cmr2` md5 `b051924366847f8226094d4dc26e3810`, cull
alternating every 2 frames, `LENA_MENUPROJ=1`), whose 3D window is frames 3630–4042.
