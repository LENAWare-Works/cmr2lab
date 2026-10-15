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

Measured 15 October 2026 against `CMR2Decomp`. **Anchors are symbol names, not line
numbers** — see §5 for why, and for the `git grep -n 'SYMBOL'` incantation that always
resolves one. Line numbers appear only where a symbol does not exist to hang them on, and
they are marked `≈` when they drift.

---

## 1. NEGATIVE SPACE — what this game does not have

Each entry is a trap: a word that suggests a system which is not there.

| you will look for | the truth | what it actually is |
|---|---|---|
| **shaders** | **there are none.** D3D7 fixed-function only. | The game submits `D3DTLVERTEX` — positions already transformed, lighting already applied, in software. The device does viewport transform, rasterise, texture-stage cascade, alpha test, fog, blend, z-test. Nothing else. |
| **shadow maps / shadow volumes / stencil shadows** | **none exist.** `ShadowVolume`, `ShadowMap`, `ShadowBuffer`, `StencilShadow` appear in **0 files**. | Shadows are **geometry**. Real meshes emitted per scene node, streamed into one vertex buffer between `Scene_BeginShadowBatch()` / `Scene_EndShadowBatch()` (`Scene_BeginShadowBatch` / `Scene_EndShadowBatch`), split into a flat `int[4]` record `{firstVertex, vertexCount, textureIndex, viewMask}` (`Scene_DrawShadowBatches`, `SceneNode.cpp:2514`; the cursor walks it at `+= 4`). |
| **any shadow render state** | **none.** There is no `D3DRS_*SHADOW` or `D3DTSS_*SHADOW` anywhere. | Confirms the above: shadows cannot be a lighting effect because nothing in the device state describes one. |
| **one shadow system** | **There are THREE, and the word alone does not tell you which.** This is the single biggest source of wasted searching here. | **① frontend menu text** (drop shadows behind UI text, `FrontendMenus.cpp`, palette `g_colourShadowWhite` / `…Text` / `…Dim`) · **② the car's own shadow** (`CarPhysics.cpp` `SHADOW_OCTAGON`/`SHADOW_CORE` macros, octagon + core, `Quad2D_QueueFixedTriangle(…, NULL, (Quad2D *)10)` — texture **NULL by design**, colour lives in the vertex) · **③ scene shadow geometry** on terrain and foliage (`Scene_AddShadowCaster` → `Scene_EmitNodeShadowGeometry` → batched `Scene_BeginShadowBatch`/`Scene_EndShadowBatch`). |
| **that `g_colourShadowWhite` is the white terrain patches** | **It is not.** That variable is **frontend menu text**. | A confident wrong answer I nearly published. The race-time flat-shadow combiner is texture-stage **mode 10** (`Graphics.cpp` `case 10:`): `COLORARG1 = D3DTA_TEXTURE \| D3DTA_ALPHAREPLICATE`, `COLORARG2 = D3DTA_DIFFUSE`, `COLOROP = MODULATE` — **the texture is used as an alpha mask**, modulated by the vertex colour. |
| **fog in the game** | **the game never turns it on.** `D3DRS_FOGENABLE` is **0 in all 24,369 calls**, uniq=1, across a full race stage. | Fog is a *driver-capability* feature CMR2 shipped behind a flag these tracks do not set. It is a **dead feature in retail**, not a missing port feature. |
| **a lens flare** | **"FLARE" is a misnomer in the decomp.** | `StageObject_SetForwardedFlareState` → `Graphics_SetFlareStateValue` → `SetRenderState(0x1c, …)`. State `0x1c` is **`D3DRS_FOGENABLE`**. `g_stageLighting[0x25]/[0x26]/[0x52]/[0x53]` drive it. Not a flare, not fog you can see. |
| **dynamic lighting to reimplement** | **there is none to write.** | The game does all transform and lighting itself before submitting. `lit` measured at a **1.0000 floor** for 99.82 % of vertices. Rewriting lighting math on the port side is rewriting something the game does not ask the device to do. |
| **the scene ambient as a missing unit of light** | **NO — measured negative, 2026-10-15.** `D3DRENDERSTATE_AMBIENT` (state 139) is MAPPED (`map_rs()`, `A7RS_AMBIENT`) and STORED and **read by nothing**; the port keeps the game's hardcoded white material ambient (`Scene_RestoreLights` → `g_sceneMaterial.ambient = 1.0`), so the lit term is a flat floor of exactly 1.0. Folding 139 into `matAmbient` (`a7vk_fill_block`) **does not move the picture.** Per-frame alternating A/B, 27 opposite-arm pairs, matched: `road_edge` **1.000 -> 1.000**, sky exactly-255 count **55 -> 55**, `oct` 8 -> 8, `mean` 0.999x. | **WHY: state 139 is `0x00000000` on 95.95 % of draws** (measured twice, 10-14 and confirmed 10-15). The zero-guarded arm is byte-identical to the control on ~96 % of geometry by construction; on the ~4 % where the blue-grey family `(105,130,163)` IS live it multiplies by ≈0.5, i.e. a few percent on a few percent of pixels. **Both forms fail, for opposite reasons**: unguarded deletes the picture (88.6 % black snow, reproduced to 3 digits across two builds), guarded changes nothing. The lever is the **zero state itself**, or the fog/material-colour path — not the substitution. Do not re-open 139 as a lighting fix. |
| **shaders on the texture path** | **there are none — and this was re-verified 2026-10-15.** `CreateVertexShader` / `CreatePixelShader` / `SetVertexShader` / `SetPixelShader` / `.hlsl` / `.fx` appear in **0 files** of `CMR2Decomp`. | The "shader" that must be matched is the **fixed-function texture-stage cascade**, and the port reproduces it twice: `a7_eval_texop` (a software reference) and `a7vk3d.frag` `argval()`/`combine()` — which is why they are written to agree byte-for-byte. Chasing a shader it does not have is exactly the §1 trap. |
| **a DXT decoder in the game** | **the game never decodes a DXT block. It cannot.** `LoadDDSTexture` copies the block bytes into a system surface and calls `Blt`, then asks the driver for a DXT texture surface (`CreateTextureSurface` -> `textureInfo4` for DXT5). | So "the stage texture is wrong" was never a game bug — the decompression is **driver** work, and on this port the driver is `DeckSurface7::Blt`. It did no format conversion until **2026-10-11**, so block bytes reached the RHI as ARGB (1.1 % left-neighbour agreement, mean alpha 16/255). Ported as `dl_decode` (`deck_dd7.cpp`), `LENA-DXTBLT`. |
| **more than one texture-NULL draw** | **exactly ONE exists in the whole game.** Every `ApplyTextureStageChange(stage, 0)` call site is a *cleanup* restoring the stage to untextured after a pass. | The single draw that is genuinely untextured **by design** is the car's own shadow: `Quad2D_QueueFixedTriangle(0, &v0, &v1, &v2, NULL, (Quad2D *)10)` at **`CarPhysics.cpp:418`** — texture NULL, and **mode 10 passed in the last argument** so the quad's colour comes from the vertex. `Graphics_DrawCubeMappedShadowTriangles` is the other texture-ish path but it binds a *cube map*, not NULL. |
| **a texture stage beyond 2** | **stages 0-2 are the whole budget** and only 0 and 1 are ever *bound* with a texture. | `SetTextureStageState([0-2]` is the complete set (`Graphics.cpp`); `ApplyTextureStageChange` is called with a non-zero stage only for 1 and 2, and stage 2 only ever with **0**. In a race, **stage 1 is never bound at all** — see §6 item 3. |
| **mip chains from the driver** | The game *asks* (`Graphics.cpp:1481`, `:1495`) and the driver was expected to build them. | Now ported — but for years this was the "does not exist" entry, and it is why minified terrain flickered. |
| **alpha on most textures** | Not present in the data. | Stage textures arrive with usable alpha; the all-ones-alpha case was a **decode** fault, not absent data. |

