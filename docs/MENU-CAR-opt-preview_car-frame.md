# the option-preview car's frame — what the numbers say about `frames/md_car_raw.000.png`

written 2026-10-11 10:3x EEST by the `MENU-CAR-FLATTENED` worker (round 4).
png md5 `d71a7580459eb9887d834418b367aec5`, from `md_car_raw.000.ppm` (1280x800).
run: `out-md2/cmr2` md5 `cfd9cb7980dff26a5e56649467845432`, **default** index base (no
`A7VK_IDXBASE`), `LENA_MENUDRAW=1 LENA_MENUDRAW_MAX=3000`, route reaching the option camera
`eye=(0.14 -0.09 -5.00)`.

## why this frame

It is the first capture any run has ever taken **inside the option-preview car's own draw
window**. The instrument itself timestamped it: at that frame 1,377 `MENUDRAW` lines were in
flight (the car), and the owner map sampled 17 frames earlier says 463/2560 cells (18.1 % of the
frame) owned by 8 textures, 2,073 triangles, view depth 4.15-5.55 with the camera at 5.00.

## what the picture contains

| measured | value |
|---|---|
| distinct colours | **232** |
| dominant colour | `(140,150,158)` = **96.417 %** of the frame |
| pixels that are not the dominant colour | 3.58 %, bbox `x[56..1061] y[46..752]` |
| densest regions | a text block top-left and top-centre, a vertical strip near x≈600 at y 330-600, a 508x33 px band at y 600-633, a block bottom-left — i.e. **2D UI**, matching the frame's 13,462 TL draws |

**The car's own screen cells (owner map cols 7..51, rows 11..28 → x 140..1020, y 220..560) show
no pixel that differs from the backdrop.** The submitted geometry is there — 2,073 triangles,
car-shaped, textured, at the right depth — and the presented frame has nothing where it lands.

## what it does NOT mean

* It is **not** evidence about the index base: the same run's instrumented draws are all
  in-range and part-local (see `progress.md` §0i), and the same page under `A7VK_IDXBASE=sub`
  loses the car entirely (1.1 % coverage instead of 18-25 %).
* One capture is one frame. Two readings survive and this file does not separate them: the car
  renders **in the backdrop colour** (a flat fill, e.g. one solid texel), or the car's fragments
  never reach the presented image (z-order against the full-screen 2D backdrop, depth, or the
  snapshot reading earlier than the 3D). Naming which one is the next measurement, and it needs
  several captures inside one car window, not one.
* A pre-fix capture of the same page (`work/RACE/out/owner1.02_t68.ppm`, 07:20, option camera up)
  differs in exactly one region, `x 896..1150 y 167..530`, which is **partly** inside the car's
  cells and partly outside them — so it is not yet attributable to the car. Flagged, not claimed.
