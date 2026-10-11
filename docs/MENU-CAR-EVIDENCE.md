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
