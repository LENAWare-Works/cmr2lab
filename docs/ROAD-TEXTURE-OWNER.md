# THE ROAD TEXTURE'S OWNER — the game asks, the port binds it, and the port's draw is what is broken

`work/RACE`, 2026-10-11 ~05:5x EEST. Round: **"of the 40+ Kenya track textures, only
`TER_KN4A` and `GR_001` are ever bound in a race — which side owns that, the game's
material selection or a query the port answers wrongly?"**

Read with `CHECKPOINT.md` (how to re-run) and `DXT-COPY-PATH.md` (the round before).
Every number below is measured on this Deck tonight, in the game's own binary, in the
game's own attract-mode route to a race.

> **THIS FILE IS NOW HISTORY, NOT THE SHAPE. `BLUEPRINT.md` §6 wins.**
> Appended 2026-10-15 by `TEXTURE-MAPPING-TRUTH-20261015`. The structural facts this file
> establishes — a `textureId` is a slot, the game never decodes DXT, the index re-base is
> the road's real bug, the coverage print's top-ten cap manufactured the "never reaches a
> draw" premise — are all in the blueprint with symbol anchors, end to end, alongside the
> combiner table and the measured race bindings. **Where this file and `BLUEPRINT.md` §6
> disagree, the blueprint is right**; the numbers here are the round's evidence, and they
> are kept as evidence.

---

## 0. THE ONE LINE