---

## 2. VOCABULARY — what things are actually called, and where they live

| what people say | what it is | anchor |
|---|---|---|
| the road / the track | a stage; loaded by `Race_LoadSelectedStage()`, returns 1 on success | `Race.cpp` |
| white shadows (on terrain / foliage) | **scene shadow geometry** — real meshes emitted per node, batched, drawn flat. NOT a lighting effect and NOT the `g_colourShadowWhite` variable | `Scene_AddShadowCaster` → `Scene_EmitNodeShadowGeometry` → `Scene_BeginShadowBatch`/`Scene_EndShadowBatch` |
| white box under the car | the car's **own** shadow, a separate path: octagon + core, texture NULL by design, then texture-stage **mode 10** (texture as alpha mask × vertex colour) | `CarPhysics.cpp` `SHADOW_TRIANGLE`; combiner at `Graphics.cpp` `case 10:` |
| `g_colourShadowWhite` | **frontend menu text shadow** — nothing to do with the race | `g_colourShadowWhite0x00524974` (`FrontendDraw.cpp`) |
| the sim / interior pass | `05`/`06`-prefixed parts — unlit or additive, **not bodywork** | `.c3d` part-name prefix |
| light effects | `14`-prefixed parts — additive flares | `.c3d` part-name prefix |
| underbody sim | `15`-prefixed parts | `.c3d` part-name prefix |
| the `.c3d` | `PP_F` — a set of **render passes**, not one mesh | `docs/C3D.md` |
| the `.bfl` | texture container | `docs/CONTAINER.md` |
| a "proper" wheel | there is no single wheel part: `L` = **L**ight wheels, `S` = **S**now wheels. Same size because both are a wheel set — **not** left/right | `StageTiming.cpp` string globals |
| steering / pedals not working | the pad button **stride**: the port wrote button bytes 4 apart where the game reads them 1 apart | fixed 2026-10-13 |
| dropped state | a `SetRenderState` the game makes and the port accepts with `D3D_OK` and **ignores** | `docs/S2-CENSUS.md` |
| "the texture id" | **a SLOT index into `textureBuffer[2048]`, not an image** — and a port `texId` is a *second*, different number assigned at first bind. §6.2 | `CTexture::FindLoadTexture` -> `pTexture->textureId = i`; `DeckDevice7::SetTexture` -> `nextTexId++` |
| "the texture is wrong" | **split it at §6.1**: stage track textures are **DXT5** and are decompressed by the **blit** (`DeckSurface7::Blt` -> `dl_decode`); frontend and car textures are **TGA** and decode in software. A complaint about one is not a complaint about the other. | `CGraphics::LoadDDSTexture` / `LoadTGATexture` |
| the shadow decal's texture | **forced to combiner mode 10**, not stored as 10 — `Scene_DrawShadowBatches` writes 10 onto the Texture, binds, then restores. A trace around the call reads 0. §6.4 (iii) | `Scene_DrawShadowBatches` -> `Frontend_SetObjectField118(pTexture, 10)` |
| "the combiner" | `Texture::blendMode` -> `CGraphics::ConfigureTextureStageBlendMode`, cases 0-11 and 0xff. The full measured table is §6.7 | `Graphics.cpp` `ConfigureTextureStageBlendMode` |

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
| graphics / device | `Graphics.cpp` | 7,566 | **229 of the tree's 289 device-state/draw call sites (79 %) live here**; 6 other files touch the device at all — `Sprite.cpp` 19, `Game.cpp` 18, `SceneNode.cpp` 16, `StageTiming.cpp` 6, `StageObjects.cpp` 2, `Race.cpp` 2. (Was "82 % / only 4 other files": re-measured 2026-10-15, see §5.) |
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


---

## 4. HOW TO USE THIS

* **Before searching for a word**, check §1 and §2. If the word is in §1, the system does not
  exist and the search will only produce confusion.
* **When you learn a structural fact**, add it here the same day, with the anchor. This file
  is worth exactly what is in it, and a fact that only lives in a round report is a fact that
  will be re-derived by someone else next week.
