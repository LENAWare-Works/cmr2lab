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

## The two things that are easy to get wrong

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
[`CAR-FORMAT.md`](CAR-FORMAT.md).

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
  spans. An intact car is **1** on essentially every row. An exploded mesh shows **5–10**.
* **bounding-box fill** — intact cars land around **0.65–0.70**.

Both numbers are stable across the whole fleet. If a change drops either of them, the
geometry broke, whatever the render looks like.

For the banner specifically, the shadow is verifiable by rendering it twice at strength 0
and 1 and diffing: the shadow should be present as a distinct region extending below the
car's bottom edge. If the car fills the frame vertically there is nowhere for it to land,
which is why `make_assets.hero()` reserves a strip of ground underneath.

---

## Licence note

These scripts ship; the **game's files do not**. `CMR2_CARS` points at *your own* copy of
the retail game. Nothing in `assets/` contains redistributed Codemasters content beyond
images rendered from a user's own install — the same rule the rest of this project follows.