**Neither (i) nor (ii). The game asks for the road textures, the port hands back exactly
the texture that was asked for — and then the port draws it with the wrong vertices,
because `DeckDevice7::DrawIndexedPrimitiveVB` subtracts a vertex base that
`Mesh_BuildParts` had already subtracted. Measured: of 404,000 indexed draws with a
non-zero base, 404,000 (100.00 %) fit the game's convention and 0 (0.00 %) fit the
port's.** The material table is innocent, the texture lookup is innocent, and the
premise (that the road's paint never reaches a draw) was an artefact of the coverage
instrument printing only its top ten.

```
                                    game asks      port binds      port draws
RD_GA.DDS   (slot 88 -> texId 102)  1 288 / 1 288  1 288 / 1 288   2 000 draws, cov 0.0
```

…and with the index base corrected, the same 2,000 draws carry **347,599 screens** of
area — the largest single coverage in the frame. §6 and §7.

---

## 1. THE INSTRUMENT — the request path, logged at the source

`patch_texreq.py` (env `DECK_TEXREQ=1`). The question said "trace
`CGraphics::FindLoadTexture`, or whatever the tree actually names it". The tree's names
matter here, because **this engine's draw-time texture request is not a name at all — it
is an index**, and a trace that only watched `FindLoadTexture` would have watched
loading and called it selection:

| where | what it is | what the engine does with it |
|---|---|---|
| `CTexture::FindLoadTexture` (`Texture.cpp`) | load-time, by name | allocates a slot, `pTexture->name`, `pTexture->pSurface` |
| `Mesh_BuildParts` (`Mesh.cpp`) | **the material table** | reads each triangle's 10 texture indices, groups triangles, writes `MeshPart::texture` = a slot index |
| `Sector.cpp` (`textureRecords`/`m_textureCount`) | the index base for a stage block | rebases every triangle's texture index by the textures already loaded |
| `Graphics_DrawMeshPartsByTexture` / `Graphics_MeshTextureBatches` (`Graphics.cpp`) | **the request** | `textureBuffer[pPart->texture]` → `ApplyTextureStageChange(0, tex)` → `pD3D->SetTexture(stage, pTexture->pSurface)` |

So the trace prints at each of those ends, and the two logs are joined **on the
surface pointer**, which is the only join that cannot be fooled by ordering (the
id→name table in the previous handoff was built by order, not by pointer):

```
[TEXREQ] LOAD-REQ  name='…MR_1B.DDS' file=… didFileLoad=1 param5=0 flag=00000090
[TEXREQ] LOAD-OK   name='…MR_1B.DDS' from=ARCHIVE -> slot=87 texname='…\MR_1B.DDS' surf=0x3543f10
[TEXREQ] MESH      mesh=0xee59d158 tris=2 parts=1 flags=0000086a: [p0 slot=155 name='…TRE_123.DDS' idx=6]
[TEXREQ] DRAW      window=5 … [TEXREQ]   part slot=88 draws=1288 bind=1288 skip=0 name='…RD_GA.DDS'
[TEXREQ] BINDFIRST stage=0 slot=88 tex=0x16d8460 name='…RD_GA.DDS' surf=0x16d85d0 blend=0
[TEXREQ] DD7 NEWID surf=0x3544190 -> texId=102 64x64 px0=236696ff      (the port's end)
```

`BINDFIRST` fires once per (stage, slot) **only when the call was not eaten by the
game's own stage cache**, and `skip=` counts the calls that were. That distinction is
why `draws` and `bind` are printed side by side.

In a race, 232 stage-0 slots were bound at least once and **all 232 got a port texId**,
so the join is total on that side.

---

## 2. INERTNESS, MEASURED ON THE BINARY HE RUNS

`work/PLAY/out-plain/cmr2` = `work/RACE/out-texreq/cmr2` =
**`b960621bcc5657e135640e35aa70869f`** (the previous one is kept, §8). Run
`out/final_inert` — `env` with every new variable unset, one Enter to clear the legal
notice, attract mode, a race reached:

```
[TEXREQ]  lines: 0        [IDXTRACE] lines: 0
[TEXUSE]  lines: 0        [SURF]     lines: 0
[CENSUS] draws by FVF: 0x1c4 TL=… 0x2d2 MESH=417596 refused_by_backend=0
GPU ring timeouts 12 -> 12
```

Zero lines from every instrument, the stage still reached. The three inertness runs
tonight (`texreq_inert`, `texreq2_inert`, `final_inert`) each printed 0 `TEXREQ` lines.

---

## 3. THE PREMISE WAS AN ARTEFACT OF THE INSTRUMENT, TWICE OVER

`A7VK_TEXUSE` accumulates, per bound texture id, the NDC area of every 3D draw
(`cov`) and the draw count (`draws`). Two filters stood between that accumulator and
the sentence "every `RD_*` has cov=0.0, draws=0":

1. **it printed only the biggest ten by coverage.** In a race the top ten is entirely
   taken by ids whose coverage is inflated by near-plane blow-ups (a single triangle
   projecting to NDC x ≈ 6×10², capped at 100 screens each). Anything smaller than the
   tenth entry was never printed — and a road surface is a thin strip under the car.
   `patch_texuse4.py` prints every id.
2. **it selected ids by `cov > 0.0`.** `tu_draws[id]` is incremented once per draw
   *after* the triangle walk, so a draw that contributed no area was dropped from the
   print even with a thousand draws behind it. `patch_texuse5.py` selects by draws **or**
   coverage. "cov=0.0, draws=0" and "draws=2000, cov=0.0" are not the same claim and the
   old print could not tell them apart.

Both are additive changes to the existing instrument behind the same env var, nothing
else. With them lifted, the same run that "showed" cov=0.0 shows:

| slot | texture | port id | game asks (draws/bind/skip) | port draws | port coverage |
|---|---|---|---|---|---|
| 88 | `RD_GA.DDS` | 102 | 1288 / 1288 / **0** | 2000 | **0.0 screens** |
| 93 | `MRG_KN1.DDS` | 107 | 1594 / 1594 / 0 | 2400 | 0.0 |
| 94 | `MRG_KN2.DDS` | 108 | 1266 / 1266 / 0 | 2000 | 0.0 |
| 98 | `MOU_TER4A.DDS` | 112 | 1594 / 1594 / 0 | 2400 | 0.0 |
| 75 | `TER_421C.DDS` | 89 | 790 / 790 / 0 | 2000 | 0.0 |
| 81 | `TER_KN4A.DDS` | 95 | 3588 / 1752 / **1836** | 4400 | 21148 (blow-up inflated) |
| 53 | `GR_001.DDS` | 67 | — (below the top-12 cut) | 6803 | 1076 |

(`out/texreq4_race.log`. The window is 60,001 part-draws; the race windows all look
like this.)

---

## 4. SO: DOES THE GAME ASK? YES — and this is the answer to (i)

`[TEXREQ] DRAW` counts **every 3D draw's requested slot, at the draw**, with the name
that slot holds. In the race window above the game asked for `RD_GA` 1,288 times, and
it asked for `MRG_KN1`, `MRG_KN2`, `MOU_TER4A`, `TER_421C`, `RD_GB`, `RD_GC`,
`MRG_KN0B`, `TER_KN4B` and the rest of the track's material set in every window of
every run tonight (`out/texreq*_race.log`, 13 `part slot=88` lines across 5 windows in
one run). The mesh-level trace names the same thing from the other side:

```
[TEXREQ] MESH mesh=0xee2785e0 tris=62 parts=1 flags=000009f4: [p0 slot=81 name='…TER_KN4A.DDS' idx=186]
```

**Ruled out, with the trace behind it:** a wrong texture index out of the c3d trailer,
the submesh split, and the track's own material table. The part tables carry real
Kenya names — road, terrain, grass, buildings, trees, banners, the car — and
`pPart->texture` resolves through `textureBuffer[]` to a `Texture` whose `name` is the
file the stage asked for. `partsSlotNull=0` and `oob=0` in every window: no part ever
pointed at an empty or out-of-range slot.

*(The one real oddity this instrument did find in the game's side is the stage cache:
for `TER_KN4A`, 1,836 of 3,588 requests were skipped as "already bound", and for the
road textures 0 of 1,288. That is consistent — the terrain is re-requested back to back
while the road alternates with its neighbours — and it is the game's own cache, in front
of a bind that is correct when it happens.)*

---

## 5. DOES THE PORT ANSWER WRONGLY? NO — and this is the answer to (ii)

The port's end of the handoff, joined by surface pointer:

```
[TEXREQ] BINDFIRST stage=0 slot=88 … name='…RD_GA.DDS'  surf=0x16d85d0      (game)
[TEXREQ] DD7 NEWID surf=0x3544190 -> texId=102 64x64 px0=236696ff            (port)
```

The surface the game hands to `SetTexture` is the surface the port uploads and assigns
a texId to, and that texId is the one the draw owns. There is no substitution anywhere:
not in the name→path table, not in the part→texture mapping, not in a lock or an
upload, and not in the cache — `a7vk_combo_set` keys its descriptor set on
`(tex0, tex1, sampler hashes)`, so the image a draw samples is the image of its own id
(and its white fallback is only reachable when the id was never used). **The port
returns exactly what was asked for.** (ii) is false as posed.

What the port *does* do with it is §6.

---

## 6. WHAT THE PORT DOES WITH IT — the draw is addressed with the wrong vertices

`port/rhi/deck_dd7.cpp`, `DeckDevice7::DrawIndexedPrimitiveVB`, verbatim:

```c
    /* D3D's indices are absolute into the vertex buffer; api7's are relative to
     * the array it is handed. Subtracting does NOT corrupt the game's index array
     * -- it is copied into a scratch buffer the RHI owns. */
    const uint16_t *use = (const uint16_t*)idx;
    if (startVert) { … for (i…) idxScratch[i] = (uint16_t)(idx[i] - startVert); use = idxScratch; }
    a7_draw_indexed_fvf(…, v->data + (size_t)startVert*stride, use, (int)numVerts, (int)numIdx);
```

It shifts the vertex base by `startVert` **and** subtracts `startVert` from every index.
The two cancel: the vertex actually read is `data + idx*stride` instead of
`data + (startVert + idx)*stride`, so `startVert` is lost. The game's own loader says the
indices are relative, and it says it twice:

* `Mesh_BuildParts` (`Mesh.cpp:231`) — after computing each part's `minIndex`/`maxIndex`
  from the raw vertex indices, it **rebases the index array**:
  `pMesh->pParts[i]->pData[k] -= (short)pMesh->pParts[i]->minIndex;`
* `Graphics_DrawMeshPartsByTexture` (`Graphics.cpp:7352`) — then draws it with
  `startVert = pMesh->vertexOffset + pPart->minIndex`, `numVerts = pMesh->field_0x10 - pPart->minIndex`.

Two independent pieces of game code agree: the array handed over is already relative to
`startVert`. The port's comment says the opposite and re-bases it again.

**Measured, `patch_idxtrace.py`, `DECK_IDXTRACE=1`, run `out/idxtrace_race.log` — every
indexed draw with `startVert != 0`, and both readings tested per index:**

```
[IDXTRACE] running: draws(startVert!=0)=404000  rawInRange=15969393/15969393
                    usedInRange=349174  relOk=404000 absOk=0 neither=0
[IDXTRACE] draw startVert=840 numVerts=116 numIdx=156 raw[0..115] rawInRange=156 usedInRange=0
[IDXTRACE] draw startVert=956 numVerts=9   numIdx=24  raw[0..8]   rawInRange=24  usedInRange=0
[IDXTRACE] draw startVert=965 numVerts=4   numIdx=6   raw[0..3]   rawInRange=6   usedInRange=0
```

* **100.00 %** of indices (15,969,393 of 15,969,393) are inside `[0, numVerts)` as the
  game wrote them; **2.19 %** (349,174) are inside it after the port subtracts.
* `raw[0..115]` for `numVerts=116` is a part whose indices are *exactly* the window it
  was handed: not a near miss, a tailored array.
* 404,000 draws with a non-zero base in one ~90 s run — this is the whole indexed path,
  not one mesh.

That is why the road's draws measure zero area in §3: `tu_note`'s walk (and the GPU)
address `data + idx*stride`, so for a part whose base is not 0 the indices land outside
the vertex window it was handed, and every triangle is rejected. The road textures are
not unbound — they are drawn from the wrong vertices.

---

## 7. THE FIX, AND WHAT IT CHANGES — one condition, A/B'd in one build

`patch_idxfix.py`: `A7VK_IDXBASE=sub` restores the old behaviour; the tree's default is
now the corrected one (§8). Same binary, same route, two runs:

| | before (default was `sub`) | after (`raw`) |
|---|---|---|
| `RD_GA` / id 102, port coverage | **0.0** screens (2000 draws) | **347,599.57** screens (2000 draws) — the largest in the frame |
| `MRG_KN1` / id 107 | 0.0 (2400 draws) | 237,993.76 (2400 draws) |
| `MOU_TER4A` / id 112 | 0.0 (2400 draws) | 210,545.06 (2400 draws) |
| `TRE_129` / id 170 | not printed (0 area) | 96,649.44 (3600 draws) |
| frame at t=78, clear-colour pixels | 57.9 % | **0.0 %** |
| frame at t=78, distinct sampled colours | 817 | **2535** |

Runs `out/texreq4_race.log` and `out/idxfix_race.log`; frames
`out/texreq4_race.04_t78.ppm` and `out/idxfix_race.04_t78.ppm`; both frames read with
`look.py`. 121 ids carry coverage in both — but before the fix they are the blow-up
ids and the dust, and after it they are the track: road, terrain, objects, car.

**GPU: 12 → 12 ring timeouts in every run tonight (seven runs, including both sides of
this A/B).** No window left on his desktop, no stray process.

---

## 8. STATE OF THE DISK

| file | change |
|---|---|
| `port/rhi/deck_dd7.cpp` | `DrawIndexedPrimitiveVB`: the index re-base is now **off by default**; `A7VK_IDXBASE=sub` restores it. `DECK_IDXTRACE` counting added (gated) |
| `port/rhi/a7_vk32.c` | `A7VK_TEXUSE` prints every bound id (not the top ten) and selects by draws **or** coverage, and reports per id why a draw added no area. **Inert unless `A7VK_TEXUSE`** |
| `port/tree/CMR2Decomp/Texture.cpp`, `Graphics.cpp`, `Lenatrace.cpp` | `DECK_TEXREQ` request/bind/mesh/draw trace. **Inert unless `DECK_TEXREQ`** — so, as last round, `Graphics.cpp`/`Texture.cpp` carry gated prints and the "66/66 objects" claim is not this round's |
| `work/PLAY/out-plain/cmr2` | **now `b960621bcc5657e135640e35aa70869f`** — the index-base fix plus the inert instruments. The binary that was there (`e43d7a1e4279fe2c05647c7c053d4fd3`) is kept as `cmr2.bak-pre-idxbase-20261011` |
| `work/RACE/out-texreq/cmr2` | the same binary, same md5 |
| `work/RACE/` | `ROAD-TEXTURE-OWNER.md`; `patch_texreq.py`, `patch_texuse4.py`, `patch_texuse5.py`, `patch_texuse6.py`, `patch_idxtrace.py`, `patch_idxfix.py` (all idempotent); logs `out/texreq*`, `out/idxtrace_race.log`, `out/idxfix_race.log`, `out/final_inert.log`; frames |

Every patch script is idempotent and prints `already applied` on a second run — checked,
not assumed. Backups carry the pre-run `.bak-pre-*` name next to each source.

**Re-run:** `python3 patch_texreq.py && python3 patch_texuse4.py && python3 patch_texuse5.py && python3 patch_texuse6.py && python3 patch_idxtrace.py && python3 patch_idxfix.py`,
then `cd ~/.lena_cmr2/port/rhi && ./build32_rhi.sh && ./build32_dd7.sh`,
`cd ~/lena/work/RACE && OBJ=… OUT=out-texreq ./build-plain-race.sh`,
`DECK_TEXREQ=1 A7VK_TEXUSE=1 DECK_IDXTRACE=1 BIN=… ./run_fe.sh <tag> "w12,s=00_boot,k=enter,w42,s=01_t54,w8,s=02_t62,w8,s=03_t70,w8,s=04_t78"`.

---

## 9. WHAT THIS DOES NOT CLAIM

* **The picture has not been checked against a reference.** What is measured is that
  the road's own draws now project real area and that the frame is no longer 57.9 %
  clear-colour — 0.0 % clear, 2535 distinct sampled colours, dominantly dirt browns.
  Whether the framing, the near plane and the alpha wash are what a Kenya stage should
  look like is the next round's question, and `look.py` plus `A7VK_AB` are the tools for
  it. This is the one claim in this file I would not defend without a picture beside it.
* **`startVert` is not the only base in the engine.** `DrawIndexedPrimitive` (the
  non-VB form, used by the billboards and the 2D path) has no `startVert` and was never
  touched by this bug, which is why the dust and the skinned 2D layers always looked
  like themselves while the stage did not.
* **The terrain's own coverage number is still a floor, not a measurement** — §3's
  blow-ups are capped at 100 screens per triangle, so `TER_KN4A`'s 21148 and the road's
  347,599 are "at least this much", not areas. They are comparable to each other, which
  is all §7 uses them for.
* **Nothing about blend state, `TEXTUREFACTOR` or the alpha path was touched**, and this
  file does not re-report them. Stage 1 is still never bound; it is not new and it is
  not this round.
