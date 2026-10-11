# MENU-CAR-EVIDENCE — the addendum, measured

`work/RACE`, task **MENU-CAR-EVIDENCE-VISION**, 2026-10-11 07:35 → 08:5x EEST, worker 2.
Written as the evidence addendum to `MENU-CAR.md` (round `MENU-CAR-FLATTENED`, closed
`partial`), so this file is the work order's answer, not a new round of the same work.

**Nothing was run on the GPU this round.** The box was held by worker 1's
`HE-PLAYED-IT-LIGHTING-AND-DEATH` runs the whole time (the phone's rule: *the death comes
first*), and their driver and ours share one hardcoded handshake. Everything below is
measured from **bytes already on disk** — captures, logs, kernel journal — or read out of
the game's own source, and every claim says which.

---

## 0. THE FIVE LINES

1. **The discriminating A/B the phone asked for has still not been run on her screen —
   and it cannot have been, because no run that carried a `DECK_IDXTRACE` instrument ever
   displayed the option/setup screen.** Measured: the option-menu camera
   `eye=(0.14 -0.09 -5.00)` appears in **`owner1`, `owner2`, `owner3`, `owner4`,
   `owner5`** (12, 4, 16, 4, 2 hits) and in **none of the six trace runs that also carry the
   camera instrument** — `mk_raw` 98 camera lines, `mk_sub` 99, `mq_raw` 160, `mq_sub` 160,
   `mp_sub` 209, `mcafter_sub` 117, all with **0** option-menu hits. (The two trace logs
   without the camera instrument, `idxtrace_race` and `idxfix_race`, have 0 camera lines
   each, so they cannot speak to it either way and are not counted.) The complementarity is
   exact: every log with `IDXTRACE>0` has 0 option-menu hits and every log with option-menu
   hits has `IDXTRACE=0`. So `MENU-CAR.md` §0.1's sentence
   *"the pre-race / in-race menu car does NOT use the opposite index convention"* is
   **over-claimed**: what was measured is that the indexed draws of a run that never
   entered that screen are relative. §2 below says why the *conclusion* still holds — but
   for a different reason than the round gave, and the difference matters.
2. **Her mechanism is dead anyway, and by a stronger argument than a trace: there is no
   call site in the game that could want the old re-base.** All ten
   `DrawIndexedPrimitiveVB` calls in the game (enumerated in §2, with their index arrays
   and their `startVert`) hand either mesh-local 0-based indices with
   `startVert = vertexOffset`, or part-local indices already re-based by `minIndex` with
   `startVert = vertexOffset + minIndex`. The port's shipped default reads
   `startVert + idx` — the vertex the game built — in **both** cases. `sub` reads `idx`.
3. **Her observation is not explained by any of that, and her five constraints are the
   best evidence this project has of what the patch actually is.** They are recorded
   verbatim in §4 and used as constraints, not as instructions. The families of mechanism
   that survive them are listed there, with the single instrument that discriminates them.
4. **Her optional item is answered from the draw path: missing text cannot be a
   missing-path artefact.** Font atlases load on both screens (measured, `mk_raw.log`
   lines 84–87 and 444–450), `Font_DrawText` → `Font_DrawChar` → `Sprite_Queue` →
   `Sprite_DrawLayer` → `DrawPrimitive(D3DFVF_TLVERTEX)` is implemented, and that path is
   exercised 1.66–1.87 M times per run. §5 has the citations and the one thing that would
   settle the pixels.
5. **What I added that the last round did not have: the control for its own A/B.** Two
   runs of the *same* convention differ by 1.61–1.67 % of pixels; the raw-vs-sub pair
   differs by 1.55–1.66 %. The A/B is inert on those frames — confirmed, not asserted.
   §3 has the numbers, including the bbox that is identical in both comparisons.

---

## 1. WHAT WAS CHECKED FIRST — every claim in the phone's message, against what exists here

Her message is five pixel observations and one reading. I have no copy of the two photos
(they are on the phone side; `work/RACE/fromlenaphone/` holds the *earlier* task's two race
JPEGs, nothing from today), so her observations are **taken as given** — she says they are
measurements of pixels, not guesses, and nothing here contradicts them. What I could test
is the machine she was pointing at, and that is what follows.

