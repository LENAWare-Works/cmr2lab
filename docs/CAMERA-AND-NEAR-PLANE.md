# THE CAMERA AND THE NEAR PLANE — measured against the game's own code, with a picture beside the numbers

`work/RACE`, 2026-10-11 ~07:5x EEST. Round: **the one §0f refused to claim.** §0f said,
verbatim, *"The picture has not been checked against a reference. … Whether the framing and
the near plane are what a Kenya stage should look like is the next question, and it needs a
picture beside the numbers."* This is that question, answered with numbers, and with four
frames in `frames/`.

Read with `docs/ROAD-TEXTURE-OWNER.md` (the index-base fix this measures the far side of) and
`docs/DRAW-CENSUS-RACE.md` (what is drawn). Nothing here re-derives those.

---

## 0. THE THREE LINES

1. **The race camera is the game's own, it is rigid, and it is sane.** It moves along the
   stage, 3–50 units above the ground, with `znear` **0.877 → 5.694** and `zfar` pinned at
   **200**. The frontend's is **1.0 / 250**. Neither is absurd and neither is stale.
2. **The near plane cannot be what smears the frame — and that is arithmetic, not a
   preference.** This projection's 3rd row is `[0 0 Q 1]` and its 4th is `[0 0 −Q·zn 0]`, so
   `w_clip = z_view` and `z_clip = Q(z_view − zn)`. Therefore

   ```
   NDCx = x_view · m11 / z_view      <- no zn term
   NDCy = y_view · m22 / z_view      <- no zn term
   NDCz = Q · (1 − zn/z_view)        <- the ONLY place zn appears
   ```

   `znear` can clip geometry and it changes depth quantisation. It **cannot** change where a
   vertex lands on the screen. If the picture is wrong in screen space, `znear` is not the
   mechanism. (A camera sitting *inside* geometry is a different claim, and §4 measures it:
   zero cells of the frame are nearer than the near plane, in every frame sampled.)
3. **What the frame actually is, measured per frame:** 100% of every race frame is owned by
   3D stage geometry and nothing else, and in one shot **the road's own texture — `RD_GA`,
   texId 102 — owns 12.3% of the frame** as a band across the middle, with the Kenya horizon
   panorama (`KEN_1A`, texId 208) at 33.0% and distant terrain (texId 95) at 25.4%. The
   road's paint reaches the frame as *pixels*, not only as a coverage total.

---

## 1. WHERE THE IN-RACE CAMERA COMES FROM

The phone's order asked exactly this. It is answerable from the game's own recovered source,
and the answer is three functions deep:

| where | what it does |
|---|---|
| `SceneNode.cpp:2503` `Scene_SetViewFromCamera` | inverts the camera **node's** world matrix into `viewMatrix` and sets `D3DTRANSFORMSTATE_VIEW` — but only when `g_viewSetupMode < 5 && pCamera->dirty != 0` |
| `Car.cpp:8360-8380` `View_BlendCameraStates` | blends two camera records with `CameraState_Interpolate`, then exports `g_unk0x005391cc[view] = state.field_0x54` (**the zoom**) and `g_unk0x00538df0[view] = state.field_0x4c` (**the near plane**), builds the node's matrix and marks it dirty |
| `FixedPoint.cpp:718` `View_SetPlayerProjection` | `fovY = 0x2147a·(zoom·0x275c2)`, `fovX = 0x123d7·(zoom·0x275c2)·aspect`, then `CGraphics::SetProjection(fovX, fovY, g_unk0x00538e04[i], g_unk0x00538df0[i])` — far plane and near plane, both per view |
| `Graphics.cpp:2161` `CGraphics::SetProjection` | builds the matrix and calls `SetTransform(D3DTRANSFORMSTATE_PROJECTION)` |

**So `znear` and `zoom` are not constants and not port guesses: they are stage camera-record
data, interpolated per frame.** That is why they ramp smoothly instead of stepping, and it is
why a "correct" frame looks different at different seconds. Measured over one clean run:

```
near plane   0.877  0.887  0.900  1.000  1.183  1.746  2.610  4.691  5.684  5.694
zoom         0.625  0.625  0.625  0.625  0.625  0.625  0.650  1.100  1.112  1.112
far plane    200    200    200    200    200    200    200    200    200    200
```

There is **no separate race camera path in the port** — the race sets the same three
transform states the frontend does, through the same `IDirect3DDevice7::SetTransform`, and
the port latches all three (`a7_set_transform`). What differs between the frontend and a race
is the *values the game puts in them*, not the route.

### One correction to an earlier document, because it changes a conclusion

