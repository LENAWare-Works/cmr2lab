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

---

# ROUND 2 ADDENDUM — `MENU-CAR-EVIDENCE-VISION`, 2026-10-11 08:5x–09:1x EEST

Round 1 of this task wrote §0–§9 above and stopped on the step limit. **No GPU run this
round either** — Miami was driving (verified below), so this is again all bytes on disk.
Two things changed on the box after §5 was written, and one of them overturns part of it.

## 10. THE TEXT ITEM — RE-ANSWERED, AND PART OF §5 IS NOW WRONG

§5 said the missing labels are "not a missing text path". That is still true of the *path*.
It is no longer the whole answer, because **there was a fatal defect on that screen's text
placement path, and it was fixed 13 minutes after §5 was written.**

1. **The defect.** `OptionMenu_TransformHudPointToScreen` (CMR2 `0x00503b70`, definition
   `GameInfo.cpp:6068`) was declared **`int`** in every build of the port and **never
   returned a value**. clang synthesises `ud2` for a non-void function that falls off its
   end, so **every call died with SIGILL** — the body's work done, then the process killed.
   Backup on disk proving the before-state:
   `GameInfo.cpp.bak-pre-missingreturn-20261011` line 6068 reads `int`, the live file reads
   `void`. The prototype in `RallyData.cpp:7132` always said `void`; the definition did not.
2. **It is on the option screen's text path, and it is called twice per icon.** Both call
   sites are inside the loop in `RallyData.cpp` that places the option menu's labels:
   `RallyData.cpp:7210` (guarded by `g_unk0x0082ca04[i] == 100` → literally
   `OptionMenu_DrawTransitionTextShortCoords(..., CFrontend::GetTextString(0xfe),
   rect[0], rect[1], ...)`) and `RallyData.cpp:7237`. The x/y handed to the text call are
   the ones that function just wrote. There is no way to place that label without calling it.
3. **She photographed a build that had it.** Her message is timestamped **07:35 EEST**; the
   `int`→`void` fix was built and swapped in at **08:53** (`work/PLAY/out-plain/cmr2`,
   md5 `d26a09231a98ebb25b6da8b664275f87`). So the binary her photos came from is the
   pre-fix one, by 78 minutes.
4. **It was still firing this morning, in his own session.** `coredumpctl list` shows the
   last two SIGILLs at **08:40:03**, both from
   `/home/deck/lena/work/PLAY/out-plain/cmr2` — his play binary, 13 minutes before the fix.
   Those are the only ILL entries anywhere near this window; nothing SIGILLs after 08:53.
5. **BUT — and this is why §5 is only half-wrong — text does draw on that screen.**
   Measured on a local capture of a menu screen from a pre-fix build (§11): the frame
   contains antialiased glyph strokes. `(125,131,138)` is 2,370 px in **1,115 components**,
   the largest of which is **17 px = 1 wide × 17 tall** — a 1-px-wide vertical stroke
   13–17 px high is a character, not a shape. `(109,114,118)` is the same picture
   (2,036 px / 1,150 components / largest 13 px = 1×13). `(79,79,79)` is 11,190 px in 1,426
   components. So the frontend text pipeline renders on at least one page of this menu on a
   pre-fix build.

**So the honest answer to her optional item, which she asked me to state one way or the
other: text draws in general, and her page may still be the trap.** The discriminating test
is one run on the current build: reach the option screen and look. If text appears on the
page she photographed, the trap was hers; if the page is still bare while another page has
text, it is the page. **Nothing in the pixels can settle it and nothing here claims it.**

## 11. THE FIRST LOCAL CAPTURE OF THAT SCREEN — measured, not described

Round 1 §1 recorded that no capture in this repo shows her patch, and that `owner1…owner5`
were the only runs whose camera set includes the option menu's
`eye=(0.14 -0.09 -5.00)`. **Those runs have captures on disk, and round 1 did not read them.**
`out/owner1.02_t68.ppm`, `.03_t83.ppm` and `.04_t98.ppm` are 1280×800 frames taken at
**07:20:40, 07:20:56 and 07:21:12**, at frames 3996, 4883 and 5798, all with the
option-menu camera. They are from a pre-fix build (`out-owner/cmr2`).

New tools this round: `shard_bbox.py` (where is the content, per colour family, with
row/column profiles), `shards.py` (per exact colour: 4-connected component count, largest
component, fragment count), `region_map.py` (a crop as letters, one letter per exact colour,
background blanked). Everything below is counted.

* **The frame is one flat colour.** `(140,149,158)` is **956,980 px = 93.455 %** of the
  frame — and it is **956,980 px in all three captures**, 800 and 1,800 frames apart, along
  with `(79,79,79)=11,190`, `(116,64,50)=5,342`, and whole-family counts identical
  (`r=21,643 k=16,010 O=5,501 g=2,615`). Only the grey/white families differ between them.
  So: a static screen, ~93.5 % empty, with one small animated white/grey element.
* **Content sits in four bands**: y46–85 (top), y186–275, y606–635, y666–725 (footer).
  Non-background bbox `x[56..1223] y[46..756]`.
