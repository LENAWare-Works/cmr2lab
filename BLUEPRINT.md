# BLUEPRINT

**Read this before grepping.** Everything below is a fact about the shape of CMR2 and of
this port. It exists because searching for a word is not the same as knowing the system:
when someone says "the white shadows are wrong", grepping `shadow` takes you through
`RallyData.cpp`, `StageTiming.cpp`, `SceneNode.cpp` and `FrontendMenus.cpp` looking for a
lighting implementation **that does not exist**. One line of blueprint replaces that sweep.

Two rules for this file:

1. **§1 is the most valuable section.** Knowing what a system does *not* have is what stops
   the wrong search. A negative is as load-bearing as a positive and takes far longer to
   re-derive.
2. **If you learn something structural, add it here the same day.** Not in a round report.
   Round reports are history; this is the shape.

Measured 15 October 2026 against `CMR2Decomp`. Anchors are `file:line` where the anchor is
stable, file only where it is not.

---

## 1. NEGATIVE SPACE — what this game does not have

Each entry is a trap: a word that suggests a system which is not there.

| you will look for | the truth | what it actually is |
|---|---|---|
| **shaders** | **there are none.** D3D7 fixed-function only. | The game submits `D3DTLVERTEX` — positions already transformed, lighting already applied, in software. The device does viewport transform, rasterise, texture-stage cascade, alpha test, fog, blend, z-test. Nothing else. |
| **shadow maps / shadow volumes / stencil shadows** | **none exist.** `ShadowVolume`, `ShadowMap`, `ShadowBuffer`, `StencilShadow` appear in **0 files**. | Shadows are **geometry**. Real meshes emitted per scene node, streamed into one vertex buffer between `Scene_BeginShadowBatch()` / `Scene_EndShadowBatch()` (`RallyData.cpp:6242–6265`), split into `{first vertex, vertex count, texture, …}` (`SceneNode.cpp:1599`). |
| **any shadow render state** | **none.** There is no `D3DRS_*SHADOW` or `D3DTSS_*SHADOW` anywhere. | Confirms the above: shadows cannot be a lighting effect because nothing in the device state describes one. |
| **one shadow system** | **There are THREE, and the word alone does not tell you which.** This is the single biggest source of wasted searching here. | **① frontend menu text** (drop shadows behind UI text, `FrontendMenus.cpp`, palette `g_colourShadowWhite` / `…Text` / `…Dim`) · **② the car's own shadow** (`CarPhysics.cpp:414–519`, octagon + core, `Quad2D_QueueFixedTriangle(…, NULL, (Quad2D *)10)` — texture **NULL by design**, colour lives in the vertex) · **③ scene shadow geometry** on terrain and foliage (`Scene_AddShadowCaster` `StageTiming.cpp:8011` → `Scene_EmitNodeShadowGeometry` `RallyData.cpp:6110` → batched `Scene_BeginShadowBatch`/`EndShadowBatch` `RallyData.cpp:6242/6265`). |
| **that `g_colourShadowWhite` is the white terrain patches** | **It is not.** That variable is **frontend menu text**. | A confident wrong answer I nearly published. The race-time flat-shadow combiner is texture-stage **mode 10** (`Graphics.cpp` `case 10:`): `COLORARG1 = D3DTA_TEXTURE \| D3DTA_ALPHAREPLICATE`, `COLORARG2 = D3DTA_DIFFUSE`, `COLOROP = MODULATE` — **the texture is used as an alpha mask**, modulated by the vertex colour. |
| **fog in the game** | **the game never turns it on.** `D3DRS_FOGENABLE` is **0 in all 24,369 calls**, uniq=1, across a full race stage. | Fog is a *driver-capability* feature CMR2 shipped behind a flag these tracks do not set. It is a **dead feature in retail**, not a missing port feature. |
| **a lens flare** | **"FLARE" is a misnomer in the decomp.** | `StageObject_SetForwardedFlareState` → `Graphics_SetFlareStateValue` → `SetRenderState(0x1c, …)`. State `0x1c` is **`D3DRS_FOGENABLE`**. `g_stageLighting[0x25]/[0x26]/[0x52]/[0x53]` drive it. Not a flare, not fog you can see. |
| **dynamic lighting to reimplement** | **there is none to write.** | The game does all transform and lighting itself before submitting. `lit` measured at a **1.0000 floor** for 99.82 % of vertices. Rewriting lighting math on the port side is rewriting something the game does not ask the device to do. |
| **mip chains from the driver** | The game *asks* (`Graphics.cpp:1481`, `:1495`) and the driver was expected to build them. | Now ported — but for years this was the "does not exist" entry, and it is why minified terrain flickered. |
| **alpha on most textures** | Not present in the data. | Stage textures arrive with usable alpha; the all-ones-alpha case was a **decode** fault, not absent data. |