* **Facts here are measured, not remembered.** If one disagrees with the code, the code wins
  and this file is wrong — fix it.
* **Cite the symbol, name the tree.** §5. A `file:line` here is a footnote, not the anchor.
* **When you say "which texture", say WHICH OF THE THREE.** §6.0 separates the per-face id, the
  texture-stage combiner mode, and the blend. Conflating them is what produced a false finding
  that survived a whole round. §6 is the end-to-end texture path with the measured race numbers.

---

## 5. HOW TO CITE — anchors that survive, because these ones did not

Added 15 October 2026, the same day as this file, because **this file's own first draft
shipped anchors that were already wrong when it was pushed.** Every anchor below was
re-verified against the tree; **all six** were off or false:

| anchor as first written | symbol's actual line | why it moved |
|---|---|---|
| `StageTiming.cpp:8011` (`Scene_AddShadowCaster`) | **8029** | uncommitted edits in the tree the file was measured against |
| `RallyData.cpp:6110` (`Scene_EmitNodeShadowGeometry`) | **6138** | same — **and this one moved *forwards*** |
| `RallyData.cpp:6242` (`Scene_BeginShadowBatch`) | **6135** | same tree, **different direction** |
| `FrontendMenus.cpp:1238` (`g_colourShadowWhite`) | **1234**, and the flag lives in **`FrontendDraw.cpp:23`** | 1238 was the *call site* in a menu-draw routine, not the definition |
| `SceneNode.cpp:1599` ("split into `{first vertex, vertex count, texture}`") | **`Scene_DrawShadowBatches`, `SceneNode.cpp:2514`** | **plain wrong file position** — 1599 is a file-buffer *free* routine, nothing to do with shadow batches. The correct record is a flat `int[4]` = `{firstVertex, vertexCount, textureIndex, viewMask}`, consumed by the cursor at `SceneNode.cpp:2526` (`+= 4`) |
| `Graphics.cpp` = "82 % of all D3D7 calls", "only 4 other files touch D3D7" | **79 % (229 of 289)** and **6 other files** | re-measured; the old number was either from a different tree or a different denominator — either way it was asserted, not measured |

**Six anchors, six different displacements, some of them in opposite directions — and two
of them wrong outright, not merely stale.** The cause is not one-off sloppiness: it is
structural. the `CMR2Decomp` working tree in
`~/.lena_cmr2/repo` carries **thousands of lines of uncommitted edits** (1,554 changed lines
across just those four files), and it sits **116 commits behind `origin/main`**, where the
same symbols land on entirely different lines again (`Scene_AddShadowCaster` is at **8060**
on `origin/main` and **8029** locally). Add a line anywhere above a symbol and every
`file:line` below it silently becomes a lie that still *looks* verified.

**So: cite symbols, not lines.** The line number is the one part of an anchor that is
guaranteed to rot and the one part that reads as most authoritative.

    git grep -n 'SYMBOL'          # or: git grep -n 'SYMBOL' -- '*.cpp'
    git grep -n 'SYMBOL' origin/main
    git grep -n 'SYMBOL' HEAD --   # which commit am I even reading?

**Say which tree you measured.** `HEAD`, working tree, or `origin/main` — they do not agree,
and "I checked the code" means nothing without it. A claim verified against a dirty tree is
verified against nobody's tree.

**What survived was right and what moved was noise.** Everything §1 and §2 *assert* about
the three shadow paths, mode 10, the negative space (0 files for shadow maps / volumes /
buffers, 0 `D3DRS_*SHADOW` render states), and `g_colourShadowWhite` being frontend-only
(it appears in exactly 4 files: `FrontendDraw.cpp/.h`, `FrontendMenus.cpp`,
`FrontendScreens.cpp` — no race-time file) all re-verified as true. The claims were sound;
only the addresses were stale. That is the whole lesson: **a structural fact is durable, a line number is not** — so write
down the fact, and let the symbol carry it home.

---

## 6. THE TEXTURE PATH — `.bfl` to the pixels, end to end

Added 15 October 2026, the same day as the round that mapped it. **This is the GAME
RENDERER's path.** It is not the car poser's, which is a different program with a
different texture path; verifying a texture complaint against the poser answers a
question nobody asked.

**Every link carries a symbol, per §5** — the line numbers here are footnotes and are
marked where they were measured. Measured against the `CMR2Decomp` **working tree** at
`~/.lena_cmr2/repo` (HEAD `9af4401`, dirty) and the port at `~/.lena_cmr2/port`.

### 6.0 THE THREE THINGS EVERYONE CALLS "WHICH TEXTURE"

**Conflating these is what let "every `RD_*` road texture never reaches a draw"
survive a whole round as a finding.** They are different quantities, owned by
different code, and a report that does not name which one it means is not a
measurement. Say the letter.

| | what it is | who owns it | how to observe it |
|---|---|---|---|
| **(a) the per-face texture id** | an integer that indexes `textureBuffer[2048]`. Set per triangle by the stage loader, per *mesh part* by `Mesh_BuildParts`, and per *shadow batch* by the batch record. | `Sector_BuildC3DModelScene` -> `Mesh_BuildParts` -> `Graphics_DrawMeshPartsByTexture` reads it and passes `textureBuffer[pPart->texture]` to `ApplyTextureStageChange(0, ...)` | the first argument of `ApplyTextureStageChange`. In a draw census: `b->tex0` / `b->tex1` in the RHI, i.e. **which image the descriptor set names** |
| **(b) the texture-STAGE combiner mode** | `Texture::blendMode`, a small enum (0-11, 0xff). It selects the *arithmetic*: which args, which operation. | `CGraphics::ConfigureTextureStageBlendMode` — a `switch (pTexture->blendMode)`, called from `ApplyTextureStageChange` on every non-cached bind | `[TEXREQ] BINDFIRST ... blend=N`; `case 10:` in `ConfigureTextureStageBlendMode` |
| **(c) the blend** | `D3DRS_SRCBLEND` / `D3DRS_DESTBLEND` render-state pair. It composites the *result* against the framebuffer. | `CGraphics::SetCachedSourceDestinationBlend(param1, param2)`, called with the fixed pairs each combiner case names | the second pair of numbers in each `case`: `SetCachedSourceDestinationBlend(5, 6)` = SRCALPHA / INVSRCALPHA |