* **The flat, unshaded, straight-edged fragment cluster is real, and it is in the upper
  right.** Four-plus distinct flat tones with **no gradient between them**, all inside
  `x[902..1150] y[187..269]` (250 × 83 px = 19.5 % × 10.4 % of the frame):
  `(116,64,50)` 5,342 px in **65 components**, largest 1,988 px, bbox `x[902..992] y[187..251]`
  (91×65); `(151,86,69)` 3,713 px in 63 components, largest 724 px; `(94,55,41)` 2,288 px in
  19 components, largest 911 px; plus saturated yellow `(255,219,14)` and black. Large flat
  wedges with hard straight edges, adjacent, unshaded — **the same class of object she
  described, at 19.5 % × 10.4 % rather than 10–15 % × 10–15 %, in the upper right rather
  than below centre.** I am not going to pretend that is the same patch. It is either a
  different element on a different page, or her position description is loose; §13 asks her
  for the one thing that decides it.
* **No car anywhere in the frame.** No silhouette, no roofline, no wheel arches, no wheel,
  and no two-sided object — at any of the three captures, by colour family or by map.
* Note what both pictures have in common: **flat colour, hard edges, no shading, no
  perspective.** Hers has the livery in it. Mine has UI plates three times in a column at
  `x[598..636]`, `y≈270, 349, 421` — `(255,255,255)`, 36×20 px each, black-outlined
  (`shards.py`: 4,615 px in 79 components, largest 523 px `x[601..636] y[349..368]`).

## 12. THE MEASUREMENT THAT CHANGES THE RANKING — draws, but no triangles

Round 1 §4 ranked four mechanism families and picked the instrument that separates them
(A world/view for the preview; B the preview's own deform path; C stride/FVF on the 32-byte
fixed buffers; D 2D-over-3D ordering). **This run's owner map, read end to end, moves B to
the front and does it without needing the menu to be photographed.** From `out/owner1.log`,
the owner-map line at every dump (frame in brackets):

| frame | cells owned | draws | triangles |
|---|---|---|---|
| 200–2800 (13 dumps) | 0 / 2560 | 0 | 0 |
| **3200** | **711 / 2560 (27.8 %) by 8 textures** | 6,757 | **489,067** |
| **3600** | **711 / 2560 (27.8 %) by 8 textures** | 9,628 | **207,801** |
| **4000, 4800, 5800 …** | **0 / 2560** | **9,628** | **0** |

**The same 9,628 draws that put 207,801 triangles on screen at frame 3600 put zero there by
frame 4000, with the camera unchanged at `eye=(0.14 -0.09 -5.00)` and `0 tris behind eye`
reported.** The captures in §11 are at frames 3996, 4883 and 5798 — i.e. **inside the
zero-triangle window**, which is why they are 93.5 % flat and why there is no car in them.

Geometry that is submitted and rasterises nothing is not a wrong index base (that produces
*wrong* triangles, loudly — 91 % of the frame at frame 2450, §3) and it is not a world/view
that is merely misplaced (that produces *displaced* triangles, her "nothing off-screen"
notwithstanding). It is what **degenerate geometry** looks like: vertices collapsed onto a
point, a line, or a plane, so the triangles have ~zero area and the rasteriser drops them —
and a *near*-degenerate version of exactly that is jagged fragments compressed into a small
area, still wearing the mesh's own paint, with nothing fanning off and nothing off-screen.
That is her picture, and it is the deform path (§4 family B), the one piece of code in the
game that **moves and re-uploads preview vertices every frame**:
`OptionPreview_RebuildDeformedGeometry` (`GameInfo.cpp:8147`, twelve generated corners →
camera plane → per-vertex limit normals) and `CarDamage_ApplyCameraSpaceMeshDent`
(`StageTiming.cpp:5340+`, radius/falloff arithmetic in 16.16 fixed point), both ending in
`Mesh_Rebuild` (`Mesh.cpp:103`), which re-`memcpy`s the whole vertex array into the shared
buffer. Miami's own words for the result were "one flat piece of paper". I have **not**
found the bug in that code and I am not going to claim one off a read; I am saying the
measurement now points there, and §4's `LENA-MENUDRAW` spec is the instrument that proves it
in one run (per-draw object-space bbox vs screen-space bbox: a car-sized object-space bbox
with a few-hundred-px screen bbox is A; an object-space bbox that is itself a point or a
plate is B).

## 12a. CORRECTION TO §12 — candidate C predicts this measurement AT LEAST as well

A peer round landed in this repo at **09:03** (`../archive/docs/MENU-CAR-ROUND2.md`, `tools/patch_menudraw.py`)
while §12 was being written, and it does the arithmetic on **candidate C** — the preview's own
converted vertices being **32-byte 16.16 fixed** (`Unk0x0082d220VertexFixed`, `GameInfo.cpp:1383`,
built by `OptionPreview_AllocateConvertedWheelVertices`, `GameInfo.cpp:7727`) while the port's
stride rule is `TLVERTEX ? 32 : 48` (`deck_dd7.cpp:1442`) and the mesh FVF `0x2d2` is 48. Read as
IEEE float, a 16.16 fixed coordinate is a **denormal** (`1.0000 -> 9.18355e-41`,
`-1.0000 -> nan`), so the vertices stop being a car and start being one point.

