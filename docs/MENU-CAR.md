# THE MENU CAR AND THE INDEX BASE — the hypothesis is dead, and this is the measurement

`work/RACE`, round **MENU-CAR-FLATTENED**, 2026-10-11 07:23–08:15 EEST.
Every number below was measured on this Deck tonight, in the game's own binary, and
every claim says which run it came from. Rounds/files: `work/RACE/run_mcab*.sh`,
`work/RACE/mc_drive.py`, `work/RACE/cmp_frames.py`, `work/RACE/crop_map.py`.

Read with `CHECKPOINT.md` (how to re-run) and `ROAD-TEXTURE-OWNER.md` (the index-base
round this one is the other side of).

---

## 0. THE THREE LINES

1. **The pre-race / in-race menu car does NOT use the opposite index convention.** With
   `DECK_IDXTRACE=1` on a whole frontend→stage→race run: **40,000 indexed draws with a
   non-zero base**, `rawInRange = 100.00 %` (1,358,988/1,358,988 indices), `usedInRange
   = 0`, `relOk = 40,000`, **`absOk = 0`**, `neither = 0`. The first indexed draws of
   the run — which are the first 3D the game draws at all, i.e. everything after the
   100 %-2D frontend — are already relative, and they show it in their own arithmetic:
   `startVert=840 numVerts=116 numIdx=156 raw[0..115]`, `startVert=1009 numVerts=60
   raw[0..59]`, `startVert=977 numVerts=32 raw[0..15]` … the indices land exactly in
   `[0, numVerts-1]`.
2. **There is no call site in the game that needs the old re-base.** Both index sources
   are relative to `startVert` *by construction*:
   * parts path — `Mesh_BuildParts` subtracts each part's `minIndex` from `pData`
     (`Mesh.cpp:230-234`) and the draw passes `startVert = vertexOffset + minIndex`
     (`Graphics.cpp:7476`, `7485-7508`);
   * runs / batches path — the index array is the mesh's own 0-based
     `pTriangle->vertexIndex` and the draw passes `startVert = vertexOffset`
     (`Graphics.cpp:7540`, `7540-7560`, `Game.cpp:2190`).
   Subtracting `startVert` is a **second** re-base in both. `Mesh.h:19` says it in the
   game's own words: *"minIndex … first vertex used (indices are relative to it)"*.
3. **A/B with one variable** (`A7VK_IDXBASE` unset = shipped corrected default, vs
   `sub` = the old path), **same binary, same frame numbers**: the 2D/menu frames do not
   move, the 3D frames move completely.
   | frames | what is on screen | pixels differing >8 | mean abs diff | bbox |
   |---|---|---|---|---|
   | 2100–2400 | 2D frontend/loading | **1.60–1.73 %** | 0.19–0.22 | x[146..1078] y[186..551] |
   | 2450–2700 | stage loading + race start | **91.3–98.2 %** | 30.8–40.7 | whole frame |
   | 2800–3600 | race | **95.8–99.7 %** | 31.4–48.9 | whole frame |
   The 2D frames' difference is bounded to one box and averages 0.2/255 — animation, not
   geometry. The PNG pair `frames/race2600_idxbase-RAW.png` (920 kB) vs
   `frames/race2600_idxbase-SUB.png` (54 kB) is **the same frame number, the same
   binary, one env var apart**.

**Scope answer to the order.** The fix does not have to be scoped to the race path by
hand, because it is already scoped by arithmetic: `DrawIndexedPrimitiveVB` now subtracts
only for a draw whose indices are *impossible* as written. Nothing in the run is
impossible as written, so nothing in the menu path changes. **Do not revert, and do not
add a second convention** — there is no call site that wants one.

---

## 1. WHAT MOVED, WHAT DID NOT

* **Moved (measured):** every indexed 3D draw in the stage — road, terrain and the car
  in the stage. 90–99 % of the pixels of a race frame, and the PNG pair above.
* **Did not move (measured):** the 2D frontend/menu path. 1.6–1.7 % of pixels, mean
  0.2/255, one box — the same value in both directions, which is what an animated menu
  element looks like when nothing else changed.
* **Did not move and cannot move (measured, not argued):** the *convention* of the menu
  car's own draws. They are relative before and after; `sub` would corrupt every one of
  them (that is what `usedInRange = 0` means), and the corrected default reads exactly
  the vertices the game built.

---

## 2. THE ONE THING I COULD NOT DO, AND WHY — stated plainly

**I could not photograph the pre-race setup menu on the current build**, so the picture
pair the order asked for (menu car whole under `sub`, flat under the corrected default)
does not exist in this round. Why:

* on this build the game's own attract route goes **frontend → stage load → race**
  without stopping at that screen (dumps every 25–50 frames, `mq_raw`/`mq_sub`/
  `mk_raw`/`mk_sub`, 4 runs);
* opening it deliberately (one Esc during the race, `mp_sub`, 14 captures) did not
  produce the option-menu camera either;
* the runs that *do* show it — `owner1`…`owner6`, camera
  `eye=(0.14 -0.09 -5.00)`, `450/2560` cells, `8` textures, ~48 draws and ~2,770 tris
  per frame — are runs in which a **second driver was injecting keys machine-wide
  through `/dev/uinput`** (the pollution `run_owner2.sh` documents). The menu in those
  runs was opened by an injected key, not by the route. That is where the only pictures
  of it come from, and one of them is in this repo now:
  `frames/menu-prerace_before-idxfix_23h09.png` (`out/patched-with-snaps.04_idle.ppm`,
  the 23:09 run, i.e. **the pre-fix binary** `b46d80fee5489834b87f843fd15484e0`).

