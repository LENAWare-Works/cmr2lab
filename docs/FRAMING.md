# THE FRAMING — the frame is the 3D path and nothing else, the transform is the game's own, and the picture is near-plane blow-up

`work/RACE`, 2026-10-11 06:5x EEST. Round: **"whether the framing is right"** — the one
claim `ROAD-TEXTURE-OWNER.md` §9 refused to defend without a picture beside it.

Read with `CHECKPOINT.md` (how to re-run) and `ROAD-TEXTURE-OWNER.md` (the index-base
fix this measures the other side of). Every number below is measured on this Deck,
off the frames in `out/` and `out/ab/` and off two runs on **his** binary
(`work/PLAY/out-plain/cmr2`, `b960621bcc5657e135640e35aa70869f`).

Where a sentence here disagrees with anything written before it, this file wins and
says so.

---

## 0. THE THREE LINES

1. **The picture is the 3D path and only the 3D path.** With the 3D batches switched
   off *by frame number inside the same run*, the frame is **exactly one colour** —
   `0x9cb4ac`, 100.000 % — so the 2D layer puts nothing on screen in a race: no HUD,
   no backdrop, no text. With the 3D path on but no texture bound, the frame is
   **exactly one colour** — `(255,255,255)`, 100.000 % — so the 3D geometry alone
   covers **every pixel** of the frame. There is no un-covered region anywhere in it
   for a horizon, a sky or a road verge to live in.
2. **The transform is not the port's fault, and that is now measured against the
   game's own code, not against a hunch.** The projection the port hands the shader
   reproduces `CGraphics::SetProjection` + `View_SetPlayerProjection` to four decimals,
   with the aspect ratio coming out at **1.600 exactly** (1280/800) in every sample.
3. **What the numbers do support is the phone's second guess: near-plane blow-up.**
   In a static-camera shot the geometry handed to the draws spans clip `w` ∈
   [-89.3, +121.5] against a **near plane of 5.86**, and its NDC `x` reaches
   **-2.8 × 10⁷** (worse at other frames). Those are screen-spanning triangles with a
   near-flat texture gradient — smeared blocks of colour, exactly what the vision pass
   described. It is not "a horizon sitting too high"; the horizon reading is what a
   blow-up looks like from the outside.

---

## 1. LENA-ON-THE-PHONE'S MEASUREMENT, REPRODUCED INDEPENDENTLY

She measured `out/idxfix_race.04_t78.ppm` and `out/final_inert.03_t70.ppm` on the
phone and said "if your numbers say something different, your numbers win". They
don't differ. `frame_forensics.py` walks **every pixel** of the 1280×800 frame
(1,024,000 px, no sampling) and gets, for `idxfix_race.04_t78.ppm`:

| her number | mine, every pixel |
|---|---|
| clear colour 0x9cb4ac = 0 px, 0.0 % | **0 px, 0.0000 %** |
| 54,664 / 53,442 distinct colours | **54,664** here (the other frame is the 70 s one) |
| top five all browns | **(33,16,0) 12,765 px 1.25 %, (115,85,49) 9,693, (90,60,33) 7,948, (82,56,33) 7,721, (41,20,8) 6,747** |
| hard horizontal edge at y 124-130, ~15/channel | **largest row jump dy=16 at y=130**: (156,131,123) → (172,144,137); the whole ramp is y=122…132 |
| no sky, no road, no car, no HUD | the 96×40 block map is `r` (R ≥ G+16) over **96 % of its cells**, with one blue-dominant wedge at the top-left corner and two darker blobs — nothing else |

Full numbers and the map: §5 of this file, and `frame_forensics.py` re-derives them.

**And she is right about the stale item.** Her control claim checks out: the earlier
"unidentified white screen" is gone. `out/final_inert.00_boot.ppm` is
**99.626 % exactly `0x9cb4ac`** with **17 distinct colours in the whole frame** and
0.20 % pure white. The `FIXBG` fix landed; item 3 of the old open list was measuring
something that is no longer there and is struck in `CHECKPOINT.md`.

---

## 2. ONE RUN, ONE SCENE, ONE VARIABLE — the A/B pictures

`run_framing.sh` (new). Two runs are never the same scene, so the switch is driven by
the RHI's own frame counter and the captures by `A7VK_SNAP`'s frame list: **ten frames
out of one run, in five pairs twenty frames apart**, each pair straddling one switch.

| frame | mode | distinct colours | clear % | what else |
|---|---|---|---|---|
| 3290 | normal | 126,474 | 0.000 | htrans 0.842 — per-pixel detail, noise-like |
| 3310 | **notex** | **1** | 0.000 | **100.000 % (255,255,255)** |
| 3590 | notex | **1** | 0.000 | 100.000 % white (null test on the mode, 280 frames later) |
| 3610 | normal | 128,653 | 0.000 | content back — the switch is what changed |
| 3890 | normal | 122,455 | 0.000 | **20.53 % pure white** inside a textured frame |
| 3910 | opaque | 67,829 | 0.000 | (76,50,27) 11.10 %, (51,52,30) 9.63 %, white 7.87 %, (153,160,164) 6.64 % |
| 4190 | normal | 55,889 | 0.000 | the browns of §1 |
| 4210 | **skip3d** | **1** | **100.000** | **the whole frame is the clear colour** |
| 4490 | skip3d | **1** | 100.000 | same |
| 4510 | normal | 55,021 | 0.000 | top six identical to frame 4190, 320 frames later |