**§12 said the zero-triangle measurement "is the deform path". That is too strong and I am
correcting it.** Both survive the measurement:

* **C** — positions collapse/mangle, so the triangles are degenerate → the rasteriser drops
  them → zero triangles, exactly as measured. And because the colour field sits at **the same
  byte offset (0x18)** in the fixed layout as in the float layout, the **vertex colours and UVs
  are still read correctly** while the positions are destroyed.
* **B** — the deform path moves vertices onto the camera plane without touching the colour or
  UV stream, giving the same zero-triangle result.

**Her observation is the discriminator, and it favours C.** She did not report a grey blob or
a mangled rainbow: she reported **the car's own livery, correctly painted — white bodywork,
black graphics, saturated orange/red diagonals, mid-grey — with the textures right, torn up.**
A stride mismatch that leaves colour and UV at the same offsets produces *exactly* "right paint,
destroyed positions". C also explains "compressed into one small area" better than B does
(a collapse toward the origin is one area by construction). I am not going to swap one
paragraph's overclaim for another: **§4's families A/B/C/D remain, the measurement in §12 kills
A and D on this screen, and it leaves C and B standing with C now the better-supported.**

The separating instrument already exists — the peer round wrote and linked it
(`patch_menudraw.py`, `LENA-MENUDRAW`), and it prints the same vertex **decoded both ways**
(48-byte float and 32-byte fixed) with the min/max per axis. One line of its output says which:
a car-shaped fixed decode with a collapsed float decode **is** C. So the GPU run named in §15
is now the only thing missing, and the tooling for it is on disk.

## 13. THE TIMELINE — where her photos sit, and why that matters

| time (EEST) | event |
|---|---|
| 07:19:42–07:21:12 | `owner1` captures the option screen, frames 679 / 3140 / 3996 / 4883 / 5798 — **the only local pictures of that screen family** |
| **07:25:40** | `[gfxhub] page fault`, `Process cmr2 pid 498908` → `ring gfx_0.1.0 timeout` → **MODE2 reset** |
| **07:31:49** | `[gfxhub] page fault`, `Process cmr2 pid 501251` → **MODE2 reset** — the display death |
| **07:35** | her message, with the two photos |
| 08:40:03 | two **SIGILL** coredumps, `out-plain/cmr2` — the `ud2` (§10.4) |
| 08:53 | `int`→`void` fix built and swapped in; md5 `d26a09…` |
| 08:57 | Miami launches that binary — the fixed build, live |

Two things follow. **First**, her photos are from a session that was 4–16 minutes from two
hard GPU resets and that ended in them; the closest local capture to her photos is a *clean*
pre-fault one, so the shards are **not** a reset artefact — they were on the screen before
any fault. That is a negative control in the good direction, and it is worth more than the
coincidence is. **Second**, "no menu text" now has two live candidates and no way to pick
between them from here: the `ud2` on that page's text placement (§10), or a phone photo of a
screen (blur/moiré). Her phone has the capture timestamp in the file metadata. **That is
the cheapest thing anyone can give me and it is the first thing I would ask for.**

## 14. WHAT I DID NOT DO, AND WHY — plainly