| her item | status here |
|---|---|
| small patch, 10–15 % of W and H, just below vertical centre, on the horizontal centre line | **no capture in this repo shows it.** The nearest measured object on the current build is a **880 × 280 px** mass at y 280–540 (`MENU-CAR.md` §3, owner-map, coarse). Not the same shape — hers is ~150 px square. |
| shards, hard edges, flat unshaded colour | no capture shows this either |
| colours are the car's own livery, positions roughly right | this is the constraint that does the work; see §4 |
| no silhouette / no perspective | ditto |
| no long triangles, none off-screen, one or two stray white triangles | ditto |
| no menu text anywhere | answered from the draw path in §5 |

**The honest state of the picture:** the only capture of that screen in this project is
`frames/menu-prerace_before-idxfix_23h09.png`, and it is from the **pre-index-fix, pre-DXT
build** (`out/patched-with-snaps.04_idle.ppm`, `b46d80fee5489834b87f843fd15484e0`), i.e.
before the change her hypothesis blames. Measured on it just now: 60.53 % of the frame is
the frontend backdrop `(156,180,172)`, **277,067 distinct colours**, and the 3D/UI content
sits in a band of rows 8–21 of 30 — a busy, image-like screen, not a flat one with a patch.
It cannot be the "after" of her photo in any useful sense, and with the DXT blit still
undecoded at 23:09 its textures are not the textures Miami is looking at.

---

## 2. THE MECHANISM — enumerated from the game's own source, not from a sample of one run

This is the part that is new, and it does not depend on any run having reached the screen.
Every `DrawIndexedPrimitiveVB` call in the game (10 of them, 5 functions) and what each
one hands the device:

| # | site | index array | what it contains | `startVert` | correct read |
|---|---|---|---|---|---|
| 1 | `Game.cpp:2166`, `2191` (`Game_DrawMeshTextureRuns`) | `g_unk0x0059be74`, filled at `:2175-2177` from `pTri->vertexIndex[0..2]` | mesh-local, `0 … field_0x10-1` | `pMesh->vertexOffset` | `startVert + idx` |
| 2 | `Graphics.cpp:3393`, `3422` (`Mesh_DrawEnvMapped`) | `g_unk0x006dd9bc`, filled from `pMesh->pTriangles[i].vertexIndex` | mesh-local | `pMesh->vertexOffset` | `startVert + idx` |
| 3 | `Graphics.cpp:7311`, `7358` (`Graphics_DrawCubeMappedShadowTriangles`) | `g_unk0x006dd9bc` | mesh-local | `pMesh->vertexOffset` | `startVert + idx` |
| 4 | `Graphics.cpp:7474` (`Graphics_DrawMeshPartsByTexture`), `7506` (`Graphics_MarkTexturesAndDrawMeshParts`) | `pPart->pData` | **already re-based by `minIndex`** (`Mesh_BuildParts`, `Mesh.cpp:230-234`) | `pMesh->vertexOffset + pPart->minIndex` | `startVert + idx` |
| 5 | `Graphics.cpp:7540`, `7559` (`Graphics_DrawMeshTextureBatches`) | `g_unk0x0059be74` | mesh-local | `pMesh->vertexOffset` | `startVert + idx` |

`Mesh_BuildParts` (`Mesh.cpp:136-241`) is explicit about it — it scans each texture group,
takes `minIndex`/`maxIndex`, then `pMesh->pParts[i]->pData[k] -= (short)minIndex`, and
`Mesh.h:19` calls `minIndex` *"first vertex used (indices are relative to it)"*. The port's
default does exactly that arithmetic; the `sub` path subtracts a **third** time.