**(a) is "which image". (b) is "what arithmetic reads it". (c) is "how the result lands
on the frame".** A road texture can be bound, with the right combiner, and still not
appear — and that is precisely the case that was found here (§6.5, `startVert`).
Any claim of the form "texture X is not drawn" must say which of the three it means.

### 6.1 `.bfl` -> CMPR -> DDS -> the surface the game writes

```
.bfl on disk            gzip stream wrapping a CMPR container          docs/CONTAINER.md
  CMPR TOC              4-byte-aligned entries; last 4 bytes of file    docs/CONTAINER.md
    'DDS ' payload      DXT5 (BC3) or DXT1, or a TGA                    bfl_dds.py
      Sector_BuildC3DModelScene        rebase every triangle's 10 tex indices by +m_textureCount
      Graphics_LoadTextureRecordList   build the file name, choose the flags, load each entry
        CTexture::FindLoadTexture      .dds in archive, else .tga; miss -> disk
          CGraphics::CreateTextureFromImageData
            LoadDDSTexture            block bytes -> system surface -> Blt -> the texture
            LoadTGATexture            decoded in software (frontend + cars take this path)
```

* **The container.** `Sector_BuildC3DModelScene` (`Sector.cpp`) computes
  `textureRecords = *(int *)(pData + 0xc) + (int)pData` and `pEnd = pRecords +
  recordSize * 0x5c`, then calls `Graphics_LoadTextureRecordList((int)pEnd,
  textureRecords, *(unsigned short *)(pData + 0x24), *(int *)(pData + 4), param_3)`.
* **The index rebase, before anything is loaded.** Same function, immediately above:
  for every triangle (stride `0x4c`), the **10 texture index fields at offset +4** are
  walked and each non-`-1` value gets `+= (int)CGraphics::m_textureCount`. **A stage's
  texture indices are RELATIVE to the textures already resident**, and become absolute
  slot ids at load time. Anything that reads a stage texture index without knowing
  `m_textureCount` at that moment is reading a number in the wrong space.
* **The name and the flags.** `Graphics_LoadTextureRecordList` upper-cases the entry
  name, builds `fileName` from `CInstallInfo::GetTexturesDirectory()` plus the last path
  component of the entry, and picks flags by record type: type **6** -> resident-check
  then `Graphics_HasLocalSuffix` -> `0x100` / `0x40`, type **10** -> `0`, **else `0x90`**.
* **Archive first, disk second.** `CTexture::FindLoadTexture` (`Texture.cpp`, `0x004a9e60`)
  calls `Texture_GetPathStem` for the basename, appends `.dds` and tries
  `CGenericFileLoader::FindFileInArchive`; on a miss it rewrites the last 4 bytes to
  `.tga` and tries again. Only if the archive has neither does it fall through to
  `CGraphics::LoadDDSThenTGATexture` (disk). `pTexture->pArchive = pFile` on the archive
  branch — that pointer is what makes the device-loss reload possible.
* **The magic decides the decoder, not the extension.**
  `CGraphics::CreateTextureFromImageData` (`Graphics.cpp`, `0x004a48c0`) tests
  `*(DWORD *)pData == 0x20534444` (`'DDS '`): true -> `LoadDDSTexture`, false ->
  `LoadTGATexture`. It also rewrites the name's last 4 bytes to `m_ddsExtension` when
  the data is DDS, so the name on disk and the name in the slot can disagree in case.
* **DXT is DECOMPRESSED BY THE BLIT, never by the game.**
  `CGraphics::LoadDDSTexture` (`Graphics.cpp`, `0x004a94e0`, ~3145) sets
  `pTexture->flags |= 0x2000` for `DXT5` / `0x4000` for `DXT1` — but only if
  `m_hasTexFormatDXT5_16/32` (resp. DXT1) says the device reported that format in
  `CGraphics::EnumTextureFormatsCallback`. It then creates a **`DDSCAPS_SYSTEMMEMORY`
  surface straight from the DDS header**, `Lock`s it and writes the **block bytes**
  (either one `memcpy` of `dwLinearSize` on the `DDSD_LINEARSIZE` branch, or a row loop
  otherwise). `CGraphics::CreateTextureSurface` then picks the destination format from
  `textureInfo4` (DXT5) / `textureInfo3` (DXT1) / `textureInfo2` ... and
  `pTexture->pSurface->Blt(NULL, pTemp, NULL, DDBLT_WAIT, NULL)` is the conversion.
  **The game's own source contains no DXT decode loop.** On real hardware the driver
  did this; on this port `DeckSurface7::Blt` is the driver.
* **The port's decode.** `LENA-DXTBLT`, `deck_dd7.cpp`: `dl_is_dxt(fcc)`
  (`DL_DXT1 0x31545844` / `DL_DXT5 0x35545844`) -> `dl_decode()` -> `dl_block()` per 4x4
  block into B8G8R8A8, `dirty = 1`, return early. Landed **2026-10-11**. `dl_block`
  handles DXT1 3-colour mode (index 3 -> alpha 0) and DXT5's 8-entry alpha ramp, and
  `dl_colours` uses the correct 2/3- and 1/3-point interpolation. The `surface_fill_desc`
  side reports a compressed surface **as compressed** (`DDSD_LINEARSIZE` +
  `dwLinearSize` + real block-row `lPitch`) so the game takes the branch it wants.
* **Both formats in play.** Stage track textures are **DXT5**; frontend and car
  textures are **TGA** and take the software decode. So a texture complaint is
  format-dependent, and "the textures are wrong" splits at this line.