* **No game run.** Miami was driving the whole round: `ps` shows `cmr2` pid **588344**
  (started 08:57:12) with ppid **1374 = `systemd --user`**, cgroup
  `user.slice/user-1000.…`, and **no entry in `~/.lena_harness/own.d/`** — a foreign game by
  the guard's own rule. `sh gpu-guard.sh --list` agrees: `588344 FOREIGN cmr2
  /home/deck/lena/work/PLAY/out-plain/cmr2`. The phone ranks the display death first; I did
  not queue behind it, I stayed out of it.
* **The A/B she asked for is still not run, and it is still runnable.** Verified rather than
  assumed, because worker 1 rebuilt the play binary at 08:53 and a rebuild is where a
  diagnostic switch silently disappears: **`A7VK_IDXBASE` is still in the live binary**
  (`strings` finds it in `out-plain/cmr2`) and still live in source at `deck_dd7.cpp:1421`
  (`ib_raw = (e && e[0]=='s') ? 0 : 1` — unset or `raw` → the corrected default
  `startVert + idx`; `sub` → the old re-base). So the discriminating pair survives the
  rebuild and costs one run.
* **`gpu-guard.sh` is mode 644 and that is NOT a bug.** I found it non-executable and went
  to fix it; `drive.py:52`, `mc_drive.py` and `menu_hunt.py` all invoke it as
  `subprocess.run(["sh", GUARD, …])`, so the bit is irrelevant to the yield path. Left alone.
* **I did not identify which page of the menu her screen is.** The camera identifies the
  screen family, not the page. Unresolved, and marked unresolved.

## 15. WHAT I WOULD HAND HER, IN ORDER (round 2)

1. **The `ud2` — one sentence, because it orphans her one unverifiable item.** The option
   screen's text-placement function was a decompiled function with no return; every call
   was SIGILL; her photos predate the fix by 78 minutes. It is fixed and live. Text does
   draw on that screen on the pre-fix build (§10.5), so this is a candidate, not a proof —
   and it is now testable.
2. **The screen's 3D stops rasterising** (9,628 draws / 0 triangles / 93.5 % flat, §12) —
   the first measurement on this screen that points somewhere specific, and it points at the
   deform path (§4 B), not at the index base (§2, still dead). One run of `LENA-MENUDRAW`
   proves or kills it by comparing the object-space and screen-space bbox of one draw.
3. **Ask her for the photo timestamps** (not a better photo — the timestamps). They decide
   whether her picture is a pre-fault clean frame or the reset aftermath, and that decides
   whether the shards are geometry or transport.
4. Then the A/B, on a frame that actually shows the screen this time (§3's control shows the
   switch is loud — 91 % of the frame — when the 3D is real, and inert when it is not).

## 16. FILES ADDED THIS ROUND

| file | what it is |
|---|---|
| `shard_bbox.py` | background + non-bg bbox, per-family count/bbox, row & column profiles |
| `shards.py` | per exact colour: 4-connected components, largest, fragment count, bboxes |
| `region_map.py` | a crop printed as letters, one per exact colour, background blanked |
| this §10–§16 | appended to `MENU-CAR-EVIDENCE.md`, not a replacement for §0–§9 |

Nothing of worker 1's or worker 2's was modified. No source edited, no binary built or
copied, no run started, no window on his desktop. Kernel ledger unmoved at
`gfx_0.0.0 timeout = 12`; the two `gfx_0.1.0` + `MODE2` events are the 07:25/07:31 pair.

---

# ROUND 3 ADDENDUM — `MENU-CAR-EVIDENCE-VISION`, 2026-10-11 09:2x–09:5x EEST

Round 3 got **no GPU run of its own** (the card was the peer's `out-md2/cmr2` for the whole
round; `gpu-guard.sh --list` read `899595 owned` at 09:22 and empty from 09:25). What follows
is measured **off the peer's own run** — `work/MENU-CAR-FLATTENED/out/md_raw.log` (5 MB, 66,664
lines), its 7 captures `frames/md_raw.000-006.ppm`, and `~/.lena_cmr2/port/rhi/` — read only,
nothing started, nothing built, nothing of theirs touched.

## 17. THE `raw` ARM RAN — AND IT IS THE FIRST REAL PER-DRAW DECODE OF A MESH SCREEN

`run_md.sh md_raw` (raw = the shipped, corrected default) finished 09:24:17, rc=0, ring
timeouts `12 before / 12 after` (no wedge). It produced **7 bursts of 1,500 indexed 3D draws**
and **7 captures**, at frames **8264, 9125, 10006, 10881, 11757, 12626, 13499**.

**17.1 The draw census — 4,661 logged draws, and they are 214 frames of the same 7 meshes.**
Every logged draw is `fvf=0x2d2 stride=48 vb=0x17429a0 bytes=96000` — one 2,000-vertex buffer.
The draws repeat in a fixed cycle of **seven** `(startVert, numVerts)` meshes, ~214 times per
burst (`md_log_stats.py`, written this round, reads the log; no GPU needed):

| startVert | numVerts | draws | md_decode | object-space extent (float48) | idx[0..5] |
|---|---|---|---|---|---|
| 1532 | 116 | 215 | SOLID | 160 × 57.82 × 160 | 2,1,0,1,2,3 |
| 1648 |   9 | 215 | PLANAR | 200 × 0 × 200 | 2,1,0,4,2,3 |
| 1657 |   4 | 214 | PLANAR | 200 × 0 × 200 | 2,1,0,3,0,1 |
| 1669 |  32 | 214 | SOLID | 160 × 65.68 × 160 | 2,1,0,0,1,3 |
| 1685 |  16 | 214 | SOLID | 160 × 65.68 × 160 | 2,1,0,0,1,3 |
| 1701 |  60 | 214 | SOLID | 160 × 65.57 × 160 | 2,1,0,0,1,3 |
| 1713 |  48 | 214 | SOLID | 160 × 65.57 × 160 | 2,1,0,0,1,3 |

**17.2 The measurement §12a was written to wait for, and it came out against C.**
`float48` — the same bytes the draw read, decoded as 48-byte IEEE float — is **non-degenerate,
finite, and constant across all 214 frames** (`nonfinite=0` on every line). The 16.16 decode of
those bytes (`fixed48`) and the 32-byte-stride packed decode (`fixed32`) are both nonsense
(±1.5e4 … ±2.6e4 where the float reading is ±80 … ±100). **So on these draws the vertex array
really is the 48-byte float layout: candidate C (32-byte 16.16 read as 48-byte float) is REFUTED
here, and candidate B (the preview's own deform collapsing vertices into one place) is refuted
too** — the positions span 160 × 58 × 160 units, they are not collapsed. §12a's "if float48 is
degenerate and fixed48 is car-shaped then C" did **not** fire. C is dead on this screen; B
survives only as something the vertex *data* cannot see.

**17.3 The index-base question, answered from the same log — and it inverts the A/B's premise.**
All 4,661 draws are `zeroBase=no` (`startVert ≠ 0`), so per the instrument's own definition
**every one of them is a draw the `A7VK_IDXBASE` switch CAN change** — the cheap per-draw test
the peer built for exactly this. And `idxInRange=yes` on all of them, with **every index ≤ 200
across all 10,500 sampled draws** while `startVert` is 1532–1713 and `numVerts` 4–116. The
indices are therefore **relative to `startVert`**, not absolute into the buffer — which is what
`36bec65d` found over 404,000 draws and it is true on this screen as well. Under the raw default
`vertex = startVert + idx` lands on the mesh, and the instrument reads a car-shaped box there.
Under `sub` the port computes `idxScratch[i] = (uint16_t)(idx[i] - startVert)` (deck_dd7.cpp:1591),
i.e. `2 − 1532 → 64,506`, and hands **that** to the backend as a vertex index.

**17.4 A warning about the other arm, because it reads outside the window it owns.**
The draw path copies `vcount` vertices into a 24 MB arena and copies the indices **verbatim**
(`a7_vk32.c:2437-2460`); only the *copy cursors* are clamped (`a7_vk32.c:2443`), and **index
values are never validated against `vcount`** — the three `a >= vcount` checks in that file
(1717, 1856, 2200) are all inside the trace/owner instrumentation, not the draw. So the `sub`
arm does not draw a differently-based car on these draws; it makes every index of every draw
point ~3.07 MB (64,506 × 48 B) past its own mesh, into an arena whose contents are whatever the
last frames left there. That is normally wrong-triangles rather than a fault (24 MB arena), but
it is an **unvalidated read taken on his card**, the same class as the read that wedged his
display at 07:25 (different client — texture, not vertex). My reading, not an instruction:
**run the `sub` arm only with the kernel ledger and `gpu-guard` watching, and do not be
surprised if it neither fixes nor cleanly explains anything** — on the draws measured here, `sub`
is refuted by arithmetic before it is refuted by pixels.

**17.5 The pictures do not contain her patch — for the third run in a row.**
Her defect is not in `md_raw.000-006.ppm`: 31,117–33,416 **distinct colours** per frame with the
top colour at 0.62 %, **zero** pixels with `r>110, r−g>55` (no orange/red at all), no flat
unshaded hard-edged cluster, and two captures 800 frames apart differ **only in the top 336
rows** — the lower scene is pixel-identical, so nothing at the centre is sharding. Her patch
sits "just below vertical centre, roughly on the horizontal centre line" at 10–15 % of the
frame; that region is a smooth texture with no hard edges in any of the seven frames.

**17.6 WHY THEY MISSED THE SCREEN — the trigger's own latency, and it is a bug in the driver.**
The last `[OWNER] cam` line before **every** capture is `eye=(-0.00 -0.00 -0.00) fwd=(0,0,1)`,
`zfar=200`, frame depth p10=26.66 p50=32.83 p90=63.21, 100 % of cells owned by 9 road/ground
textures, 473 tris. The option camera `eye=(0.14 -0.09 -5.00)` appears 16 times — at frames
**7675–7725**, i.e. ~6 s and ~500 frames *before* the first burst, when the screen was **0/2560
cells owned, 0 tris drawn**. So the bursts fired on the screen the game moved on to, not on the
one the driver stopped on. The cause is in `md_drive.py`, and it is visible in its own output:
it arms `next_burst = el + 1.0` when it first sees the camera line, but its loop prints are
**6.7 s apart** (`[132.4] … SEEN`, `[139.1] BURST 1`, `[145.8] nudge`, `[154.0] BURST 2`)
because every iteration runs `log_text()` over the whole growing 5 MB log **and** a full
`gpu-guard.sh --foreign` subprocess (md_drive.py:100-139), so the "1 second" delay is really
6.7 s and the option screen is gone by the time `/tmp/mdnow` is touched. Fix before the next run:
throttle `competing()` to every ~10 s and read only the log's last N KB — then the burst lands
within one loop of the camera line, where the car actually is.

**17.7 Her optional text item: no new evidence, and I am not going to manufacture any.**
§10 stands (text draws on at least one page of this menu on a pre-fix build, measured as 1-px
antialiased strokes; her photographed build was 78 minutes older than the `int`→`void` fix).
The round-3 frames do show static white in a right-hand strip `x[876..1264] y[50..789]`
(6,306 px, identical count in all 7) — that is a UI element in the frame, but these are not her
screen and I cannot tell a plate from a glyph in them, so it changes nothing. The discriminating
run is still the one §10 named: reach the page she photographed on the current build and look.

**17.8 What to do next, in order.** (1) Fix `md_drive.py`'s loop as in 17.6 — without it the
next run misses again. (2) Re-run **raw** and confirm the burst frame contains the option camera
and non-zero `owner map` cells. (3) Only then the `A7VK_IDXBASE` A/B, watching
`journalctl -k | grep 'ring gfx_0.0.0 timeout'` before/after. (4) Ask her for the two photo
timestamps (§13) — still free, still unanswered, and now the only thing that can tie her patch
to a build.

**17.9 What I did on disk this round.** `work/RACE/md_log_stats.py` (new: reads a `[MENUDRAW]`
log, classifies every draw, needs no GPU). Nothing else written, nothing run, no source edited,
no binary built, no window opened, no peer file modified. Kernel ledger untouched.

**17.6a THE 6.7 SECONDS, MEASURED.** `sh gpu-guard.sh --foreign` takes **4.53 s** on this box
(timed at 09:5x); `log_text()` over the 5 MB log takes 0.01 s. `md_drive.py` calls *both* every
loop iteration, so its nominal `time.sleep(0.5)` loop is really a **4.5–8.5 s** loop — which is
exactly the spacing of its own output (keys 8.4 s apart with `HUNT_EVERY=5`; `BURST 1` 6.7 s
after the arm that scheduled it 1.0 s out). That is the whole of 17.6: not the game, not the
log, the guard poll.

---

# §18 ONWARD — ROUND 4 (2026-10-11 10:0x EEST): THE A/B, RUN AT LAST, ON BOTH ARMS, INSIDE THEIR OWN WINDOWS

Round 3 and the peer ticket both ended with the same sentence: *the A/B has not been run
because no run that reached the option screen also carried the trace.* That is no longer
true. The peer's run `md_geo` (launched 09:57, shipped default, `A7VK_OWNER=1` +
`A7VK_GEOTRACE=1`) **reached the option screen and held it**, and two earlier runs
(`md_raw` 09:22, `md_sub4` 09:48) did too. All three logs are on disk. I re-read them
inside their own windows instead of by frame number, and the discriminating test the phone
asked for now has an answer **in both directions**.

**Method (this is the whole of it):** the setup/option screen is the unique screen whose
camera is `eye=(0.14 -0.09 -5.00)`. For each run I take the frame range in which that
camera line is present, and read the per-frame owner-map coverage **only inside that
range**. `A7VK_OWNER` prints coverage, triangle count and texture count once per 25 frames;
the coverage number is the fraction of the frame's 64×40 cells that any 3D triangle
actually reached during that present. Nothing else is used.

## §18.1 THE MEASUREMENT

| run | arm | option-screen window (frames) | best in-window coverage | tris | 3D textures | bbox of the covered cells |
|---|---|---|---|---|---|---|
| `md_raw` | **raw = shipped default** | 7675 → 8050 | **599/2560 = 23.4 %** (f 7900) | 2,099 | 8 | x[180..1020] y[260..580] → **65.6 % W × 40.0 % H**, centre (46.9 %, 52.5 %) |
| `md_geo` | **raw = shipped default** | 3350 → 3525 | **595/2560 = 23.2 %** (f 3450) | 2,073 | 8 | x[120..1080] y[220..560] → **75.0 % W × 42.5 % H**, centre (46.9 %, 48.8 %) |
| `md_sub4` | **sub = old re-base** | 6650 → 7225 | **28/2560 = 1.1 %** (f 6950) | **48** | 8 | x[760..900] y[320..400] → **10.9 % W × 10.0 % H**, centre (64.8 %, 45.0 %) |

* **Two independent raw runs, three runs apart in wall-clock and different frame numbers,
  agree to 0.2 % of frame area and to 26 triangles on ~2,080** (23.4 % / 23.2 %,
  2,099 / 2,073). The default's picture of that screen is stable and reproducible.
* **`sub` is not a variation of it. It is a factor of ~21 down in covered area and ~43
  down in triangles** — 48 triangles is the whole car.
* All three arms bind the **same 8 car textures** on that screen (the `CML*` Lancer
  liveries that load immediately before it, `md_geo.log` 1900–1930). So the difference is
  not texture starvation and not missing parts: the same parts are asked for and 8 of them
  bind in both arms.
* The raw arm's cell map is **car-shaped** — two symmetric textured masses left and right
  (wheels) around a wide body, centred on the frame's horizontal middle, sitting across
  the vertical middle (`md_raw` f7900 and `md_geo` f3450 both, reproduced in §18.2). The
  `sub` arm's cell map is a **single featureless block of one texture family** in the
  lower right of centre.

## §18.2 THE TWO MAPS, SIDE BY SIDE (same screen, same camera, same 64×40 grid)

```
raw  (md_geo f3450)  75.0% W x 42.5% H          sub  (md_sub4 f6950)  10.9% W x 10.0% H
 |              BBBBBBBB   BBBBBBBB     |        |                                |
 |             BBBBBBBBB   BBBBBBBB     |        |                                |
 |             BBBBBAAAAAAAAAAAAABBBBBA |        |                                |
 |       AAEEAEEBBBBBBAAAAAAABBBBBBBAAA |        |                                |
 |       AAAAEEEEEBBAAAAAAAAAAABBBBAABAA |        |                                |
 |       AAEEAAAAAAAAAAAAAAAAAAAAAAAAAAA |        |                                |
 |       AAAAAAAAAAAACCCCCDDDDDDDAAADDAA |        |          AAAAAAA               |
 |       AAAAAAACCCDCCCCCCCCCCDDDDDCDDDD |        |          AAAAAAA               |
 |       AAAAAADCCCCDCCCCCCCCDDDDDCDDCCA |        |          AAAAAAA               |
 |      AAAAAAACDDCCCDCCCCDDDDCCCCDDDDCD |        |          AAAAAAA               |