So the order's question is answered **by arithmetic and by numbers and not by a look**,
and I am not going to dress one up as the other.

---

## 3. WHAT THE MENU SCREEN'S OWN NUMBERS SAY (and what they kill)

From the option-menu dumps in `out/owner2.log` (f1500), `owner3.log` (f1200–f2700) and
`owner4.log` — the same screen, three runs, identical signature:

```
cam eye=(0.14 -0.09 -5.00) fwd=(0.000 0.000 1.000)      <- OptionMenu_CreateBackgroundWorld's
proj znear=1.0000 zfar=250.00 | xscale=1.5185 yscale=2.0985   own camera and SetProjection
depth: min=4.12 p10=4.12 p50=4.18 p90=4.29 max=4.60 | cells nearer than znear: 0 (0.0%)
owner map: 450/2560 cells (17.6%) by 8 textures | ~48 draws, ~2,770 tris per frame
A tex=33 211 cells 8.2%  B tex=36 68 2.7%  C tex=34 44 1.7%  D tex=38 2 0.1%
```

* **The near-plane story does NOT apply here.** 0 of 2,560 cells are nearer than the
  near plane; the whole car sits 4.12–4.60 units away against `znear = 1.00`. The race's
  blow-up (`w ∈ [-89.3, +121.5]` against `znear = 5.86`, NDC x to `-2.8e7`) is not
  present on this screen at all, so "the menu car looks flat because of the near plane"
  is dead too.
* **What the car looks like in numbers** (owner map, 64×40 cells, 20 px each): geometry
  spans rows 14–27 (y 280–540) and columns 7–51 (x 140–1020) — a **880 × 280 px** mass,
  aspect ≈ 3.1 : 1, with two symmetric clusters at its top corners (cols 9–18 and 38–47)
  and a separate lower block of textures B/D along its bottom edge. That is the shape to
  put beside the pre-fix PNG. It is coarse, it is honest, and it is the only picture of
  that screen this project has from the current build.

---

## 4. WHAT I DID NOT CLAIM

* **Not claimed:** that the menu car is fixed; that it is broken; that I saw it.
* **Not claimed:** any RHI change. **No source was edited this round.** After this
  measurement the correct end state is the state the tree is already in: the corrected
  base stays the default, `A7VK_IDXBASE=sub` stays as the A/B switch.
* **Not re-derived:** the race baseline (delivered in `ROAD-TEXTURE-OWNER.md`), and not
  re-reported: stage 1, `TEXTUREFACTOR`, the S2a dropped states, the alpha path, the DXT
  blit, `wroteByGame`, the handoff.
* **Not claimed:** that the runs that showed the option menu are usable as race
  baselines — they were key-polluted, and `run_owner2.sh` already says so.

## 5. WHAT I WOULD DO NEXT, in order

1. **Open the car-setup menu deliberately and photograph it**, on the corrected default
   and on `A7VK_IDXBASE=sub`, same frame numbers (the A/B machinery in
   `run_mcab4.sh` already presses one Esc during the race; it needs the *car setup page*
   of the menu, not the pause page, and a longer hold). That is the picture pair this
   round could not get.
2. **The strongest remaining suspect for a flat menu car is the menu's own geometry
   path, not the device's.** The option menu builds its own 32-byte fixed-point vertex
   buffers (`OptionPreview_AllocateConvertedWheelVertices`, `0x20` stride) and deforms
   them per frame (`OptionPreview_RebuildDeformedGeometry`,
   `CarDamage_ApplyCameraSpaceMeshDent`, `GameInfo.cpp:7727/8147`, `StageTiming.cpp:5340`),
   and *that path is used by no other screen*. `DeckDevice7::DrawIndexedPrimitiveVB`
   derives its stride from the FVF as `TLVERTEX ? 32 : 48` — if the preview meshes ever
   reach it with a 32-byte non-TL vertex, the device reads them at the wrong stride, and
   "all mangled and jungled up into one flat piece of paper" is exactly what that looks
   like. Worth one instrumented run before anything else: print the FVF and the stride
   per menu draw and compare them with the mesh's own `sizeUnits`/`field_0x10`.
3. Put the pre-fix menu PNG (`frames/menu-prerace_before-idxfix_23h09.png`) beside a
   current one of the same screen — that single pair answers "regression or not" with an
   eye, which no amount of map-reading will.

## 6. HOUSEKEEPING

* Six runs this round (`mc2`, `mcafter`, `mcafter_sub`, `mcbefore`, `mk_raw`, `mk_sub`,
  `mq_raw`, `mq_sub`, `mp_sub`): **GPU ring timeouts 12 → 12**, every time.
* **His binaries untouched:** `work/PLAY/out-plain/cmr2` =
  `b960621bcc5657e135640e35aa70869f`; the pre-fix backup
  `cmr2.bak-pre-idxbase-20261011` = `e43d7a1e4279fe2c05647c7c053d4fd3` (md5s re-checked
  after every copy). Instrumented copies live in `work/RACE/mkr`, `mks`, `mcbefore`,
  `mcafter` and are named so `pkill -x cmr2` does not match them.
* No window left on his desktop, no stray process, `/tmp/mc.ppm.*`, `/tmp/mk.ppm.*`,
  `/tmp/mq.ppm.*`, `/tmp/mp.ppm.*`, `/tmp/snapnow` cleared.
* **The box has two workers.** `mc_drive.py` refuses to fight: it watches for a competing
  game and yields within a second, and it never touches `/tmp/snapnow` or
  `/tmp/trig.ppm.*` (the RHI's hardcoded handshake is a single shared resource). Five
  attempts were yielded to the other worker's runs this round; nothing of theirs was
  killed or touched.