Two controls sit inside this table: 3590 vs 3610 (both normal-mode pairs that should
differ only by the switch) and 4190 vs 4510 (normal before and after the skip3d
interlude — same picture). The modes are not being silently ignored.

`frame_compare.py` (new) produced the table; `out/ab/abfix.ppm.*` are the frames.

**What this settles.** `skip3d` = one colour means the entire visible frame in a race
comes from the 3D batches. There is no 2D HUD layer, no 2D backdrop, nothing behind
the 3D scene — so "the framing is wrong" cannot be fixed in the 2D path, and equally
"no HUD, no text" is not evidence of a HUD bug. It is evidence that nothing else is
being drawn.

---

## 3. THE TRANSFORM, CHECKED AGAINST THE GAME'S OWN SOURCE

The instruments print the matrices the **game** set (`D3DTRANSFORMSTATE_VIEW`/`_PROJECTION`,
latched after the game's own `SetTransform`). Read against the decomp:

```
FixedPoint.cpp:718  void View_SetPlayerProjection(unsigned int player) {
FixedPoint.cpp:719      int zoom = g_unk0x005391cc[i];
FixedPoint.cpp:720      fovX = FixMul(0x123d7, FixMul(FixMul(zoom, 0x275c2), aspect));
FixedPoint.cpp:721      fovY = FixMul(0x2147a, FixMul(zoom, 0x275c2));
Graphics.cpp:2161   void CGraphics::SetProjection(fovX, fovY, farPlane, nearPlane) {
Graphics.cpp:2194       m_projection11 = m_fovX * scale;      // scale = m_projectionScale = 0.5f
Graphics.cpp:2196       matrix._22 = m_projection22 = scale * m_fovY;
Graphics.cpp:2191       m_projection33 = m_farPlane / range;
Graphics.cpp:2204       m_projection43 = -(m_nearPlane * m_farPlane) / range;
```

At zoom = 1.0 (`0x10000`) that is `m22 = 0.5 × 2.08 × 2.46 = 2.558`. Checked against
the printout: frames 3400-3600 read `|row1|` = 2.8035 … 2.8781 → zoom 1.096…1.125, and
`|row0| / |row1|` = 0.8769 → `0.548 × aspect` → **aspect = 1.600**, which is
1280/800 exactly. **The port's composed transform and the game's own projection agree;
there is no scale, no swap and no aspect bug in it.** `VIEW` is rigid and orthonormal
(`|row0..2| = 1.0000`, `row0·row1 = 0.0000`, last row `(0,0,0,1)`) in every sample —
frontend and race.

**What the same print shows, and this is new:** the race's camera is *not* a fixed
projection. Over one run the game's own `zoom` (the blended `CameraRecord.field_0x54`,
`Car.cpp:8377`) ranges **≈1.0 → 7.1**, i.e. the vertical FOV goes **42.7° → 6.4°**, and
the near plane (`state.field_0x4c`, the same blend) goes **1.00 → 5.86** with the far
plane pinned at 200. Those are camera-record values, blended per frame by
`CameraState_Interpolate` — which is why they ramp smoothly instead of stepping.

I am **not** claiming that is a bug. It is the game's own camera data, and CMR2's
attract mode is a TV-style flyby that cuts between long-lens shots. It is written down
because it changes what a "correct" frame should look like at any given second, and
because it is the first place to look if the framing is wrong after all.

---

## 4. WHAT THE GEOMETRY IS ACTUALLY DOING — `A7VK_GEOTRACE` at ONE dump per frame

`run_perframe.sh` (new) runs the same instrument at `A7VK_GEOTRACE_EVERY=1`, so the
camera block and the geometry block belong to the **same frame**. That was the whole
problem with the 60-frame dumps: the attract camera cuts inside them.

Frames 4120-5120 are a **static shot** — the camera sits at (-585.2, -21.8, 149.9)
for seven seconds — which makes its numbers easy to read:

```
f=4480  cam (-585.3 -21.8 149.8) | obj x=[-100.0 167.1] y=[-0.6 100.0] z=[-100.0 742.9]
        w=[-89.2 +121.4]  ndc x=[-832455.8 +634.7] y=[-159.9 +58077.4]  behind=6837/19417
        coverage: tri_full=… screens_covered=24.46  screens_all=4746.4
```

* **The clip-space extents are astronomical.** NDC `x` to **-8.3 × 10⁵** here and
  **-2.8 × 10⁷** at frame 4560, against a viewport of ±1. A vertex a hair in front of
  the near plane projects to millions: that is a near-plane blow-up, and each one
  rasterises as a screen-spanning triangle with an almost flat texture gradient.