**And the preview/setup car is not a separate draw path.** `OptionPreview_RebuildDeformedGeometry`
(`GameInfo.cpp:8105+`, the per-frame deform) ends in `Mesh_Rebuild(...)` (`GameInfo.cpp:8279`,
`GameInfo.cpp:2822`, `StageTiming.cpp:4327`, `5442`) — the *same* `Mesh` object, uploaded into
the *same* shared vertex buffer by `Mesh_Rebuild`/`Mesh_UploadVertices` (`Mesh.cpp:103`, `:260`),
and drawn by whichever of the five functions the scene renderer uses for it. So whatever the
setup screen shows, its triangles come from the same index sources in the table above.

**Consequence, stated plainly:** the phone's reading — *positions right, colours right,
connectivity wrong ⇒ wrong index base* — is a sound reading of a picture, but the code
cannot produce that failure mode on this screen. Something else is tearing the car up, and
`MENU-CAR.md` §5.2's "the menu's own geometry path, not the device's" survives as the
better lead; §4 sharpens it.

### What a wrong base *would* have looked like (so the phone's reasoning is not wasted)

If a mesh were read one `startVert` too far along its own vertex buffer, the triangles would
be built from a *neighbouring* run of vertices in the **same** car buffer: still inside the
car's local space (so still a small blob where a car sits), still wearing the car's paint
(the buffer is car), and completely shard-like in shape. That is exactly the signature she
measured — which is why her colour observation does **not** discriminate, and why the
arithmetic in the table above has to. It does, and it clears the index base.

---

## 3. THE A/B, RE-MEASURED — with the control the last round lacked

Two captures of the same frame number, same binary, one env var apart
(`out/mc/mk_raw.ppm.*` vs `out/mc/mk_sub.ppm.*`; also `mcafter` vs `mcafter_sub`).
`ab_diff.py` (new this round) counts every pixel. Pixels differing by >8 / >32, mean abs
difference over all three channels, and the bbox of the differing pixels:

| comparison | frames | d>8 | d>32 | mean | bbox |
|---|---|---|---|---|---|
| **CONTROL — same convention, two runs** (`mcbefore` vs `mcafter`) | 1000, 1100 | 1.608 %, 1.671 % | 0.937 %, 0.992 % | 0.510, 0.540 | x[146..1071] y[186..551] |
| **A/B — raw vs sub** (`mcafter` vs `mcafter_sub`) | 1000…1600 | 1.548–1.657 % | 0.920–0.971 % | 0.489–0.528 | x[146..1084] y[186..551] |
| **A/B — raw vs sub** (`mk_raw` vs `mk_sub`) | 2100…2400 | 1.587–1.659 % | 0.926–0.992 % | 0.509–0.538 | x[146..1075] y[186..551] |
| A/B, stage/race frames (`mk_raw` vs `mk_sub`) | 2450, 2500 | **91.303 %, 89.433 %** | 86.988 %, 85.086 % | 70.6, 69.5 | whole frame |

* **The control is the finding.** Two runs of the *same* convention differ by the same
  amount, in the same box, as the two conventions differ: that box is an animated element
  on the loading/frontend frame, and the index base moves **none** of it. `MENU-CAR.md` §1
  asserted this ("animation, not geometry"); it is now measured against a control instead
  of inferred.
* **The switch is not inert.** At frame 2450 the same pair of runs differs over 91 % of the
  frame with a mean of 70/255 — so when the convention matters, it is loud. It simply does
  not matter on the frames that were captured.
* **The bbox is the same in every comparison above**, `x[146..1084] y[186..551]`
  (centre ≈ (608, 368) — *above* vertical centre, 72 % × 46 % of the frame). Her patch is
  a ~150 px square *below* centre. **Different object. Different screen.**

### The whole run, one window of detail