```
(`A` = texId 40, `B` = 42, `C` = 43/45, `D` = 45, `E` = 41/46 — eight livery textures,
2,073 tris on the left, 48 on the right.)

### §18.3 CREDIT, AND WHAT IS ACTUALLY NEW HERE

Checked against the lab repo before writing this: the commit `229c886` (09:52, the
`MENU-CAR-FLATTENED` worker) already carries the line
*"option-camera coverage: 599 / 591 / 450 cells = 23.4 / 23.1 / 17.6 % vs 0/2560 cells in
21 dumps, at most 28/2560 = 1.1 %"*. **The coverage A/B is theirs, and it is right.** What
this round adds on top of it is:

1. **the window-scoping method stated and applied** — a coverage number is only about that
   screen if it was taken while that screen's camera was up, and it lets their three
   numbers (23.4 / 23.1 / 17.6 %) be read as one stable picture plus two partial ones;
2. **the bbox in % of frame** — 10.9 % W × 10.0 % H — which is the number that meets the
   phone's own estimate and is what turns "1.1 %" into "that is her patch";
3. **the capture audit** (1 of 41 captures inside its own window, and that one 48 frames
   too late), which voids §0g's "no car in the default frame";
4. **the GEOTRACE frame** (§19) and **the environment audit** (§22).

Nothing above is a correction of their conclusion — their commit reaches the same one
("the old re-base kills the car"). It is a correction of §0g's *picture* claim and of
§16's control, and it supplies the number that answers the phone.

## §19. THE RAW ARM'S MENU FRAME, IN THE GAME'S OWN MATRICES AND BOXES

`md_geo` frame 3480 is the only captured moment in this project's history where the
**option screen and `A7VK_GEOTRACE` were on at the same time**. Everything below is one
frame, printed by the port itself:

```
[GEO] f=3480 | 3D draws=1836 verts=104244 tex=1836 notex=0 lit=1768 | TL draws=19691 verts=96602
[GEO]   obj  x=[-2.1 2.1] y=[-0.5 0.7] z=[-0.9 0.9]
[GEO]   w=[4.076 6.158] ndc x=[-0.811 0.741] y=[-0.422 0.459] z=[0.758 0.841]
        behind=0 nonfinite=0 draw_behind=0 draw_alloff=0