---

## 2. VOCABULARY — what things are actually called, and where they live

| what people say | what it is | anchor |
|---|---|---|
| the road / the track | a stage; loaded by `Race_LoadSelectedStage()`, returns 1 on success | `Race.cpp` |
| white shadows (on terrain / foliage) | **scene shadow geometry** — real meshes emitted per node, batched, drawn flat. NOT a lighting effect and NOT the `g_colourShadowWhite` variable | `StageTiming.cpp:8011` → `RallyData.cpp:6110` → `RallyData.cpp:6242/6265` |
| white box under the car | the car's **own** shadow, a separate path: octagon + core, texture NULL by design, then texture-stage **mode 10** (texture as alpha mask × vertex colour) | `CarPhysics.cpp:418`; combiner at `Graphics.cpp` `case 10:` |
| `g_colourShadowWhite` | **frontend menu text shadow** — nothing to do with the race | `FrontendMenus.cpp:1238` |
| the sim / interior pass | `05`/`06`-prefixed parts — unlit or additive, **not bodywork** | `.c3d` part-name prefix |
| light effects | `14`-prefixed parts — additive flares | `.c3d` part-name prefix |
| underbody sim | `15`-prefixed parts | `.c3d` part-name prefix |
| the `.c3d` | `PP_F` — a set of **render passes**, not one mesh | `docs/C3D.md` |
| the `.bfl` | texture container | `docs/CONTAINER.md` |
| a "proper" wheel | there is no single wheel part: `L` = **L**ight wheels, `S` = **S**now wheels. Same size because both are a wheel set — **not** left/right | `StageTiming.cpp` string globals |
| steering / pedals not working | the pad button **stride**: the port wrote button bytes 4 apart where the game reads them 1 apart | fixed 2026-10-13 |
| dropped state | a `SetRenderState` the game makes and the port accepts with `D3D_OK` and **ignores** | `docs/S2-CENSUS.md` |

---

## 3. THE SHAPE — subsystems and how a frame flows

Entry path, read from the decomp, stable:

```
WinMain (main.cpp:52)
  → CMain::Initialize            (0x004a9720)
  → CMain::CreateGameWindow      (main.cpp:137)
  → message pump
  → CMain::MessageHandler        (main.cpp:186)
  → CGame::RunStateRenderCallbacks   (Game.cpp:1147)
  → Game_DrawSceneViewport       (0x0049d3f0, Game.cpp:2580)
      → BeginScene … EndScene
```

Windowed is a **first-class path** — `isFullscreen` only changes the style. Use it.

| subsystem | file | lines | what it owns |
|---|---|---|---|
| graphics / device | `Graphics.cpp` | 7,331 | **82 % of all D3D7 calls live here**, and only 4 other files touch D3D7 at all |
| scene graph | `SceneNode.cpp` | 2,817 | nodes, shadow batches, per-node geometry emission |
| game / main loop | `Game.cpp` | 3,586 | state machine, viewport, fog enable |
| race logic | `Race.cpp` | 5,464 | stage load, race state, per-frame resources |
| car | `Car.cpp` | 8,423 | physics and mesh are **decoupled** — physics reads `halfExtents` + `wheelPos[4]` and never consults the mesh |
| stage objects | `StageObjects.cpp` | 16,230 | largest file; lighting presets, stage lighting table |
| menu / frontend | `RallyData.cpp` | 8,648 | menu flow, attract mode, shadow batching for the frontend |
| timing / HUD | `StageTiming.cpp` | 9,546 | clock, countdown, car-format string globals |
| sectors | `Sector.cpp` | 956 | nearest-corner height, stage grid |

**Where the D3D7 surface actually is:** 298 call sites, 27 distinct methods, of which only
**21 are draws**. **277 are state.** 245 of the 298 are in `Graphics.cpp` alone. Any question
of the form "does the port handle X" is therefore almost always a question about *state
mapping*, not about drawing.

---

## 4. HOW TO USE THIS

* **Before searching for a word**, check §1 and §2. If the word is in §1, the system does not
  exist and the search will only produce confusion.
* **When you learn a structural fact**, add it here the same day, with the anchor. This file
  is worth exactly what is in it, and a fact that only lives in a round report is a fact that
  will be re-derived by someone else next week.
* **Facts here are measured, not remembered.** If one disagrees with the code, the code wins
  and this file is wrong — fix it.