The per-draw detail lines (24 of them, the instrument's own first-24 cap) are quoted in
`MENU-CAR.md` as evidence about the menu car. Where they actually are, printed from the log:

* in `mk_raw.log` every one of the 24 sits between line 881 and 905, i.e. at **frame ≈2400**,
  immediately after `[RACE] state InRaceMenu_AdvanceCascade entered` (line 840) and
  `Race_LoadStageGeometry` (802) — the stage-load / race-start window, on the game's own
  attract route, which on this build goes frontend → stage load → race and stops nowhere;
* the aggregate continues for the rest of the run (`mk_raw`: 620,000 draws with
  `startVert!=0`; `mq_raw`: 958,000; `mp_sub`: 546,000; `idxtrace_race`: 404,000), all
  `relOk`, `absOk=0`, and all of it on runs whose measured camera set is
  `(-0.00 -0.00 -20.00)` (frontend) and the race cameras (`(83.18 18.53 598.47)`,
  `(100.00 14.06 514.95)`, `(377.59 13.12 241.83)`, …) — **no option-menu camera in any of
  the six that have the instrument**, counted line by line as above.

`MENU-CAR.md` also quotes the trace as "40,000 indexed draws". No log here ends at 40,000;
the nearest is `idxtrace_race.log` at 404,000 (the race round's own run). The quoted
`rawInRange 1,358,988/1,358,988` does not appear in any tail either. Flagging it as a
transcription slip, not as fraud: every log's *result* is the same shape (100 % relative,
`absOk=0`), so the conclusion is unaffected — but the numbers in that §0.1 should be
re-taken from the log before they are quoted at Miami.

### The per-draw signatures, for the record

In `mk_raw.log` the traced draws are exactly seven per frame, repeating identically from
frame ≈2400 to the end of the run:

```
startVert=840  numVerts=116 numIdx=156   startVert=993  numVerts=16 numIdx=24
startVert=956  numVerts=9   numIdx=24    startVert=1009 numVerts=60 numIdx=36
startVert=965  numVerts=4   numIdx=6     startVert=1021 numVerts=48 numIdx=36
startVert=977  numVerts=32  numIdx=24
```

285 vertices, 282 indices, 94 triangles, in one contiguous VB window `[840 … 1069]` — a
7-texture car drawn the same way every frame. It starts at the stage load and never stops,
on a run that is *in a race*; that is the stage car, not a menu car. Which is the same
conclusion as §0.1, reached from the signature instead of from the claim.

---

## 4. WHAT SURVIVES HER CONSTRAINTS — and the one instrument that separates them

Held fixed (hers): small compact patch, roughly where a car preview sits; the car's own
livery colours present; no gradients or shading; no silhouette, roofline, wheels or
perspective; nothing stretched out of the patch and nothing shooting off-screen.

| # | mechanism | fits her constraints? | how a single run separates it |
|---|---|---|---|
| A | **wrong WORLD/VIEW for the preview** (e.g. the screen's own `OptionMenu_CreateBackgroundWorld` camera not used by the renderer, or a degenerate/scale-collapsed world matrix). Vertices land in a few hundred pixels and overlap → jagged shards, flat, colours and UVs untouched, nothing off-screen. | **fits all five** | print, per 3D draw, the composed W/V/P actually handed to the backend and the object-space bbox read from the vertices → a screen bbox that is a few hundred px wide *from a car-sized object* names this one immediately |
| B | **the preview's own deform path** (`OptionPreview_RebuildDeformedGeometry`, `StageTiming.cpp:5340`, `CarDamage_ApplyCameraSpaceMeshDent`) collapsing vertices — Miami's own phrase is "one flat piece of paper", and this is the only code in the game that *moves* preview vertices per frame and re-uploads them (`Mesh_Rebuild`) | fits, and explains "flat" literally | same line as A, plus: object-space bbox per axis vs the record's stored `centre`/`halfSize` (`GameInfo.cpp` struct offs. 0xb4/0x168). One flat axis = this |
| C | **stride/FVF mismatch on the menu's own converted vertices** — the preview builds 32-byte 16.16 fixed-point buffers (`Unk0x0082d220VertexFixed`, `GameInfo.cpp:1382`, `OptionPreview_AllocateConvertedWheelVertices`, `:7740+`) while the device's stride rule is `TLVERTEX ? 32 : 48` (`deck_dd7.cpp:1441`) | **partial** — positions scramble, but the diffuse/normal bytes are read from the wrong offsets too, so plain livery colour is not what you would expect | per-draw line: FVF, the stride the device chose, the VB pointer, the first six indices, and the first vertex decoded both ways (48-byte float and 32-byte fixed) — one run, no GUI |
| D | **2D-over-3D ordering / viewport** — the preview drawn with the screen-space TL transform instead of the 3D one | fits "compressed into one place" | the same per-draw line: a 3D draw whose callers' W/V/P are the 2D ones |

**Both A and B and D are answered by one instrument, and it does not need the menu to be
navigated to be written.** Spec, in the shape of the instruments already in the tree
(`patch_owner.py`, `patch_idxtrace.py` — idempotent, env-gated, inert when unset):

`LENA-MENUDRAW=1`, in `a7_draw_indexed_fvf`'s caller (`deck_dd7.cpp`), one line per indexed
3D draw, rate-limited: `fvf`, the stride the rule chose, `vb` pointer, `startVert`,
`numVerts`, `numIdx`, `idx[0..5]`, a hard cap of ~4 KB of the VB decoded at 48-byte float
**and** at 32-byte 16.16 fixed (first/last vertex, min/max per axis), and — the part that
pays — the **screen-space bbox** of the vertices this draw actually read, computed in the
same place the vertices are already transformed. Then: the draw that owns a ~150 px patch
in the lower centre prints its own bbox, and the disagreement between "object-space size"
and "screen-space size" is the diagnosis, in numbers, with no picture and no menu hunting.

---

## 5. THE TEXT ITEM — answered from the draw path (she asked "say which", so: which)

The vision pass reported no menu text, no labels, no numbers. From the code:

1. **The atlases load.** `mk_raw.log` lines 84–87 (frontend) and 444–450 (stage):
   `.\Fonts\general\hel_12pt.tga`, `hel_15pt`, `hel_36pt`, `dot`, then `hel_13pt`,
   `hel_20pt`, `lcd_14pt`, `lcd_640`, `ocr_12pt`, `ocr_60pt`. Ten font textures, both
   screens, in one run.
2. **The path is implemented end to end.** `Font_DrawText` (`Font.cpp:302`) →
   `Font_DrawChar` (`:275`) → `Sprite_Queue(..., g_fontBlendMode, …)` (`:295`) →
   `Sprite_DrawLayer` (`Sprite.cpp:66`) → `DrawPrimitive(D3DPT_TRIANGLESTRIP,
   D3DFVF_TLVERTEX, …)` (`Sprite.cpp:177`) → `DeckDevice7::DrawPrimitive`
   (`deck_dd7.cpp:1386`) → `a7_draw_indexed_fvf`. Every hop exists.
3. **The layer the glyphs go to is a drawn layer.** `Font_DrawChar` passes
   `g_fontBlendMode` as the layer; it is `1` at init (`Font.cpp:32`) and set to `2` by the
   menu/race callers (`GameMenus.cpp`, `RallyData.cpp:4789/7869`,
   `StageObjects.cpp:15917`) or `TRUE`=`1` (`Game.cpp:1813`). `Sprite_Queue` implements
   **layers 1–4 only and silently drops anything else** (`Sprite.cpp:322-343`) — 1 and 2 are
   among them, and `Game.cpp:2667/2772-2778` draws layers 4, 3, 2, 1 every frame. Nothing
   falls on the floor.
4. **It is exercised, not just present.** In `owner6`'s census: `DrawPrimitive=1,917,490`,
   `draws by FVF … 0x1c4 TL=1,874,255`, `refused_by_backend=0`.

**So: the missing labels are not a missing text path, and not a dropped sprite layer.** If
they are really missing on that screen, what it would take to see them is a capture of that
screen — the same capture her A/B needs. That is the one thing both items are waiting on,
and it is stated here rather than dressed up.

---

## 6. WHAT I COULD NOT DO, AND WHY — plainly

* **I did not run the game.** Worker 1's `out-death/game_lit` runs held the GPU from 08:11
  through the end of this round (`control2` 08:11→08:16, `control4` 08:17→08:22, further
  runs after), and the phone's own instruction ranks the display death above this ticket.
  Our driver yields to theirs by design, so a run now would either queue or fight.
* **I did not get her photos.** They are not on this machine; the only images from her are
  `fromlenaphone/f_3890.jpg`, `f_t84.jpg` (the earlier race-frame task). Her five
  observations are used as measurements and labelled as hers.
* **I did not reach the car-setup screen**, so the picture pair still does not exist. What I
  did instead is remove the reason it looks unreachable: the screen *was* reached, five
  times, by `owner1`–`owner5` — the runs that had foreign keys injected and, in owner1's
  case, a scancode count of 199–215 (`run_owner2.sh` counts them). The last round recorded
  that as an accident it could not reproduce. It is a lead, not a mystery: keys at the
  frontend reach that screen. The next GPU window should spend itself on **that**, and
  `run_menuhunt.sh` + `menu_hunt.py` (written this round, untested — no GPU) are the
  smallest thing that tests it: inject a slow key burst at the frontend, watch the log for
  the option-menu camera, **stop injecting the moment it appears** (the screen waits for
  input, so it then holds), and capture at fixed frame numbers on both conventions.
* **I did not touch the tree.** No source was edited, no binary relinked, no binary copied.
  `work/PLAY/out-plain/cmr2` is whatever worker 1 last linked — I did not hash it because I
  did not need it.

---

## 7. WHAT I DID CHANGE ON DISK (all in `work/RACE`)

| file | what |
|---|---|
| `MENU-CAR-EVIDENCE.md` | this file |
| `ab_diff.py` | per-pixel A/B of two captures of the same frame number: d>8, d>32, mean, bbox, where-map |
| `menu_read.py` | read a capture offline: dominant colour, non-dominant bbox as % of frame, colour families, family map |
| `menu_hunt.py`, `run_menuhunt.sh` | the reach-the-screen driver (untested: no GPU this round) |

Nothing of worker 1's was touched; their files in `work/RACE` are as they left them.

---

## 8. THE KERNEL LEDGER STANDING BESIDE THE DEATH TICKET

Read from `journalctl -k`, no root (the phone ranked this ticket first; this is what the
journal says, offered to worker 1's ticket, not claimed as mine):

* **Two events today, both before the fix rounds started**: `07:25:40` (page faults,
  `TCP (0x8)`, `RW: 0x0`, `Process cmr2 pid 498908`, pasid 14518) and `07:31:49`
  (page faults, `Process cmr2 pid 501251`, pasid 14553), each followed ~6 s later by
  `ring gfx_0.1.0 timeout → ring reset failed → MODE2 reset` — `GPU reset(14)` and
  `GPU reset(15)`.
* **Nothing since 07:31:56.** No `[gfxhub] page fault`, no `ring gfx_*` timeout, no
  `MODE2 reset` in the journal after that timestamp — through `owner1…owner6`, `mk/mq/mp`,
  `death1`, `death2`, `control1…control4`. So every instrumented run of this morning,
  including the ones that reached a race, has been clean on that ledger.
* Cumulative in the log: `ring gfx_0.0.0 timeout = 12`, `ring gfx_0.1.0 timeout = 3`,
  `MODE2 reset = 14` — the 12 has not moved, and the 3/14 pair is the two this morning
  plus the same-day history the previous rounds recorded.

---

## 9. WHAT I WOULD HAND THE PHONE, IN ORDER

1. **Kill the index-base reading for good, in one sentence, with the table in §2** — not
   because the trace said so, but because all ten call sites re-base (or don't) exactly the
   way the shipped default reads them.
2. **Ask her for one thing the photos cannot give: a full-screen shot at native
   resolution**, so the patch's position can be compared with the owner map's 880 × 280 px
   mass at y 280–540 and with the frontend's animated box `x[146..1084] y[186..551]`. Two
   of the three candidate explanations in §4 differ precisely in where the patch sits
   relative to those.
3. **Then instrument, don't photograph**: `LENA-MENUDRAW` (§4) in one run, on whichever
   screen the game can be made to show, and read the screen bbox of the draw that owns the
   patch. That is a single run's worth of GPU time and it does not depend on navigating
   anything.
4. Only if (3) needs the setup screen specifically: `run_menuhunt.sh`, whose whole idea is
   that `owner1–owner5` reached that screen by accident with keys, so keys are the route.