[GT2]   WORLD identity; VIEW rigid orthonormal t=(-0.140 0.090 5.000);
        PROJ xscale=1.5185 yscale=2.0985 znear=1.0 zfar=250.0
[GT2]   coverage: tri_full=140964 part=0 behind=0 screens_covered=194.398
```

Read against the phone's five constraints, on the arm she proposed to reject:

| her constraint | what the default build actually does on that screen |
|---|---|
| small patch, not spread | **no** — object-space box is **4.2 × 1.2 × 1.8 world units**, a car, and its NDC box is x[-0.81..0.74] y[-0.42..0.46], i.e. it spans most of the frame |
| jagged shards, nothing smooth | **no** — `part=0` (not one triangle straddles the viewport edge), `0` behind the eye, `nonfinite=0` |
| colours are the car's own livery | **yes, and it is the same set on both arms** (8 `CML*` textures) — so this observation of hers does not discriminate, exactly as §2 said |
| no silhouette, no perspective | **no** — the covered cells form wheels-plus-body; the box is affine and 4.2 units long against 1.8 wide |
| nothing stretched off-screen | **yes — but as a measured zero, not as a symptom**: `draw_alloff=0 draw_behind=0` |

**The frame she says she is looking at is not what the default build produces on that
screen.** The nearest thing to her description that this project has ever measured is the
`sub` arm.

## §20. HER PATCH IS THE `sub` SIGNATURE — AND THAT INVERTS HER READING

Her measurements: *"roughly 10–15 % of screen width and height, sitting just below
vertical centre, roughly on the horizontal centre line … jagged, ragged-edged shards …
flat unshaded colour … the colours inside the patch are the car's own livery … nothing
smooth, no gradients, no shading."*

| her number | `sub` measured | verdict |
|---|---|---|
| 10–15 % of width | **10.9 %** (x 760→900 = 140 px) | matches |
| 10–15 % of height | **10.0 %** (f 6950) / **5.0 %** (f 6925, 6975) | matches at the top of her range |
| 1–2.25 % of frame area | **1.1 %** (28/2560 cells) | matches |
| car's own livery, several flat colours | 8 `CML*` livery textures bound; the patch carries 3 different car parts (`A`,`B`,`C`) inside one block | matches |
| sitting below vertical centre | cell centre y **67.5 %** at f6925/f6975 | matches |
| on the horizontal centre line | cell centre x **64.8–66.4 %** across | **does not match** — the patch is right of centre, not on it |
| no long triangles, none off-screen | 48 triangles inside 28 cells; nothing outside | consistent |

**So the test she asked for comes back negative, and worse than negative: the old re-base
is not what the menu path is missing — the old re-base is what *makes* the patch.**
`A7VK_IDXBASE=sub` on this screen is not a repair, it is the defect, and scoping it to the
menu draw path would install her photo onto Miami's screen. The default (corrected) base
stays. That is the answer to the only question this ticket was ever about.

One honest caveat, in the same breath: her position reading (centre line) and mine
(64.8–66.4 % across) disagree, and her photo is still not on this machine, so what she
photographed has not been *identified* — only its *shape and size* have been matched to an
arm. §22 says what would settle it, and it needs no new instrument.

## §21. WHY NO RUN IN THIS TICKET EVER PHOTOGRAPHED THAT SCREEN — COUNTED, NOT SUSPECTED

| run | option-screen window | captures | captures **inside** the window |
|---|---|---|---|
| `md_raw` | 7675 → 8050 | 7 (8264, 9125, 10006, 10881, 11757, 12626, 13499) | **0** |
| `md_geo` | 3350 → 3525 | 19 (3955 … 15857) | **0** |
| `md_sub4` | 6650 → 7225 | 15 (7023, 7720, …, 16609) | **1** — frame 7023 |

* **`md_raw`'s "the default run's frame has no car" is a capture-timing artefact.** Its
  window closed at 8050 and its first capture is 8264, 214 frames later. That picture is
  not of the setup screen at all.
* `md_raw.000.ppm` (frame 8264) measures **31,117 distinct colours** — a busy screen, not
  the option screen and not a flat one.
* **The one in-window capture is not of the car either.** `md_sub4.000.ppm` is frame 7023;
  the `sub` arm's 3D on that screen exists at owner samples 6925 / 6950 / 6975 and is
  **gone by 7023**. Measured on the pixels: **33 distinct colours, 99.233 % `#8c959e`** —
  the nearly-flat frame the peer published as `…_IDXBASE-sub_FLAT.png`. True of the
  picture, and it says nothing about the arm.