### 6.2 How a texture gets its id, and WHAT AN ID MEANS

**A `textureId` is a SLOT index into a fixed 2048-entry table. It is not an image.**

* The table: `m_pTextureManager->textureBuffer[0x800]` (2048 `Texture *`).
* Allocation, in **both** `CGraphics::CreateTextureFromImageData` and
  `CGraphics::LoadDDSThenTGATexture`: scan `i = 0 ... 0x7FF` for the **first NULL**,
  allocate a `0x130`-byte `Texture` there, set **`pTexture->textureId = i`**, and
  `m_textureCount++`. So the id is the first free hole, **not** a load order and **not**
  stable across a reload.
* The slot holds a `name`, a `pSurface`, a `pArchive`, a `blendMode`, and flags. The
  slot is what is reused. `Graphics_ReloadAllTextures` relies on this and only acts
  when the entry is live and self-consistent:
  `if (pTexture->textureId == i)` — i.e. **slot index == stored id is the liveness test**.
  `CGraphics::EvictManagedTextureResources` uses the same identity to release surfaces.
* **Consumers index it as an array.** Every draw site does
  `CGraphics::m_pTextureManager->textureBuffer[pPart->texture]` (or
  `textureBuffer[g_shadowBatch[2]]` for the shadow batches). There is no lookup
  function on the draw path — the id *is* the index.
* **Where the per-face id comes from.** `Mesh_BuildParts` (`Mesh.cpp`, `0x004b1ac0`)
  walks the triangles' shared texture field at stride `0x4c` and starts a new
  `MeshPart` on every change of `*(int *)((BYTE *)pMesh->pTriangles + off + 4)`. That
  value is copied to `(*ppPart)->texture`, and `indexCount` accumulates 3 per triangle.
  It then computes `minIndex`/`maxIndex` per part and **rebases the part's index array**:
  `pMesh->pParts[i]->pData[k] -= (short)pMesh->pParts[i]->minIndex;`. Parts are
  contiguous texture runs, so **(a) is a per-run quantity, not a per-triangle one** —
  which is exactly why `Graphics_DrawMeshPartsByTexture` can draw one call per part.
* **A port texId is a different number, assigned at a different time.**
  `DeckDevice7::SetTexture` (`deck_dd7.cpp`) assigns from `nextTexId++` on the
  **first bind**, not at load: `int needUpload = (s->dirty || s->texId < 0); if (s->texId
  < 0) s->texId = nextTexId++;`. From then on the id is a slot in `p->tex[]`
  (`A7VKTex`), and **a re-upload targets the same id** — the image and its view are
  destroyed and replaced. The id is then passed to the RHI as the opaque handle
  `(void *)(texId + 1)`.
* **A slot, not an image — and that is a live crash class, not a nitpick.**
  `a7_upload_texture` (`a7_vk32.c`) destroys and recreates the image on re-upload. A
  descriptor-set cache keyed on the id alone therefore hands the next draw a set
  **naming a destroyed view** -> fragment shader reads unmapped memory -> `[gfxhub] ...
  Faulty UTCL2 client ID: TCP` read fault -> `gfx_0.0.0` ring timeout -> **MODE2 reset
  that takes the compositor and his session with it**. Measured 2026-10-11 at 07:25:40
  and 07:31:49, twice, same page, `Process cmr2`. Fixed by keying `a7vk_combo_set` on
  the **views**, not the ids (`A7VKComboKey.{v0,v1}`), plus
  `a7vk_drop_combo_views(p, view)` called after `vkDeviceWaitIdle` and **before**
  `vkDestroyImageView`. `A7VK_OLD_COMBO=1` is the control arm. See
  `docs/GPU-LIFETIME-FIX.md` and `docs/DEATH-AND-LIGHT.md` section 1.

### 6.3 How the id reaches a draw: the SetTexture call, the slot, the LIFETIME

| step | where | what it does |
|---|---|---|
| pick the part's texture | `Graphics_DrawMeshPartsByTexture`, `Graphics_MarkTexturesAndDrawMeshParts`, `Graphics_DrawMeshTextureBatches` (`Graphics.cpp`) | index `textureBuffer[pPart->texture]` (or the per-triangle field for the batch walker) |
| submit it | `CGraphics::ApplyTextureStageChange(0, (intptr_t)pTexture)` | **the one funnel.** Every texture bind in the game goes through here |
| the game's own cache | `ApplyTextureStageChange` first two lines | `if (m_unk0x0065fa38 == param2 && m_unk0x00520b28 == param1) return;` — a **(texture, stage) memo**. An eaten call reaches neither the device nor the stage combiner |
| the call | `pD3D->SetTexture((DWORD)stage, (IDirectDrawSurface7 *)*(int *)(param2 + 0x114))` | the surface pointer is read out of the `Texture` at **offset `0x114`**, not passed in |
| the combiner | `CGraphics::ConfigureTextureStageBlendMode(stage, pTexture)` | §6.7 |
| the port's bind | `DeckDevice7::SetTexture(DWORD stage, IDirectDrawSurface7 *surf)` (`deck_dd7.cpp`) | NULL -> unbind. Else upload-if-needed, then `a7_set_texture(rhi, stage, (void *)(texId + 1))` |
| the RHI's bind | `a7_set_texture(A7Device*, int stage, void *texture)` (`a7_vk32.c`) | `d->boundTexture[stage] = texture`; counts a switch. **No GPU work.** |
| the draw's snapshot | `a7vk_draw_indexed_fvf` -> `b->tex0 = d->boundTexture[0] ? (int)(intptr_t)d->boundTexture[0] - 1 : -1` | the id is captured **per batch**, together with the stage state and the samplers, because at record time the device state is whatever the last draw left |
| the descriptor | `a7vk_combo_set(p, b->tex0, b->tex1, b->smp0, b->smp1, b->smpH0, b->smpH1)` | keyed on ids **and views and sampler hashes** |

