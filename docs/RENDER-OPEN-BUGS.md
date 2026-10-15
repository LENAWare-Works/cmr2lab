# The renderer's open bug list

Written 15 October 2026. This file exists because the bug list in the commit that
fixed the part filter was **too short**: it named one defect and the page carried
six more. Everything below is measured, and where a thing is *not* a bug it says
so and gives the measurement that ruled it out.

Scope: `tools/render/` — the offline car renderer that produces `assets/`. Not the
port. Not the Deck viewer.


## Fixed

### A parameter that was accepted, documented, and never applied

`build()` took `skip_parts` and tested it with `np.isin(TP, skip_parts)`. Every
caller passed a **set**, and `np.asarray({12})` is a 0-d *object* array, not an
array of elements — so `isin` matched nothing and the argument was inert from the
first commit. The wheel list worked because `wids` is a plain **list**. Two
parameters written the same way, behaving differently, for a year of runs.

The symptom was a `.c3d` drawn as if it were one mesh. It is a **set of render
passes** and only some are bodywork: `06UnlitSim`, `15undsim`, `05BonCam` and
`14LightEffe` are unlit / additive / special-cased in the engine. Drawn opaque and
lit, they leave a flat grey slab through the car and loose plates around it.
`06UnlitSim` alone measured **~8,600 px** of dark grey in the 205's frame.

Fixed by normalising to a list and dropping those passes by the two-character
draw-order prefix (`05` `06` `14` `15`). Pinned in `docs/RENDER.md` §3.


## Open

### 1. Axle positions are one hardcoded constant for the entire fleet

`render_tex.py`: `WHEEL_X, WHEEL_Y, WHEEL_Z = 1.245, -0.227, 0.747`.

That places every car's wheels at corners of **±1.245 / ±0.747**, whatever the car
is. Measured body length:

| car | body length | gets wheels at |
|---|---|---|
| Mini | 3.075 m | ±1.245 |
| 205 | 3.817 m | ±1.245 |
| Subaru | 4.312 m | ±1.245 |

The constant is close for the 205 (~2.49 m wheelbase, real 2.42) and clearly wrong
for the Mini, where the wheels land outside the arches.

**What makes this a defect rather than a limitation:** the real positions are in
the file. They are the scene nodes the Deck viewer already reads. This is guessing
where the data exists — and the docstring used to present the guess as the same
constraint the engine has, which it is not.

### 2. `make_wheels()` is dead code — 25 lines, never called

`render_tex.py:88`. Documented as "used for measuring the true contact line". It is
not called by anything in this repository; `grep -rn make_wheels --include=*.py`
returns only its own definition. The contact line is measured in
`make_assets.hero()` from the render mask instead. Annotated in place rather than
deleted, so the next reader does not rewrite it.

### 3. The 4th channel is sampled and thrown away

`render_tex.py:179` — `rgb = sample(t, u, v, flip)[..., :3]`.

Alpha is decoded, interpolated, and discarded, so everything renders opaque.
`07SemiTrans` (glass) is **8.9 % of the part's triangles**, and `14LightEffe` is
the light flares — both are alpha-blended or additive in the engine, and this
repository already documents that (`livery.py` header, `docs/FRAME-NOTE.md` §3).
The parts are simply drawn as lit opaque geometry.

### 4. `flip` is threaded through the sampler and never used

`sample(..., flip=False)` and `render(..., flip=False)`; every call site leaves it
False. The V orientation of the car atlas is therefore **unverified**.

Tested 15 October: rendering with `flip=True` changes the frame by
0.2 luminance (97.6 → 97.4), i.e. nothing. So it is not a live defect — it is a
latent trap that looks configurable and has never been exercised either way.

### 5. Sampling is nearest-neighbour — no filtering at all

`render_tex.py:118` — `texel[v.astype(np.int32), u.astype(np.int32)]`.

Every magnified texel is a hard square. A 128–1024 px texture across a few hundred
screen pixels gives visible stair-stepping on the decals. No bilinear, no
mip chain, no anisotropic. This is the cheapest of the open items to fix and the
most visibly wrong at close zoom.

### 6. The lighting term is overbright and hides a magic constant

`render_tex.py:181` — `diff = 0.42 + 0.58 * l1 + 0.22 * l2 + 0.10`

Maximum reachable value is **1.32**, which is then clipped, so the top third of the
range is dead. The `+ 0.10` is an ambient floor added *inside* the expression, which
means it scales nothing and reads as a fudge. There are three directional lights
declared elsewhere in the project and two used here.

### 7. `pick_livery()` is ranking on decode noise

`tex.py:70`. It chooses the body texture by highest mean saturation. Measured on
the 205, the two candidates are:

| texture | mean saturation | carries |
|---|---|---|
| `ap5dbodf` | 0.06 | the decals — Michelin, Bilstein, SKF, Peugeot, a race number |
| `ap5bodbu` | 0.00 | no decals |

The decision rests on **0.06 versus 0.00**. It has returned the right answer every
run so far, but that was checked by *looking at the textures*, not by this
function. The old docstring also asserted the other one was "an AO pass" — an
assertion that was never measured. Docstrings corrected to say so; behaviour left
alone deliberately, because changing it without looking would be the same mistake
in the other direction.


## Not a bug — ruled out by measurement

### The car body is grey, and it is not the lighting

The committed car renders come out mid-grey (mean luminance ~98 on a white-with-
decals texture) where the Deck viewer's own frames show white. Investigated and
**not caused by any of the above**:

* **Texture decode is correct.** The livery decodes with readable Michelin /
  Bilstein / SKF / Peugeot markings and a race number.
* **UVs are clean** — 0.0 % of them fall outside 0…1, and the body spans
  u 0.012–0.472, v 0.414–0.801 (17.8 % of the atlas).
* **The body samples white texels** — at the body's vertex UVs, median luminance
  **0.907**, 82.6 % of them above 0.8.
* **It is not the shading term.** Rendering with the lighting bypassed entirely
  (`rgb = clip(rgb, 0, 1)`) still gives mean **117.8**, median **120.3**. The loss
  is upstream of the shading.
* **Camera and normals are correct.** The eye sits 1.56 m above the 205's roof, the
  roof projects above the floor on screen, and stored normals agree with winding
  orientation on **100 %** of triangles.

So the remaining gap is *which* region of the atlas the per-pixel UVs land on
versus what the Deck viewer does differently — one shader, two implementations.
Unresolved, and stated here unresolved rather than filed under a cause it does not
have.


## Two traps worth knowing before you measure this pipeline

* **`render()` re-centres the camera on whatever vertices it is handed.** Subset the
  vertex array along with the triangles and every part is framed differently, so
  per-part numbers are not comparable and the "dominant" part changes run to run.
  Keep the full `V`; subset only the triangle list.
* **Do not ask a vision model to settle geometry.** On this inspection one
  described a correct render as viewed *from below* — the camera is 1.56 m above the
  roof — and called the car broken both before and after the fix. Vision is good for
  *what is there*; the numbers are for *which part is where*. A side-by-side A/B is
  far more reliable than any single absolute description.
