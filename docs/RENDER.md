# The car renderer (`tools/render/`)

Every car image in `assets/` is generated from the retail game's own files by the four
scripts in `tools/render/`. No 3D engine, no game process, no GPU.

```sh
CMR2_CARS=/path/to/game/Game/Cars python3 tools/render/make_assets.py
```

`CMR2_CARS` defaults to `./Game/Cars`. Output goes to `assets/`.

---

## The four files

| file | what it does |
|---|---|
| `c3dlib.py` | reads `PP_F` geometry: header, part records, vertex pool, face records |
| `tex.py` | reads the `.bfl` container and returns the car's `.dds` textures |
| `livery.py` | decides which texture goes on which part |
| `render_tex.py` | assembles one car and rasterises it |
| `make_assets.py` | the driver: renders the set, the grid, and the banner |

The field map in `c3dlib.py` is measured from the files, not inferred — see
[`C3D.md`](C3D.md) for how it was established.

---

## The three things that are easy to get wrong

### 1. A car is not one mesh, and the wheels are not where you think

A `.c3d` holds **several parts**, and **four of them are wheel parts** — each modelled
at the origin. Draw the file as it comes and all four wheels land inside the body. The
result reads as an **exploded / papercraft model**, which is a failure that looks like a
shading problem and is not one.

`render_tex.build()` therefore takes the body *without* the wheel parts and stamps **one**
wheel part out to the four corners:

```python
WHEEL_X, WHEEL_Y, WHEEL_Z = 1.245, -0.227, 0.747   # metres, car space
```

These are the fleet's axle positions. A car with a different track or wheelbase needs them
adjusted — the same constraint the engine has: the game reads `halfExtents` and
`wheelPos[4]` for physics and **never consults the mesh**, so a swapped model whose wheels
do not match its collision box will have its wheels visibly detach. See
[`CAR.md`](CAR.md).

There are also **ten `.c3d` variants per car** (`a1`, `a5`, `c1`, `c3`, `c5`, `d1`, `d3`,
`e3`, `f3`, `f4`). The suffix is a variant selector, not a side — `L` is *light wheels* and
`S` is *snow wheels*, not left and right.

### 2. Two body textures, and only one is the livery

There are usually two textures whose name contains `bod`. The **colourful** one is the
livery; the other is a **grey ambient-occlusion pass**. Picking by name is fragile because
the suffixes are not stable across the fleet, so `tex.pick_livery()` picks by **saturation**:

```python
cands = [k for k in d if 'bod' in k and 'df' in k] or [k for k in d if 'bod' in k]
best  = max(cands, key=lambda k: sat(d[k]))
```

Parts left deliberately untextured: the lights and the underbody. In the engine these are
unlit / additive, and giving them a body texture makes them look painted on.

### 3. A `.c3d` is a set of render passes, and only some of them are the car

Measured 15 October, and it had been wrong in every image this pipeline ever produced.

A car file is not "the car". Laid out by name, `205a1N.c3d` holds fourteen parts and only
six of them are bodywork:

```
01WhlLOD00 x4   the wheels (stamped to the four corners by build())
05BonCam        bonnet-camera interior
06UnlitSim      unlit shadow / interior pass
07SemiTrans     glass
08BodySim       ┐
09Bonnet        │
10RBump         │  the body panels
11Boot10        │
13RSpoiler      ┘
14LightEffe     light-effect flares, unlit / additive
15undsim        underbody pass
```

None of `06UnlitSim`, `15undsim`, `05BonCam` or `14LightEffe` is bodywork. In the engine
they are unlit, additive or otherwise special-cased passes. This rasteriser draws
everything opaque and lit, so drawing them leaves a large flat grey slab through the
middle of the car and loose plates around it — which reads as an exploded model and is
not one. `build()` now drops them, selected by the **first two characters** of the part
name: those prefixes are stable across the fleet even where the names are not
(`06UnlitSim` / `06IntSim` / `06Unlit`, `15undsim` / `15UndSim`, `09Bonnet` / `09BonDay`).

**The bug that hid it.** `build()` accepted `skip_parts` and tested it with
`np.isin(TP, skip_parts)` — but every caller passed a **set**, and `np.asarray({12})` is a
0-d *object* array, not an array of elements. `np.isin` therefore matched nothing, every
time, and the parameter was silently inert from the first commit. The wheel list worked
because `wids` is a plain **list**; the two were written the same way and behaved
differently. The fix normalises to a list.

A parameter that is accepted, documented, and never once applied is invisible to every
check that only asks *did it run*.

---

## Why the grounding is not in the rasteriser

`render_tex.render()` is the thing that produces the verified silhouette, so it is left
alone. The floor and the contact shadow are drawn **afterwards**, into the background, and
the car is composited on top with a real alpha channel (`want_mask=True`).

That separation is what made the banner fixable without touching geometry code. It also
means: **take the alpha from the render's mask, never from an RGB file.** An RGB round-trip
has no alpha, so the whole background comes with the car and shows up as a pale rectangle
pasted over the gradient.

---

## Verification

A solid car and an exploded one are easy to confuse by eye — especially at small sizes, and
especially with a language model looking at the picture. The check that settles it is
numeric, and it is the one this pipeline was validated with:

* **runs per row** — walk each row of the silhouette and count the number of continuous
  spans. Re-measured across the fleet on 15 October, the honest figures are **1 on ~60 % of
  rows, 2 on ~33 %, and never more than 3** (e.g. 205: 54 rows of 1, 32 of 2, 2 of 3). The
  extra spans are the wheels separating from the body below the sill, which is correct. An
  exploded mesh shows **5-10 per row**, so the useful threshold is the **maximum**, not the
  mean — a mean hides a handful of blown-out rows.
* **bounding-box fill** — intact cars land around **0.56–0.69**, fleet-wide.

Both numbers are stable across the whole fleet. If a change drops either of them, the
geometry broke, whatever the render looks like.

**And they did not catch the defect in §3.** Both passed on every image this pipeline
had ever produced, because the stray parts were *coincident* with the body rather than
detached from it: the silhouette stayed one span per row, the fill stayed in range, and
the car was still wrong. These two checks verify that the mesh is **connected**. They
cannot verify that the mesh is the **right** mesh.

What found it was isolating one part at a time and rendering it *at a fixed camera*.
Two traps when you do that, both hit on the way here:

* **`render()` re-centres the camera from whatever vertices you hand it.** Subset the
  vertices along with the triangles and every part is framed differently, so the numbers
  are not comparable and the part that "dominates" changes run to run. Keep the full
  vertex array and subset **only** the triangle list.
* **Do not ask a language model to settle it.** On this very inspect, one described a
  correct render as seen *from below* — measured, the camera is 1.56 m above the roof —
  and it called the car broken both before and after the fix. Use vision for *what is
  there*; use the numbers for *which part is where*. A side-by-side A/B is far more
  reliable than any single absolute description.

For the banner specifically, the shadow is verifiable by rendering it twice at strength 0
and 1 and diffing: the shadow should be present as a distinct region extending below the
car's bottom edge. If the car fills the frame vertically there is nowhere for it to land,
which is why `make_assets.hero()` reserves a strip of ground underneath.

---

## Licence note

These scripts ship; the **game's files do not**. `CMR2_CARS` points at *your own* copy of
the retail game. Nothing in `assets/` contains redistributed Codemasters content beyond
images rendered from a user's own install — the same rule the rest of this project follows.