**The lifetime, in order.** The game's Texture slot outlives the port's image:
a **dirty** surface may be re-uploaded on any bind, and `a7_upload_texture` then does
`vkDeviceWaitIdle` -> `a7vk_drop_combo_views(t->view)` -> `vkDestroyImageView` ->
`vkDestroyImage` -> `vkFreeMemory` -> create image + view + (LENA-MIPS) the full chain.
**The port id survives; the image behind it does not.** So "the texture at id N" is only
meaningful within one upload generation — and `A7VK_TEXDUMP` / `mt_snap` /
`sky_snap` exist to hold CPU copies for exactly that reason.

**Stage 1 and 2 are unbinds, always.** Every `ApplyTextureStageChange(1, ...)` /
`(2, ...)` call site in the game passes **`0`**, and appears in a *cleanup tail* after a
texture-mapped pass: `Graphics_DrawCubeMappedShadowTriangles` (`Graphics.cpp`, ~3430)
and the cube-map sibling at ~7365. The only non-zero stage-1 **bind** in the tree is the
cube-map reflection pass, gated on `g_unk0x005210bc`, which is
`Graphics_SetShadowGeometryState(value)` — default 1, set from
`!CGameInfo::IsRecordFlagSet(0xf)` in `RallyData.cpp` and `GameInfo.cpp`.
See §6.4: in a race, measured, **stage 1 carries no coverage at all.**

### 6.4 Which texture each STAGE draw actually binds in a race — MEASURED

Measured, not inferred. Three independent instruments, all already on disk.

**(i) The game's own request trace.** `DECK_TEXREQ=1` (`work/RACE/patch_texreq.py`,
prints in `Texture.cpp` and `Graphics.cpp`). `[TEXREQ] BINDFIRST stage=%d slot=%d
tex=%p name='%s' surf=%p blend=%d` fires once per (stage, slot) **only when the call was
not eaten by the memo in §6.3**; `skip=` in the `part slot=` lines counts the calls that
were. From `work/RACE/out/texreq4_race.log`, one race, 232 stage-0 slots bound at least
once and **all 232 got a port texId** — the join is total on that side.

```
[TEXREQ]   part slot=88    draws=924     bind=925     skip=0       name='...TRACKTEX\PCLOW\RD_GA.DDS'
[TEXREQ]   part slot=81    draws=2772    bind=1233    skip=1540    name='...TRACKTEX\PCLOW\TER_KN4A.DDS'
[TEXREQ]   part slot=156   draws=3213    bind=2602    skip=612     name='...OBJECTS\PCLOW\TRE_129.DDS'
[TEXREQ]   part slot=196   draws=923     bind=1386    skip=308     name='...CARS2\FOC2000\...\CFFDBODF.tga'
```

**Stage distribution: 232 of 232 `BINDFIRST` lines are `stage=0`. Stage 1: zero.**
Blend-mode distribution of those bindings: **211 `blend=0`, 18 `blend=1`, 2 `blend=2`,
1 `blend=4`** — i.e. the race is overwhelmingly combiner mode 0, with a thin tail.
(The `skip` column is why `draws` and `bind` differ, and it is the game's own cache
working as designed — not a dropped state.)

**(ii) The RHI's per-id coverage, post-index-fix.** `A7VK_TEXUSE=1`, printing
**every** id and selecting on **draws OR coverage** (`patch_texuse4/5.py`; the earlier
print capped at the top ten by coverage, which is what manufactured the false finding —
see §6.5). From `work/RACE/out/idxfix_race.log`, frame 2800, 42,065 3D draws,
**65 distinct ids carrying draws**:

| port id | coverage (screens) | draws | what it is |
|---|---|---|---|
| 95 | 4861.48 | 3463 | `TER_KN4A` — terrain |
| 170 | 5835.02 | 4006 | objects |
| 165 | 5513.58 | 2947 | objects |
| 102 | 401.77 | 1113 | **`RD_GA` — the road** |
| 112 | 368.99 | 1357 | `MOU_TER4A` |
| 107 | 267.46 | 1330 | `MRG_KN1` |
| 117 / 118 / 119 | 73.40 / 55.40 / 32.85 | 190 each | fence / barrier family |
| 25, 58, 59, 60, 61 | <= 0.01 | 2-3 each | dust and fragments |

and the instrument's own zero-area breakdown, which is the part that makes the table
readable rather than merely sorted:

```
[TEXUSE]   d id=202  draws=198   tri=11423  zeroArea=3331   wDropped=15738  idxDropped=0
```

**`d id=` is why a coverage number must never be read alone**: `zeroArea` is triangles
whose projection collapsed, `wDropped` those behind the eye, `idxDropped` those rejected
on index range. Pre-fix, ids 102/103/104/107 read `cov=0.00` with **draws in the
thousands** — and `idxDropped=0` rules out the index path; those draws were losing their
area to `wDropped`, which is a *near-plane* fact, not a texture fact.

**(iii) The shadow batches, measured independently the same day.**
`LENA_SHADOWTR=1` (`SHADOW-MECHANISM-FOUND-20261015`), `[SHADOWTR] f=... ser=N
tex=K(used=1) texBlend=0 bat=i/6 view=...` per batch, 400 matched draws:

```
ser=100 tex=144(used=1) texBlend=0 bat=3/6
ser=101 tex=146(used=1) texBlend=0 bat=4/6
ser=102 tex=145(used=1) texBlend=0 bat=5/6
ser=103 tex=144(used=1) texBlend=0 bat=6/6      (cycles 144,146,145,144,146,145,144,...)
```

**Six shadow batches per frame, cycling exactly three texture ids (144, 145, 146), all
`texBlend=0`.** Note the deliberate contradiction with §1's mode-10 entry: the batch's
*stored* `blendMode` is 0, and `Scene_DrawShadowBatches` (`SceneNode.cpp`, `0x004b6240`)
**forces 10 for the duration of the batch** —
`Frontend_SetObjectField118((Unk0x004a3e20 *)pTexture, 10)` before
`ApplyTextureStageChange(0, pTexture)`, then immediately restores `blend`. So for these
draws **(b) is 10 by force, not by data**; the trace reads the field around the call and
sees 0. Both numbers are true and neither is the other. This is the trap in §6.0 in the
wild, and it cost a round.