An earlier note read the **translation row** of the VIEW matrix as the camera's world
position and got `y = −21.8`, which put the camera **under the ground** and made "the camera
is inside the scenery" look plausible. For a rigid row-vector view matrix that is wrong:
`v_view = v_world·R + t`, so `eye·R = −t` and `eye = −t·R⁻¹`. Corrected, the same frame's eye
is **(83.18, 18.53, 598.47)** — 18.5 units *above* y=0 — looking along `(0.994, 0.002,
−0.113)`. Every eye position in §4 below is computed that way, and the instrument now
prints it directly.

---

## 2. THE PROJECTION THE PORT HANDS THE SHADER

Two frames, taken off the same instrument, one frontend and one race:

| frame | matrix set | `m11` | `m22` | `Q` | `znear` | `zfar` | `m22/m11` | viewport aspect |
|---|---|---|---|---|---|---|---|---|
| 200 | frontend | 1.1685 | 2.0985 | 1.0040 | 1.000 | 249.76 | 1.7959 | 1.6000 |
| 2650 | race | 2.5239 | 2.8781 | 1.0045 | 0.900 | 200.00 | 1.1404 | 1.6000 |
| 4850 | race | 15.966 | 18.207 | 1.0293 | 5.693 | 200.00 | 1.1404 | 1.6000 |

`Q = m33 = zfar/(zfar−znear)` and `m43 = −Q·znear` in both, which is `Graphics.cpp:2191` and
`:2204` exactly. So the port is not "correcting" anything: it hands the game's own matrix to
the shader and the numbers come back out of it.

---

## 3. A REAL 1.40× HORIZONTAL STRETCH — measured, and the game's own formula

`m22/m11 = 1.1404` in every race frame while the viewport is `1.6000`. For square pixels a
perspective needs `m22/m11 = viewport aspect`, so the race image is **stretched horizontally
by 1.6000/1.1404 = 1.403×**, and the frontend's is *squeezed* by 0.891×.

Where it comes from, from the constants the decomp carries:

```
m11/m22 = (0x123d7 / 0x2147a) · aspect = 0.54811 · aspect
square pixels need  m11/m22 = 1/aspect   ->   aspect = 1.35073
```

The game's own fovX/fovY constants are only self-consistent at a **1.3507** aspect. At 16:10
(1.6000) they are not, and at 4:3 (1.3333) they are off by 2.6%. This is the engine's
arithmetic, faithfully reproduced — **and it is not the mush**: a stretched frame is still a
road with a horizon, just a wider-looking one. It is written down because it is real, it is
measurable, and it is exactly the kind of thing that gets "fixed" into a second bug.

---

## 4. WHAT THE FRAME IS MADE OF — a coverage number that clips

Both existing coverage instruments skip or drop exactly the triangles in question, and
**neither clips**:

* `tu_note` (`DECK_TEXUSE`) divides by `w` and skips only `w ≤ 1e-6`, then caps each triangle
  at 100 screens. That is where "RD_GA = 347,599 screens" comes from (index-base fix, §0f):
  near-plane straddlers, capped, not a texture covering the frame.
* `gt2_note_cover` adds area **only** for triangles with all three vertices inside NDC.
  Most of a real scene contributes 0.00.

New this round (`A7VK_OWNER=1`, inert when unset): Sutherland–Hodgman against the eye plane
(`w ≥ 1e-4`) in homogeneous clip space, then against the viewport rect in NDC, then a
scanline fill into a 64×40 grid with a z-buffer **on view depth**, keyed by texture id. It
resets on **every present**, so each dump is exactly one frame. It is a picture in numbers,
and it names what owns each region:

| frame | eye | `znear` | cells owned | frame depth p10 / p50 / p90 | top textures (share of frame) |
|---|---|---|---|---|---|
| 2650 | (436.9, 10.1, 161.7) | 0.900 | 100.0% | 2.74 / 23.9 / 63.6 | 202 (35.1%) · 197 (27.5%) · 206 (12.1%) · **102 (RD_GA)** |
| 3150 | (259.3, 40.2, 439.6) | 0.884 | 100.0% | 27.6 / 57.2 / 70.1 | **208 (KEN_1A, 33.0%)** · 95 (25.4%) · **102 (RD_GA, 12.3%)** · 107 (7.2%) |
| 3750 | (482.7, 11.9, 191.2) | 1.000 | 100.0% | 2.33 / 12.7 / 27.8 | 269 (24.2%) · 122 (13.3%) · 121 (12.4%) · 178 (10.3%) |
| 4850 | (83.2, 18.5, 598.5) | 5.693 | 100.0% | 6.87 / 7.03 / 8.65 | **151 (CAR_PK1C, 53.1%)** · 153 (CAR_PK1A, 33.6%) · 152 (CAR_PK1B, 13.3%) |

