# THE MENU CAR, ROUND 2 — the hypothesis is dead one call site deeper, the instrument now exists, and the GPU was not mine to take

`work/MENU-CAR-FLATTENED` (round 2), 2026-10-11 09:00–09:10 EEST. Read with `MENU-CAR.md`
(round 1 of this ticket), `MENU-CAR-EVIDENCE.md` (the round that corrected it), and
`CHECKPOINT.md`. **No game run this round** — §1 says why, and it is a decision with a reason.

---

## 0. THE FOUR LINES

1. **The menu car's index convention is relative, and now it is pinned to the preview car by
   its own argument list, not to a race car by a trace.** `Graphics.cpp:7474`/`:7506` pass
   `startVert = pMesh->vertexOffset + pPart->minIndex` and `numVerts = pMesh->field_0x10 -
   pPart->minIndex` with `pPart->pData` already re-based by `minIndex` (`Mesh.cpp:233`). The
   array index the backend needs is `pData[k]` — **raw**. `Mesh_UploadVertices`
   (`Mesh.cpp:241-252`) gives **every** mesh a non-zero `vertexOffset`, so the switch does
   apply to the preview car, and the correct setting is the *same* as the race path's.
2. **So the corrected default cannot be what broke the menu car** — the old default
   double-rebased the menu car too. Miami's "it rendered fine before this fix" has no capture
   behind it: the only pre-fix capture of that screen here is from a build whose DXT textures
   were still undecoded.
3. **The instrument the ticket asked for is written, compiled and linked** —
   `LENA-MENUDRAW`, specced in `MENU-CAR-EVIDENCE.md` §4 and absent from the tree until now.
   `work/MENU-CAR-FLATTENED/out-md/cmr2`, md5 `5b1a1902cf65e46a4c116eadf33221a3`. No peer
   artefact was touched: `port/rhi/deck_dd7.o` and `PLAY/out-plain/cmr2` are still 08:53.
4. **The leading mechanism is now candidate C, with its arithmetic done**: 16.16 fixed read
   as IEEE float is `1e-41` per coordinate and NaN when negative — i.e. every vertex collapses
   into one place, which is Miami's sentence ("flattens into one place ... one flat piece of
   paper"). One `LENA-MENUDRAW` line separates it from geometry/transform causes.

## 1. WHY NO RUN — the card was somebody else's, and I could see it

| time | what was on the card |
|---|---|
| 08:57:12 | `out-plain/cmr2` pid 588344, live, with a `/tmp/snapnow` trigger loop firing every ~11 s (trig.ppm.000…010) |
| 09:00 | pid 595534, same binary, replacing it |

`gpu-guard.sh --foreign` returned `588344` — a game alive that this harness did not start.
The guard's own rule is that his runs and a peer's runs look identical from here and *both*
mean stand down; and two `cmr2` on one card is what wedged the display at 07:25. I did not
start a third, and I did not touch `/tmp/snapnow` or `/tmp/trig.ppm.*` — another worker was
mid-campaign with them. **The peer `MENU-CAR-EVIDENCE-VISION-r2` holds the window.**

## 2. WHAT I DID INSTEAD — the measurement that does not need the screen

### 2.1 Item 1, answered at the call site, for the preview car

```c
DrawIndexedPrimitiveVB(D3DPT_TRIANGLELIST, pVertexBuffers[pMesh->vertexBufferIndex],
                       pMesh->vertexOffset + pPart->minIndex,   /* startVert */
                       pMesh->field_0x10 - pPart->minIndex,     /* numVerts  */
                       pPart->pData, pPart->indexCount, 0);
```

Both parts-path sites (`Graphics.cpp:7474`, `Graphics_MarkTexturesAndDrawMeshParts`
`Graphics.cpp:7506`) are identical here. `Mesh_BuildParts` (`Mesh.cpp:222-234`) takes each
texture group's `minIndex`, stores it, and does `pData[k] -= (short)minIndex`; `Mesh.h:19`
says in the game's own words *"minIndex … first vertex used (indices are relative to it)"*.
`Mesh_UploadVertices` sets `vertexOffset = vertexBufferFill[i]`, accumulating inside a
2000-vertex shared buffer — so the preview car's `startVert` is **not** zero and the switch
does reach it. Everything the menu car draws is one of these ten sites; all ten want raw.

### 2.2 `LENA-MENUDRAW` — what it prints, and why each field is there