**The negative, stated plainly: in a race, stage 0 carries the whole 3D picture and
stage 1 is never bound with a texture at all.** `[TEXUSE] STAGE1: distinct ids with
coverage=0 total=0.00 screens drawsBoth=0 other=0.00` — 13 consecutive frames, two
separate runs. So any *stage-1 texture* claim about the race path is describing a path
that is not taken. `stage1En=0` in the frame's own state block agrees.

### 6.5 The instrument trap that produced the false finding

**"Every `RD_*` road texture never reaches a draw" was an artefact of the coverage
print, twice over, and both filters are gone:**
1. it printed only the **biggest ten by coverage**, and in a race the top ten is entirely
   near-plane blow-ups capped at 100 screens per triangle. A road is a thin strip under
   the car.
2. it selected ids by **`cov > 0.0`**, and `tu_draws[id]` increments once per draw
   *after* the triangle walk — so a draw that contributed no area was dropped from the
   print **even with a thousand draws behind it**. "cov=0.0, draws=0" and
   "draws=2000, cov=0.0" are different claims and the old print could not tell them apart.

The real cause of the missing road was elsewhere and is not a texture bug at all:
`DeckDevice7::DrawIndexedPrimitiveVB` re-based an index array that `Mesh_BuildParts` had
already rebased, so the draw read `data + idx*stride` instead of
`data + (startVert+idx)*stride`. Measured: of 404,000 indexed draws with a non-zero base,
**404,000 (100.00 %) fit the game's convention and 0 (0.00 %) fit the port's**; before
the fix the road's 2,000 draws carried **0.0** screens and after it **347,599.57** — the
largest coverage in the frame. Fixed (`LENA-IDXFIX`, `A7VK_IDXBASE=sub` restores the old
behaviour). Full detail: `docs/ROAD-TEXTURE-OWNER.md`.

### 6.6 The sampler: format, mips, filter, wrap

**Format.** The port's image format is `p->offFmt`; uploads are `w*4` bytes per row of
B8G8R8A8, so **every texture the RHI holds is uncompressed 32-bit**, whatever it was on
disk. That is the point of §6.1: DXT is converted at the blit, once, on load.

**Mips.** The game asks for `CGraphics::SetMipMapCount` -> `Mip_LowZeroBits(dim)` capped
at **3** total, and `LoadDDSTexture` only touches the chain when
`(g_pGraphics->field913_0x3bc & 3) && (pTexture->flags & 0x10)`. The game also sets
`D3DTSS_MIPFILTER` from those same two bits in `ConfigureTextureStageBlendMode` case 0
(`& 1` -> `D3DTFP_POINT`, `& 2` -> `D3DTFP_LINEAR`, else `D3DTFP_NONE`) and pins
`D3DTSS_MAXMIPLEVEL = 0`. The port builds a **FULL chain to 1x1** (`LENA-MIPS`, landed
2026-10-12) — deliberately more than the game's 3, because a 1024x1024 terrain texture
minified to a few pixels needs all ten. `A7VK_NOMIPS=1` is the control arm and is the
old one-level behaviour, **out of the same binary**.

**Filter.** `a7vk_sampler(p, address, mag, min)` is cached on
`a7vk_smphash = address*7919 ^ mag*131 ^ min` and **shared by every texture size**, so it
cannot carry a level count. `magFilter`/`minFilter` come from `a7vk_filter`; `mipmapMode`
is `LINEAR` when `mips_on()` else `NEAREST`; `maxLod = 16`, `minLod = 0`. The clamp is
per-image instead: `a7vk_view_mips(..., levels, &view)` sets the view's `levelCount`, and
Vulkan clamps the LOD to the view's mip range. **A one-level view makes any mipmapMode
legal and inert**, which is what makes the A/B clean.

**Wrap.** `a7vk_addr(address)` maps `D3DTSS_ADDRESS` -> `addressModeU/V/W`. The game's
only lever is `CGraphics::SetTextureAddressClamp(int clamp)`, which sets **stage 0 only**:
`clamp != 0` -> `D3DTADDRESS_CLAMP` (3), else `D3DTADDRESS_WRAP` (1) — memoised on
`m_textureAddressClamp`. Called with `1` at device setup and at the ends of
`Graphics_DrawCubeMappedShadowTriangles` / `Scene_DrawShadowBatches`; called with `0`
around the projected-shadow pass. So **the address mode is per-pass, not per-texture** —
a wrap-mode error shows up as a seam on one pass, not on one texture.

**One genuine map gap, flagged not fixed.** `map_tss` (`deck_dd7.cpp`) maps `COLOROP`,
`COLORARG1/2`, `ALPHAOP`, `ALPHAARG1/2`, `ADDRESS`, `MAGFILTER`, `MINFILTER` — and
returns **`-1` for `D3DTSS_MIPFILTER` (18) and `D3DTSS_TEXCOORDINDEX` (11)**, which land
in `cm_tss_drop[stage][t]` / `ignoredStates`. **`TEXCOORDINDEX` is not a mip-filter
detail**: `ConfigureTextureStageBlendMode` case 11 sets it to
`D3DTSS_TCI_CAMERASPACEREFLECTIONVECTOR | 1` with `D3DTTFF_COUNT3` for the cube-map
pass, and case 9 calls `SetTexCoordIndex(param1, 1)`. The port's `a7vk3d.frag` samples
stage 1 with `vUV1` **unconditionally** (`texture(tex1, vUV1)`), which hardcodes one case
of a state the game actually varies. This is consistent with §6.4's negative (stage 1 has
no coverage in a race, so it cannot move a race frame) and that is why it is a flag and
not a fix. **Do not "fix" the TEXCOORDINDEX drop without a measurement on a pass where
stage 1 is really bound, because on this evidence there is no such pass in a race.**