* The car's own 3D is present for only **2–3 owner samples (~50–100 frames, 1–2 s at this
  build's frame rate) per window, in every arm.** A capture has to be aimed inside that
  1–2 s window; a fixed cadence that fires ~9 s after the camera line appears cannot be.
  This is the same latency failure round 3 diagnosed in `md_drive.py:139`, and it is still
  the binding constraint on this ticket — not instrument coverage.
* The windows are at **different frame numbers in different runs** (7675 vs 3350 vs 6650).
  Any A/B that pairs captures **by frame number across runs** is comparing different
  states of a screen that animates. All of §3's "the bbox is identical in every
  comparison" used such pairs; the bbox agreement is a property of the loading/frontend
  element both runs were showing, not of the menu.

## §22. IS MIAMI'S BUILD RUNNING `sub`? — NO, AND HERE IS EVERY PLACE IT COULD BE

* **Source:** `deck_dd7.cpp:1417–1424` — `ib_raw` defaults to `1` (corrected); the old
  re-base is selected only when `A7VK_IDXBASE` is present **and its first character is
  `s`**. Unset = corrected. (`patch_idxfix.py`'s own docstring still documents the *old*
  polarity, "unset → subtract"; that is stale text from before the default was flipped at
  04:2x and I am flagging it rather than editing the peer's file.)
* **His environment:** no `A7VK_IDXBASE` in `.bashrc`, `.profile`, `.bash_profile`, or
  `.config/environment.d/`; `systemctl --user show-environment` is clean; no live process
  on this box carries it.
* **His binary:** `work/PLAY/out-plain/cmr2` = md5 `d26a09231a98ebb25b6da8b664275f87`,
  08:53 today — relinked by the death lane, **not by me**, and built from a tree whose
  default is the corrected base.

**So her photo is one of two things, and the cheap test separates them:** either it is
older than the 04:2x default flip, or the screen she photographed is not this screen.
The test is one capture of the current default menu frame with the burst armed to fire
*while the car is up* (aim inside the 1–2 s window, e.g. arm on the camera line and fire
within 0.5 s, or trigger on the first 3D draw rather than on a clock). That single frame
is now the only thing this ticket is missing.

## §23. THE TEXT ITEM — UNCHANGED, PLUS ONE FREE CONFIRMATION

§5 stands: atlases load on both screens, `Font_DrawText → … → DrawPrimitive(TLVERTEX)` is
implemented and exercised 1.66–1.87 M times per run, so "no text" cannot be a missing
path. One extra line from the round-4 frame: **on the option screen itself the 2D/TL path
is busy — `TL draws=19691 verts=96602` in the single frame 3480.** If her photo really has
no text, it is not because that path is idle at that moment. Still unverified, still not
worth a run, and still answered by the same one capture as §22.

## §24. WHAT I DID NOT DO

* **No GPU run, no window, no rebuild, no source edit, no peer file modified.** The card
  was held by the peer's `md_geo` run for the whole round, and from 10:03 by the death
  lane's `PLAY/out-plain/cmr2` (pid 2145161). Nothing was killed and nothing is left
  running by me.
* **I did not get her photos** (§6, unchanged) — so §20's match is a match of *shape and
  size*, not an identification of the image.
* **The death ticket stayed first**: the card went straight from `md_geo` to the death
  lane, and I did not contend for it.