Per indexed **3D** draw (FVF ≠ `TLVERTEX`), bounded, inert when unset, every read clamped to
the vertex buffer's own byte length:

```
[MENUDRAW] #1234 fvf=0x2d2 stride=48 vb=0x... bytes=... startVert=840 numVerts=116 numIdx=156
           zeroBase=no idxInRange=yes idx[0..5]=...
[MENUDRAW]    float48 x[..] y[..] z[..] nonfinite=0
[MENUDRAW]    fixed48 x[..] y[..] z[..]      (same bytes, 16.16)
[MENUDRAW]    fixed32 x[..] y[..] z[..]      (32-byte packed?)
```

* **`zeroBase=no` is the per-draw test of the ticket's own hypothesis.** A draw with
  `startVert = 0` is one the `A7VK_IDXBASE` switch *cannot* have changed. If the setup screen's
  car draws come out `zeroBase=yes`, the hypothesis dies per draw, on that screen, without
  needing a picture.
* **`idx[0..5]` is the array the backend actually received** (`use`, after any re-base) — not
  the game's array.
* **`float48` vs `fixed48` vs `fixed32` is candidate C, decided in one line.** The preview's
  converted vertices are 32-byte 16.16 fixed (`Unk0x0082d220VertexFixed`, `GameInfo.cpp:1383`;
  built by `OptionPreview_AllocateConvertedWheelVertices`, `GameInfo.cpp:7727` — six int32 then
  packed normals at 0x18) while the stride rule is `TLVERTEX ? 32 : 48` (`deck_dd7.cpp:1442`)
  and the mesh FVF `0x2d2` is 48. If the buffer is one format and the stride the other, the two
  decodes disagree about the size of the object, on the object's own numbers.

### 2.3 Candidate C's arithmetic — measured, not argued

```
16.16 fixed read as IEEE float:
   1.0000 -> 0x00010000 -> 9.18355e-41      4.0000 -> 0x00040000 -> 3.67342e-40
   0.5000 -> 0x00008000 -> 4.59177e-41     -1.0000 -> 0xffff0000 -> nan
```

Every coordinate within rounding of one point; every negative coordinate NaN. A car drawn
from such data is **flat, mangled, and in one place** — Miami's words, arrived at without
looking at anything. This is why candidate C goes to the top of the list and the index base
comes off it.

## 3. ON DISK

| file | what |
|---|---|
| `work/MENU-CAR-FLATTENED/patch_menudraw.py` | applied; adds `LENA-MENUDRAW` to `~/.lena_cmr2/port/rhi/deck_dd7.cpp`; idempotent; backup `deck_dd7.cpp.bak-pre-menudraw-20261011-090129` |
| `work/MENU-CAR-FLATTENED/out-md/cmr2` | the game + instrument, linked in my own directory, md5 `5b1a1902cf65e46a4c116eadf33221a3` |
| `work/MENU-CAR-FLATTENED/readframe.py`, `grid.py` | frame measurement and an ASCII density map — every picture claim from me is one of these, because I cannot see an image |
| `work/MENU-CAR-FLATTENED/CHECKPOINT.md` | the checkpoint this round resumed from and updated |
| this file | the round's report |

**Nothing of a peer's was touched.** `port/rhi/deck_dd7.o` (190,700 B) and
`work/PLAY/out-plain/cmr2` (`d26a0923a98ebb25b6da8b664275f87`) are both still 08:53, i.e. the
binary other workers are measuring is the same binary they were measuring before I started.

## 4. THE NEXT GPU WINDOW, IN ORDER

1. `out-md/cmr2` with `LENA_MENUDRAW=1` on **whatever screen the game is on**, and
   `LENA_MENUDRAW_MAX=400`. If any line is `zeroBase=yes`, the ticket's hypothesis is dead on
   that screen by that screen's own numbers.
2. On the setup screen specifically: one line whose `float48` bbox is degenerate while
   `fixed48`/`fixed32` is car-shaped **is** candidate C, and the fix is a stride/convert fix in
   the port, not a change to the index base.
3. `run_menuhunt.sh` (written, still never run) for the reach-the-screen route, watched on the
   option-menu camera line so key injection stops the moment the screen is up.
4. The PNG in item 4 of the ticket still does not exist: there is no capture of the setup
   screen before or after the fix, on this machine, at this time. Pushing a race frame or a
   frontend frame under the name "the menu car" would be a worse answer than saying so.