### 6.7 What the texture-STAGE combiner does to it

`CGraphics::ConfigureTextureStageBlendMode(stage, pTexture)` — **the whole fixed-function
cascade, and the source of truth for (b) and (c).**

* `pTexture == NULL` -> `COLORARG1 = D3DTA_TEXTURE`, `COLORARG2 = 0`, `COLOROP =
  D3DTOP_DISABLE`, the same for alpha, `return`. It also writes `g_unk0x00520b18 = -1`.
  This is the untextured path, and it is the *only* one that disables a stage.
* Otherwise `switch (pTexture->blendMode)`, cases **0-11 and 0xff**. Each case sets the
  six texture-stage states and then two more things: a **fixed blend pair** through
  `SetCachedSourceDestinationBlend` and a **texcoord set** through `SetTexCoordIndex`.
  The complete table, measured:

| mode | COLOROP | COLORARG1 | COLORARG2 | ALPHAOP | blend (src,dst) | texcoord |
|---|---|---|---|---|---|---|
| 0 | MODULATE | TEXTURE | DIFFUSE | MODULATE | 5,6 | 0 |
| 1 | MODULATE | TEXTURE | DIFFUSE | DISABLE | 2,2 | 0 |
| 2 | MODULATE | TEXTURE | DIFFUSE | MODULATE | 5,2 | 0 |
| 3 | MODULATE | TEXTURE | DIFFUSE | MODULATE | 1,4 | 0 |
| 4 | MODULATE | TEXTURE | DIFFUSE | SELECTARG2 | (unchanged) | 0 |
| 5 | SELECTARG2 | CURRENT | CURRENT | SELECTARG1 | 5,2 | 0 |
| 6 | SELECTARG1 | TEXTURE | CURRENT | DISABLE | (unchanged) | 0 |
| 7 | ADDSIGNED | TEXTURE + **COMPLEMENT** | CURRENT | DISABLE | 9,3 | 0 |
| 8 | **BUMPENVMAPLUMINANCE** | TEXTURE | DIFFUSE | DISABLE | (unchanged) | 0 |
| 9 | MODULATE | TEXTURE | CURRENT | DISABLE | 2,2 | **1** |
| 10 | MODULATE | TEXTURE + **ALPHAREPLICATE** | DIFFUSE | MODULATE | 5,6 | 0 |
| 11 | MODULATE | TEXTURE | DIFFUSE | SELECTARG2 | (unchanged) | **REFLECTIONVECTOR + 1** |
| 0xff | MODULATE | TEXTURE | DIFFUSE | MODULATE | 5,6 | 0 |

  (Mode 0 additionally sets `D3DTSS_MIPFILTER` from `field913_0x3bc & 3` and
  `D3DTSS_MAXMIPLEVEL = 0`; the table omits those two for width. Mode 4 and 11 leave the
  blend pair alone, which is why "unchanged" is the honest cell and not a missing number.)
* **The cache at the end is a GLOBAL, and it is written per stage.** `g_unk0x00520b18 =
  pTexture->blendMode;` — one variable, written for *any* stage, and
  `Graphics_InvalidateTextureStageCache` (`Graphics.cpp`, `0x004a3dd0`) just sets it to
  `-1`. Nothing in this function reads it before writing. **Do not assume it gates the
  combiner** — the gate that actually eats calls is the (texture, stage) memo in
  `ApplyTextureStageChange` (§6.3).
* **Mode 10 is "the texture is an ALPHA MASK".** `COLORARG1 = D3DTA_TEXTURE |
  D3DTA_ALPHAREPLICATE` (alpha replicated into rgb), `COLORARG2 = D3DTA_DIFFUSE`,
  `COLOROP = D3DTOP_MODULATE`. So the result is `texture.aaaa * vertexColour` — the
  texture contributes its *alpha as luminance* and nothing else. That is the flat shadow:
  a dark quad whose shape comes from the texture's alpha and whose colour comes from the
  vertex. It is the combiner that makes the shadow geometry look like a decal.
* **The port reproduces the cascade twice, on purpose.** `a7_eval_texop` in `a7_vk32.c`
  is a **software reference**, and `a7vk3d.frag`'s `argval()` / `combine()` is the GPU
  path; they are written to agree byte-for-byte. `argval` decodes exactly this encoding:
  `base = ai & 0xF` (2 = DIFFUSE, 3 = CURRENT, else TEXTURE), `ai & 0x10` = complement
  (`1.0 - v`), `ai & 0x20` = alphareplicate (`v.aaaa`). `map_texarg` (`deck_dd7.cpp`)
  builds the same packing on the D3D side, with `0x5` mapped explicitly to `A7TA_TEMP`
  because the header does not name it.
* **Stage state is snapshotted at DRAW time, not at record time.** `a7vk_fill_push`
  fills `pc.f0/f1/f2/f3` at the moment the batch is built (`pc.f0[0] = boundTexture[0]
  ? 1 : 0`, `pc.f0[1..3]` = colorop/arg1/arg2, `pc.f2[*]` = the alpha side, `pc.f3[3]` =
  stage-1-enable — and that last one is a **live check, not a stored flag**:
  `pc->f3[3] = (d->stages[1].colorop > A7TOP_DISABLE && d->boundTexture[1]) ? 1.0f : 0.0f`,
  so stage 1 samples only when its op is enabled *and* a texture is bound to it at that
  draw). The comment on the sampler block gives the reason and it is the same
  reason: at record time the device state is whatever the **last** draw of the frame left
  behind. Any instrument that reads stage state later is reading the frame, not the draw.
* **One mode is declared and not implemented, and it says so.** Mode 8 is
  `D3DTOP_BUMPENVMAPLUMINANCE`; `api7.h` marks it **"1 site -- STUB + FLAG, do not
  implement bump mapping"**, and `map_texop` is where the flag lives. Treat a bump claim
  as out of scope by construction, not as a bug.