Texture ids resolved to names by joining `TEXREQ`'s `BINDFIRST` (name → surface pointer) to
its `NEWID` (surface pointer → texId), on the pointer, which is the only join ordering cannot
fool.

**Three things fall out of that table, and all three are new:**

1. **100% of the frame is 3D stage geometry in every frame sampled.** Nothing else is on
   screen — consistent with §0f's `notex` → 100% white and `skip3d` → 100% clear colour.
2. **The road's paint owns part of the frame.** `RD_GA` (102) holds 12.3% of frame 3150 as a
   band across the middle at ~121 units, next to the 107/108/112 family at the same distance.
   The index-base fix shows up as *pixels*, which is what §0f could not yet claim.
3. **There is a second class of shot, and it is what "abstract mush" was.** Frame 4850 is
   three textures — `CAR_PK1A/B/C`, the parked-car body panels — covering the whole frame,
   drawn by **two draws each with 10, 127 and 73 triangles**, at **6.87–10.13 units** from the
   eye. A handful of large flat quads a few units in front of the camera produces exactly
   "smeared blocks, one hard edge, no sky" at this resolution. The composition is a measured
   property of the shot, not a rasteriser fault: the map's boundary is a clean straight line
   where the model's panels meet.

---

## 5. THE FRAMES IN `frames/` — what each one is

All four are raw swapchain captures from the port's own `A7VK_SNAP` path, converted with
`tools/ppm2png.py` (which round-trips its own IDAT and refuses to write a file whose pixels
do not come back identical — "it produced a file" is not "the file is the picture").

| file | frame | what the measurement says it is |
|---|---|---|
| `race-sky_1800_owner4.png` | 1800 | 54,358 distinct colours; blue-dominant sky across the top 8 of 40 rows, green vegetation left, warm terrain, white patches. Frame depth (nearest dump, 1850, composite in that build): p50 19.1 units |
| `race-sky_3800_owner4.png` | 3800 | 51,707 distinct colours; same composition class, different camera (nearest dump 3750: depth p50 12.7 units) |
| `race-closeup_3100_owner6.png` | 3100 | 39,101 distinct colours, 93.3% warm; the Kenya dirt stage — the map 50 frames later has `KEN_1A` at 33% and `RD_GA` at 12.3% |
| `frontend_1900_owner6.png` | 1900 | the frontend, for contrast: 97.0% blue, **153 distinct colours in the whole frame** |

**By the order's own gate (sky up top, road receding, a car you can see):** the first two show
sky up top and a receding ground plane; the road is confirmed as *ownership* (12.3% of a
frame) rather than as a legible ribbon; **no car, HUD or timer was confirmed in any of them**,
and none is claimed.

**Two runs, deliberately labelled.** `owner4` and `owner6` are the same binary; `owner4` was
run while a peer worker's driver was injecting keys into the machine-wide input device (199
scancodes seen by the game for a sequence that sends one Enter), `owner6` was clean (4). The
*pictures* are swapchain captures and are unaffected. The *owner maps* for the `owner4`
frames are from that build, which reset its grid only at dump time, so those two maps are
**50-present composites**; every per-frame number in §4 is from `owner6`.

---

## 6. WHAT MOVED, WHAT DID NOT

**Moved:** the race camera now has a path in the game's own code and a derivation that prints
its eye, forward, near and far every frame; `znear` is measured sane and is *proved* unable to
cause a screen-space smear; a coverage instrument that clips exists and names the texture
that owns every cell of a frame; the road texture is measured owning 12.3% of a frame; and
four frames are published for eyes that are not mine.

**Did not move:** the picture's remaining faults. This round does **not** claim a legible road
with verges and a horizon, a car, a HUD or a timer. It also does not explain the 2D layer
drawing 1.87 M primitives per run while §0f measured the frame as 100% geometry — that is the
dropped-state family (S2a) and it is untouched here.

---

## 7. THE LIMITS, PLAINLY

* **12.3% is one frame's number.** It says the road's paint reaches the swapchain in that
  shot; it does not say the road looks right, and no frame is claimed to look like a reference.
* **The car is not confirmed anywhere.** No frame in `frames/` was verified to contain one.
* **Whether the attract cameras are the right cameras is not answered.** They are the game's
  own camera records, blended by the game's own code; that says nothing about whether a
  Kenya stage's flyby should spend 35 seconds 7 units from a parked car.
* **The 1.403× stretch is the game's formula reproduced, not a port defect** — but whether the
  original ran at 1.3507 or shipped with the same 2.6% error at 4:3 is not something this
  round measured.