* **The geometry crosses the near plane all the time.** `w` (view depth) spans
  -89 → +121 with a near plane of 5.86; 6,837 of 19,417 vertices (35 %) are behind the
  camera in that shot.
* **The drawn area is dominated by exactly those triangles**: triangle area clipped
  inside the viewport is 0.34-28 screens per frame (that one screen of coverage is
  what makes the frame 100 % covered), while the *unclipped* area is 300-6,100 screens
  per frame — **100× to 500× more**. The frame is being painted by triangles that
  mostly live off-screen and a little of which lands on it.
* **The geometry itself is not obviously corrupt.** Object-space ranges are plausible
  and stable (`y ∈ [-0.6, 100]` in every frame; `x`/`z` hundreds of units), no
  non-finite vertices at all (`nonfinite=0` in every dump), and the index fix's own
  census still holds.

**One thing I could NOT settle, and will not claim.** The camera's world `y` is
negative (-11 … -349) while the *object-space* `y` of everything drawn is [-0.6, 100],
which would put the camera under the ground — **if and only if** object space is world
space. `recover_world.py` (new) tries to recover the per-draw `WORLD` by solving
`W = mvp1 · (V·P)⁻¹` from what the two instruments print; it does **not** come out
rigid (row norms 0.11 / 14.3 / 1.03), so either the print conventions do not match or
the flat `mvp1` is not the composed `W·V·P` in the layout the print suggests. Until
that is resolved, "the camera is under the scene" is a **hypothesis with a number
pointing at it**, not a finding.

---

## 5. THE FRAME, MEASURED — every pixel, no sampling

`frame_forensics.py out/idxfix_race.04_t78.ppm`:

```
1280x800   distinct colours (exact): 54664 = 5.34% of 1024000 px
clear-colour 0x9cb4ac : 0 px (0.0000%)   pure white: 0 px   pure black: 0 px
top 12: (33,16,0)12765  (115,85,49)9693  (90,60,33)7948  (82,56,33)7721
        (41,20,8)6747  (66,44,24)6039  (33,16,8)5892  (44,24,10)5680
        (66,36,16)5375  (206,182,181)4993  (24,8,0)4677  (43,24,10)4340
row means: y0 (114,83,51)  y80 (88,54,31)  y120 (94,42,24)  y160 (193,162,155)
           y240 (176,140,109)  y400 (113,87,61)  y520 (117,93,68)  y760 (48,27,12)
pale fraction (luma>150) per row: y160 = 0.891, y240 = 0.539, y560..y760 = 0.000
```

`notex` 100.000 % white and `skip3d` 100.000 % clear are the two ends of the range;
everything in between is geometry times texture.

---

## 6. INERTNESS AND THE DESK

Both runs on `work/PLAY/out-plain/cmr2` = `work/RACE/out-texreq/cmr2`
(`b960621bcc5657e135640e35aa70869f`), started with `run_framing.sh` /
`run_perframe.sh`, which do the housekeeping the checkpoint asks for (kill stale
drivers by bracketed pattern, `pkill -x cmr2`, clear `/tmp/trig.ppm.*` and
`/tmp/snapnow`). **GPU ring timeouts 12 → 12 before/after both runs.** No window left
on his desktop, no stray process, both runs ended by drive.py's SIGINT census.
New env-gated instruments in this round: none — the two runs use `A7VK_GEOTRACE`,
`A7VK_GEOTRACE_EVERY`, `A7VK_AB`, `A7VK_SNAP`, all of which are already in the tree and
inert when unset.

---

## 7. OPEN, IN THE ORDER I WOULD TAKE THEM

1. **Kill the near-plane blow-ups and look at what is left.** The honest test of §4:
   skip (on the CPU, in the port) any triangle whose vertices are not all in front of
   the near plane, capture the same frame numbers, and see whether a scene appears in
   the holes. If the frame resolves, the framing question is answered — the picture was
   blow-ups over a scene. If it does not, the blow-ups were a symptom of the camera
   actually being inside the geometry and the question moves to the camera.
2. **Settle object space vs world space.** §4's unresolved bit. The cheap version:
   print each 3D draw's `WORLD` translation and the object-space bbox of that draw
   **in the same line**, then §4's static shot answers itself without any matrix
   recovery. This is one gated print in `gt_note_3d`, next to the existing one.
3. **The camera's own numbers are now instrumented and worth one run on their own**:
   `zoom` 1.0 → 7.1 and near 1.00 → 5.86 are camera-record values; if the stage's own
   camera records are right, a chase camera in a *race* (not the attract flyby) should
   sit at zoom ≈ 1 and near ≈ 1. That is a two-line check on the same printout, and it
   would separate "attract mode looks like this" from "the camera data is wrong".
4. **Still open, still not re-reported:** stage 1 never bound, `TEXTUREFACTOR` and the
   dropped states (S2a), the alpha path, the white 20.5 % inside frame 3890.
