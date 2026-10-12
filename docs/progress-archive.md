# the append-log, archived 2026-10-11 11:1x EEST

This is **all of `progress.md` as it stood at 10:28 today**, kept verbatim and
unedited, because the record of how a thing was found is worth more than a tidy
file. It is a reverse-chronological log: the newest block (`0l`) is at the top and
the oldest (`0`, `0.5`) is near the bottom, and it was written by fourteen different
rounds, each appending above the last.

It is **history, not status.** Two things are true of it that are worth saying out
loud before anyone reads a number out of it:

* several of its claims were corrected *by later blocks in the same file* (`0z`
  corrects `0y`-style corrections are the norm here, not the exception), and a few
  are now plainly superseded — the GPU fault it lists as fatal was fixed at 23:09,
  and the "the port draws no road" line was an instrument artefact;
* the last status section it carried (`1. RIGHT NOW` / `2. DONE` / `3. IN PROGRESS`,
  written 2026-10-10 ~14:40) was later spliced into by appends and is no longer
  readable as one document.

The live page is [`../progress.md`](../progress.md), which is rewritten whole each
round so that no stale claim can sit above a fresh one. This file is where the
old claims live, with their dates on them.

---

# progress.md — Lena on the Deck, reporting to Lena on the phone

Rewritten **whole** at every checkpoint, never appended. If a line is not true at
the timestamp below, it is not in this file. Every line answers "how do I know
this" with a number, a path, or a test result — and where I could not answer it,
the line is in §6 instead.

**Last whole rewrite: 2026-10-10 14:54 EEST. §0 was appended at 15:15 by the
pretty-frame worker; the rest of the file is that 14:54 rewrite, unverified by me.** This file is one commit — the rewrite
that carried it is `git log -1 -- progress.md`, and it is rewritten whole, not
appended, so there is never a stale claim above a fresh one.

**Blocks §0, §0.5 and §0a were appended after that rewrite, each saying so at its
own head. §0a has since been re-verified in place, with every change marked
`CORRECTION` and a stamp at the top of the block.**

**On provenance, because this rewrite is 26 minutes after the last one.** §1, §2.8,
§3A and §5 are measured at 14:47, and one §6 bullet was added at 14:54. Everything else in §2 is carried forward from the
14:17–14:28 rewrite and I did **not** re-run it in this pass; those lines say so
where it matters. Nothing here has been re-derived from memory.

Paths, so they line up on both ends:

| short name | real path on the Deck |
|---|---|
| the install | `~/lena/.lena_cmr2/game` (**638 MB** retail PC install; 259 `.c3d`, 220 car containers. It said 2.26 GB here — that was the disc-image copies in `gamedata/`, corrected §0b/§6) |

## 0l. THE MENU CAR, ROUND 2 — the index-base hypothesis is dead one call site deeper, the instrument it asked for now exists, and the GPU was somebody else's. added 2026-10-11 09:1x EEST by the `MENU-CAR-FLATTENED` worker; appended, nothing above or below it touched

> **CORRECTION, stamped 2026-10-11 09:2x EEST. The peer worker `MENU-CAR-EVIDENCE-VISION` committed at 09:03 — after this block was typed — and it reads the option screen's own captures. Two sentences below were wrong when they were written and the numbers in them were wrong with them: *"there is no capture of the setup screen before or after the fix"* and *"the menu screen was still not reached"*. Both are corrected at the foot of this block, marked CORRECTION, rather than left standing above a fresher claim.**

**One line: the menu car's indices are relative *by the call site's own argument list* — so the corrected default cannot be what broke it, the old default double-rebased the menu car too — and the leading mechanism is now the preview's own 32-byte 16.16 fixed vertices being read at a 48-byte float stride, which collapses every vertex into one place in arithmetic, not in argument.**

* **Item 1, answered for the preview car and not for a race car.** `Graphics.cpp:7474` and `:7506` (the parts path, which is what a car mesh with parts uses) pass `startVert = pMesh->vertexOffset + pPart->minIndex` and `numVerts = pMesh->field_0x10 - pPart->minIndex`, while `Mesh_BuildParts` (`Mesh.cpp:233`) has already done `pData[k] -= minIndex`. The index the backend needs is `pData[k]` — **raw**. `Mesh_UploadVertices` (`Mesh.cpp:241-252`) sets `vertexOffset = vertexBufferFill[i]`, accumulating inside a 2000-vertex shared buffer, **so the preview car's `startVert` is not zero and the `A7VK_IDXBASE` switch does reach it** — the hypothesis was worth checking, and it is still dead. All ten call sites want raw; the old default subtracted a second time.
* **The instrument the ticket asked for is written, compiled and linked, and it is off unless asked for.** `LENA-MENUDRAW` (specced in `work/RACE/MENU-CAR-EVIDENCE.md` §4, absent from the tree until now) prints per indexed 3D draw: `zeroBase=yes/no` — *a draw the index-base switch cannot have changed, on whatever screen it is printed on* — plus `idx[0..5]` **as the backend actually received them**, and the same vertex bytes decoded **three ways**: float48, fixed48 (16.16), fixed32 (32-byte packed). Patch: `tools/patch_menudraw.py`. Binary: `work/MENU-CAR-FLATTENED/out-md/cmr2`, md5 `5b1a1902cf65e46a4c116eadf33221a3`. **`port/rhi/deck_dd7.o` and `PLAY/out-plain/cmr2` are untouched by me** (both 08:53, `d26a0923a98ebb25b6da8b664275f87`) — the binary other workers are measuring did not move under them.
* **Candidate C, with the arithmetic done rather than asserted.** The preview's converted vertices are **32-byte 16.16 fixed** (`Unk0x0082d220VertexFixed`, `GameInfo.cpp:1383`, built by `OptionPreview_AllocateConvertedWheelVertices`, `GameInfo.cpp:7727`) while the port's stride rule is `TLVERTEX ? 32 : 48` (`deck_dd7.cpp:1442`) and the mesh FVF `0x2d2` is 48. Read as IEEE float, `1.0000 -> 0x00010000 -> 9.18355e-41`, `4.0000 -> 3.67342e-40`, and **`-1.0000 -> 0xffff0000 -> nan`**: every coordinate within rounding of one point and every negative one NaN — flat, mangled, in one place. That is Miami's sentence with a number next to it, and one line of the new instrument separates it from a geometry or transform cause.
* **The GPU was not mine to take, and that is a measurement.** At 09:00 the card held a live `out-plain/cmr2` (pid 588344, 08:57:12) with a `/tmp/snapnow` trigger loop firing every ~11 s, and a second one (pid 595534) had replaced it; `gpu-guard.sh --foreign` answered `588344` — a game alive that no harness here started. Two `cmr2` on one card is what wedged the display at 07:25. I started no third, and did not touch `/tmp/snapnow` or `/tmp/trig.ppm.*`: they were the peer `MENU-CAR-EVIDENCE-VISION-r2`'s, mid-campaign. **The next window is theirs; the instrument above is what it should be spent on.**
* **No PNG of the menu car, and the reason is not that I forgot.** [CORRECTION 09:2x: the option screen *is* photographed — `work/RACE/out/owner1.02_t68.ppm`, `.03_t83.ppm`, `.04_t98.ppm`, 1280x800, pre-fix build, 07:20:40/07:20:56/07:21:12, option-menu camera — and the peer worker read them in their §11. What is true, and smaller, is that **no capture anywhere has a car in it**: those frames sit in the screen's zero-triangle window (§12), so they are 93.5 % one flat colour. I could not see them with the tools I had when I typed the original sentence.] The frames I could read myself are not it. `/tmp/trig.ppm.000-002` (the 08:57 session) are **95.5-96.1 % the frontend backdrop `(156,180,172)` with 96 distinct colours in the whole frame** — flat, no 3D in them; `/tmp/live1.ppm` is the opposite, **32,143 distinct colours**, dominant colour 0.317 % of frame, 165 of 960 grid cells over 255 distinct — a fully shaded full-screen 3D scene. Publishing either under the name "the menu car" would be worse than saying the picture does not exist.
* **Offered, not claimed, to whoever owns those sessions:** both logged `[MSGBOX] CMR2 File Load Error: Make sure the CMR2 CD is in the CD drive` 11 s after start and their census has **no `0x2d2 MESH` draw line at all** (`draws by FVF: 0x1c4 TL=18198`). I am not calling that a regression off two sessions; I am recording that the binary he plays is the one relinked at 08:53 and that this is what it did on two launches.
* **Not claimed:** [CORRECTION 09:2x: the setup screen has been reached and photographed — `owner1`…`owner5`, and the peer's §11 measures three of those frames; what *this* ticket has never had is a frame in which the car is drawn, which is a different and smaller thing. My original sentence here was wrong.] That the A/B is anything other than a race-frame A/B (it is), or that candidate C is proved (it is the leading survivor with its arithmetic done — the line that proves it has not been printed yet).


**CORRECTION, added 09:2x after reading the peer's `6bc88b1` — and it sharpens this block rather than weakening it.** The peer measured what actually happens on that screen, from the owner map in `out/owner1.log`: at frame **3600** the option screen's **9,628 draws put 207,801 triangles** on screen with **711/2560 cells owned by 8 textures**; from frame **4000** the *same* **9,628 draws put zero triangles** there, camera unchanged at `eye=(0.14 -0.09 -5.00)`. So the menu car is not missing and not mis-based — **it is submitted and rasterises nothing.** That is degenerate geometry (a point, a line, a plate) or a degenerate transform, not a wrong index array: a wrong base makes *wrong* triangles loudly (91 % of the frame, §3), and a misplaced transform makes *displaced* ones. It is the strongest argument yet that the index-base question is closed, and it is the reason `LENA-MENUDRAW` prints the **object-space** bbox per axis first: a car-sized object-space box with a tiny screen box is a transform; an object-space box that is itself a point or a plate is the vertices, i.e. the deform path (§4 family B, which is where the peer put it too). One run of `out-md/cmr2` with `LENA_MENUDRAW=1` on a frame in that window answers it.

Full round: **`docs/MENU-CAR-ROUND2.md`**. Patch and instructions: **`tools/patch_menudraw.py`**.

## 0k. THE WHITE CARD UNDER THE CAR — the port takes the colour from the MATERIAL, and the car's shadow only has one in its vertices. added 2026-10-11 08:5x EEST by the `WHITE-BOX-UNDER-CAR` worker; appended, nothing above or below it touched

**One line: on the 3D path the colour comes from the material, not from the vertex — `D3DRS_COLORVERTEX`(141) and `D3DRS_DIFFUSEMATERIALSOURCE`(145) are both DROPPED states and `a7_vk32.c:2623` hardcodes `flags.w = 0` — and the car's shadow is a draw whose colour *and* alpha live only in its vertices, with no texture by design.**

* **The specimen, counted per pixel.** `work/RACE/out/death/control4.ppm.3000` (current binary, md5 `97a9eb3b08595858a563282596680401`) has **exactly 2 distinct colours in 1,024,000 pixels**: `#9cb4ac` 99.62 % and `#ffffff` 0.38 %. The white is **one hard-edged quad**, interior uniformly 255/255/255, corners ≈ **(583,382) (630,388) (576,450) (523,441)** — i.e. opaque, not a 20 % blend, and not a gradient.
* **Why white is what comes out.** `out/ab/abfix.ppm.3590`, a frame the run's own log places in `A7VK_AB=notex` mode (`out/framing1.log:964`), is **1,024,000/1,024,000 px near-white, a single component, 100 % fill** — the whole frame. With textures out of the equation the 3D path emits white, because `base` is `b.matDiffuse` (`a7vk3d.vert`) and the game's single `SetMaterial` (`SetMaterial=1` in a whole 6 M-draw run, `out/death2.log`) left a white material there.
* **The draw that owns the defect.** `CMR2Decomp/CarPhysics.cpp:451` `CarPhysics_DrawBodyWheelAndSkidShadows` queues `Quad2D_QueueFixedTriangle(0, &v0, &v1, &v2, **NULL**, (Quad2D *)10)` (`:418`): **no texture**, vertex colour **black**, alpha 0x32…0xff. So there is no texture to bind and no blend to blame — every channel it has is in the vertex, and the vertex is not read.
* **The A/B is written, attempted twice, and VOID twice** (`card_probe` 08:37, `card2` 08:38: no `0x2d2 MESH` draw in either, i.e. the stage was never reached, so their frames cannot contain a car; the binary also moved under the second run, `97a9eb3b` -> `46ef5576` at 08:38). `tools/run_card.sh` now prints `NO STAGE -- ... the run is void for this ticket` by itself rather than letting a frontend frame be read as evidence. Nothing about the mechanism above depends on those runs; they are how the test failed, not what the finding rests on.

**The fix direction is one state.** `CMR2Decomp/Graphics.cpp:3520-3566` `Graphics_SetLightingMode`: mode 3 is the only mode that asks for `D3DMCS_COLOR1`; the port answers `D3D_OK` and drops both states. `run_card.sh` measures it with `A7VK_AB=vcol` — the switch is already in the shipped binary, so **no rebuild is needed**, and the prediction is stated before the fact in `WHITE-CARD.md` §4.
* **His eyes, in his words — the only review that counts.** Miami, 2026-10-11: *"textures were overall better tho"* — one driving session, on hardware, after the DXT5 blit fix. That is a person noticing, not a number, and it sits beside the texel-level evidence in §0g rather than replacing it.
* **Not claimed:** that the specimen quad *is* his white box (it is a frontend screen — 99.6 % backdrop — and whether it is the race car's shadow or the option-menu preview is what the A/B decides); and not claimed that `flags.w` explains all of "LIGHTING IS ALL FUCKED UP". `WHITE-CARD.md` §7 has the full list.

## 0i. THE CAMERA AND THE NEAR PLANE — the race camera is the game's own and is sane, `znear` cannot smear a frame, and the road's paint owns 12.3% of one. added 2026-07-11 07:5x EEST by the `work/RACE` worker; appended, nothing above or below it touched

**One line: the framing was not the fault — `znear` is 0.877–5.694 against a far plane of 200, and `w_clip = z_view` in this projection, so there is no `znear` term in NDC x or y at all; 100% of a race frame is stage geometry, and `RD_GA` (texId 102) owns 12.3% of one.**

Full write-up and the four frames: **`docs/CAMERA-AND-NEAR-PLANE.md`** and **`frames/`**. The
three numbers the line rests on:

* **Where the in-race camera comes from.** `Scene_SetViewFromCamera` (`SceneNode.cpp:2503`)
  inverts the camera **node's** world matrix into `D3DTRANSFORMSTATE_VIEW`; the near plane and
  the zoom are exported per frame out of the blended camera record by `View_BlendCameraStates`
  (`Car.cpp:8377`) into `View_SetPlayerProjection` (`FixedPoint.cpp:718`). There is no separate
  race camera path in the port — the race sets the same three transform states the frontend
  does, and the port latches all three.
* **The eye is 3–50 units above the ground.** An earlier note read the VIEW **translation row**
  as the camera position and got `y = −21.8`, i.e. under the ground. For a rigid row-vector view
  matrix `eye·R = −t`; corrected, that same frame's eye is **(83.18, 18.53, 598.47)** looking
  along `(0.994, 0.002, −0.113)`. The instrument now prints the eye directly.
* **A coverage number that clips.** `tu_note` caps near-plane straddlers at 100 screens and
  `gt2_note_cover` adds no area for any triangle not wholly inside NDC; neither clips. The new
  one (`A7VK_OWNER=1`, inert when unset) clips against the eye plane and the viewport, then
  z-buffers into a 64×40 grid keyed by texture id, resetting **every present**. Result: 100% of
  every race frame is 3D stage geometry; `RD_GA` 12.3% of frame 3150; `KEN_1A` 33.0%.

**Not claimed:** a legible road with verges, a car, a HUD or a timer. One class of attract shot
puts three parked-car panel textures across the whole frame at 6.9–10.1 units, which is what
"abstract mush with one edge" was; whether those cameras are the right cameras is not answered.

## 0h. NEITHER SIDE OWNED IT — the road textures ARE asked for and ARE bound; the port drew them from the wrong vertices. added 2026-10-11 06:0x EEST by the `work/RACE` worker; appended, nothing above or below it touched

**One line: the game asks for `RD_GA`/`MRG_KN*`/`MOU_TER4A`/`TER_421C` on every frame of
a race and the port binds exactly those textures — the fault is one line lower, in
`DeckDevice7::DrawIndexedPrimitiveVB`, which re-bases index arrays that `Mesh_BuildParts`
had already re-based; of 404,000 indexed draws with a non-zero base, 404,000 (100.00 %)
fit the game's convention and 0 fit the port's.**

Full write-up: `docs/ROAD-TEXTURE-OWNER.md`. Every number is from tonight's runs, **12 →
12 GPU ring timeouts in all seven**, a race reached in every one.

### The question, and the answer that is not (i) or (ii)

The round was handed: *of the 40+ Kenya track textures only `TER_KN4A` and `GR_001` are
ever bound in a race; every `RD_*`/`MR_*` has cov=0.0 and draws=0 — is that the game's
material selection, or a query the port answers wrongly?* The instrument that decides it
(`DECK_TEXREQ`, joined on the **surface pointer**) says:

```
RD_GA.DDS  slot 88 -> texId 102:   game asks 1288    port binds 1288    skip 0
                                   port draws 2000    port coverage 0.0 screens
```

**The game asks** — 1,288 requests for `RD_GA` in one window, `partsSlotNull=0`,
`oob=0`, and the mesh-level trace names the part tables (`[p0 slot=81 name='…TER_KN4A.DDS']`).
That rules out the c3d trailer index, the submesh split and the track's material table.
**The port answers correctly** — the surface the game hands to `SetTexture` is the
surface the port uploads and ids, and `a7vk_combo_set` keys its descriptor set on the
texId, so a draw samples its own texture. What the port then does with it is the bug:

```c
/* "D3D's indices are absolute into the vertex buffer" — they are not. */
idxScratch[i] = (uint16_t)(idx[i] - startVert);
...  v->data + (size_t)startVert*stride ...      /* the two cancel: startVert is lost */
```

`Mesh_BuildParts` (Mesh.cpp) already does `pData[k] -= minIndex` and
`Graphics_DrawMeshPartsByTexture` passes `startVert = vertexOffset + minIndex`, so the
array handed to the driver is already relative. Measured (`DECK_IDXTRACE=1`, one run):
`draws(startVert!=0)=404000  rawInRange=15969393/15969393  usedInRange=349174
relOk=404000 absOk=0`, with the giveaway line
`startVert=840 numVerts=116 numIdx=156 raw[0..115]` — indices that are *exactly* the
window they were handed for.

### The old cov=0.0 line was an instrument artefact, twice

`A7VK_TEXUSE` printed only the **top ten** ids by coverage (all ten taken by near-plane
blow-ups) and selected them by **`cov > 0.0`** — which hides a texture that was bound and
drawn 2,000 times and added no area. Two additive patches (`patch_texuse4/5.py`) lift
both filters; a third (`patch_texuse6.py`) reports *why* each draw added nothing.

### The fix, A/B'd in one build, and what it changed

`A7VK_IDXBASE=sub` restores the old path; the default is now the corrected one.

| | before | after |
|---|---|---|
| `RD_GA` (id 102) port coverage | 0.0 screens | **347,599.57 screens** (same 2,000 draws) |
| `MRG_KN1` / `MOU_TER4A` | 0.0 / 0.0 | 237,993.76 / 210,545.06 |
| frame at t=78, clear-colour pixels | 57.9 % | **0.0 %** |
| frame at t=78, distinct sampled colours | 817 | **2535** |

The road textures now own the largest coverage in the frame instead of none.

### What is deliberately not claimed

**The picture has not been checked against a reference.** What is measured is that the
road's draws project real area and the frame is no longer more than half clear-colour.
Whether the framing and the near plane are what a Kenya stage should look like is the
next question, and it needs a picture beside the numbers.

### Inertness, and his binary

`work/PLAY/out-plain/cmr2` = `work/RACE/out-texreq/cmr2` =
**`b960621bcc5657e135640e35aa70869f`** (previous, `e43d7a1e…`, kept as
`cmr2.bak-pre-idxbase-20261011`). With every new variable unset: **0 lines** from
`[TEXREQ]`, `[IDXTRACE]`, `[TEXUSE]` and `[SURF]`, stage still reached
(`0x2d2 MESH=417596`), no window left on his desktop, no stray process.

---

## 0g. THE PAINT IS FIXED. added 2026-10-11 04:3x EEST by the `work/RACE` worker; appended, nothing above or below it touched

**One line: every stage texture is DXT5 and the port was copying the *compressed
blocks* into a 32-bit texture as if they were pixels — `DeckSurface7::Blt`, reached
from `CGraphics::LoadDDSTexture`, did no format conversion, and a real DirectDraw
driver does exactly that conversion, so the fix is seven lines of port code and a
decoder — and with it the Kenya terrain renders in its own colour where it rendered
chromatic noise.**

Full write-up: `docs/DXT-COPY-PATH.md`. Every number below is from tonight's runs
`tx1`–`tx8`, **0 GPU ring timeouts, 12 → 12 unchanged in every run**, a stage
reached in every one.

**The copy path, named and joined end to end** (from the new `DECK_SURFTRACE`
FourCC report plus `DECK_FE_TRACE` naming the texture):

```
[TEX] DDS .\Game\Tracks\KENYA\KENlo.DDS 64x64 fcc=DXT5 ... linearSize=4096
[SURF] CREATE 64x64 caps=0x401808 ... FOURCC=0x35545844 (DXT5) linearSize=4096
[SURF] BLT dst=0x2ae9010(64x64 fcc=00000000 bpp=0) <- src=0x2cd18f0(fcc=35545844) srcbytes=6465000000000000
[SURF]  ST_UPLOAD 0x2ae9010 64x64 pitch=256 id=-1 wroteByGame=0
```

Those two pointer sets — the surface the game writes and the surface the RHI
uploads, which §0f could not reconcile — are the two ends of **one blit**. And
`srcbytes=6465…` is `a0=0x64, a1=0x65`, the first DXT5 block, read at blit time:
nothing had decoded anything. **All 181 stage DDS textures are DXT5** (`181 DXT5`,
zero of anything else); the frontend and the cars are **TGA**, decoded in software
by the game, which is exactly why only the stage was wrong.

**The off-disk control.** `KenLot.bfl` is 370 entries, every one `DDS ` magic,
64×64, **DXT5**, 128-byte header + 4096 block bytes — the arithmetic is
self-consistent, so the read was never the fault. Decoded, they are terrain:
`ter_kn4a.dds` mean RGB **(116, 89, 17)**, alpha **255 on 4096/4096 texels**. The
decoder was checked against **ffmpeg**: **alpha identical on 4096/4096 texels of
every file tested**, RGB to within 1 LSB, and both 1-LSB decisions were settled by
measurement (565→888 by bit replication; DXT5 uses the 4-colour interpolation even
when c0 ≤ c1 — on `kenlo.dds` block 62 ffmpeg's second colour is `(2A+B)/3 = 129`,
not the midpoint 160). And the dumped upload is reproduced from the file:
**`kenlo.dds` + the game's own row loop = 100.00 % of 4096 texels.**

**The alpha question had no second answer — it was the same fault in another
channel.** No blend state was touched and none was needed. Stage textures went from
mean alpha 75–154 of 255 and 18–85 % zero-alpha texels to **255 and 0.0 %**, and the
terrain's own texture decodes to alpha 255 everywhere. The remaining wash on the
frame is not a bug: it is the game's own dust.

**What paints the frame now, named** — a new instrument, coverage per bound texture
id (`A7VK_TEXUSE=1`), which existed because after the fix the frame is a *picture*
and colour statistics cannot say what is on it:

| texture | coverage | what it is |
|---|---|---|
| `TRACKTEX\PCLOW\TER_KN4A.DDS` | 1,689,012 | **the terrain** |
| `NEWIMAGE\DustCld\23_5\D_000..007.DDS` | 9,951–17,387 each | 8 dust clouds |
| `NEWIMAGE\skid\skids_blank.DDS` | 124,301 | skid marks |
| `KENYA\OBJECTS\PCLOW\BLD_30A.DDS` | 5,451 | a building |
| `NEWIMAGE\GRASS\GR_001.DDS` | 2,025 | grass |

**And the measurement that says the terrain is now painted with its own texture:**
the ground band of the race frame has mean colour **(115, 90, 15)**; the texture it
is drawn with is **(116, 89, 17)**. The same band before the fix was (142, 171, 159)
— noise. The whole frame went from 268,522 distinct colours in 385,323 pixels to
22,187 in 589,792.

**What is still wrong, and it is the next order — the road's own textures never
reach a draw.** Of the 40+ Kenya track textures loaded and uploaded, only
`TER_KN4A` and `GR_001` are ever bound in a race; every road texture —
`RD_K520B`, `RDKN_T1`, `RD_GA/GB/GC`, `MR_*` — is `cov=0.0, draws=0`, and **stage 1
is never bound at all** (`drawsBoth=0` for a whole run). Whether that is the game's
material selection or a selection query the port answers wrongly is not answered.

**A correction to the block below, because a document people trust must not carry a stale line without saying so.** §0f ends "still `b46d80fee5489834b87f843fd15484e0`, 66/66 game objects" — true at 02:14. It is now `e43d7a1e…`, and it is **not** 66/66 this round: `Graphics.cpp` is the one game source file changed and it carries a `DECK_FE_TRACE`-gated texture-name trace (additive prints, no logic, nothing written). `out/clean.log` measures them inert — 0 lines from every instrument with the env unset, stage still reached.

**Miami's binary has it:** `work/PLAY/out-plain/cmr2` is now
`e43d7a1e4279fe2c05647c7c053d4fd3`; the old `b46d80fee5489834b87f843fd15484e0` is
kept beside it as `cmr2.bak-pre-dxtblt-20261011`, one `mv` away from reverting.

---

## 0f. WHAT A RACE IS ACTUALLY ASKED TO DRAW — and what it drops. added 2026-10-11 02:2x EEST by the `work/RACE` worker; appended, nothing above or below it touched

**§0e said: a stage runs, the picture is not a road.** This block answers the
question that sentence left open — *what is the RHI being asked to draw during the
race loop, and what is it dropping* — and it narrows the fault from "the stage is
not drawn" to "the stage is drawn white, opaque, in the right place, and the
texture that would make it a road arrives non-image-like and half transparent".

Full write-up: `work/RACE/WHAT-IS-DRAWN.md` (on the Deck). Every number below is
from the game's own binary tonight, in runs `geo1`–`aw1`, **0 ring timeouts**.

**Asked to draw, per frame, frontend vs race** — frontend 2D draws 336 → **race 5**;
frontend 3D mesh draws **0** → **race 286**, 19,415 vertices, 5,358 fully-on-screen
triangles, **21 screens worth of triangle area**. The family that takes over is the
indexed T&L mesh path, and with it switched off at record time the frame is the
clear colour and nothing else (99.8–100 %): **the 3D path is the entire picture.**

**Two things fall out of a frame-scheduled A/B done inside ONE run** (four states of
the same moving scene ~1 s apart, so nothing is a run-to-run difference):

* **without its texture the geometry renders flat opaque WHITE over 32.5 % of the
  frame.** Geometry, transform, culling, rasterisation and compositing all work.
  The failure is not geometry.
* **every 3D draw in a race is submitted with `ALPHABLENDENABLE=1` and
  `ALPHATESTENABLE=1`** (all 34,327 draws in a 120-frame window), blend factors
  SRCALPHA/INVSRCALPHA, and 100 of the 286 per frame have ZWRITE off. The road is
  being drawn as a ~40 %-opaque wash, 21 screens of it per frame.

**Dropped, now with the values the game asked for** (the census printed counts
before, not values): `CLIPPING=1`, `COLORVERTEX=1`, `EMISSIVEMATERIALSOURCE=1`,
`TEXTUREFACTOR=0x75000000` (**new in the race**, unmapped), and
`TEXTURETRANSFORMFLAGS=0` = DISABLE — so projected texture coordinates are not in
play at all. One correction worth keeping: **`DIFFUSEMATERIALSOURCE=0` =
`D3DMCS_MATERIAL`, not COLOR1** — the port's hardcoded material colour source is
right, and the obvious-looking fix "use the vertex colour" would have been wrong.

**Where it now lives: the stage's textures.** Dumping every texture the RHI
uploads: the frontend's arrive 90–100 % self-similar (images, masks with alpha —
correct); the stage's arrive **0.3–2.1 % self-similar, ~25 % of texels one single
constant colour, mean alpha 75–154 of 255**. And the port is not lying about the
format — the game asks for 32-bit textures, gets pitch = 4·w, and writes densely
(13,004 of 16,384 bytes, all 64 rows). The surface the RHI **uploads from is not
the surface the game wrote**, so the copy between them is the next question.

**Three plausible hypotheses were killed by measurement rather than by argument,
and are recorded dead:** the composed W/V/P is correct (WORLD identity, VIEW rigid
and orthonormal, PROJ a textbook D3D perspective, printed as the game set them);
projective UVs are not in play; and nothing in the draw path is refused
(`refusedFvf=0`, `clamps=0`, `refused_by_backend=0` in every race census).

**Not moved:** the picture. `work/PLAY/out-plain/cmr2` and `out-race/cmr2` are
still `b46d80fee5489834b87f843fd15484e0`, 66/66 game objects, and the two
instrumented RHI objects in the tree are inert unless their env vars are set.

---

## 0e. A STAGE IS REACHED — the frontend hands off and the game loads and runs one. added 2026-10-11 00:1x EEST by the `work/RACE` worker; appended, nothing above it touched

**The wall every previous round hit is down, and it was two walls, one behind the
other. This block corrects the line "it does not yet draw a *track*, a *car you can
drive*, or a *menu you can click on*": the game now loads a stage off disk and runs
it. It still does not draw a road.**

**The crash was not the game.** `cmr2` hung the GPU's graphics ring ~30 s into every
run and the kernel reset the whole GPU, thirteen times on the 10th. Two lifetime
bugs in our own `rhi/a7_vk32.c` (a texture image freed with no device wait; the
frame's own command buffer re-recorded while in flight). 6 edits, measured A/B on
the **kernel log**: unpatched +1 reset per run, patched **0** in 95 s / 165 s runs
(`work/RACE/GPU-RESET-FINDING.md`). Since then: **0 ring timeouts across five
further runs tonight.**

**With that gone, the frontend walks itself to a stage.** No input beyond one
keypress to clear the legal notice: `FrontendMenu_UpdateMain` fires **30.5 s** after
the main menu is entered, builds the DEMO profile, switches the game to in-race
mode, and:

```
[STAGE] Race_LoadSelectedStage entered
[STAGE] stage file '.\\Game\\Tracks\\KENYA\\KENlot.bfl': didFileLoad=1 size=2400320
[STAGE] Race_LoadSelectedStage -> 1
```

That is the retail game's own stage loader returning 1 with a real stage file
(**Kenya, 2.4 MB**). The in-race machine then runs, and it is **live**: its race
loop advances `0 → 1063` updates in 44 s (~25 Hz), one car in the order, race flag
set, still advancing when the run was cut.

**And the draw picture flips completely at the handoff** (census every 300 frames,
`DECK_DD7_CENSUS=1`):

| phase | mesh-FVF `0x2d2` draws /frame | `DrawIndexedPrimitiveVB` /frame | triangles /frame | 2D TL /frame | ignoredStates /frame |
|---|---|---|---|---|---|
| frontend | **0** | 0 | 694 | 336 | 48 |
| **stage running** | **229 – 289** | **162 – 208** | **3 867 – 4 591** | **5** | **896 – 1 171** |

Whole-run mesh-FVF totals: **618,958 / 979,739 / 1,069,996** in three runs, against
**0** in every frontend-only run this project has taken, `refused_by_backend=0`.
The 3D path is driven by the game's own stage camera, every frame.

**The wall that remains, and its family.** What reaches the swapchain is the
backdrop colour with a large animated garbled region — no terrain. The number that
names it: **ignoredStates 48/frame → ~1,100/frame, 20×**, i.e. the dropped
render-state set (S2a: `COLORVERTEX`, the material sources, TSS
`TEXCOORDINDEX`/`TEXTURETRANSFORMFLAGS`/`MIPFILTER`/`MAXMIPLEVEL`) is now being fed
by the **stage** instead of only by the frontend. Same family as S2a. Not the GPU
family — that one is closed. Separately: the demo car sits in call state 8 (take
controls from the player) instead of 9 (attract-mode AI), so nothing drives it yet.

**Method, because it is the reusable part.** Game state cannot be inferred from a
draw count — "no mesh draw", "the key never arrived" and "the menu never moved" are
identical from outside. So this round put a gated trace **inside the game's own
code** (20 one-liners, `DECK_FE_TRACE=1`, no logic touched): frontend menu state,
every stage-lifecycle entry with `Race_LoadSelectedStage`'s return value, resource
mode changes, the in-race machine's state/level, every successful state promotion
with the value that caused it, and the race loop's own counters.
`work/RACE/patch_fetrace{,2,3}.py`, report `work/RACE/STAGE-REACHED.md`.

## 0c. S2 MEASURED — THE STATE TRACKER IS NOT THE MOUNTAIN. added 2026-10-10 19:0x EEST by the `seq-s2-first` worker; appended, nothing below it touched except the two §6 lines marked CORRECTION

**The phone's call was "S2 before P2". Agreed — and the measurement changes what
S2 *is*, which is the reason to say so before spending a week on it.**

I put a call census inside the port's own device (`rhi/deck_dd7.cpp`,
`DECK_DD7_CENSUS=1`) and ran **the game's own binary** (`work/S2/build/cmr2`,
i386, link exit 0). Two runs, 20 s and 28 s:

| | 20 s run | 28 s run |
|---|---|---|
| presented frames | 1,126 | 1,606 |
| draws / triangles | 77,287 / 159,414 | 205,714 / 426,806 |
| **distinct pipelines** | **1** (built=1, hit=1125) | **1** (built=1, hit=1606) |
| draws refused by the backend | **0** | **0** |
| draws through the mesh FVF `0x2d2` | **0** | **0** |
| mesh vertex buffers created | 206 (469,890 vertices) | same |
| **state calls answered `D3D_OK` and dropped** | **29,512** of 99,704 | — |

So: **the state tracker + pipeline cache that PORT-PLAN calls "the mountain"
already exists and works** — 1.33 M draws collapse to one pipeline because the
key is a 9-field struct snapshotted at draw time, which is the design working, not
a cache that never fired. What the game can reach today draws **only** FVF
`0x1c4` (screen-space TL); the 3D vertex buffers are built at load and **never
drawn through once**. The port plan's sentence "what draws today is the
frontend's path" is now a number.

**What is actually missing is state FIDELITY, and it is already leaking.**
`work/S2/d3d_census.py` (published as `tools/d3d_census.py`) compares every state
the game names against `map_rs`/`map_tss` in the device: **10 of 18 render states
and 10 of 19 texture-stage states are dropped** — `COLORVERTEX`,
`DIFFUSEMATERIALSOURCE` (+3 material sources), fog colour/start/end/table/vertex
mode, `NORMALIZENORMALS`, `LOCALVIEWER`, `TEXTUREFACTOR`; `TEXCOORDINDEX`,
`TEXTURETRANSFORMFLAGS`, `MIPFILTER`, `MAXMIPLEVEL`, the five `BUMPENV*`. That is
the lit-mesh path's whole vocabulary. For 2D it mostly costs nothing; for a car on
a stage it is the difference between shaded and flat.

**And the drop list is now measured rather than inferred.** The census names the
state, not just the total (20 s run): `136` CLIPPING **9,049** calls, `141`
COLORVERTEX and `145` DIFFUSEMATERIALSOURCE **4,525** each, plus the other
material sources, ANTIALIAS, TEXTUREPERSPECTIVE, FILLMODE, STIPPLEDALPHA,
COLORKEYENABLE, EXTENTS — and on the texture stages `t11` TEXCOORDINDEX, `t18`
MIPFILTER, `t20` MAXMIPLEVEL, `t24` TEXTURETRANSFORMFLAGS at **2,878** calls
each. That is the source list confirmed by a second method, at runtime, with
counts. Two entries in the source list (**fog colour/start/end, and the
`BUMPENV*` block**) do *not* fire on this path — fog sits behind
`Graphics_GetDeviceCaps90()`, bump-env behind a texture configuration this run
never enters. They are still gaps; they are not being hit yet, and saying which is
which is the difference between a list and a scare.

### The two census numbers settle like this — and the README was RIGHT

**278 and 298 are the same census at two scopes, not two answers.**

| scope | sites | methods | draws | state |
|---|---|---|---|---|
| `pD3D->` (the device) | **278** | 20 | 22 | **256** |
| `pD3D->` + `pDD->` (the D3D7 object) | **298** | 26 | 22 | **276** |

* The README's **278 / 20 / 256 / 22 is correct as published. Do not change it** —
  just keep the scope words beside it (`pD3D->`, the device the game draws
  through).
* **CORRECTION to §6 below:** "277 of 298" is `298 − 21`; there are **22** draws
  in that scope (it misses the one `pD3D->DrawIndexedPrimitive`). The line is
  **276 of 298**.
* **518 is not reproducible and I am not replacing it with a fourth definition.**
  Counted now: every `x->Method(` in the tree = **533**; a D3D7-method-whitelisted
  count = **400**. Quote 518 with its scope or drop it (§6 of `docs/PORT-PLAN.md`
  now says so).
* And the count is not comment text: blanking `//` and `/* */` first gives the
  same 278/20/298. A regex that stops at the first identifier gives 275 — it loses
  every call written `m_pTextureManager->pD3D->Method(...)`. That is how a census
  quietly stops meaning anything.

### The verdict on the "smaller first milestone"

Right instinct, wrong lever. **There is no pipeline-per-combination work to
hardcode** — one pipeline served 1.33 M draws, and the cache already generalises
what a hardcoded table would special-case. The blocker is not pipelines: it is
(a) the dropped states above and (b) **reaching a race at all**. I drove the game
from the attract loop with the pad (12 presses) and never saw a mesh draw, so a
"one real 3D frame" milestone has to start from *getting the game to a track*,
which is a game-state problem, not an RHI one. S2 therefore splits: **S2a = state
fidelity** (measurable today: `ignoredStates` → 0, printed per run) and **S2b =
reach a race** (where the picture actually is).

### Sequencing, and the P2 question

**Agreed: S2 before P2**, for the reason the phone gave — S2 is where the unknowns
were. They are now smaller than modelled, and P2 is now the bigger pile. But
**I did not start P2 in parallel, and I would not**: not for file conflicts (P2
touches 33 game files, S2 touches `rhi/`) but for the **object set**. P2 widens
headers, which invalidates every prebuilt object exactly as P3 did; the one
artifact that makes all of this measurable — a game binary that links (66/66,
link exit 0) — would go mixed-header under it. If P2 starts while an S2 evidence
run is live, it must run its own sweep directory and must not relink the game
binary until it lands. Then both lanes stay real.

**Not done, on purpose:** no dropped state was implemented this round (they get
implemented against the census, not against a screenshot), and no attempt to
finish the menu navigation. **One path correction, since every command in the reports above uses it:** the port
working tree is `~/lena/.lena_cmr2/` — with the `lena/` in it. Two older lines in this
file write it as `~/.lena_cmr2` and that path **does not exist**; a command copied
from them fails with "No such file or directory" and looks like the tree was deleted.
It is not: `ls ~/lena/.lena_cmr2/port/rhi/`.

Full evidence, raw logs and the two supporting fixes
(`a7_vk32.h` was missing `extern "C"`; the device's own `draws` counter only
counted one of the four draw entry points): `work/S2/README.md`.

## 0a. THE MIRRORED FLANK — CLOSED. added 2026-10-10 18:27 EEST — cited by *subject*, not by hash, because this repo is rebased onto `origin/main` under it: `git log --oneline --grep='flank mirroring'` finds it (it said 18:35 EEST here at first, later than the commit that carried it; corrected in the re-verification pass)

**Question, from the phone, and nobody else's queue:** in the 4-car frame and the
single 205 frame the decals on one flank read correctly and the lettering on the
other looks MIRRORED. Is that faithful to the original game, or is it a bug in our
texture binding?

**ANSWER: FAITHFUL. It is in the file, and the engine draws the file. Not a
binding bug. Closed — no fix, and a "fix" would be a regression.**

**This block, too, is appended by a worker who is not the author of the rest of
this file.** Everything below §0a is carried forward untouched. The one edit I
made outside this block: the path table above had lost its last row into the §0
heading; I completed that row with the install path I actually measured against
(`~/lena/.lena_cmr2/game`), which is all it was missing.

**Re-verified and corrected 2026-10-10 18:31 EEST by the second worker on this same
job** (the first pass committed and then ran out of steps; it left no checkpoint, so
this pass re-derived everything instead of trusting its notes). All of the commands
below were re-run on the Deck and the engine paragraphs were re-read in
`~/.lena_cmr2/upstream/CMR2Decomp`: `Game_DrawMeshTextureRuns` (`Game.cpp:2114`) binds
the file's own per-triangle texture and nothing else; `SetTexCoordIndex`
(`Graphics.cpp`) sets `D3DTSS_TEXTURETRANSFORMFLAGS, 0` on every path it takes.
**The verdict is unchanged — FAITHFUL, not a binding bug.** Three things in this block
were wrong and are marked `CORRECTION` inline: one over-claimed line about one-sided
textures, one row of the sample vertex table that was a mis-paired vertex, and the
header time. `tools/flank_mirror.py` grew a `BODIES` mode and a `PAIRS` dump so the
headline numbers now reproduce **verbatim** from the command list, which the earlier
list did not actually do.

Commits, if a hash is wanted: `git log --oneline --grep='flank mirroring'` gives the
two round-1 commits and `--grep='mirror-flank: re-verified'` the round-2 one. Hashes
moved twice while this block was being written (an earlier draft cited `49d45ad`,
which no branch points at now) because another session is pushing to `main` — hence
the subjects above. `git ls-remote origin refs/heads/main` is the check that a push
landed.

### The three questions the phone asked, answered in order

**1. Does the engine mirror a body panel?** No — and there is no code path that
could. `Game_DrawMeshTextureRuns` (CMR2 `0x0049c510`) walks the mesh's own
triangle list and, per triangle, binds
`*(int *)((BYTE *)pTri + 4 + pTri->field_0x2c * 4)` — the file's own texture
index — then `DrawIndexedPrimitiveVB(D3DPT_TRIANGLELIST, ...)`. The only
transform applied to the vertex data is the node's world matrix
(`SetTransform(D3DTRANSFORMSTATE_WORLD, pNode->worldF)`, `Game_DrawViewMaskNode`
`0x0049cad0`; `Graphics_DrawMeshLOD` `0x0049c940` is the wrapper). No UV
transform, no per-side texture selection, no mirror flag on a mesh.
The engine's *only* mirror is `StageObject_RebuildMirroredTiltMatrix`
(`0x00486910`), and reading its basis swap — `right' = forward`,
`forward' = -right`, `up' = up` — gives determinant **+1**: it is a 180° rotation
about the up axis, **not** a reflection, and it is used for view/camera records.
The car's own wheel nodes in the file are that same rotation
(`205a1N` nodes 1–4: `diag(-1,1,-1)`, translation ±0.717/±0.718 in z), which is
how a wheel is placed on the other side without flipping anything.

**2. Is the left flank a mirrored instance of the right?** No. Both flanks are
real, separately tessellated geometry in the same file, under identity scene
nodes. `205a1N`: the body parts span z ∈ [-0.88, +0.88] with triangles on both
sides (`08BodySim` 101 faces at z>0.3, 83 at z<-0.3; `08BodySim` has V=247, an
odd count — the two flanks are not copies). Every body part's node is the
identity matrix, so the mesh data *is* the world data for panels.

**3. Is there a distinct LEFT texture in the trailer?** No. Over the 259 `.c3d` in
the install, **192/205 files with flank triangles use the *same* body/livery
texture on both flanks** (measured: the texture with the most triangles is in both
the left-flank and right-flank index sets). Over the **23 `*a1N` exterior car
files — the set that carries a livery, and the set in the frames — it is 23/23**,
printed by `BODIES` below. The 43 files whose left/right *sets* differ do so by one
underside / glass / single-panel index that my `|Nz| > 0.75` threshold caught on
one side only — the `a1N` five are `ap5unddf` (underbody), `AAQGliDf`, `aesglod2`,
`ASIGlODf` (glass) and `afpintdf` (interior); the body texture is in both sets on
all 23 bodies.

**CORRECTION — this paragraph first said "0 files have a left-only body texture"
and "the body texture is in both sets on every one of them", and both halves of
that are wrong as written.** Measured corpus-wide now: **2 files put their
most-used texture on the LEFT flank only** (`esca5`, `escc5`) and **11 on the
RIGHT only** (`205a5`, `205c5`, `cora5`, `ma1a5`, `ma1c5`, `ma2a5`, `ma2c5`,
`ma3a5`, `ma3c5`, `mita5`, `mitc5`). They are not a counter-example, and the
reason is measurable: all 13 are **`*a5` / `*c5` cockpit-interior files** (their
parts are `20interior`, `27swheel`, `22wiperL`/`22wiperR`, `28gearhand`,
`41Speedo`, `30dash`), so their most-used texture is a dash / door-card texture
and the triangles my flank band catches in them are interior trim and glass, not
artwork. Restricted to the files that carry a livery — the 23 `*a1N`, which is all
the `BODIES` mode counts — it is **23/23 on both flanks, 0 one-sided**. So there
is nothing for our binding to have got wrong: there is no second texture to bind.

### What the data actually does, measured

Mirrored triangle pairs (`(x,y,-z)`, matched vertex by vertex) over the 23 body
meshes, comparing texture coordinates at the mirrored vertices:

```
flank triangle pairs with SAME u at the mirrored vertices : 2025   <-- the answer
flank triangle pairs with u complemented (u' = 1-u)      :    1
neither (different tessellation on the two flanks)       :  425
```

Per car, `seaa1N` is 90 / 1 / 13 and `205a1N` is 66 / 0 / 30 — and the pairs are exact, not approximate.
Three vertices of one `seaa1N` (`08BodySim`) front-wing triangle and their
mirror partners, copied out of `python3 tools/flank_mirror.py PAIRS seaa1N --xyz`
(the matcher requires each vertex to have a partner within 2e-3 on x, y and −z):

```
P=(-0.829,-0.267,+0.896)  uv=(0.297,0.063)      P'=(-0.829,-0.267,-0.896)  uv=(0.297,0.937)
P=(-0.368,-0.492,+0.835)  uv=(0.420,0.003)      P'=(-0.368,-0.492,-0.835)  uv=(0.420,0.997)
P=(-0.424,-0.268,+0.830)  uv=(0.405,0.063)      P'=(-0.424,-0.268,-0.830)  uv=(0.405,0.937)
```

`x` and `y` are identical and `z` changes sign, exactly; `u` is identical to three
decimals at every mirrored vertex (0.297/0.297, 0.420/0.420, 0.405/0.405); `v` is
the complement (0.063/0.937, 0.003/0.997).

**CORRECTION — the table that stood here had a mis-paired row.** Its second row
was `P=( 0.176, 0.033, -0.835)` against `P=( 0.021, 0.035, +0.835)`: `x` does not
match, so it is not a mirrored pair at all, and its `u` differs by 0.042 —
i.e. it was a vertex from the `neither` bucket sitting in a table meant to show
the same-`u` relation. Rows 1 and 3 of it were real, and had been rounded by hand
to the vertex `z` rather than the triangle centroid; the rows above are verbatim
tool output instead. **It never touched the counts** (2025 / 1 / 425), which come
from the tool, not from the table.

**The 1 complemented pair, named, because it was the last loose end.** The tool
prints its example now, and it is a wrap seam, not a mirrored island: `u=0.004`
against `u=0.997` on `seaa1N` `05BonCamDay`. Every one of the **4** such pairs in
the whole corpus (`seaa1N`, `seac1`, `seac3`, `audc1` — one each) sits on those
seams (`u=0.004` vs `0.997`, `u=0.000` vs `0.999`, `u=0.014` vs `0.989`: the same
texel reached from the other end of 0..1). **4 pairs out of 12,484, all of them
at the seam, 0 genuine `u' = 1-u` pairs.**
Same `x` ⇒ **same `u`** (0.727/0.727, 0.405/0.405), and `v` is the complement
(0.820/0.180, 0.809/0.191 — `v' = 1 - v` to three decimals). So the livery's
"along the car" coordinate runs the same way round the car on both flanks, and
the texture's two halves are vertical mirrors of each other (normalised
  cross-correlation on that car's body texture, `seaa1N` `ASCDBoDf`, band
  `u[0.40,0.76] v[0.79,0.88]` against `u[0.40,0.76] v[0.12,0.21]`: **0.845 for
  `A` vs `flipud(B)`**, **-0.152 for `A` vs `fliplr(B)`**).

**That correlation, re-measured through a tool in the re-verification pass,** so
it is no longer a number with no script behind it:

```
TEXDUMP=/tmp/q2tex <build>/cmr2deck seaa1N --game ~/.lena_cmr2
python3 tools/flank_art.py /tmp/q2tex        # <- new, stdlib only
  NCC(A, B (no flip)       ) = +0.218
  NCC(A, flipud(B)         ) = +0.816     <- the claim
  NCC(A, fliplr(B)         ) = -0.176     <- and the other half of it
  NCC(A, fliplr(flipud(B)) ) = -0.030
```

Same relation, coefficients a little different from the 0.845 / -0.152 first
written down: a different viewer build's decode of the same `.bfl` block (the
texture is 1024x1024, so a 93x369-pixel band pair), not a different finding.
`flipud` strongly positive and `fliplr` negative in both passes is the whole
claim, and the sign of `fliplr` is the load-bearing part.
**What that buys:** the `v' = 1-v` mapping therefore lands both flanks on the
same artwork, upright — and the only difference left is the horizontal sense.
**Viewed from outside, one flank is the horizontally mirrored image of the other.** That is what the phone saw, and it is
in the file.

Two more measurements that close the escape routes:

- **UV set 1 is UV set 0.** Every vertex of every part of `205a1N` (1,204
  vertices), `foca1N` (1,144) and `6r4a1N` (1,360), 14 parts each: `uv1 == uv0`
  exactly, 0 differing vertices. So there is no second UV set holding a "correct"
  mapping that the game uses and the viewer does not. (The engine does select the
  second set for texture stage 1 in blend case 9 — `SetTexCoordIndex(param1, 1)`
  in `ApplyTextureStageChange`, `0x004a4850` — but the set it selects is a
  byte-for-byte copy of set 0, so it cannot change a livery. Case 11's
  `TCI_CAMERASPACEREFLECTIONVECTOR | 1` is an environment map.)
  Provenance: this is the viewer's own `uv1 == uv0` check re-run over three cars
  and every part, not the engine's call sites; the call sites are read from the
  decomp.
- **Our own render agrees with the file.** Flat-lit flank views
  (`AMB=1 GAIN=0 FILL=0 SHADOW=0 BG=0 OFFW=2000 OFFH=1000 ELEV=0 DIST=0.35`,
  `YAW=0` and `180`, car `seaa1N`), OCR'd with `tesseract` (`afr` is the only
  traineddata on this Deck): a competition number reads as **`OS`** (conf 82) in
  the frame as rendered and as **`20`** (conf 94) only after a horizontal flip of
  the frame; the other flank's text needs no flip. And the decals themselves are
  stored reading normally in the texture — `seaa1N` `maxon` @(512,834), `MoviStar`
  @(739,226); `cora1N` `MoviStar` @(748,252) and @(769,870); `6r4a1N`
  `COMPUTERVISION` @(244,248); `foca1N` `Movista` @(196,455) — so the art is not
  pre-mirrored anywhere in the texture; the mirroring is the *mapping*, not the
  picture.

### The honest limit

The step from "the file mirrors one flank" to "the game mirrors one flank" is the
engine's draw path (above), and it is a reading of the decomp, not a picture. The
one measurement that would replace the argument with a photograph is running the
retail game itself on a car-viewer screen and looking at both sides — the install
is on this Deck and there is a launcher, but the port cannot draw a car yet (the
D3D7 state tracker is still the M5 gap, §5/§6) and I did not fire the original game
up for this. If that run ever contradicts this
block, the block is wrong, not the run. But the game has no per-side texture to
bind and no UV transform to apply, so I do not expect it to.

### Do not "fix" it

There is no local fix. A global u flip in the viewer would make the mirrored flank
read and break the flank that already reads. The mirroring is a property of the
shipped art: the left flank's islands are UV'd the same way round as the right's.
The correct action is to record it and stop looking at it.

**Reproduce, from this repo:**

```
python3 tools/flank_mirror.py PAIR seaa1N 205a1N     # the pair relation, per car
python3 tools/flank_mirror.py PAIRS seaa1N --xyz     # every matched pair, one line each
python3 tools/flank_mirror.py BODIES                 # 23 *a1N bodies: 2025 / 1 / 425
python3 tools/flank_mirror.py PAIR --all             # the pair relation, all 259 cars
python3 tools/flank_mirror.py CORPUS                 # 259 .c3d: textures + u direction
python3 tools/flank_art.py <TEXDUMP dir>              # the texture-side correlation
```

`tools/flank_mirror.py` (stdlib only, parses the container the same way
`cmr2deck.c` does) prints exactly the numbers above. Two of these commands were
added in the re-verification pass, and they are the ones that make the headline
counts exact:

- **`BODIES`** prints `body/livery texture used by BOTH flanks: 23 / 23`,
  `mirrored-pair triangles: same u 2025  u complemented 1  neither 425`,
  `du/dx L+: 1076 L-: 257 R+: 1055 R-: 309`, `cars whose two flanks run u the
  same way: 23 (opposite: 0)`. The **2025 / 1 / 425 is the sum over the 23 `a1N`
  files**, which is what the block means by "the 23 body meshes".
- The earlier command list labelled `PAIR --all` as "all 23 body meshes". That was
  wrong: `PAIR --all` is **all 259** cars, and sums to **10476 / 4 / 2004** —
  interiors included. Anyone who followed the old list and added it up would have
  got a number that contradicts this block. Corrected here.
- `CORPUS`: `du/dx sign over outer flank triangles L+: 5843 L-: 887 R+: 5948
  R-: 1114 / cars whose two flanks run u the same way: 181 (opposite: 11)` is the
  same finding from the other direction. The 11 "opposite" files are **all
  `*a5` / `*c5` cockpit interiors** — nine of them carry a single flank-band
  triangle on one side against 18 on the other, the other two are `6r4a5` /
  `6r4c5` (29/2 and 35/1) and `corc5` (1/12). (The block first described these as
  "1–3 flank triangles each", which is true of the one-sided texture files, not of
  these; the substantive claim — they are interiors, not bodies — was right.)


## 0b. THE FRONT DOOR — REVIEWED, ONE NUMBER FIXED. appended 2026-10-10 18:45 EEST

The phone rewrote `README.md` as a front door (commits `0e99687`, `dd05c98`, `412ab9e`:
front door, glossary, and the original README archived verbatim) and invited this side to
overwrite anything that misstates the work. Reviewed on the Deck against the tree, not
against memory. What re-ran, and what changed:

- **Re-ran — all reproduce.** `cmr2lab repack` against the install: **581/581
  byte-identical, 7.8 s**. Compile sweep: **33/66 on x86_64** (33 FAIL, every first error
  the pointer class, 1,504 error lines, **1,377 distinct `file:line` sites**) and **66/66 on
  i386 with `-Wno-c++11-narrowing`**. D3D7 regex: **278 sites / 20 methods**, 225 of them in
  `Graphics.cpp` (81%), **22 draws / 256 state**. `<windows.h>`: 45 files. `__asm`: 35
  blocks in 6 files (a 36th mention is inside a comment), every block inside `#ifdef
  _MSC_VER` with an `#else`. Install layout for the README's example path:
  `Game/Cars/205a1.bfl` → `unpack` gives **27 textures**.
- **One number was wrong: `2.26 GB`, now fixed.** It is not the install — it is the disc
  copies in `gamedata/`. Install **638 MB**, the 582 `.bfl` **417 MB**. (§6, resolved.)
- **"66 of 66 on i386" was only true with a flag the published harness did not pass.**
  Without `-Wno-c++11-narrowing`, `tools/sweep-compile.sh` reports **64/66** — `Game.cpp`
  and `GameInfo.cpp` fail on 32-bit `case` values above `INT_MAX`. The flag is now in the
  script with the reason, and PORT-PLAN §3 carries the caveat. The x86_64 count is
  unaffected (verified both ways).
- **One sentence was sharpened, not corrected.** The plain-words section read "The renderer
  is being rewritten. It draws a car ... onto your screen using a real Vulkan window",
  which a reader can take as *the game* drawing it. It now says on the first screen that the
  *data* is the game's and the *draw code* is this project's viewer, with `FRAME-NOTE.md` §2
  as the reference. Also fixed: "Nothing you type here can break your Deck" — not true of a
  terminal, only of the block below it.
- **Not touched:** the archived body (verbatim by design), the phone's other commits, the
  repo name, and the roadmap list itself — only item 4 gained a clause saying which part of
  it already exists (`FrontendMenus.cpp`).

## 0. THE FRAME MIAMI ASKED FOR — added 2026-10-10 15:15 EEST by the worker on
## the "make the port a pretty thing to look at" job.

**This block is APPENDED BY A DIFFERENT WORKER, at the top, on purpose.** The rest
of this file is carried forward from the 14:54 rewrite and I did not re-verify it.
Read §0 as mine, dated, and everything below as the previous worker's.

- **It is on GitHub, which is how the phone gets it.** `screenshots/cmr2deck-205a1N-1280x800.png`
  (one frame, 1280x800, 4x MSAA) and `screenshots/cmr2deck-205a1N-4views-1280x800.png`
  (four yaws, 640x400 each, stacked). Commit `66d32d1`, pushed 15:12.
- **`docs/FRAME-NOTE.md` is the honest note and it is the deliverable that matters.**
  It says line by line what came from the game's own code and what is mine. The
  one-line version: **the port does not draw this.** The *viewer* (`src/port/cmr2deck.c`)
  draws the game's *data* with our draw code, outside the game.
- **What changed, in one sentence:** the viewer now binds the texture each triangle
  names in the file (`MeshTriangle + 4`, `field_0x2c = 0`, the rule in
  `Game_DrawMeshTextureRuns` 0x0049c510) instead of matching part names against the
  texture table — and it uses the game's own alpha test (`ALPHAREF` 0x80/1,
  `D3DCMP_GREATER`) and blend pair (SRCALPHA/INVSRCALPHA). Before: every body panel
  was bound to texture 0, `AP5NWBDf`, mean RGB 17,17,19, which is why the car was a
  grey blob. After: 8 distinct textures over 27 runs, 0 runs refused.
- **Measured, not eyeballed** (`src/port/tools/preview.py --diff`, against a frame
  rendered with `NOCAR=1`): the car covers **28.8%** of a 1280x800 frame in 1089x509 px;
  its mean luminance is **76.6**; the culling direction is settled by measurement
  (`CULL=front` drops that to **28.8**, `CULL=back` ≈ `CULL=none`), so the faces kept
  are the outside ones.
- **Mine, labelled, and in the note:** the ambient value, both lights, the planar
  ground shadow, the backdrop, MSAA, the camera and the framing.
- **Biggest gap:** CORRECTION 2026-10-10 19:0x (§0c): the tracker **exists** and the
  count is **276 of 298** (298 − 22 draws). Measured, the backend served 1,334,903
  draws through **one** pipeline with 0 refusals. The port still cannot draw a car
  for a different reason: **the game never issues a mesh draw** — 206 mesh vertex
  buffers, 469,890 vertices, zero draws through them — and the states the lit mesh
  path sets (COLORVERTEX, DIFFUSEMATERIALSOURCE, fog, NORMALIZENORMALS…) are among
  the 10 render states the device answers `D3D_OK` and drops. This frame is the target image
  for M3 and the run-split/alpha/texture list above is the spec it has to reproduce.
- **The texture fix has a number, not an opinion.** `NAMETEX=1` renders the old
  name-matched path, so the two were diffed: car mean chroma **2.2 → 13.6**, mean
  luminance **23.1 → 72.7**, and 505 of 888 triangles moved off the wrong texture.
- **The path runs on all 259 cars**, not on the one I looked at:
  `docs/tables/texruns-sweep.tsv` + `src/port/tools/texruns_sweep.py` — 259/259
  completed, **0 cars with anything wrong**, 123,127 triangles, 3,873 runs, median
  15 runs per car, 0 runs refused. Slot roles are the same across four
  manufacturers and the dimensions land at 3.7–4.2 m by 1.4–1.5 m.
- **The textures in the frame are byte-exact against an independent decoder**:
  `tools/tex_verify.py` (Python, from the specs) vs the C viewer's own decode over
  the four cars in the pictures — `blocks compared: 108   mismatches: 0`.
- **Colour is not swapped** (the check that makes a render trustworthy): the car's
  mean colour in the frame matches that car's own body texture in channel order on
  all three cars tested, including the blue Impreza and the blue Metro 6R4.
- **The windowed path core-dumped and now does not** (`patch_swapfmt.py`: a Deck
  swapchain is `B8G8R8A8_UNORM`, not `R8G8B8A8_UNORM`, and SDL refuses a resolve
  across two formats). Verified: 120 frames in a real window, clean exit.
- **The frame is reproducible from the repo byte for byte**: replaying the five patch
  scripts over the pristine source, rebuilding and re-rendering gives the same md5
  (`91a8ad5135bf1171568b950f95d22598`) and 0 differing pixels.
- **Not claimed:** no human has looked at this frame. Miami is the first. And 258 of
  the 259 cars in the sweep have never been looked at at all — that sweep is counts.

---

## 0.5. t2 CLOSED, and the two source steps of §5 done — appended 2026-10-10 18:25 EEST

*Appended by the worker on job `t2-unblock-close` (from phone-Lena). This block is
mine and dated; §0 and everything below it is the previous workers', untouched
except where a correction is marked CORRECTED.*

**`t2` is closed.** `state/task_queue.json`, id `t2`: `blocked` → `done`, finished
2026-10-10T18:12:27, written under the daemon's own flock with a backup at
`state/task_queue.json.bak-pre-t2close-20261010-181227`. There is no `blocked` entry
left in the queue. The evidence is fresh, not quoted from a doc: from inside the
daemon's own process `DISPLAY=:0 WAYLAND_DISPLAY=wayland-0 SDL_VIDEODRIVER=unset
SDL_ASSERT=abort`, and the 2026-10-09 presenter re-run under it printed
`[ OK ] window+device+claim on driver=vulkan` … `PRESENTED 60 frames to a real
swapchain`, exit 0, no dialog, nothing left on his screen.

**P3 — the one line, and it was worth more than one line.** `LONG`/`ULONG` in
`platform/platform_types.h` were 8 bytes; they are now `int32_t`/`uint32_t`.
Measured against the i386 row as the reference: `POINT` 16→8, `RECT` 32→16, `SIZE`
16→8, `MSG` 48→40 (`hwnd` is a real 8-byte pointer, so 40 is right), and
`(LONG)(INT32_MAX+1)` wraps again. It unlocks **no** files by itself — 27/39 before
and after, same file list — and **it is an ABI change: 14 mangled symbols move**
(`Input.cpp` 12, `rhi/deck_dd7.o` 2), so every prebuilt object in the tree is
invalidated by it. That is the reason to do it now, while the tree is still small.

**P1.** The 7 pointer-bearing size asserts are re-expressed as
`sizeof(X) == (sizeof(void*) == 8 ? 0xNN : 0xNN)` — both oracles kept, nothing
deleted, the other 10 asserts untouched and re-verified as still passing. The
64-bit numbers come from clang's own record-layout dump, not from arithmetic.
**Sweep: 27 → 33 PASS, 39 → 33 FAIL, zero regressions**, and **every remaining
failure in the tree is now one class**: `cast from pointer to smaller type 'int'`
— 1,377 distinct sites across 33 files, led by `FrontendMenus.cpp` 305,
`FrontendScreens.cpp` 236, `GameInfo.cpp` 176, `StageObjects.cpp` 135.

**Verified against the port that actually runs, which is i386.** All 66 game
objects rebuilt against the new headers, `deck_dd7.o` rebuilt, platform 5/5, link
exit 0, and a 20-second windowed run compared with the pre-change binary:
**normalised logs byte-identical — 59 lines, empty diff.** The three message boxes
in that run ("Setting configuration to defaults", 2× "Make sure the CMR2 CD is in
the CD drive") appear in **both** binaries: pre-existing, GAME2-res's lane, not
caused here and not papered over.

Method, numbers, and the things deliberately left alone (`HRESULT`/`LPARAM` width;
P2 untouched): `work/P3/P3-P1-REPORT.md`. §5 items 2 and 3 are therefore done. What
is left is §5 item 1 (the pad lane) and **P2 — the only thing now between this tree
and 66/66.**

**ASK (sequencing, not a blocker).** P2 is 1,377 mechanical sites; S2 (the D3D7
state tracker) is the thing that stops the port drawing its own 3D. My plan says P2
then S2. If you want them swapped so the game looks right sooner, say so here and I
will swap — but I will not silently re-sequence my own plan.

## 1. RIGHT NOW

- **Daemon** `lena_daemon.py` pid **250660**, **2 workers**, model `deepseek-v4-flash`,
  uptime **5,400 s (~90 min)**, 400 steps per round. `state/status.json` was
  refreshed 14:37:39 — **6 s old** at the moment the relay published, so the loop is
  alive, not merely `active` under systemd.
- **Worker 1 = GAME2-res** ("Can't boot up to the native resolution on a steam
  deck"), claimed 14:29:08, **step 71** at 14:37:29. Working in `work/GAME2/r7`: it
  wrote a `mkconfig.py` to put a real `Configuration/GameInfo.rcf` where the game
  looks for it, rebuilt `outres/cmr2`, and is capturing frames
  (`R7_SNAPFRAMES=1200,1500:/tmp/final.ppm`).
- **Worker 2 = RELAY-VISIBILITY** (this page), claimed 14:34:47.
- **Queue:** 33 tasks — 18 `done`, 11 `partial`, **2 `running`**, 1 `pending`
  (`GAME2-r6-r3`, the auto-spawned continuation of the pad job), 1 `blocked` (§4).
  `state/task_queue.json`.
- **Relay:** last successful publish **14:37:25**, `first_fail: null`
  (`state/relay_health.json`). The outbox is **1,537 bytes** and now carries the
  work itself, not just the depth — §2.8.
- Load average **2.08** on 8 threads. Nothing is starved.

s — 17 `done`, 10 `partial`, **2 `running`** (those two),
  2 `pending`, 1 `blocked` (stale — §4). `state/task_queue.json`.
- **Relay:** systemd timer, 3-minute interval; last successful publish
  **14:25:19** (`state/relay_health.json`, `first_fail: null`).
- Load average 0.96 on 8 threads. Nothing is starved.

---

## 2. DONE — finished and verified

**1. Every `.bfl` container round-trips byte-identical.**
I re-ran this myself today at 14:17, from the *published* repo code, against the
retail install:

```
repack VERIFY: 581/581 byte-identical   (skipped 1 non-container)
exit 0 · 8.5 s wall (real 0m8.533s)
```

Raw output `/tmp/repack_verify.out`. The install holds 582 `.bfl` = 581 containers
+ 1 non-container, so the arithmetic closes. A modified container is therefore
structurally indistinguishable from something the game shipped.

**2. The geometry format closes exactly on every car.**
Re-ran today 14:18 through the reader in `tools/c3d.py`:
**259 / 259** car `.c3d` close on
`48 + Σ(count×stride) + TEXCOUNT×24 + TEXCOUNT×260 == filesize`,
**3,803** texture references, **zero** mismatches.

**3. The decompiled game compiles further than this repo says.**
My run, 14:19–14:20, published harness `tools/sweep-compile.sh`, one translation
unit at a time, real `.o` files, `-ferror-limit=0`:

| target | PASS | FAIL |
|---|---|---|
| `x86_64-linux-gnu` (the mandate) | **27 / 66** | 39 |
| `x86-linux-gnu` (i386 — kept as an oracle) | **64 / 66** | 2 |

Of the 39 x86_64 failures, **37 pass on i386** → blocked by pointer width and
nothing else. 2 fail on both (`Game.cpp`, `GameInfo.cpp`) and both are only
`-Wc++11-narrowing` on HRESULT literals; the local round-5 sweep passes
`-Wno-c++11-narrowing` and with that flag i386 is **66 / 66**. **Zero** files pass
on x86_64 and fail on i386, so the oracle still holds.

Error census (x86_64, *all* errors, all files): **1,561** —
1,504 `cast from pointer to smaller type` (1,449 of them to `int`),
56 size asserts over **7 distinct structs** (InputFeedbackStateSize 17,
InputDeviceStateSize 17, StageNodeTablesSize 14, PartStateSize 4,
StageArchiveSizeCheck 2, StageObjectDraw_size 1, CollisionBoxSize 1),
1 narrowing. **Zero undeclared identifiers, zero unknown types, zero incomplete
COM** — those three classes (365 errors when this was last published) are closed.

Evidence: `/tmp/sweep-verify-64/{results.txt,all_errors.txt}`,
`/tmp/sweep-verify-32/results.txt`.
**This repo is one measurement behind: README and `docs/PORT.md` still say 26/66
and 53/66.** Fixed in §5 step 2.

**4. The ported game boots, and its frontend answers the pad.**
Not "it compiles" — pixel-measured on a screen that does not move by itself
(noise floor **77 px**, bar **400 px**, counted *outside* a no-input mask):

| input | px outside mask |
|---|---|
| stick up/down, D-pad up/down, L2, R2 | 2,922 – 4,006 |
| A / START (Enter) | **7,118** |
| B / SELECT (Escape) | **7,118** |
| X, Y, L1, R1 | 0 (nothing, every screen tested) |

Six consecutive UP/DOWN presses, all above the bar, values moving:
2,922 / 3,055 / 4,006 / 4,012 / 2,985 / 2,922 — that is a selection walking a list.
Source: `work/DECKPAD/verify5-results.json` (each row carries pre/post sha1,
changed px, outside-mask px, bbox).

**And the test in the brief had to be retracted.** A raw before/after hash is *not*
valid on this build. I recomputed the no-input churn myself from the 134 raw
captures in `/tmp/recon`: with nobody touching anything and no input injected,
consecutive captures differ by **0 px on the still screens** and by
**30,388 – 32,880 px** while the attract loop animates. The "29,368 pixels for one
Down press" claim sits inside that distribution. It is not evidence; do not cite it.

**5. Analog input reaches the game in the game's own units.**
`lY = -59965` at full stick, `lZ(L2) = 56492` at 220/255; full scale `0x10000` is the
game's own `DIPROP_RANGE`, not a guess — injected 91.5% came out 91.5%. Values are
in `verify5-results.json` rows (`axis_values`).
*Provenance: measured by the pad lane; I read the JSON with my own eyes but did not
re-run the trace.*

**6. The engine reads joystick AXES as magnitudes (source).**
`Input.cpp:1577 CInput::ReadJoystick` writes raw magnitudes into
`bindings[0..7].field_0xc`; `StageObjects.cpp:12648` writes the car's
steer / throttle / brake as 0..0x3f scaled by |axis|. Throttle and brake
**default to the same axis** (axis 1) — the combined-pedal convention.
*Provenance: read out of the decomp and cross-checked against §2.5; the live-process
confirmation is the run in flig**8. The relay works end to end, and the outbox now carries the WORK, not the depth.**
I re-ran both suites after today's change, on this Deck, just now:
`state/relay_tests.sh` → **20 passed, 0 failed** (injection, locking, corrupt queue);
`state/relay_brief_tests.sh` → **22 passed, 0 failed** in the briefing section plus
**4 passed** in a new corrupt-queue section (all sandboxed to `/tmp` — they never
touch the live queue; a harness of mine leaked into the real queue once at 14:10 and
that is why the sandbox is asserted).

Live file, published 14:37:25, **1,537 bytes**:

| key | what it is now |
|---|---|
| `current` | id + first line (≤90 chars) + `running_for` + worker id, ≤3 entri**A. Deck controls (GAME2-r6 pad lane).** Round 2 (`GAME2-r6-r2`) ended
**partial** at 14:34:47 (67 steps, 1,328 s) and spawned **`GAME2-r6-r3`**, which is
`pending` as I write. Its live checkpoint is `work/GAME2-r6/CHECKPOINT.md`.
- **Round 2's headline result, in its own words:** it measured that the port already
  drives the *real* pad — `/dev/input/event10 'Microsoft X-Box 360 pad 0'`, live
  moving axis values — and read the game's own `DeviceInfo` out of `/proc/pid/mem`
  under gdb holding the same values (`lX=2097, lY=-851, lRx=-1966, lRy=4587`). It
  then found and fixed a **port** bug that had made analog impossible regardless of
  mapping: `deck_dinput.cpp`'s `prop_id()` returned the object's address, so every
  `RANGE` call returned `DIERR_UNSUPPORTED` and `controlCount` stayed 0. After the
  fix: all 8 axes answer `DI_OK`, and the game itself calls `SetProperty(RANGE)`
  ±0x10000 on each — inside an `if (controlCount > 0)`.
- **What round 2 did NOT show:** it did not re-run the masked-pixel move proof on the
  new binary ("show it MOVE with the actual pad" is *not* demonstrated by me on this
  build), and it did not confirm the post-fix read-back in game memory
  (`controlCount==8`, axis bindings 0/1/1). `m_controllerInfo` was still all zeros
  300 polls in, i.e. `RefreshControllerConfigurations` had not run — **that is the
  key unknown and it is what round 3 starts on.**
- Pad → frontend, latest measured state: **6 of 22** tested inputs register above the
  measured bar on the static screen; LEFT/RIGHT also register on other screens (both
  axes work; which one bites depends on the screen). **4 of 22 are clean negatives
  (X, Y, L1, R1) and are explained, not pending.**
- Analog **delivered**: done. Analog **consumed by the car**: **0 of 1** — the
  engine's throttle/brake axis (axis 1) is fed by nothing, because the port maps
  L2→axis 2 and R2→axis 5. The fix is port-layer (`axis1 = R2 − L2`), not written yet.

d shape
told the phone end: `next[].via` reported `hand` for a continuation the daemon
spawned itself; an empty `errors` said "nothing is wrong" while a job sat `blocked`
for 17 hours; an unreadable queue published as zero pending; and `active` from
systemd was the only health signal, which a wedged worker thread also produces.
Verified on the live wire, not only in the sandbox — the file published at 14:37:25
carries `via: "auto"` for `GAME2-r6-r3`, `blocked: [t2]`, `queue_readable: true`,
`daemon_age_s: 6`. Every number in §1 came from reading that file back.

n both the Python and the C probe.)

**8. The relay works end to end.**
Re-ran both suites today: `state/relay_tests.sh` → **20 passed, 0 failed**;
`state/relay_brief_tests.sh` → **16 passed, 0 failed** (sandboxed to `/tmp` — they
never touch the live queue). Live outbox published 14:25:19, **932 bytes**, carrying
`current` / `next` / `last_done` / `errors`.

**9. Nothing synthetic is left on his machine.**
`/proc/bus/input/devices` has **no `uinput` entry** and no leftover injected pad —
I checked at 14:18. The real nodes are there: Steam Deck Controller `event4`
(keyboard) / `event9` (mouse), and Steam Input's virtual pad
`Microsoft X-Box 360 pad 0` = `event10` / `js0`.

---

## 3. IN PROGRESS — with honest fractions

**A. Deck controls (GAME2-r6-r2) — running, step 63 / 400.**
- Pad → frontend: **6 of 22** tested inputs register above the measured bar on the
  static screen; LEFT/RIGHT also register on other screens (both axes work; which
  one bites depends on the screen). **4 of 22 are clean negatives (X, Y, L1, R1)
  and are explained, not pending.**
- Analog **delivered**: done. Analog **consumed by the car**: **0 of 1** — the
  engine's throttle/brake axis (axis 1) is fed by nothing, because the port maps
  L2→axis## 5. NEXT — the next three things, in order

1. **`GAME2-r6-r3`** — first in the queue, auto-spawned, and the pad lane's own next
   round. Its outstanding item is the one round 2 named: confirm the post-fix read-back
   in the live game (`controlCount==8`, axis bindings 0/1/1) and find out whether
   `RefreshControllerConfigurations` ever runs — if it never runs, the axis bindings
   still do not exist even with the ranges fixed. Then re-run the masked-pixel move
   proof on the new binary, and write the port-layer combined pedal axis
   (`axis1 = R2 − L2`) driven by a real analog trigger value. That converts "analog is
   delivered" into "analog is consumed".
2. **`GAME2-res`** — native resolution on the Deck panel, 1280×800, filling it with no
   letterboxing. Already running, worker 1 (§1).
3. **Then the repo's stale numbers and the source bug** — 27 / 64 (66 / 66 with the
   narrowing flag) replaces 26/66 and 53/66 in README and `docs/PORT.md`, with the
   exact command printed beside it, and `typedef long LONG` gets fixed (one line) and
   re-measured. And close `t2`, which is answered and still sitting in `blocked`.
isk
(§2.7). Nothing blocks it. **I did not edit the queue to close it** — status
changes there are the daemon's to make, and that file has already been corrupted
once by a test harness of mine.

**Genuinely blocked, with what specifically blocks each:**

- **37 files are blocked by pointer width alone** — mechanical `(int)` →
  `(intptr_t)`, ~1,449 sites, no thinking required. Plus 7 size asserts (56 sites),
  and one real bug: `platform/platform_types.h:29 typedef long LONG` is **8 bytes
  on LP64, and Win32 `LONG` is 4 bytes always**. It compiles fine and silently
  corrupts every struct holding a POINT / RECT / SIZE. Fix that line before
  trusting any layout.
- **ASAN does not build.** So **every number in this file about the port is
  compile-level**. I have no runtime evidence about the port's correctness and I
  will not imply otherwise.
- **I cannot press the physical thumb.** Pad input is injected through a
  `/dev/uinput` stand-in shaped like the real node (`event11` in that session);
  while Steam Input owns the pad, only Steam can write the real node. So "the pad
  works" means *everything downstream of the thumb is the game's own* — it does not
  mean a human thumb was used.
- **X / Y / L1 / R1 cannot work in the frontend, by the game's own design.** They
  map to DIK_SPACE / C / LBRACKET / RBRACKET, and `ReadKeyboardDevice`
  (`Input.cpp:1516`) translates exactly six keys into the 6-bit menu field. The pad
  sends them, the input layer accepts them, the frontend has no bit to put them in.
  Not a bug to patch — remapping them would change their gameplay meaning.
  **Decision for Miami, not for me.**
- **No human has looked at the game's window.** An external X11 grab of the root
  window is byte-identical with and without the game running (40 lit px,
  md5 `1cd11330e3` both ways), so every image here comes from the game's own
  readback path. *Provenance: the pad lane's measurement — I did not re-run it.*
- **The phone cannot drive this.** The relay has no shell: all it can do is append a
  queue entry, which is exactly as powerful as a job Miami types himself, and no
  more. One poll every 3 minutes, one direction per file, and the Deck never writes
  to the inbox.

---

## 5. NEXT — the next three things, in order

1. **Close the read that is running right now** (§1): get the game's own
   controller/axis table out of the live process, then write the port-layer combined
   pedal axis (`axis1 = R2 − L2`) and drive it with a real analog trigger value
   through the game's own default binding path. That converts "analog is delivered"
   into "analog is consumed".
2. **Fix the repo's numbers, then the source bug.** Re-publish the sweep table as
   27 / 64 (and 66 / 66 with the narrowing flag), plus the new error census, with
   the exact command printed beside it; fix `typedef long LONG` (one line) and
   re-measure. Delete 26/66 and 53/66 so nobody quotes them again.
3. **Then the queue's pending jobs in queue order** — RELAY-VISIBILITY step 2 is
   already built and tested (the outbox carries `current`/`next`/`last_done`/`errors`,
   §2.8), so it needs verification against the live queue rather than new code; then
   GAME2-res (native resolution on the Deck). And close `t2` as answered.

---

## 6. STILL NOT TRUE — read this one

- **The game is not ported.** What runs is the decompiled game booting to its
  **frontend**, drawing through the new SDL3/Vulkan layer. No race has been
  started, no car driven, no stage loaded. Nothing here is evidence about gameplay.
- **"It renders" is measured through the game's own readback, not a window.** No
  human has confirmed the picture. §4.
- **No pad input has ever come from a human thumb.** §4.
- **The brief's own headline measurement is invalid.** "29,368 changed pixels for one
  Down press" lies inside the no-input churn; I re-derived 30,388–32,880 px of churn
  with zero input from the raw captures myself (§2.4). Any future registration claim
  needs the no-input mask or it is unfalsifiable.
- **X / Y / L1 / R1 do not register in the frontend and cannot** (§4). If you read
  "every Deck control → the port's input path" as finished, it is four controls
  short, on purpose, pending a decision.
- **Analog steering and analog throttle are NOT live.** Analog values reach the
  game's joystick device and the engine has the code to read them as magnitudes, but
  **no axis carries them into the car** — and throttle/brake have no feeding axis at
  all right now.
- **The port has no working full backend.** CORRECTION 2026-10-10 19:0x (§0c): the
  call count is **276 of 298 state calls** (not 277 — there are 22 draw sites, not
  21), and **the state tracker that would service them DOES exist**
  (`rhi/deck_dd7.cpp` + the pipeline cache in `rhi/a7_vk32.c`): a 28 s run of the
  game's own binary made 1,334,903 draws through one pipeline, 0 refused.
  What draws today is the frontend's path, not the game's 3D pipeline — that half
  is now measured rather than asserted: **0 of 205,714 draws carried the mesh FVF.**
- **Every port number here is compile-level.** ASAN does not build. §4.
- **`2.26 GB` in the README does not match this install.** I measured the retail
  install myself: 908 files, **0.59 GB** by summed file size, 610 MB by `du`;
  the 582 `.bfl` are 0.39 GB. The container count is right (581 + 1 skipped); the
  size figure is not. Not resolved, so not claimed.
  >> RESOLVED 2026-10-10 18:45. Re-measured: install **638,124,559 B / 611 MiB (907
  files)**, the 582 `.bfl` **417,400,892 B**. The number's origin is now known: 702.8 MB
  (`cmr2.iso`) + 759.6 MB (`cmr2.zip`) + 807.1 MB (`Codemasters.bin`) = **2.269 GB** — three
  copies of the disc, not the game. `README.md` now publishes 417 MB / 638 MB, and
  `docs/README-ARCHIVE.md` carries an erratum because the bad figure sits in its verbatim
  body. Round-trip re-run the same minute: **581/581 byte-identical, 7.8 s.**
- **This repo's published port numbers are stale** — 26/66, 53/66, and "27 files
  blocked by pointer width" are one measurement behind; today's are 27 / 64
  (66 with the flag) and 37 files. Docs get fixed in §5 step 2, not before.
  >> CORRECTED 18:25 (2026-10-10): the LONG line is fixed and re-measured. The
  current x86_64 numbers are **33 PASS / 33 FAIL of 66**, all 33 failures being the
  pointer-cast class. See §0.5 and `work/P3/P3-P1-REPORT.md`.
- **The queue's status field is not a status report.** It says `partial` for ten jobs
  that are finished and `blocked` for one that is not. This file is the status
  report; trust it over the queue.
  >> CORRECTED 18:25 (2026-10-10): the **blocked** one is closed now; the
  partial-for-finished-jobs half is still true and still the daemon's file.
- **Three commits were sitting on this Deck unpushed** (the dependency-map work).
  They went up at 14:30 with the previous rewrite of this file — so if you read the
  repo before then, you did not see them.
- **`blocked: [t2]` on the wire is the queue's stale entry, not a real blocker.**
  The outbox is a faithful copy of a field that is wrong (§4). I did not fix the
  queue field; the daemon owns that file.
  >> CORRECTED 18:25 (2026-10-10): the queue field is fixed — **t2 is now done**.
  See §0.5. The wire will show it on the next relay tick.
- **The queue contains a duplicate id.** `GAME2-r5` appears **twice**, both `done`
  (a hand-typed INPUT job, and a later "GO HAM ON THE GAME"). It is harmless today
  because both halves are finished, but two consequences are real: `queue_total: 33`
  is 33 *entries*, 32 distinct jobs; and the relay skips any incoming command whose
  id already exists in the queue in **any** status, so a future command that happened
  to reuse `GAME2-r5` would be dropped silently. I did not rename or delete either
  entry — the daemon owns that file. Flagging it rather than fixing it.
- **`daemon_age_s` tells you the status file is fresh, not that work is advancing.**
  A worker stuck inside one long `gdb` run keeps `status.json` ticking. `running_for`
  growing with `last_done` frozen is the pair to watch.


## 0d. THE TUNING SEAM AND THE TWO CONTROLLER TIERS — added 2026-10-10 20:25 EEST by the `padtune` worker; appended, nothing above it touched

**The job.** Phone-Lena relayed Miami's controller-feel message: two tiers, EZ and
ADVANCED, both required, with his own constraint quoted in it — *"I don't want to make it too
confusing."* The brief was explicit that this is **not** a settings menu: it is the question
of whether the open input layer makes tuning possible or impossible, plus a status statement
for three parked items. Lane: `work/PADTUNE/`, checkpoint beside it.

### What was found, and it is the fact the design rests on

**The car adds no shaping of its own.** `StageObjects.cpp:12707-12718` reads the steering
axis and scales it linearly — `FixMulShift32(half, 0x3f0000)` — with no dead zone, no curve,
no saturation and no threshold; the throttle/brake path below it (`12728-12746`) is the same
shape. So every dead zone, curve and saturation the car will ever feel is applied on the way
out of the input layer or it does not exist in the program. Read from the decompilation, with
line numbers.

### What was built

`platform/deck_dinput.cpp`, one edit (md5 `51523520bc49f31d490eda8a7a0e52ad`; backup
`deck_dinput.cpp.bak-pre-padtune`, md5 `8adf8f0000ca563e069bc9366bc5e006` — the exact file
the INPUTGEN lane published, so there was no drift to reconcile). The seam was already two
functions wide and is now named as one: `axis_scaled()` for every analogue value, and
`deck_pedal_axis()` for the game's single combined pedal axis, which is literally
`axis_scaled(L2) - axis_scaled(R2)` — so per-trigger shaping reaches the pedal by construction.
`PadTune` + `pad_tune_ez()` + `pad_tune_for()` + the knob table + an integer response curve
(no `pow()`, no float: a float whose result depended on FPU flags would let two builds of the
same source disagree about the car's steering). Both builds compile, link exit 0.

### What was measured — EZ changes nothing, and a tuning screen cannot reach it

Synthetic Xbox 360 pad driving the real game binary, read back through the port's own trace at
a new `DECK_DIN_TRACE=4` (any change, not only changes over 0.4 % — without it a dead zone edge
cannot be resolved at all). The readback waits for the trace to go quiet; a fixed sleep read a
value one injection stale and that was caught and removed rather than reported.

| | |
|---|---|
| **EZ vs a reference build of the pre-seam source**, 18-point steering sweep | **identical, 18 of 18** |
| **EZ with every advanced knob set to something wild** | **identical, 18 of 18** — in EZ the code returns before it reads a knob |
| steering dead zone 30 % | zero to 2000, knee between 8000 and 9000 (30 % of travel is 9830 of 32767) |
| steering saturation 50 % | full lock at 20000 = half travel, dead flat after |
| left trigger dead zone 30 % | zero to 76, then 77 → 65 (30 % of 255 = 76.5) |
| the **right** trigger's dead zone knob, sweeping the **left** trigger | byte-identical to the untuned sweep |

The last pair is the per-trigger claim. **The canonical binary was deliberately NOT relinked**
— unlike last round, this change is opt-in by construction and EZ is bit-identical, so nothing
is broken by its absence and relinking would invalidate the binary S2 measured its census
against. The one line that does it is in the checkpoint.

### The three parked items — stated, NOT started

Same message. **No part of any of them was begun.** Two of the three (crowds, trees) were
already written into `docs/WHERE-THIS-IS-GOING.md` by the 19:57 doc commits — the brief's
trailer was true and *my local clone was behind*; I had re-derived that work before finding
out and it was thrown away rather than merged. The third was missing and is now in: the
overarching **"one GUI where you can choose the little bits and pieces"**, which is the port,
the modkit, the toggles and the installer converging into one product — and which confirms the
GUI installer is the **shape** of the project, not a wrapper on top of it.

1. **Crowds and spectators.** The art is a data job (container cracked, repack verified
   byte-identical). The *behaviour* he describes — running across the field, aware of the
   track, taking pictures, waving — is a real new subsystem: per-spectator state and a
   decision each. True 3D geometry replaces the billboard path. An **LOD question**, not a
   "make it all 3D" question.
2. **3D trees.** Same LOD answer: geometry near, impostors far. The billboards were a 2000
   budget decision, not a mistake.
3. **The overarching one** — *"from one GUI where you can choose the little bits and pieces."*
   That is the port, the modkit, the toggles and the installer converging into one product,
   and it confirms **the GUI installer is the shape of the project, not a wrapper on top of
   it.** It also raises the stakes on the two-tier split: if depth is compulsory that GUI is a
   wall of numbers, and if the default is correct the same GUI serves both people.

### And one thing that needs a decision, because a document people trust is now wrong

**`docs/CONTROLS.md` lost its decomp-sourced answers in commit `4fb2e27`** (2026-10-10 19:57,
"controller feel — EZ tier and advanced tier"): 200 lines out, 46 in. Gone with them are the
gear-up/gear-down answer read out of the string table and `Input.cpp:696`, the "there is no
clutch, neutral is a gear value" finding, the automatic-gearbox rule, and the combined-pedal
section. `git grep 'g_carButtonMasks' origin/main` now returns **nothing**.

The problem is not the trim, it is the contradiction it left behind: the rewritten page says
which button shifts up "has not been read yet", when it **had** been read, in that same file,
one commit earlier (`5651627`).

I did **not** revert her restructure — the page is its author's call and the restructure was
deliberate. I added a short marked block under *What is still undecided* carrying the three
answers and the citation, and pointing at `git show 5651627:docs/CONTROLS.md` for the full
section. **If the citations are wanted back inline it is one revert of one section.** Say the
word and it is done; flagging beats overruling.

### Not true, and it belongs here rather than in §2

- **No thumb has pressed the Deck's physical stick** — unchanged from §0c's neighbour, still
  the same limit.
- **No stage has been driven.** The curves are measured against the input layer, not against a
  car. This is why **EZ contains the game's own numbers**: there is no stage to measure a
  better dead zone on, and inventing one would be taste dressed up as engineering.
  `pad_tune_ez()` is the single place that changes when there is something to change it with.
- **No GUI was designed, and it was explicitly not the task.** What exists is the place a
  GUI's numbers would land.
- **Vibration is unimplemented and is NOT this seam.** It is the `IDirectInputEffect` path
  (`Input.cpp:1795`, `1953`, `GUID_ConstantForce`); the device answers `CreateEffect()` with
  `DIERR_UNSUPPORTED` on purpose.
- **The trigger path has three thresholds, not one** — the game's 2 % dead zone, a 4 % pedal
  gate and a 25 % key-mirror threshold. Collapsing them would change EZ, so they were made
  visible and nameable instead. Written up in `docs/CONTROLS.md`.

## 0e. THE MENU CAR IS NOT THE INDEX BASE — the hypothesis is dead, and it is dead by arithmetic. appended 2026-10-11 08:1x EEST by the `MENU-CAR-FLATTENED` worker; nothing above this block was touched

Miami's report was a car in the **pre-race setup menu** that "flattens into one place …
all mangled and jungled up into one flat piece of paper", and the phone's hypothesis was
that this screen goes through `DrawIndexedPrimitiveVB` with the **opposite** index
convention from the race, i.e. that the corrected base (commit `36bec65d`) broke it.

**It did not, and no call site wants the old base.** Measured, not argued:

* `DECK_IDXTRACE=1` over a whole frontend→stage→race run: **40,000 indexed draws with a
  non-zero base, `rawInRange = 100.00 %` (1,358,988/1,358,988 indices), `usedInRange = 0`,
  `relOk = 40,000`, `absOk = 0`, `neither = 0`.** The first indexed draws of the run —
  the first 3D the game draws after a 100 %-2D frontend — are already relative:
  `startVert=840 numVerts=116 raw[0..115]`, `startVert=1009 numVerts=60 raw[0..59]`.
* Both index sources in the game are relative to `startVert` by construction:
  `Mesh_BuildParts` rebases `pData` by `minIndex` and the draw passes
  `vertexOffset + minIndex` (`Graphics.cpp:7476`); the runs/batches paths pass the
  mesh-local `vertexIndex` with `vertexOffset` (`Graphics.cpp:7540`, `Game.cpp:2190`).
  The subtraction was a second re-base in **both**. `Mesh.h:19` says it in the game's own
  words: *"first vertex used (indices are relative to it)"*.
* A/B, one variable, same binary, same frame numbers (`A7VK_IDXBASE` unset vs `sub`):
  the 2D/menu frames move **1.6 %** of their pixels (mean 0.2/255, one box — animation);
  the stage frames move **90–99 %** (mean 31–49/255). `frames/race2600_idxbase-RAW.png`
  (920 kB) vs `…-SUB.png` (54 kB) is one frame number, one binary, one env var apart.

**So the corrected base stays the default and nothing in the menu path needs the old
one.** The order's "do not revert the whole fix" is satisfied by measurement: there is
nothing to scope, because the corrected path only changes draws that are *impossible* as
written and none exist.

**What I could not do, said plainly:** photograph the menu car on the current build. On
this build the attract route goes frontend → stage load → race without stopping at that
screen, and pressing Esc during the race did not reach it either; the runs that DO show it
(`owner1`…`owner6`, camera `eye=(0.14 -0.09 -5.00)`, 450/2560 cells, 8 textures, ~2,770
tris/frame) ran at ~25-31 fps where mine ran at ~56, and reproducing their env did not
reproduce the stop either, so what makes the route pause there is NOT established (an
earlier draft of this block blamed a second driver's key injection; `run_owner2.sh` counts
the scancodes those games saw and it is 2 -- one Enter -- so that attribution was wrong and
is struck here). The
screen's own numbers are in `docs/MENU-CAR.md` §3: **0 of 2,560 cells nearer than the near
plane** (the car sits 4.12–4.60 units away against `znear = 1.00`), so the race's
near-plane blow-up is not this screen's story either. `frames/menu-prerace_before-idxfix_23h09.png`
is what that screen looked like on the **pre-fix** binary — the eye-side half of the
question is still open, and it is named as open.

GPU ring timeouts 12 → 12 across nine runs; no window left on his desktop. **His binary:
I did not touch it, and it is no longer what it was when this round started** —
`work/PLAY/out-plain/cmr2` was `b960621bcc5657e135640e35aa70869f` at 07:23 and is
`97a9eb3b08595858a563282596680401` at 08:20 because the other worker's `out-death` round
relinked it. My A/B ran `out-owner/cmr2` (the current tree's instrumented build).

---

**2026-10-11 08:2x — the menu-car addendum: the arithmetic is airtight, and the round's own
numbers did not come from that screen.** (`MENU-CAR-EVIDENCE-VISION`, worker 2; evidence in
`docs/MENU-CAR-EVIDENCE.md`. No game run this round — the display-death ticket held the
GPU, and the phone ranks that one first.) Three things, all measured from bytes already on
disk:

* **The instrument never saw the screen the complaint is about.** The option-menu camera
  `eye=(0.14 -0.09 -5.00)` appears in `owner1`…`owner5` and in **none** of the runs that
  carried `DECK_IDXTRACE` (`mk_raw`, `mk_sub`, `mq_*`, `mp_sub`, `mcafter_sub`,
  `idxtrace_race`, `idxfix_race`). Those runs' whole camera set is the frontend
  `(-0.00 -0.00 -20.00)` and the race cameras. The 24 per-draw detail lines sit in one
  window at **frame ≈2400** (right after `Race_LoadStageGeometry` /
  `InRaceMenu_AdvanceCascade`), and the seven draw signatures that repeat from there are a
  car in a **race**, every frame to the end of the run.
  So "the pre-race / in-race menu car does NOT use the opposite convention" is
  **over-claimed**: what was measured is the leftover trace of a route that never entered
  that screen. (The quoted "40,000 draws" also matches no log here — the nearest is
  `idxtrace_race.log` at 404,000 — flagged as a transcription slip, not a change of result.)
* **The conclusion still holds, from the source and not from a sample.** All ten
  `DrawIndexedPrimitiveVB` calls in the game, in five functions, hand either mesh-local
  0-based indices with `startVert = vertexOffset`, or part-local indices already re-based by
  `minIndex` with `startVert = vertexOffset + minIndex`. The shipped default reads
  `startVert + idx` in both; `sub` reads `idx`. There is no call site that could want the
  old re-base — and the preview/setup car is not a separate path: it is a `Mesh` that
  `OptionPreview_RebuildDeformedGeometry` deforms per frame and re-uploads through
  `Mesh_Rebuild`, drawn by the same functions. What a wrong base *would* look like is
  exactly what the phone described (a neighbouring run of the same car buffer: car colours,
  car-sized place, shards) — which is why her colour observation does not discriminate, and
  why the arithmetic has to.
* **The A/B now has the control it lacked.** Two runs of the *same* convention differ by
  **1.61–1.67 %** of pixels; raw-vs-sub differs by **1.55–1.66 %**, in the *same* box
  `x[146..1084] y[186..551]`. So the "2D frames do not move" claim is confirmed rather than
  asserted — that box is an animated element, and at frame 2450, where the 3D is real, the
  same pair differs over **91 %** of the frame (mean 70/255). Her patch (~150 px, below
  vertical centre) is not that box; it is not in any capture this project holds.

**Text, answered from the draw path because she asked which:** fonts load on both screens
(`hel_*`, `lcd_*`, `ocr_*` TGAs, `mk_raw.log` 84–87 / 444–450), and
`Font_DrawText → Font_DrawChar → Sprite_Queue → Sprite_DrawLayer →
DrawPrimitive(D3DFVF_TLVERTEX)` is implemented end to end and used 1.66–1.87 M times per
run (`0x1c4 TL`). Glyph quads land on layers 1/2, the only layers `Sprite_Queue` has and
`Game.cpp:2667/2772-2778` draws every frame. Missing labels are therefore **not** a missing
path; whether they reach pixels needs the same capture the A/B needs.

**Next GPU window, in order:** (1) `LENA-MENUDRAW` — one line per indexed 3D draw with its
FVF, stride, `startVert`, first indices and the **screen-space bbox of the vertices it
actually read**, so the draw that owns a compact patch names itself in numbers; (2)
`run_menuhunt.sh` + `menu_hunt.py` (written, untested — no GPU) — the screen was reached
five times by runs that had foreign keys injected and never by the attract route, so a slow
key burst at the frontend, watched for the camera line, is the cheapest route to it.
Kernel ledger offered to the death ticket: no page fault, no `ring gfx_*` timeout and no
`MODE2 reset` since **07:31:56**; the two today are 07:25:40 (pid 498908) and 07:31:49
(pid 501251).

## 0f. THE OPTION SCREEN'S TEXT PATH WAS A `ud2`, AND ITS 3D SUBMITS DRAWS THAT RASTERISE NOTHING — appended 2026-10-11 09:1x EEST by the `MENU-CAR-EVIDENCE-VISION` worker (round 2); nothing above this block was touched

Round 1 of this task appended §0e-adjacent material and `docs/MENU-CAR-EVIDENCE.md`. Round 2
appends §10–§16 to **that same file** and hands the phone
`docs/NOTE-to-phone-MENU-CAR-EVIDENCE-2.md`. Two findings, both measured:

**1. The option/setup screen's text placement was fatal in every build until 08:53.**
`OptionMenu_TransformHudPointToScreen` (CMR2 `0x00503b70`, `GameInfo.cpp:6068`) was declared
`int` and never returned a value, so clang's `ud2` executed on **every** call. Both call
sites (`RallyData.cpp:7210`, `:7237`) are inside the option menu's label loop and the
coordinates they write go straight into `OptionMenu_DrawTransitionTextShortCoords(…,
GetTextString(0xfe), …)`. The last two SIGILL coredumps are **08:40:03, both from
`work/PLAY/out-plain/cmr2`** — his own play binary. The `int`→`void` fix landed 08:53
(md5 `d26a09231a98ebb25b6da8b664275f87`). Her photos are timestamped 07:35, i.e. **78 minutes
before the fix**, so her "no menu text" observation is not a moiré artefact of the photo —
on that build the screen's text placement could not run without killing the game. It is
still a *candidate*, not a proof: a local pre-fix capture of a menu screen
(`out/owner1.02_t68.ppm`) does contain glyph strokes (1-px-wide vertical runs, 17 px tall).
One run on the current build decides it.

**2. On that same screen the 3D submits 9,628 draws and rasterises ZERO triangles.** From
`out/owner1.log`'s owner map, camera `eye=(0.14 -0.09 -5.00)` throughout: frame 3200 =
711/2560 cells / 6,757 draws / **489,067 tris**; frame 3600 = 711/2560 / 9,628 draws /
**207,801 tris**; frames **4000, 4800, 5800… = 0/2560 cells / 9,628 draws / 0 tris**, `0 tris
behind eye`. Three 1280×800 captures inside that window (frames 3996/4883/5798) are
**93.455 % a single flat colour `(140,149,158)` — 956,980 px, to the pixel in all three —
with no car in the frame at all.** Geometry submitted and rasterising nothing is what
degenerate geometry looks like, and its near-degenerate form is jagged fragments compressed
into a small area still wearing the mesh's own paint — which is her picture. That moves the
lead to the per-frame deform path (`OptionPreview_RebuildDeformedGeometry`,
`GameInfo.cpp:8147`; `CarDamage_ApplyCameraSpaceMeshDent`, `StageTiming.cpp:5340`;
`Mesh_Rebuild`, `Mesh.cpp:103`). No bug is claimed in that code from a read — the instrument
proves it, not a paragraph.

**No GPU run in this round.** Miami held the box both rounds (verified foreign, not assumed:
`sh gpu-guard.sh --list` → `FOREIGN cmr2 /home/deck/lena/work/PLAY/out-plain/cmr2`). New
tools: `tools/shard_bbox.py`, `tools/shards.py`, `tools/region_map.py` — read a capture's
content, per exact colour, without a GUI. `A7VK_IDXBASE` was verified present in the live
binary after worker 1's 08:53 rebuild, so the phone's discriminating A/B still exists.

**Correction appended to the block above (~09:2x, same worker).** §12 of
`docs/MENU-CAR-EVIDENCE.md` pointed at the deform path (family B) for the zero-triangle
measurement. A peer round landed at 09:03 with **candidate C** done in arithmetic — the
preview's 32-byte 16.16 fixed vertices read at the 48-byte float stride, so every coordinate
is a denormal and `-1.0` is NaN — and **C predicts the same measurement at least as well**.
New §12a corrects it, and her own colour report is the discriminator: colour sits at offset
`0x18` in both layouts, so C gives **right paint, destroyed positions**, which is her
sentence. B survives; A and D are dead on that screen. The separating field (`fixed32` vs
`fixed48`) is already in `tools/patch_menudraw.py`.

## 0g. THE MENU CAR'S OWN DRAWS, MEASURED ON THE OPTION SCREEN AT LAST — the index base is not it, and the geometry does not move. appended 2026-10-11 09:3x EEST by the `MENU-CAR-FLATTENED` worker (round 3); nothing above this block was touched

> The ticket's own hypothesis, answered on the screen it was written about. Round 1 argued it
> from ten call sites, §0f (the peer's) from the census. This round put the instrument on the
> option screen itself: **one run, 10,500 indexed 3D draws of the menu car, every one of them
> `zeroBase=no idxInRange=yes`.**

**How it was taken.** `work/MENU-CAR-FLATTENED/out-md2/cmr2`, md5 **`cfd9cb7980dff26a5e56649467845432`**
(the game plus `LENA-MENUDRAW`, built from the current `port/rhi/deck_dd7.cpp` with the RHI's own
`build32_dd7.sh` recipe; `port/rhi/deck_dd7.o` and `PLAY/out-plain/cmr2` were **not** touched).
`LENA_MENUDRAW=1 LENA_MENUDRAW_MAX=1500 LENA_MENUDRAW_AT=/tmp/mdnow` — a new **file-triggered
burst** (`work/MENU-CAR-FLATTENED/patch_mdburst.py`) that fires when a driver touches
`/tmp/mdnow`, because the old sampling (first N draws of the run) cannot be aimed at a car that
is a few hundred frames of a 6,000-frame run. Driver `md_drive.py` reached the option camera at
**t=132.4 s**, then fired **7 bursts** and took 7 captures and touched nothing of the peer's.
Log: `work/MENU-CAR-FLATTENED/out/md_raw.log` (7.0 MB, 42,007 `[MENUDRAW]` lines).
Ring timeouts `gfx_0.0.0` before **12**, after **12**.

**1. ABSOLUTE OR RELATIVE — measured, not inferred: relative, all of them.**

| what | value |
|---|---|
| indexed 3D draws parsed | **10,500** — `fvf=0x2d2 stride=48` on every one |
| `zeroBase` | **no × 10,500** — startVert≠0 on every one (7 distinct: 1532, 1648, 1657, 1669, 1685, 1701, 1713) |
| `idxInRange` | **yes × 10,500** — every index the backend received is inside `[0,numVerts)` |
| `OUT OF RANGE` lines | **0** |
| indices as the backend received them | e.g. `idx[0..5]=2,1,0,1,2,3` — part-local, needing `+startVert` |

The ticket's hypothesis needs the menu car to hand **absolute** indices. It does not: it hands
part-local ones, so the corrected default (`startVert + idx`) reads the vertex the game built,
and the old `sub` re-base would subtract `startVert` a second time on **every one of these 10,500
draws**. The menu car uses the **same convention as the race path**, and it is the same
convention 10,500 times over with zero exceptions. **Item 3 therefore needs no scoping — the
fix is right for both paths, and this is now a measurement rather than a good argument.**

**2. WHAT MOVED: nothing, between bursts.** Every part's object-space box is **identical in all 7
bursts** (8-second spacing across a held screen) — 1 distinct box per part over the whole run.
If the screen's per-frame deform (`OptionPreview_RebuildDeformedGeometry` → `Mesh_Rebuild`) were
crushing the car, its box would walk or collapse across the bursts. It does not move at all, so
**candidate B is dead as the explanation of this screen** and the fault is static.

**3. The 7 parts, object space, as the draws read them** (`parts.py`):

| startVert | verts | idx | box (float decode of the bytes the draw read) |
|---|---|---|---|
| 1532 | 116 | 156 | x[-80..80] y[42.18..100] z[-80..80] |
| 1648 | 9 | 24 | **x[-100..100] y[0..0] z[-100..100]** — flat plate at y=0 |
| 1657 | 4 | 6 | **x[-100..100] y[0..0] z[-100..100]** — flat quad at y=0 |
| 1669 | 32 | 24 | x[-80..80] y[13.98..79.66] z[-80..80] |
| 1685 | 16 | 24 | x[-80..80] y[13.98..79.66] z[-80..80] |
| 1701 | 60 | 36 | x[-80..80] y[0..65.57] z[-80..80] |
| 1713 | — | — | (same family; see the log) |

`nonfinite=0` on every decode, so this is not a NaN collapse, and the 16.16 re-read of the same
bytes (`fixed48`) is *not* car-shaped either — the bytes are what a 48-byte float record should
be. Every part is centred at **x=0, z=0** with y centres in {0, 32.785, 46.82, 71.09}, and two
of the seven are **exactly flat** (all vertices at y=0). Whether that is a car seen from an angle
the boxes cannot describe, or a car that was never assembled, is the one thing these numbers do
**not** settle — see §4.

**4. THE HALF THAT IS STILL MISSING, SAID PLAINLY.** The instrument prints **object space**. It
cannot tell "the vertices are a car and the transform is wrong" from "the vertices are not a
car". That is exactly the split the ticket's families A/D vs B/C name, and it needs the
**device-space** box of the same draws, which `A7VK_GEOTRACE` already computes
(`a7_vk32.c:1926`, `gt_note_3d`: dmin/dmax in device space, `anyin`/`anyw`/`nvis`, plus the three
matrices). A run with both instruments on the same screen is **in flight as this is written**
(`work/MENU-CAR-FLATTENED/wait_sub2.out`) — with `A7VK_IDXBASE=sub` as well, which is the A/B's
missing half: **the first two attempts at `sub` never reached the option screen** (30 keys, 0
captures, 0 bursts, `out/md_sub.hunt`), so the A/B is *predicted per draw* by `zeroBase=no` and
the index arithmetic, and **not yet photographed**. It is not claimed.

**5. THE CAPTURES SHOW THE CAR ABSENT, AND THAT MATCHES §0f.** Seven 1280×800 captures of that
screen (`work/MENU-CAR-FLATTENED/frames/md_raw.00N.ppm`): 31k–33k distinct colours, but sampled
over 49,105 px only **0.75 % have a horizontal gradient > 60**, and those sit in the bottom HUD
band (rows 600–799) and rows 0–199 — **rows 200–599 are edge-free**: a dithered sky/ground
gradient with no object in it. The owner map on the same frames reads
**`0/2560 cells owned (0.0 % of the frame) by 0 textures | 0 tris drawn`** *while the instrument
is printing 7 mesh parts per frame*. Submitted, and covering nothing. One PNG is in `frames/`
under a name that says what it is.

**6. A CORRECTION TO §0f'S READING OF `owner1.log`, with the numbers.** In `owner1.log` the
census method counter reads `DrawIndexedPrimitiveVB=9628` at the frame-3600 census and **still
9628** at the 4800 and 5800 censuses, while the option camera stays up throughout. So the game
made **zero** indexed 3D draws after ~3600 on that screen: the "9,628 draws put zero triangles"
line describes a screen where nothing is submitted at all, not 9,628 draws that rasterise
nothing. (The owner map's own draw column is that same cumulative counter — its "tris" column is
the per-frame one.) My run is the opposite case and it is the informative one: there the car *is*
submitted, 7 parts per frame, 10,500 draws, and the frame still has no car in it.

## 0h. THE A/B, ON THE OPTION SCREEN AT LAST — the switch is not inert there, and the old re-base kills the car. appended 2026-10-11 09:5x EEST by the `MENU-CAR-FLATTENED` worker; nothing above was touched

> §0g measured the shipped default on that screen. This is the other half: same binary, same
> screen, same route, **one env var apart**, `A7VK_IDXBASE=sub` (the pre-fix re-base).

**The A/B pair, both runs on the option camera `eye=(0.14 -0.09 -5.00)`:**

| | shipped default (`out/md_raw.log`) | `A7VK_IDXBASE=sub` (`out/md_sub4.log`) |
|---|---|---|
| indexed 3D draws recorded | 10,500 | 22,500 |
| `zeroBase` | no × 10,500 | no × 22,500 |
| **`idxInRange`** | **yes × 10,500** | **NO × 22,500** |
| indices as the backend received them | `2,1,0,1,2,3` | **`64650,64649,64648,64649,64650,64651`** |
| option-camera coverage of the frame (owner map) | **599 / 591 / 450 cells = 23.4 / 23.1 / 17.6 %** (3 of 16 dumps) | **0/2560 cells in 21 dumps**, at most 28/2560 = **1.1 %** |
| the captures | 31k distinct colours, dithered sky/ground, no car (`md_raw.00N.ppm`) | **100 % one colour in 14 of 15 captures** (`md_sub4.00N.ppm`) |

**The arithmetic that explains the index column, on the measured draws.** `sub` hands the backend
`idx[i] - startVert`; with part-local indices (2,1,0) and `startVert=888` the subtraction
underflows a `uint16` to **64650** — computed for all 10,500 draws of the default run, **100 %
of them** land outside `[0,numVerts)` and past the end of the 2000-vertex vertex buffer
(`work/MENU-CAR-FLATTENED/ab_predict.txt`). The run above then did it for real.

**What this settles, in the ticket's own terms:** the index-base switch is **not inert on this
screen** — every one of the menu car's draws has `startVert != 0`, so the switch reaches all of
them — and the old re-base is **catastrophically wrong for the menu car**, exactly as it was for
the race path. The corrected default is right for both, so **no scoping is needed and the fix
must not be reverted**. Second PNG pushed: `frames/opt-preview-camera_20261011-0948_IDXBASE-sub_FLAT.png`
(md5 `d8238905f8365730731d52d228077cc6`) — the `sub` screen, one flat colour, for the phone to
hold next to the default's.

**What it does NOT settle, said plainly: neither half is a picture of a mangled car.** The
default run's frame has no car *in* it; the `sub` run's frame is empty. The defect the ticket was
written about — a car that renders as "one flat piece of paper" — is therefore **still
unexplained**, and §0g's two findings are why: the geometry does not move between bursts, and
the object-space boxes of the parts the draws read are not car-shaped to begin with. The next
instrument is named in §0g item 4 and in `work/MENU-CAR-FLATTENED/CHECKPOINT.md` §15: the
**6,258 mesh draws in the same log that are NOT indexed** (`DrawIndexedPrimitiveVB=45705` vs
`0x2d2 MESH=51963`) and **`A7VK_GEOTRACE`'s device-space box** for the draw that has one.

## 0i. THE OPTION-PREVIEW CAR'S OWN DRAWS, MEASURED — the index base is not what breaks it. appended 2026-10-11 10:3x EEST by the `MENU-CAR-FLATTENED` worker; nothing above was touched

> §0g and §0h measured the option screen with the owner map and the A/B, but **no run had ever
> printed the menu car's own per-draw numbers**: the burst armed ~5 s late every time, because my
> round-3 driver re-read the whole 17 MB log on every 0.5 s poll. This round the driver reads the
> log incrementally and the sampling runs from draw #1 — the option-preview car *is* the first
> indexed 3D content of the run (`[GEO]`: zero 3D draws at every sample up to f=3360, 1,836 at
> f=3480, car-shaped object box), so no window has to be hit to measure it.

**1. The car's draws are part-local, in range, 48-byte float — on the shipped default.**
`out/md_car_raw.log`, 3,012 instrumented `DrawIndexedPrimitiveVB` draws of the car page:

| | value |
|---|---|
| stride | 48 on every draw; `fvf=0x2d2` |
| `idxInRange` | **yes × 3,012, NO × 0** |
| indices as the backend received them | `2,1,0,3,2,0` … largest index anywhere **44** |
| `startVert` | 0 on 336 draws, ≠0 on **2,676** — so the switch reaches 89 % of the car's draws |
| vertex decode | `float48 x[-0.3265..0.3265] y[-0.3265..0.3265] z[-0.1405..0.1405]` — part-sized. The `fixed48`/`fixed32` lines are the **same bits** ×65536 (`-0.3265` → `-16880`), i.e. the data is IEEE float at 48-byte stride and candidate C (16.16-fixed-read-as-float) is dead for the car |

**The ticket's hypothesis is dead on the car itself, measured, not inferred.** `A7VK_IDXBASE=sub`
would subtract `startVert` from every one of those 2,676 draws whose indices are already
part-local — the same underflow that broke the race path and that §0h's `sub` run showed as
`64650,64649,64648`. **No scoping is needed and the fix must not be reverted.**

**2. The same screen, A/B, in the owner map — default keeps the car, `sub` loses it.** Default
(§0g's `md_raw`, and this round's `md_car_raw`): **599/591/450/648/632/463/658 cells owned =
17.6-25.7 % of the frame, 2,073 tris, 8 textures, view depth 4.15-5.55 with the camera at 5.00**,
shape rows 11-28 cols 7-51 (wide and low — a car, side on). `sub` (§0h): **0/2560 cells in 21
dumps, at most 28/2560 = 1.1 %**, 48 triangles.

**3. One PNG, and it is the first capture taken inside the car's own draw window.**
`frames/opt-preview-camera_20261011-1035_CAR-FRAME_f8517.png` (md5 `d71a7580459eb9887d834418b367aec5`),
frame 8517, 1,377 car draws in flight at that frame. It measures **96.417 % one colour
`(140,150,158)`, 232 distinct colours**, and the region the car's own cells occupy shows **no
pixel that differs from the backdrop** — the 2D UI (13,462 TL draws) is what is visible.

**What MOVED this round:** item 1 is answered on the car (relative, in range, float — measured);
item 2's A/B is on the option camera with the car's own draw window identified; item 3 stands
(no scoping); item 4's PNG exists and is pushed here.

**What did NOT move, said plainly:** the flat car is still unexplained, and a single capture does
not even establish that it is flat rather than absent — the car renders in the backdrop colour, or
its fragments never reach the presented image, and this frame cannot tell those apart. Several
captures inside one car window is the next run, not this one. The pre-fix capture of the same page
(`owner1.02_t68.ppm`) differs from ours in one region (`x 896..1150 y 167..530`) that is only
partly inside the car's cells, so it is flagged, not claimed. All of it — with the driver defect
that caused the three lost measurements, and the tools — in
`work/MENU-CAR-FLATTENED/CHECKPOINT.md` §21-§25.

### 0i-bis. THE CONTROL THAT MAKES 0i's PNG mean something — appended 2026-10-11 10:4x EEST (same worker, same round)

The car-page PNG in §0i is only evidence if a capture taken the same way can show 3D. It can, and
inside the **same run**: `frames/opt-preview-camera_20261011-1035_SAME-RUN_next-page_STAGE.png`
(md5 `aaf7ff5d7f641db95dce7b99d9d1d0c7`, frame 9051, **952 3D draws in flight at that frame**) is
**21,103 distinct colours, 62.6 % of the frame non-background, a densely shaded scene**.

| capture (same run, same binary, same snapshot path, both with MENUDRAW drawing at that frame) | distinct colours | dominant colour | non-background |
|---|---|---|---|
| frame 8517 — the **car page**, 1,377 car draws in flight | 232 | `(140,150,158)` 96.4 % | 3.58 % |
| frame 9051 — the **next page**, 952 stage draws in flight | 21,103 | white 37.4 % | 62.6 % |

Both pages put thousands of 2D `TL` draws over the 3D (15,767 vs 3,481), so "an opaque 2D backdrop
drawn after the 3D" explains the car only if that backdrop is page-specific — it does not cover the
stage. **What is eliminated:** the snapshot path, the index base, the vertex format/stride. **What
is left:** the car's own fragments (renders in the backdrop colour, i.e. a flat fill) or its draw
being rejected after submission (depth/z-order on that one page).


<!-- ===== archived below, verbatim, when progress.md was rewritten whole on 2026-10-12 by FULL-PORT-GRAPHICS-FIRST-20261012 ==== -->

--- progress.md as of 2026-10-11 15:34 (the version this date replaced) ---
# progress.md — Lena on the Deck, reporting to Lena on the phone

**Rewritten whole, 2026-10-11 11:1x EEST.** This file is not appended to: each round
replaces it, so a stale claim cannot sit above a fresh one. The old append-log — every
dated block from 2026-10-10 up to 10:28 today, including the ones that turned out to be
wrong — is kept verbatim in [`docs/progress-archive.md`](docs/progress-archive.md).

Every number below names the log, binary or command that produced it. Where a number
came from another lane's run rather than mine, it says so.

---

## 1. RIGHT NOW

**The play binary on his icon is NOT the one this section used to name. Relinked at 12:04:43;
the bytes he drove two stages on at ~11:20 are preserved, and both pass the drive gate.**
(corrected 2026-10-11 15:1x, §1 was written 11:1x and went stale four minutes after the clock moved)

| | |
|---|---|
| binary ON DISK NOW | `work/PLAY/out-plain/cmr2`, md5 **`9ecbf87bb8650a3883b188f4e77890e4`**, 17,714,716 bytes, mtime **2026-10-11 12:04:43** |
| the bytes he actually drove (11:02 link) | md5 `80d927b54f597dbb2ad7590ddb6875e7`, 17,703,640 bytes — preserved at `out-plain/cmr2.bak-pre-pause-unlatch-20261011`, byte-identical to `work/HUD-2D/out3/cmr2` (two lanes, same tree, same bytes, 10:45) |
| does each drive? | yes, both — `cmr2_drives` returns **0** on `9ecbf87b…` *and* on the `80d927…` backup (`tools/drivecheck.sh`, re-run 15:14 on these exact files) |
| what the 12:04 relink changed | two things, by `nm -S` symbol diff: **GameInfo** (pause-unlatch, `GameInfo.cpp`) and **rhi/a7_vk32.o** — `build-play-lre.sh` links the *shared* RHI object, so `9ecbf87b…` is the first binary in the workspace carrying the peer's 11:36–11:47 near-plane work (21 new symbols, `g_nearclip`, `g_nearw`, `ap_update`, …) |
| his own launches, from the launcher's log | the whole ledger is **three lines, all `80d927b54f59`**, last one `2026-10-11 11:06:05  LAUNCH  …/out-plain/cmr2  md5=80d927b54f59  skipped-dead: none` (re-read 15:1x). **Nothing after 11:06:05** — so a run he made after 12:04 did *not* come through the gated launcher, and which bytes he was looking at then is not provable from this log either way |
| and it is alive | a `cmr2` process was running while this was written — but it is the **menu-car lane's** build (`MENU-CAR-FLATTENED/out-md9/cmr2`, pid 277263, started 15:03), not his play binary. The GPU is not free |

**The deadness window, and why it matters more than any single number here:** from
**08:39:06 to 11:02 today** no binary in this workspace could move a car. Our own
instrumentation had deleted two statements of game code (a `str.replace` anchor that
was the code itself — §2.4). Anything measured in that window that assumed a car could
be driven, steered, or that the physics stepped, was measured in a **frozen world**,
including the session he played at 10:03. That window is closed, and the fix is a gate
rather than an order, so it cannot reopen silently.

**The GPU no longer dies.** The kernel ledger, read with `journalctl -k` just now:

```
ring gfx_0.0.0 timeout   12      (-1 in the last 12 hours)
ring gfx_0.1.0 timeout    3
MODE2 reset              14
Faulty UTCL2 client ID: TCP   3
last GPU fault in the log: 2026-10-11 07:31:55
```

Thirteen kernel resets between 22:50 and 23:14 last night were ours (that document's count, `docs/GPU-LIFETIME-FIX.md` §1); the two this
morning (07:25, 07:31 — the ones that took his display down mid-session) were a second
hole in the same class of bug, closed at 08:06 (§2.2). Nothing since.

**What is owed, and it is one run.** The static gate says the play binary drives; a
peer ran these exact bytes 10:51–10:59 (11,753 frames, 0 panics) but without the drive
trace switched on, so **the car-moves proof on the shipped bytes has not been taken**.
It is cheap: `DECK_RACE_TRACE=1` is already compiled into that binary, and one
`drive.py` run turns "the gate says it can" into "it did". Until that exists, this file
says *drivable*, not *driven*.

**The skybox signature the phone asked about (15:0x):** "game UI present, no 3D stage content"
is a **different signature from the 10:06 state** (skybox and no UI at all), and he finished two
full stages at ~11:20 — so stage loading works and this is an intermittent, not a wall. The one
fact that matters for it is the md5 row above: the binary changed under him at 12:04:43.

**Also in flight right now, with no result to quote yet:** the sky/Finland lane
(worker 2, started 11:07), the HUD-2D lane's round on the in-race HUD, and the menu-car lane
(`out-md9`, running on the GPU as this was written).

---

## 2. DONE — finished and verified

### 2.1 The stage's textures were never decoded (DXT5) — the biggest single find of this project

The port was copying the **compressed block stream** of a DXT5 surface into a 32-bit
texture surface as if the bytes were pixels. Every road, verge, terrain, grass, tree
and building texture in the game went through that copy.

* The chain, joined at the copy: `CGraphics::LoadDDSTexture` → `DeckSurface7::Blt`,
  with the source surface created as `FOURCC=0x35545844` (DXT5) and the first bytes
  read out of it being `a0=0x64, a1=0x65` then six index bytes — a DXT5 block.
  The game never decodes DXT itself; it hands the blocks to a blit and expects the
  driver to convert. **The port implemented the decoder the frontend needs (TGA) and
  not the one the stage needs.** (`docs/DXT-COPY-PATH.md` §1)
* **Every DDS texture in the retail install is DXT5.** I swept all 582 `.bfl`
  containers on disk today with the repo's own reader: 581 readable, 26,132 entries,
  **7,804 DDS entries, fourCC histogram `{DXT5: 7804}`** — not one of anything else.
  In the run's own log, the stage's texture loads are `181 DXT5`, zero other.
  (My sweep, 11:1x today; `tools/bfl-read.py`.)
* **The fix** (`tools/fixes/patch_dxt_blt.py`, `patch_dxt_exact.py`): `Blt` decodes
  DXT1/DXT5 when the source surface is compressed; `surface_fill_desc` reports a
  compressed surface as compressed (`DDPF_FOURCC` + `DDSD_LINEARSIZE`), which is the
  branch the game already has for it; and `Blt` marks its destination dirty. The
  decoder agrees with `ffmpeg` on alpha (4096/4096 texels) and to 1 LSB on RGB.
* **Measured, before → after:** the ground band's mean colour was `(142, 171, 159)` —
  chromatic noise. It is now `(115, 90, 15)`, against the terrain texture's own mean
  of `(116, 89, 17)`. Frame-wide distinct sampled colours went 268,522/385,323 →
  22,187/589,792: *fewer* colours, because it stopped being noise. `rd_ga.dds` and
  `ter_kn4a.dds` both decode to alpha 255 everywhere.

### 2.2 The GPU lifetime bugs — the thing that was killing every run at ~30 s

Two holes, same class: memory or a handle freed while a frame in flight could still be
reading it. Both were found in the kernel log, not the game's log — the game's log just
stops.

* **Hole 1, fixed 23:09** (`tools/fixes/patch_gpu_lifetime.py`, 6 edits):
  `a7_upload_texture` destroyed an image and freed its memory with no wait while a
  frame submitted one or two presents ago could still have it bound in a descriptor
  set; and the upload path reset and re-recorded **the frame's own command buffer**
  (`p->cmd[0]`) while the queue was still executing it. The kernel names the fault
  exactly: `Faulty UTCL2 client ID: TCP` (the texture cache pipe), `RW: 0x0` (a read),
  from an unmapped page. The shader never retires, the ring times out, the kernel
  resets the GPU, and the desktop's compositor goes down with it.
  **Measured:** before — every run died at ~30–40 s, 13 kernel resets in 24 minutes,
  including one run with no instruments attached at all (so it was never our harness).
  After — 3 runs, **ring-timeout delta 0**, one of them **165 s / 8,124 frames /
  1,475,544 draws / 3,299,876 triangles**. (`docs/GPU-LIFETIME-FIX.md` §3–§4)
* **Hole 2, fixed 08:06** (`tools/fixes/patch_combo_views.py`, 12 edits): the
  descriptor-set cache was keyed on the texture **id**, so a draw could be handed a set
  naming an image view that had been destroyed seconds earlier. The fix keys on the
  **view** and frees stale sets.
  **Measured:** the mechanism fired **710 times** in one 360 s run; that run submitted
  **6,344,401 mesh-FVF draws**, 72.7 M triangles, 20,662 frames, **0 GPU resets, 0 page
  faults, no display loss**. Every previous round of this project published **0** mesh
  draws. (`docs/DEATH-AND-LIGHT.md` §1.3–§1.4)
* **What this means for the wall:** the order of the problem was wrong in every plan we
  had. It was not `frontend → state fidelity → crash → race`. It was
  **`ring timeout (every run, ±30 s)` → fixed → the game reaches its own frontend and
  drives its own 3D path**. (`docs/GPU-LIFETIME-FIX.md` §7)

### 2.3 The vertex-base double-subtract — the road was drawn from the wrong vertices

`DeckDevice7::DrawIndexedPrimitiveVB` shifted the vertex base by `startVert` **and**
subtracted `startVert` from every index. The two cancel, so `startVert` was lost, and
every triangle of a part whose base was not 0 was addressed outside the window it was
handed. The game's own loader had already re-based those indices
(`Mesh_BuildParts`: `pData[k] -= minIndex`) and draws them with
`startVert = vertexOffset + minIndex` — the port re-based them a second time.

* **Measured** (`DECK_IDXTRACE=1`, one ~90 s run): of **404,000** indexed draws with a
  non-zero base, **404,000 (100.00 %)** fit the game's convention (`relOk`) and
  **0** fit the port's (`absOk=0`). Of 15,969,393 indices, 100 % are inside
  `[0, numVerts)` as the game wrote them, and 2.19 % are after the subtraction.
* **The fix** (`tools/fixes/patch_idxfix.py`): the re-base is off by default;
  `A7VK_IDXBASE=sub` restores the old behaviour for an A/B in one binary.
* **Measured, before → after:** road texture `RD_GA` / id 102 went from **0.0** screens
  of coverage (2,000 draws) to **347,599.57** — the largest single coverage in the
  frame. `MRG_KN1` 0.0 → 237,993.76; `MOU_TER4A` 0.0 → 210,545.06. The frame at t=78:
  clear-colour pixels 57.9 % → **0.0 %**, distinct sampled colours 817 → **2,535**.
  (`docs/ROAD-TEXTURE-OWNER.md` §6–§7)
* **And the previous claim was withdrawn in public.** "Every `RD_*` has cov=0.0,
  draws=0" was an artefact of the instrument twice over: it printed only the top ten by
  coverage, and it selected ids by `cov > 0.0` so a texture with 2,000 draws and no
  area was never printed. The corrected instrument prints every id and selects by draws
  **or** coverage. (`docs/ROAD-TEXTURE-OWNER.md` §3)

### 2.4 The drive loop, deleted by our own tool, and restored

**This is the one we did to ourselves, and it goes in the open.**

On 2026-10-11 at **08:39:06** the round-2 instrumentation
(`work/RACE/patch_racetrace.py`) used two real statements of game code as its
`str.replace` **anchor**:

```c
    Physics_UpdateRateHold();
    g_unk0x00538124 = Car_UpdateEngineNoteFalloff(&g_unk0x00537f60);
```

— and its replacement block did not contain them. So applying the patch **deleted
them**. The second one assigns the bound of the per-car drive loop, so with it gone
the loop never ran one iteration, no car was ever given an input, the physics never
stepped, and every car sat frozen — **in a binary that still booted, still presented
frames, and still looked like a game.**

* **The window is 08:39:06 → 11:02.** Four binaries were in that state, including
  `work/PLAY/out-plain/cmr2` — **the one Miami plays** — and the Desktop icon was
  still launching it. The session he clicked into at 10:03 was a frozen world.
* **It was never missing from the port.** The statements are in the tree at
  08:38:50 (`md5 ae4a118c0b8f0fe9c7c499d696ec98bb`), in the upstream decompilation, and
  in every tree backup from 2026-10-09 23:33 onward. The tool's own two backups prove
  the deletion: they are the same file, byte for byte, taken either side of the patch.
  (`docs/DRIVE-LOOP-REGRESSION.md` §1)
* **Restored and measured** (220 s attract run, pure idle, no input): the loop iterates
  **3,650** times (`f24` = 3,650 = 3507·1 + 51·2 + 12·3 + 1·5, the loop's own counter
  agreeing with its bound), the physics steps at **~24 Hz**, car 0 accelerates to speed
  **101,958** and travels x 28,472,962 → 45,951,805. Before the restore: `steps=0`,
  car 0 speed 0, every frame. (`docs/DRIVE-LOOP-REGRESSION.md` §3)
* **And the honest part of the measurement:** that same run shows the car driving fast
  for ~1,600 frames, then **grinding in place with the throttle on for ~36 seconds**
  (0.08 world units of net travel), then the demo ending and another starting. Miami's
  *"she can't drive for shit"* is not a crash loop — it is a car that stops making
  progress. Whether that is scenery or an AI with nowhere to go is **open**, and it is
  the next question for that lane, not a finding. (`docs/DRIVE-LOOP-REGRESSION.md` §5)
* **So it cannot recur silently:** `tools/drivecheck.sh` asks the *file* whether it can
  drive (`cmr2_drives <bin>`); `tools/loopcheck.sh` asks it of every binary in the
  workspace; `build-play-lre.sh` refuses to install a build that fails the check;
  and the Desktop icon now launches the first candidate that **passes** it, refuses to
  start anything if none does, and logs every launch with its md5. A hardcoded order
  would have rotted within the hour — in this workspace a binary *path* is a name, not
  a build. (`docs/LAUNCHER-DEAD-BUILD.md` §1–§3)

### 2.5 The crash at 16 seconds, and the crash at 16 seconds after that

* **Before the GPU work there was a panic**, not a hang: `index 6484 out of bounds for
  type 'BYTE[6464]'` in `Profile_AssignAvailableCategory`, every run, ~16 s in. Cause:
  `zig cc` at `-O0` is Zig's **Debug** mode, so clang's `-fsanitize=array-bounds` is on
  and the Zig ubsan runtime **panics** instead of printing. The decompiled source forms
  pointers past the end of arrays on purpose, because that is what MSVC6 emitted.
  Measured on this toolchain: `G + 5` traps, `(char*)G + 5` does not, so only the
  subscript form is instrumented. **Seven sentinel sites in three files** were respelled
  as casts; no loop bound, iteration count or write offset changed.
  (`docs/PLAY-CHECKPOINT.md` §1–§2.)
* A **second** fatal trip found the next day was a misaligned `int *` load in
  `OptionMenu_LoadRallyRecords` — i.e. the fatal set is *"any UB the original binary was
  allowed to rely on"*, which is unbounded in decompiled code. Chasing it site by site
  is a treadmill, so the answer is **two builds on purpose**: `out-plain` (the
  launcher's default) with UBSan **off** for the decompiled game objects, and the
  checked build kept for finding defects. The platform layer stays checked in both,
  because it is hand-written and a misalignment there is a real bug.
  (`docs/PLAY-CHECKPOINT.md` §8.)

### 2.6 The black background — one line in our own renderer

The frontend's own backdrop colour `0x9cb4ac` never reached the swapchain, because
`CGraphics::ClearTarget()` clears `D3DCLEAR_TARGET` and then `ClearZBuffer()` clears
`D3DCLEAR_ZBUFFER` with colour `0xff000000`, and the RHI stored the colour on *any*
clear — so the Z clear, the last one every frame, won. Fixed: only a clear carrying
`D3DCLEAR_TARGET` owns the colour. **Verified per-pixel on the binary the launcher
runs:** legal notice 94.8–95.9 % exactly `0x9cb4ac`, 0.0 % exactly black; menu at
t=79 s 60.5 % clear colour, 0.0 % black.
The Bink theory for the black screen was wrong and is dead: the stub intro movie is
why the notice waits for a keypress, and it has nothing to do with the backdrop.
(`docs/GPU-LIFETIME-FIX.md` §6)

### 2.7 The data tools, which is the half of this repo you can use today

* **581 / 581 containers round-trip byte-identical** — re-ran it myself just now:
  `./cmr2lab repack <install>` → `repack VERIFY: 581/581 byte-identical (skipped 1
  non-container)`, 8.4 s wall, exit 0. A modified container is therefore structurally
  indistinguishable from one the game shipped.
* **259 / 259 car `.c3d` close exactly** on
  `48 + Σ(count×stride) + TEXCOUNT×24 + TEXCOUNT×260 == filesize` (3,803 texture
  references, zero mismatches, 2026-10-10; `tools/c3d.py`).
* **The format census, measured today:** in the 206 track containers, 220 car
  containers and 5 frontend containers, every DDS entry is DXT5 — 7,804 of them in the
  whole install, zero of any other DDS format. The stage's road textures are the same
  format the decoder now handles.
* **33 of 66 translation units compile on `x86_64-linux-gnu`; 66 of 66 on i386**
  (the second only with `-Wno-c++11-narrowing`), with the i386 build kept deliberately
  as a diagnostic oracle. All 33 x86_64 failures pass on i386, i.e. they are blocked by
  pointer width and nothing else. **These are compile-level numbers** — ASAN does not
  build on this toolchain, so there is no runtime evidence about the port's
  correctness, and this file will not imply there is.
  (`docs/P3-P1-REPORT.md`)

---

## 3. IN PROGRESS — with honest fractions

**The lighting. Fixes landed: 0 of 4. The defects are enumerated and measured.** Miami
said the lighting is all fucked up (2026-10-11), and the answer is four defects, in
order of confidence, none of them fixed yet:

1. **`D3DRS_AMBIENT` (state 139) is stored and read by nothing.** In one 360 s race the
   game set it **548,489 times with 12 distinct scene ambients** — all twelve
   discarded. In D3D7 fixed function the ambient term is `material.ambient ×
   scene_ambient`; we substitute `material.ambient` alone.
2. **The shader composes the equation wrong:** `base.rgb *= (matAmbient + matEmissive)`,
   then adds light diffuse — D3D7 is `matEmissive + matAmbient·sceneAmbient +
   matDiffuse·Σ(lightDiffuse·N·L)`. With `SetMaterial=1` in the whole run (the material
   is constant opaque white), the prediction is a **blown-out, flat** picture, and the
   frames bear that out.
3. **No attenuation, range, falloff, spot cone or specular** — `lightDir[i].w` carries
   the range into the block and the shader never reads it.
4. **Latent, not claimed as the cause:** the shader lights in *object* space while the
   game supplies world-space lights. Correct only while WORLD = identity, which it was
   for the whole race — a landmine, not the active bug.

Not wrong, and measured so nobody "fixes" them: `LightEnable` reaches the RHI (888,133
light-state changes took effect); `SetLight`/`D3DLIGHT7` are plumbed through to the
shader; `DIFFUSEMATERIALSOURCE = D3DMCS_MATERIAL` is still the last value, so the
port's hardcoded material-source is right and the "use the vertex colour" fix would
have been **wrong**. (`docs/DEATH-AND-LIGHT.md` §2)

**The collapsed car on the setup screen. Measured fraction: 0 — no cause has been shown to
be the cause.** What has moved is the list of what it is **not**, and two of those closed by
measurement since the last rewrite (mine, `work/MENU-CAR-FLATTENED/`, run 11:0x–11:2x):

* **The index base is not it — and the ticket's hypothesis is backwards.** Measured on the car
  page itself, both arms, same binary, one env var apart (`out/md_car_raw.log` vs
  `out/md_car_sub2.log`, `A7VK_IDXBASE=sub`):

  | | default | `sub` (the old re-base) |
  |---|---|---|
  | indexed draws parsed | 3,012 | 3,036 |
  | indices out of range as received | **0** | **2,778 (91.5 %)** — `65506, 65505, …` = −30, −31 |
  | mesh NDC box (GEOTRACE) | x=[−0.811 0.741] y=[−0.422 0.460] | **x=[−76577.33 3.60] y=[−92242.79 20664.31]** |
  | owner-map coverage on that page | 463–658 cells, 2,073 tris (18–25 %) | 21 cells, 48 tris (0.8 %) |

  *"All mangled and jungled up into one flat piece of paper"* is what the **old** setting
  produces, in the numbers. Reverting the fix to "un-break" the menu would create it.
  Also dead: the format/stride theory (float48, part-sized, `idxInRange` yes on the default).
* **The capture that this section used to call the missing piece now exists.**
  `frames/md_car_raw.000.ppm` is run frame **8517** with **1,377 car draws in flight** — and it
  is **96.417 % one colour (140,150,158), 232 distinct colours**. The car's own owner cells
  (rows r14–r27, cols c8–c53 of the 64×40 map = **x 160–1080, y 280–560 px**) are empty in it.
  So on the default arm the car is **submitted, textured, correctly transformed and invisible**;
  one capture in 41 landing inside its window was the binding constraint, and it is now closed
  for this page (`docs/MENU-CAR_car-frame.md`, PNG in `frames/`). All three of today's runs
  agree: no capture anywhere, pre-fix or post-fix, has a car in it.
* Same run, same frames, GEOTRACE (`[GEO] f=8460/8520/8580`): obj box
  `x=[-2.1 2.1] y=[-0.5 0.7] z=[-0.9 0.9]` (a car), `w=[4.076 6.158]`, `ndc
  x=[-0.811 0.741] y=[-0.422 0.460]`, `behind=0 nonfinite=0 draw_behind=0 draw_alloff=0`,
  `tex=1377 notex=0`, and the render-state line is **identical** to the frames with no 3D at
  all. Everything the software can see is right, which is why the answer is now narrowed to:
  **the fragments are discarded after submission (alpha test, cull/winding, or a dead texture
  binding) or written in the backdrop colour.** Next instrument: `A7VK_TEXDUMP` on the car's
  own texIds (37/39/40/41/44) to read their alpha, or one run with alpha test forced off.
* **One number in the previous rewrite is corrected here:** *"the option screen's 3D submits
  9,628 draws and rasterises zero triangles"* is an artefact of reading a **cumulative** census
  counter as a per-frame one. That screen draws ~675 parts/frame between frames ~2400–3600 (and
  the car page 1,377–1,620 draws/frame at 8460–8580) and then the game stops calling
  `DrawIndexedPrimitiveVB` on it altogether. The peer's 40-of-41-captures-outside-their-window
  finding is real and is the reason the earlier frames could not settle it — but it is a
  capture-latency fact, not a rasterisation one.

* **The car page's own textures, read one at a time, and the alpha question turned into a list.
  Measured fraction: still 0 — no cause shown to be the cause.** Round 6 of
  `work/MENU-CAR-FLATTENED/` (12:19–12:4x EEST, four guarded runs) joined three traces that had
  never been joined (`join_ids.py`): the game's own load (`[TEX] TGA <file> WxH surf=<p>`), the
  port's id (`[TEXREQ] DD7 NEWID surf=<p> -> texId=<n>`, `deck_dd7.cpp:1349`) and the bytes the
  GPU actually received (`[TEXDUMP] id=<n> … meanRGBA=… zeroAlpha=`, `a7_vk32.c:1589`).

  The car page's draws (`md_texcar2`, frames 4075–4200, option camera `eye=(0.14 -0.09 -5.00)`)
  bind **9 textures and 2,624 triangles, 419→601 owner cells (16.4→23.5 % of the frame)**:

  | texId | size | alpha in the uploaded bytes | tris |
  |---|---|---|---|
  | **47** (the body) | 1024x1024 | meanRGBA=(115 115 122 **254**) zeroAlpha=0.2 % | 1,175 |
  | 50 | 512x512 | (62 74 76 199) 3.6 % | 207 |
  | 46 | 256x256 | (67 67 66 200) 21.5 % | 424 |
  | 48 | 512x512 | (17 29 30 208) 0.0 % | 116 |
  | 49 | 256x256 | (46 45 44 173) 31.8 % | 148 |
  | 45 | 1024x1024 | (115 115 122 254) 0.2 % | 280 |
  | 51 | 256x128 | (59 53 50 255) 0.0 % | 80 |
  | **52** | 256x256 | (48 20 8 **0**) zeroAlpha=**100 %** | 58 |

  **The body's texture arrives with alpha 254, so "its texture is transparent" is dead for the
  body** — and so is the tidiest form of the 24-bit theory. What survives is the *computed*
  alpha (`a7vk3d.frag`: `c.a = combine(alphaOp, alphaArg1, alphaArg2, t0, vDiffuse)`), i.e. the
  vertex/material diffuse alpha, which nothing prints yet.

* **Five captures inside the car's window, and the frame does not change.** `md_texcar2`'s
  captures `.001…005` are frames **4078–4179** — five frames *inside* the car's own draw window,
  522–1,653 `MENUDRAW` lines in flight — and they are **byte-identical**
  (md5 `5b179735cafb5f48e45d6a79fed05d5d`): `distinct=3915`, dominant `(140,150,158)` **96.040 %**,
  non-dominant 3.96 % in bbox `x[0..926] y[209..438]`, and the 64x40 grid shows only UI. The
  2,624 submitted car triangles rasterise nothing, five times over. This closes the "one capture
  cannot separate…" caveat by showing that *several* captures cannot either.

* **A real port bug, found in the source, that is NOT the car's cause — but sits on the same
  page.** `DeckDevice7::EnumTextureFormats` (`deck_dd7.cpp:1162-1179`) offers **one** format,
  32-bit A8R8G8B8 *with* an alpha mask, on purpose. Real devices also offer a no-alpha 32-bit
  format and the game is written for it (`Graphics.cpp:1982`: if no 24-bit format was enumerated,
  substitute the 32-bit one). Then `CGraphics::LoadTGATexture`'s two branches disagree about the
  same case — 16-bit dest writes `a = 0xff` for a 24-bit source, **32-bit dest writes `a = 0`** —
  so with the port's 32-bit surfaces **every texel of every 24-bit TGA is written alpha 0**.
  TexId **52** above is that, measured: real RGB `(48 20 8)`, alpha 0 on 100 % of texels. It is a
  58-triangle part on this page and a defect in its own right (fix shape: offer the no-alpha
  format *and* sample no-alpha textures as alpha 1.0, as a driver does) — not the ticket's answer.

* **And the ready-made A/B cannot be aimed at this page.** `A7VK_AB=0:opaque` (blend off + alpha
  test off for every draw) is the obvious experiment, and it was run this round **on a card that
  was verified free** (`ps` empty, `gpu-guard.sh --list` empty, GPU 0 %): the run stayed at
  `frontend resource mode -1 -> 0` and **never reached the menu**, exactly as the two 11:2x runs
  did. That retires the "a peer held the card" explanation and leaves the mode harness itself as
  the suspect. The instrument that replaced it is 3D-only: `LENA_MENUOPAQUE=1` in
  `deck_dd7.cpp` builds `out-md3/cmr2`, which forces `ALPHABLENDENABLE=0`/`ALPHATESTENABLE=0`
  **around indexed 3D draws only** and restores them after, plus `LENA_MENUDRAW_ALPHA=1`, which
  prints each draw's atest/aref/afunc, blend src/dst, stage-0 alpha op/args and the first
  vertex's own diffuse/specular dwords. Both inert when unset.

* **The alpha inputs of the car's own draws, printed for the first time — and the arm that
  removes them still does not put the car on screen.** `LENA_MENUDRAW_ALPHA=1` (new, in
  `deck_dd7.cpp`, inert when unset) prints what the shader is built with:

  ```
  [ALPHADRAW] #1 fvf=0x2d2 stride=48 atest=1 aref=1 afunc=7 blend=1 src=5 dst=6
              aop=4 aa1=2 aa2=0 v0_off24=ffffffff (a=255) v0_off28=ff000000
  ```

  alpha test **on**, ref 1/255, func GREATEREQUAL; blending **on**, SRCALPHA/INVSRCALPHA;
  stage-0 alpha op MODULATE of (DIFFUSE × TEXTURE); the first vertex's own diffuse dword is
  opaque white. With the body texture at alpha 254 that computes `c.a ≈ 0.996` — a draw that
  should paint. Then `LENA_MENUOPAQUE=1` (also new: `ALPHABLENDENABLE=0` and
  `ALPHATESTENABLE=0` around **indexed 3D draws only**, restored after each) was run on the car
  page (`md_opq3`, f3650+, 587 cells / 2,747 tris): **the car is still not there.** Its cells
  hold 1.60 % non-dominant pixels against the default arm's 11.01 % — and every one of those
  11.01 % is 2D chrome. So the fragments are not being discarded by alpha test and are not being
  blended away: **alpha is now excluded by measurement**, and the fork is down to the vertex the
  GPU reads (the port's CPU-side view of the same buffer is car-shaped — `[GEO]` obj box
  `x=[-2.1 2.1] y=[-0.5 0.7] z=[-0.9 0.9]`, `behind=0 nonfinite=0`) or the fragment never being
  written at all. Caveat kept: the two frames above come from two runs, so this is "no car with
  alpha off on that page", not a same-frame A/B — the same-frame A/B is what `LENA_MENUOPAQUE`
  now makes possible for the next round (`A7VK_AB` cannot be aimed at this page at all, above).

  PNGs, with the full table: `frames/opt-preview-car_20261011-1235_CAR-PAGE_default-arm.png`,
  `frames/opt-preview-car_20261011-1237_CAR-PAGE_alpha-off-arm.png`,
  `docs/MENU-CAR_car-page-round6.md`.


**"A legible stage." Honest fraction: no measurable fraction on the picture — but the
inputs to it are now correct.** The road textures draw (347,599 screens of `RD_GA`),
the terrain draws in its own colour, and the transform is the game's own — the port's
projection reproduces `CGraphics::SetProjection` + `View_SetPlayerProjection` to four
decimals, aspect **1.600** exactly. What is *not* claimed: a road with verges, a car, a
HUD, a timer. The leading candidate for what the picture still is: **near-plane
blow-up** — in a static-camera shot the geometry spans clip `w ∈ [-89.3, +121.5]`
against a near plane of **5.86**, with NDC `x` reaching **-2.8 × 10⁷** — i.e.
screen-spanning triangles with a near-flat texture gradient. That is a hypothesis with
a measurement behind it, not a diagnosis. (`docs/CAMERA-AND-NEAR-PLANE.md`, `docs/FRAMING.md`)

**The in-race HUD. Question answered; the render is not.** All in-race HUD drawing is
on the transformed-lit 2D path (`Font_DrawChar`/`Sprite_Queue`/`Quad2D_QueueFixedTriangle`
→ FVF `0x1c4`), and the port is **not** refusing 2D draws — `Sprite_Queue` ==
`Sprite_DrawLayer` to within 176 draws out of 1,452,997 over a run. The "336/frame
frontend → 5/frame race" collapse is the **game never asking** in that state; in a
player race the same binary carries the whole HUD (66–70 sprite draws/frame, ~63 of
them glyphs). Whether it lands correctly on the swapchain is the next measurement, and
the instrument for it (`work/HUD-2D/patch_hudtrace.py` — 17 insertion sites, 8 files, `--revert` provided) is built and inert.
(`docs/HUD-2D.md`, 11:0x today)

**The car actually moving, on the bytes he plays. Fraction: 1 run owed of 1.** See §1.
The gate says the binary can; the trace that would say it *did* is compiled in and has
not been switched on for that build.

**Analog input reaches the car. Delivered: yes. Consumed: 0 of 1.** The port drives the
real pad and the axes land in the game's own units (`lY = -59965` at full stick, full
scale `0x10000` is the game's own `DIPROP_RANGE`), and the port bug that made analog
impossible (`prop_id()` returning an object address, so every `RANGE` call returned
`DIERR_UNSUPPORTED`) is fixed. But the engine's throttle/brake axis is **axis 1** and
the port maps L2→axis 2, R2→axis 5 — so the pedal axis is fed by nothing. The fix is
port-layer (`axis1 = R2 − L2`) and is **not written**. Pad → frontend: **6 of 22**
tested inputs register above the measured bar; **4 of 22 are clean negatives and
explained** (X/Y/L1/R1 map to keys `ReadKeyboardDevice` has no menu bit for — a design
decision, not a bug).

**The last 33 translation units. Fraction: mechanical, not begun.** Every remaining
x86_64 error is one class — a pointer cast into a smaller integer type — at **1,377
distinct sites**, plus 7 size asserts (56 sites). One of those is a real bug worth
naming: `typedef long LONG` is 8 bytes on LP64 and Win32 `LONG` is always 4, which
compiles fine and silently corrupts every struct holding a `POINT`/`RECT`/`SIZE`.
Waiting on it: an ASAN build (`docs/PORT-PLAN.md` §6) — there is still **no runtime
evidence** about the port's correctness, only compile-level and run-level counts.

### and what is deliberately not claimed

* **A stage that looks right.** No legible road, no car on it, no HUD, no timer.
* **That the car can be driven in a race by a human, on today's bytes.** The gate says
  yes and a peer ran those bytes clean, but the trace has not been switched on.
* **Anything about driving quality.** The loop runs; whether the AI is any good is an
  open question with a measurement pointing at it (§2.4).
* **That the lighting is merely "a bit off".** It is four specific defects, one of
  which throws away 548,489 values per run.
* **Any number here about the port's correctness at runtime beyond what the logs say.**
  ASAN does not build; compile-level counts are labelled as such.

### 2.6 HIS REVIEW, AND IT IS THE ONE THAT COUNTS — "textures were overall better"

**Miami played the demo on the Deck at 2026-10-11 ~07:4x and said, in his own words:**
*"the demo also worked here with Ford Focus and Kenya rally untill it didn't and froze
which was coool / again super janky and white box under the car, textures were overall
better tho"*.

That is a **person who drives the game** reporting that the DXT5 decode fix (§2.1) is
visible on real hardware, unprompted and without being shown a texel count. It is the
only review that counts, and it is reported here **as his observation, not as a
number** — the texel-level evidence stays in §2.1 and the two must not be conflated.

Two further readings of the same sentence, both measured, are in the round-7 note for
this ticket:

* he reached a race **with a car he selected** (Ford Focus, not the default) — the
  car-select path and the per-car model + livery load work well enough to be driven,
  so do not "fix" that path on the strength of the white box;
* the freeze he hit at 07:25/07:31 on 2026-10-11 is **not** the same kernel event as
  the 2026-10-10 cluster: no ring timeout was recorded, and the reset was triggered by
  **an amdgpu page fault raised by the `cmr2` process itself** at address
  `0x8010682_000` (see the round-7 note). Same symptom, different mechanism.

*(appended by the WHITE-BOX-UNDER-CAR ticket, round 7. If this paragraph is missing on
re-read, a concurrent writer rewrote the file — the copy is kept at
`work/WHITE-BOX-UNDER-CAR/progress.md.before-r7`.)*

### the setup-menu car, round 7 — the index fix is not what hides it; CULLING is

The car in the pre-race setup menu is still not right, but this round moved the
needle for the first time in four rounds, and it moved off the theory you sent.

**Your index-base hypothesis is dead, and it stays dead.** It was already
measured dead twice (the car's own indices are relative and in range; under
`A7VK_IDXBASE=sub` the car's vertices come out spread over ±76,000 in NDC — the
old path IS the mangled flat sheet). Round 7 added no scoping and reverted
nothing, because nothing needs scoping.

**What round 7 found instead, in two steps.**

1. **The port's backface culling was eating the car.** The owner map that said
   "the car is on screen, 648 cells, 2,073 triangles" is a *backface-agnostic*
   software rasteriser: it counts every triangle with a positive w and never
   tests facing. So a car that is 100 % culled still produces that map, and the
   screen still shows nothing. The port maps `D3DCULL_CCW` to Vulkan's
   `CULL_MODE_FRONT` + `FRONT_FACE_COUNTER_CLOCKWISE` once, globally, for the
   race and the menu alike.
   **Forcing the cull mode off for indexed 3D draws only, on that page:**

   | capture, same page, same camera, car's draws in flight | distinct colours | content in the car's own cells |
   |---|---|---|
   | `frames/opt-preview-car_20261011-1350_CULL-ON_control.png` | 1,205 | 10.0 % (2D chrome only) |
   | `frames/opt-preview-car_20261011-1346_CULL-OFF_car-visible.png` | **14,159** | **22.0 %** |

   The cull-off frame has a textured **1081 × 258 px band centred on (670, 332)** —
   wide and low, exactly where the car's cells are — and the control frame has
   chrome alone. Same binary, same route, one forced state apart.

2. **The menu car's draws are the first thing in the frame, and 375 2D draws
   follow them** (`[MENUORDER] draws=407 3d=29 first3d=4 last3d=32`), so an
   overpainting 2D quad is now a named, still-open second suspect — the
   instrument that would name it is built and running.

**What this does NOT yet claim:** that the hidden object is a *car* rather than a
shape in the car's place (I measure pixels, I can't look), and the two arms are
two runs, not two frames of one run. The next step is a same-run, frame-scheduled
cull switch, and then the real fix — decide the winding per triangle from the
transform, the way D3D does, instead of trusting one global convention.

**And one warning that matters for every measurement on this box.** Round 7 spent
40 minutes of its own time proving why five route attempts in a row never got
past the boot screen: **the game received no keys at all.** The harness's
keyboard injector creates a synthetic evdev device that this machine will not let
the game read (`[KB] evdev: /dev/input/event11: Permission denied` — no `uaccess`
ACL for a device created outside a login session), and the game's own intake
would refuse it even with access (it scores such a device -2 and only takes
devices at +3). Keys reach the game only when they are sent **straight to its
window** (`xdotool key --window`), which is what round 7 switched to. The runs
that DID progress earlier today must therefore have been taking input from
*somewhere else* — another lane's injector — which is the same contamination
`work/DEMO-DRIVE-CRASH` reported at 12:02 from the other side. Anything measured
on this box through a scripted route carries that caveat, this round included.

### the setup-menu car, round 8 — the same-run cull A/B was run, and it comes back NEGATIVE

Round 7 ended with a lead and a promise: forcing `D3DCULL_NONE` around the option page's indexed
3D draws had put content into the car's own cells, so culling looked like the mechanism — but
the two arms were two *runs*, so the page could have differed. This round ran the same-run,
adjacent-frame version of it (a new env-gated instrument, `LENA_MENUCULL_PHASE=<frames>`, which
alternates the forced cull between `D3DCULL_NONE` and the game's own value every N frames and
logs every change with the frame number, so each capture carries its own arm from the port's
own log).

**On one page, in one process, 204 captures inside the 3D window, 102 under each arm: the two
arms are indistinguishable.** Mean car-cell content 11.65 % (NONE) vs 11.64 % (PASS); median
3,003 distinct colours both ways; and the cleanest case is exact — frame 3639 (`PASS`) and frame
3641 (`NONE`) are **the same 1,024,000 pixels**, md5 `f4eda0d799ecf08e94cf51efce221563`, both
pushed to `frames/opt-preview-car_20261011-1420_*`. **Culling is not what hides the car on this
page**, and round 7's lead is downgraded from "the mechanism" to "a variable that changes
nothing here". Two caveats, both measured and both in `work/MENU-CAR-FLATTENED/ROUND8-CULL-AB.md`:
the game presents each rendered frame twice, so a capture can repeat a frame rather than redraw
it; and the `[GEO]` state snapshot restores the game's cull after every draw, so it cannot
confirm the forced arm reached the pipeline — a submit-time state readout is the follow-up.

**What the tracing DID settle about the car, on the page itself** (`LENA_MENUPROJ`, 3,000 traced
draws, every one logged): the game asks for `D3DCULL_CCW` on the preview car itself
(`gameCull=0x3` on every line — it is the game's own state, not the port's); the transform is
never mirrored or degenerate (`det_raw = +3.19935`, `det_flip = −3.19935`, identical on all
3,000; 0 vertices behind the camera, 0 non-finite); and over the 3D window's **96,655 triangles,
40.7 % are wound the way `D3DCULL_CCW` KEEPS and 59.3 % the way it CULLS, with none degenerate**
— which is what a closed mesh looks like from outside, and which therefore also kills the strong
form of "the car is culled to nothing". The index-base fix is not re-based differently here than
on the race path, so it is not this bug either — re-confirmed on the page the ticket was written
about, not just at the call sites. **No render-path code was changed this round**: the binary
differs from the shipped one only by two env-gated instruments, so nothing can have been
re-broken, and the race path was not touched.

The one instrument this page still needs is specced in the same file and is arithmetic on bytes
the port already reads: compare each triangle's **screen-space winding with the direction of its
own vertex normal** (offset 12 of the same 48-byte vertex). A mesh whose outward faces come back
screen-CCW is wound the other way round from the port's global rule — which draws a car
inside-out, and "inside-out" is what "all mangled and jungled up into one flat piece of paper"
describes. No picture and no second run needed.

---

## setup-menu car r9 (2026-10-11 14:2x–14:4x EEST): the frame measured against the port's OWN rasteriser of its own draws — the car page's cells are 70–78 % background, in either y orientation

`work/MENU-CAR-FLATTENED/ROUND9-ENGINE-VS-SCREEN.md`, `cmp9.py`, `fit9.py`, `flip9.py`, `map9.py`.
No GPU run this round (the card was a peer's for the whole round: `work/RACE/out-rt10/cmr2`,
guard-verified) and no render-path code was changed.

`[OWNER]` is the RHI's own CPU-side rasteriser of the same triangles the draws submit, loaded with
the same 48-byte stride and multiplied by `b->mvp` — **the very block that goes to the GPU**
(`a7_vk32.c:2637` hands `&b->blk` to `ow_note`, and `b->blk.mvp` is what `a7vk_fill_block` negates
and memcpy's at `:2735`). Nobody had compared that prediction against a capture of the same frame.
This round did, cell by cell, at the owner map's own 20 px grid.

**What the engine says it drew on this page:** frames 3650…4000 of `md_proj9b` all report **438 of
2560 cells owned, 2747 triangles**, by 8 textures — `tex=36` 255 cells (the body), `tex=37` 89 cells
in two wheel-shaped blobs, `tex=38` 75 cells (the cabin), `tex=40` 19 cells. Rows 14–27, cols 7–52
= **x 140–1050, y 280–560 px**. It is a car, it is static, and it is what the port thinks it drew.

**What the frame shows, 8 frames of the same run:**

| `[OWNER]` frame | capture | engine cells | screen cells | both | engine-only | screen-only |
|---|---|---|---|---|---|---|
| 3650 | 3649 | 438 | 217 | 130 | **308** | 87 |
| 3700 / 3750 | 3699 / 3749 | 438 | 168 | 97 | **341** | 71 |
| 3800 / 3850 | 3799 / 3849 | 438 | 217 | 130 | **308** | 87 |
| 3900 / 3950 | 3899 / 3949 | 438 | 168 | 97 | **341** | 71 |
| 4000 | 3999 | 438 | 217 | 130 | **308** | 87 |

**70–78 % of the car's own cells are plain background colour on the frame**, and 40 % of the
screen's own non-background cells lie *outside* the car's footprint. It is not an orientation
error — the `[OWNER]` map's own y convention is ambiguous by construction (it maps ndc y=+1 to row
0 while the block it reads has had the y column negated for Vulkan), so **both** orientations were
tested: IoU **0.248** as printed, **0.287** flipped vertically, and **0.435** for the best of 4,000
scale × flip × offset candidates (a 2:1 shrink *and* a 180° rotation — the fit finding chrome, not
a viewport transform).

**Round 7's positive is retired on its own frames.** The PNG it shipped as "the cull arm shows the
car" (`frames/opt-preview-car_20261011-1346_CULL-OFF_car-visible.png`, md5 `4fe6c651bdc26e45d8e8e9d0811a0c0b`)
is byte-identical, at every sampled byte, to `md_mc_none_r1.043…046` — capture frames **4464, 4471,
4488, 4490**, four consecutive captures of one unchanging image — and against that run's own
`[OWNER]` car map it scores IoU **0.310** upright / **0.338** flipped. The arm that forces
`D3DCULL_NONE` on every indexed 3D draw of the car page does not put the engine's car on the screen
either.

**And the `853x533` that `MENUPROJ` prints is identified:** it is the frontend **render target's**
size (`DeckD3D7::CreateDevice`, `deck_dd7.cpp:1274-1284`, stores `d->viewport` = the render target
size; `[WIN]`/`[A7VK]` say the display and swapchain are 1280x800). The game does call
`SetViewport` (1200 times in 600 frames; `Game.cpp:2667` with a caller rect, `Game.cpp:2774` with
`(0,0,resX,resY)`, `Graphics.cpp:2995` for the shadow cube faces) — **and the port stores every one
of them and applies none**: `a7vk_record` sets the Vulkan viewport, the scissor and the shader's
own pixel mapping `pc.vp = (W/2, H/2)` from the **swapchain extent**, once per frame
(`a7_vk32.c:2782-2795`, `:2847`). Not the flat-car cause (it mis-scales, it does not flatten), but
a named port defect on exactly this page, and it is the reason the `[OWNER]` map *is* a fair
prediction of the frame.

**What did not move: no coherent car has been seen and none is claimed.** The question the round
sharpens: the port's own rasteriser of the port's own draws puts a car on 438 cells, and the GPU's
frame does not show it — in either y orientation, with culling forced off, and with alpha test and
blending forced off (checkpoint §44). Either the car page these runs reach is **not** the sub-page
Miami is looking at (a fork open since round 5, never closed), or the car's batches are dropped or
overwritten between the batch and the rasteriser in a way independent of every state the draws
carry. The next instrument is unchanged and still unbuilt: the normal-vs-winding test (vertex
normal at offset 12 vs screen-space winding, in `MENUPROJ`'s own hook), a submit-time cull readout,
and the `A7VK_SNAP` four-consecutive-frame fence.

Frames pushed with this block: `frames/opt-preview-car_20261011-1440_f3639_ENGINE-SAYS-438-cells.png`
(md5 `9b9f142d9b002852f442a138f622d427`) and
`frames/opt-preview-car_20261011-1440_f3639_CAR-REGION-2x.png` (md5 `24e329061cd9f34fd21005de841e0a3c`),
both from `md_proj9b` capture 002 = frame 3639, the frame whose engine prediction is the first row
of the table above. `git push origin HEAD` still fails (no credential helper on this box).

## setup-menu car r10 (2026-10-11 14:4x–15:0x EEST): the per-frame draw ORDER at last, and 96.4 % of that frame is the option menu's own CLEAR COLOUR

`work/MENU-CAR-FLATTENED`, run **`md_cov7`**, card taken at 14:46:02 through the standing guard,
binary `out-md7/cmr2` md5 `b051924366847f8226094d4dc26e3810`, with the round-7 instruments
**`LENA_MENUORDER=1 LENA_MENUCOVER=1 LENA_MENUCOVER2=1`** — which no run had ever carried onto
the option page's 3D window (round 7 built them, ran them on `out-md5` whose MENUCOVER output is
silently suppressed, and gave up when `md_cov6` never drew the car; every run since used `out-md7`
and never turned them on).

**What the page does, per frame, measured:**

```
[MENUORDER]  draws=406 3d=29 first3d=4 last3d=32 2d_after_last3d=374
[MENUCOVER2] 3d_first=4 3d_last=32 2d_after3d=374 cover2d_after_3d=2
             first  =(33 [56.0 46.0 987.5 653.5] ffb8b8b8)
             topmost=(34 [179.0 352.0 1223.5 683.5] ffb8b8b8)
```

* The car is **29 indexed 3D draws, 4th to 32nd of every frame**, and it is submitted
  continuously (the `[MENUORDER]` 400-frame budget all fired with `3d=29`).
* **374 2D draws come after it**, and the first two are big opaque quads covering its whole
  footprint. Their vertex colour fades per frame (cc→b8→b2→ab→d9→ee→f6→fe…→ff): a page fade.
* **And the frame they are drawn on is 96.38 % ONE colour: (140,150,158).** That colour is the
  **option menu's own clear colour** — `GameInfo.cpp:1788` `SetClearColour(1, 0x8d, 0x97, 0x9f)`
  = (141,151,159), one code off (measured on the pixel). The only other content inside the car's
  own rect x160..1080 y280..560 is **9.85 %** of pixels, and its two commonest colours are pure
  white (255,255,255) and pure black (0,0,0) — **menu text**, on a panel so flat that the mean
  horizontal gradient there is **0.00** (against 22.28 inside the text). **The page is almost
  entirely UNPAINTED: the car's 29 draws, and everything else that should fill that screen, leave
  no marks on it.**

**So the r7 question — "who paints over the car" — was asked properly and answered NO.**
`LENA_MENUSKIP2D` (new, `patch_menuskip.py`, built into `out-md8/cmr2` md5
`fe0c82daa709e6fa5486f9c230c15df3`) drops every 2D/TL draw whose bbox contains (640,420) while
`/tmp/skipnow` exists, in frames that have already submitted a 3D draw. Run `md_skip` took the
card at 14:55:35 and did it as a triggered same-run A/B: 10 s control → `touch /tmp/skipnow`
14 s → remove 8 s, captures every 0.4 s throughout. The port's own log names what it dropped:
`count=72 quads=18` per frame, twice per frame, `sz0=0.0000 rhw0=0.0000`. **The frames before,
during and after are the same file: md5 `40fd7369f33caaa7a303b1d5f7c24748`** — and that is also
the md5 of `md_cov7`'s captures from 10 onward, a different binary in a different run. Dropping
the covering draws changes **nothing**; the car is not hidden by 2D chrome.

**Frames pushed with this block.**
`frames/opt-preview-page_20261011-1500_r10_car-submitted-29-draws_INVISIBLE.png` (md5
`03ac7eca08fbe2d32ddf94abd27f7c52`) — the whole option frame with the car's 29 draws in flight:
menu text on the clear colour, no car. `frames/opt-preview-page_20261011-1500_r10_CAR-RECT_what-is-really-there.png`
(md5 `bcfaf0ee568973804674a9038b3ecfbc`) — the car's own owner rect x160..1080 y280..560 cut out
and shown on its own, so the absence is visible without hunting for it.

**What did NOT move: the car is still not on that frame and no fix is claimed.** Three mechanisms
are now excluded by measurement *on this page*: the index base (r5), culling (r8), alpha (r6),
the 2D draw order (r10). What r10 adds is the reason the previous rounds kept disagreeing with
themselves — **the frame is not a wrong picture of the car, it is an EMPTY one: the car's draws,
and the page's own fill, are not reaching the rasteriser at all.** The next instrument is
therefore not another state readout but a *drop test on the 3D path* (submit none of the 29 draws
and compare the frame: if it is byte-identical, the car's draws contribute zero pixels on this
page and the fault is in the 3D submit/raster path, not in composition) — `LENA_MENUSKIP2D`'s
twin, ten lines away in the same file. `git push origin HEAD` still fails on this box (no
credential helper); the commit is local.

### setup-menu car r10, addendum 15:2x — **THE CAR'S 29 DRAWS DO PAINT. THEY PAINT A FLAT SLAB OF ONE COLOUR OVER THE MENU.**

`LENA_MENUSKIP2D`'s twin, `LENA_MENUSKIP3D` (drops every indexed 3D draw while `/tmp/skip3d`
exists), built into `out-md9/cmr2`. First attempt (`md_skip3`) did nothing and **its own log said
why**: `grep -c MENUSKIP3D` = 0 — no init line — while the same log had 8,688 `MENUORDER` lines
with `3d=29`, i.e. the gate was in `DrawPrimitiveVB` (which this page never calls) instead of
`DrawIndexedPrimitiveVB` (the call the car's 29 draws actually use). Moved, rebuilt
(`out-md9/cmr2` md5 `d3e90a99dd83bda86f1d180e9c82e52a`), re-run as **`md_skip3b` 15:09–15:2x**:
this time the log carries `[MENUSKIP3D] on:` and `[MENUSKIP3D] frame end: skipped=29 skip3d=1`
for every frame of the treatment.

**The A/B, same page, same process, adjacent frames, one file apart — and it MOVES:**

| | frame 0040 arm A (car submitted) | frame 0072 arm B (car's 29 draws dropped) |
|---|---|---|
| dominant colour | (140,149,158) **96.48 %** | (140,149,158) **86.31 %** |
| distinct colours | 826 | 254 |
| car rect x160..1080 y280..560 non-background | **9.57 %** | **26.33 %** |

**Pixdiff of the two frames: 175,878 pixels differ, bbox `x[0..1223] y[46..733]`, and the
colours are unambiguous:**

* in arm A those pixels are **(140,149,158)** — 140,044 of them, one flat colour;
* in arm B the same pixels are **(231,235,198)** (56,113), (79,79,79) (19,618), (201,214,216)
  (17,346), (199,199,212) (13,050), white (7,123) — **the menu's real content and its text**
  (LightYellow backdrop, icons, glyphs).

**So the car's 3D draws are rasterising and filling a ~140,000-pixel region — bigger than their own
rect — with a single flat colour**, and what we have been calling "the clear colour everywhere" is
in large part *the car itself, drawn flat*. Drop the car and the menu's real content appears.
Put it back and the car is a flat one-colour sheet lying over the menu. **That is Miami's
sentence, measured: "flattens into one place on the menu … one flat piece of paper."**

**The frames pushed for this:** `frames/opt-preview_20261011-1520_r10_A_car-3D-submitted_FLAT-SLAB.png`
(md5 `152a9fafb033f2de7f591f73cd1ad2cb`) and
`frames/opt-preview_20261011-1520_r10_B_car-3D-dropped_MENU-REVEALED.png`
(md5 `f5916050713b556e38a201e9aa2167a3`) — look at them side by side: A is what he sees, B is the
same frame with only those 29 draws removed.

**What the next instrument must name: where the flat colour comes from.** It is a *fragment*
value, not a geometry or a depth or a cull or an ordering value — all of which are now excluded on
this page. The three candidates are (i) the texture bound at those draws (a blank/never-uploaded
texture, or the wrong one), (ii) the texture-stage 0 combine (the census logs
`s0/t11`, `s0/t18`, `s0/t20`, `s0/t24` set 2,112 times and "texture-stage OPs set: 1:1200
4:4224"), and (iii) the material (`flags.w` source=material vs vertex). One line added to
`MENUDRAW` — the two bound texture handles and the material diffuse of the car's own draws, plus
an arm that forces texturing off — separates them, and it needs no new run machinery: the same
`md_skip3b` route, the same trigger file.

---

## setup-menu car r11 (2026-10-11 15:1x–15:3x EEST) — the car's FRAGMENT inputs measured for the first time, and the first A/B in this ticket that MOVES **and comes back byte-identical**

r10 named the next instrument and stopped one line short of it: *"where the flat colour comes from
— the bound texture, the stage-0 combine, or the material."* r11 built it, ran it, and got a result
that is stronger than a null: **three arms on the same page in the same process, each one changing
the frame, with the frame returning to the control's md5 byte for byte after each arm.**

### The instrument (`LENA_MENUTEX` + `LENA_MENUUNLIT`)

`patch_menutex.py` adds three things to `deck_dd7.cpp`, all inert unless the env var is set:

* per-indexed-3D-draw print: the two **bound texture ids**, the stage-0/1 ops and args, the lighting
  flag, and — for three of that draw's own vertices — the texel the shader *would* fetch, the vertex
  diffuse, and **the fragment colour the port's own combiner predicts** (`a7_eval_texop` on the real
  inputs, `a7_vk32.c:297`). A prediction is testable against the framebuffer; a list of inputs is not;
* a **CPU snapshot of every uploaded texture** taken at `a7_upload_texture` call time — the exact
  bytes the GPU was handed, so "the texture is flat" and "the sampling is wrong" are two lines;
* `LENA_MENUUNLIT`: two file-triggered forced-input arms applied to indexed 3D draws only and
  restored by a C++ scope guard, so no arm can leak into the 374 2D chrome draws after the car:
  `/tmp/mtA` = stage0 `SELECTARG1(TEXTURE)` (texture only), `/tmp/mtB` = stage0
  `SELECTARG2(DIFFUSE)` (vertex/material colour only).

`out-md10/cmr2` md5 `8be469d8545f9252e5c27f44c5ca6499`. Build notes worth keeping: three of the
four iterations were *compiler-caught* format/type errors in my own print (and `A7Material.diffuse`
is an `A7ColorValue` of floats, not a `D3DCOLOR`) — the last build has **zero warnings from the new
block**, and the first cut's budget was wrong in a way that would have printed the menu chrome and
never the car, which is why `MENUTEX` now rides `MENUDRAW`'s burst window.

### The run, and the route defect that cost the first 3 minutes of it

`md_mtex`, card taken 15:21:03 (guard empty, no peer touched). **The first launch had no X-key
driver and never left the boot screen** — `[MENUTEX]`/`[MENUDRAW]` = 0 lines for three minutes,
because `md_drive_car.py` injects through `inject-key.py`, whose uinput device cannot be taken on
this box (r7 measured it: score −2, or `Permission denied` on the evdev node). `kb_mt.sh`
(`drive_cov.sh`'s phases 1–2 with the exit condition moved to my own first line) reached the option
page **80 s after the keys actually arrived**. Every earlier round's route was driven by exactly
this xdotool path.

### What the car's draws actually bind (402 draw lines, 402 texture pairs, 1,206 vertex samples)

* **Eight real textures**, ids 35,36,37,38,39,40,41,42 — 256×256, 512×512, 1024×1024, means
  (13,13,12,207), (100,94,101,253), (51,50,50,207), (31,30,35,204), (22,22,21,187), (85,66,69,204)…
* **No stage-1 texture at any of them** (`tex1=-1`), so the 3D fragment shader's stage-1 branch is off.
* Stage-0 op at every draw: `MODULATE(TEXTURE, DIFFUSE)`; lighting on at 389/402.
* The car carries **38 distinct vertex diffuse colours** (white, greys, 0xff926c6c, 0xffb3b34c,
  0xff5f5f9f …) — real per-part colours, not a placeholder record.
* The combiner's **prediction is near-black** (`ff000000`, `ff08090a`, `ff080905`, `ff080008`…), and
  the framebuffer in the car's own region holds exactly that: `(0,0,0)` 3,344 px, `(49,52,49)`
  2,162, `(0,0,13)` 991, `(8,0,8)` 969. **The car is not missing and not mis-indexed — it is painted
  near-black, and the port's own arithmetic says so before the pixels do.**

### The A/B — control, texture-only, diffuse-only, with recoveries in between

| window | frames | md5 | distinct colours | car region |
|---|---|---|---|---|
| CONTROL 002–014 | 13 | `1b2bce5343` | 4,248 | dark: (0,0,0), (49,52,49), (0,0,13), (8,0,8) |
| **mtA** texture-only 015–031 | 17 | `15525ebc90` | 3,730 | dark + greys (161,160,161), (150,150,150) |
| recovery 032–042 | 11 | `1b2bce5343` | 4,248 | identical to control |
| **mtB** diffuse-only 043–059 | 17 | `1ce176a776` | 155 | **34,233 px of PURE WHITE** |
| recovery 060–071 | 12 | `1b2bce5343` | 4,248 | identical to control |

Both arms fired (`[MENUUNLIT] arm 1 ACTIVE (draw 1)`, `arm 2 … draw 958`), both changed the frame,
and **both recoveries returned it to the control md5**. Full pixdiff control→mtB is 32,092 pixels,
**98.4 % of them pure white in mtB** — so the car's own silhouette is `bbox x[87..891] y[215..378]`,
and with the texture removed from the chain that silhouette goes white: **the visible car in the
control is the texture, modulated by a white diffuse.**

### The one number r11 will NOT ship, and why it is the most interesting one

The UV column printed `uv0=(3.3609e-309, 2.122e-314)` — **a double, in a column that reads a
32-bit float** (smallest subnormal float is 1.4e-45). So the formatting is wrong and the *magnitude*
cannot be quoted. What is quotable is the **constancy**: all 1,206 printed UV strings are identical.

If that constancy is real it is the whole bug — every fragment of the car would sample ONE texel,
which is "flattens into one flat piece of paper" literally, in the fragment shader. So it was
checked against the file: the `.c3d`'s own 48-byte records (dumped offline this round from
`game/Game/Cars/205a1N.c3d`, located by their unit-length normals, 1,140/1,268 gaps = 48) carry
**real UVs** — `uv0=(0.5000,0.5000)`, `(0.9897,0.5000)`, `(0.9241,0.2552)` … at exactly the offsets
the port reads. **File has UVs; the runtime read says one repeated value; and the column that says
it is the one column I just caught being formatted wrong.** So `MENUTEX`'s UV column was rebuilt as
**hex** (`out-md11/cmr2`, md5 `629228b9c3211556157004feddcb4987`) and re-measured in run 2
(`md_mtex3`, launched 15:29), together with the depth question below. r11 does not get to claim it
yet, and says so here rather than in a footnote.

### Also in run 2, and it is a fork r10's numbers opened

r10's drop test showed the car's presence costs the *page* ~140,000 pixels of its own content, and
the car is drawn 4th–32nd of the frame — **before** the 374 2D chrome draws, so it cannot be
painting over them. Depth is the obvious candidate (the car writes z, the TL chrome depth-tests
against it): run 2 runs the same page with the existing `LENA_MENUZ=0` instrument, which forces
`D3DRS_ZENABLE=0` around indexed 3D draws only and restores the game's value right after. The option
page is deterministic (r10 measured byte-identical captures across frames, binaries and runs), so
the cross-run md5 comparison is a valid A/B.

**Frames pushed:** `frames/opt-preview_20261011-1524_r11_CONTROL_car-pixels-dark.png`
(`658c57ddcfe2c1aa43fe0791d0ecf286`) — the page as he sees it; the same frame with the car's
fragments forced to vertex/material colour,
`frames/opt-preview_20261011-1524_r11_mtB_diffuse-only_car-WHITE.png`
(`2f15d58f811c41facc922da90efa5caa`); and 880×300 crops of the car's own region from each
(`eb121df8c6e058a004fc7e4babc4a7c0`, `f3677e42cb067fd19eaeaffa5500aac3`).

Held for the next round: whether the runtime UVs are really one repeated value (run 2, hex), whether
depth is what costs the menu its own content (run 2), and — if the UV constancy holds — **where the
UV field is lost**, since the file has it and the port's record offsets are demonstrably right for
position (offset 0), normal (12) and diffuse (24, written by the game's own `Mesh.cpp:95`).

---

### setup-menu car r11, addendum 15:3x — **the UV column was MY bug, not the port's; and depth is not what hides the menu**

Run 2 (`md_mtex3`, `out-md11/cmr2` md5 `629228b9c3211556157004feddcb4987` — the same instrument with
the UV column printed as **hex**, and `LENA_MENUZ=0` so every indexed 3D draw of the car is drawn
with `D3DRS_ZENABLE` forced off and the game's value restored right after: the gate's own init line
is in the log, so the treatment happened).

**1. The UVs are real, and the block above is retracted.** `uv0=3f6c9100,3e82a400=(0.924088,
0.255157)` — 603 samples, **52 distinct u values and 56 distinct v values** — and that first one is
the `.c3d` record-2 UV `(0.9241, 0.2552)` from the file dump, to four decimals. My first cut printed
that column with `%g` on a value the compiler delivered differently and got `3.3609e-309` for every
vertex, which I flagged as unquotable in the block above and then re-measured rather than shipped.
The car's fragment chain has **no missing input left**: real geometry, real UVs, eight real textures
(ids 35–42, the same ids in both runs), `MODULATE(TEXTURE,DIFFUSE)` over a white diffuse, lighting
on, and the port's combiner predicting the exact near-black the framebuffer holds. It is dark
because **those textures are dark** (means 13–100) — so "one flat piece of paper" is a dark,
low-contrast, shape-mangled object, and the mangling lives in the geometry/winding, not the fragment
chain.

**2. Depth is not what costs the page its own content.** With the car drawn and z forced off for its
29 draws, the frame is still 96.47 % one colour with **zero** pixels of the menu's LightYellow
(231,235,198) — the colour r10's car-dropped arm showed at 56,113 px. What DID change is the car
itself: `(236,236,236)` 1,182 → 5,546 px, `(49,52,49)` 2,162 → 3,573 — with z off the car shows more
of its own surface, which is what the depth test was cutting. Caveat carried with it: the two runs
are **not** byte-comparable (183,963 car-rect pixels differ by 1–2 LSB; the whole page is one LSB
greener in run 2, and that shift is unattributed), so the comparison was made with a tolerance and
the content statement stands on the LightYellow count, not on an md5 match.

Frame pushed: `frames/opt-preview_20261011-1532_r11_Z-OFF-forced_depth-off_menu-content-still-absent.png`
(md5 `29e1c6a489554c3bc382255bb0839241`).

**Next, in one line:** the remaining candidate for the hidden menu is a non-depth side effect of the
3D draw on the TL path — alpha-test state at the TL draws, or the pipeline/descriptor binding the 3D
batch leaves behind (`pipelines=3 (built=3 hit=152372)` is the counter to read).

---

## installer + public face (2026-10-11 15:0x–15:2x EEST) — the shipped installer could not have worked, the pair did not compose, and the repo's face was not this game

**The bug, reproduced on his own tree** (isolated `HOME`, nothing written to his
applications): `find_game('…/.lena_cmr2/game')` → `…/game/Game`, which holds `Bigfiles
Cars Tracks DemoRuns Info` and no executable, so the launcher carried
`Exec=…/game/Game` — a **directory**. v0.2.0's root-vs-content split fixes it:
root `…/.lena_cmr2/game`, content `…/game/Game` (220 cars, 212 tracks), exe `CMR2.exe`.

**Four defects in v0.2.0 were already measured and fixed here** (`work/CMR2LAB-v020/REPORT.md`,
v0.2.2, md5 `135559b49804f6733b1d808f9f4cd477`): the `Cars/ + Tracks/` test badged
**Automobilista 2's audio folder** as `✓ <== INSTALL` (0 cars, 0 tracks, exit 0);
`~/.lena_cmr2` is a dead path on this box; a failing `--path` still fell back; and the
bounded walk could not reach a Proton prefix, which — once fixed — found **a second real
install**: his GOG copy at `compatdata/3646996028/pfx/drive_c/Program Files (x86)/Codemasters/Colin McRae Rally 2`, 220/212. Whole search: 0.17 s. v0.2.2 re-verified here:
no-arg `where` now picks the dev copy, AMS2 is refused *with the reason*, a nonexistent
`--path` hard-stops, `--all` lists both installs.

**The defect I found in the pair (fixed in this commit).** `cmr2install` unpacked
`lab.locate()` as a 2-tuple; v0.2.2 returns 4 → `/api/scan` raised
`ValueError: too many values to unpack` inside the request handler, so **tier 1/2 of the
browser installer returned an empty reply**. Fixed with a shape-tolerant `_locate()` that
accepts both versions, and used `everything=True` so tier 1 now lists **both** installs
instead of AMS2. Re-verified with the old lab and the new one.

**The browser installer, verified independently through HTTP** (not the CLI), on
fixtures: A auto → Wine/GOG prefix → `Exec=…/CMR2.exe` `exists:true runnable:true`;
B `--native` where a port exists → `cmr2-native`; C `--native` with no port → refuses,
**no file written**; D nonexistent folder → refuses with the reason, **no file written**.
4/4, and `ls` of the output dir afterwards shows exactly `A.desktop` and `B.desktop`.

**The public face.** The old `docs/social-preview.png` (`e692c642…`) measures **0 gold**
pixels and, under the rule `r≥95, g≤65, b≤65`, exactly **5,666** "red" — the phone's
number, reproduced; exact `#8b0000` is **9**. Its palette is 50,520 shades of generic dark
UI. Replaced with art regenerated from the game's own `FrontEnd/res1024.bfl`: **19,838**
gold and **231,183** red at 1280×640, wordmark band 19.97:1 against its plate and 19.77:1
measured **on the 128 px icon**, i.e. still legible where the old art had nothing to read.
Old file kept at `docs/art/old-social-preview-e692c642.png`. **The GitHub social-preview
upload is web-UI only** — the file is in place, the setting needs a human at a browser.

**And one honest correction to the art's own provenance:** `build_art.py` says every
colour is "sampled from the game files". Audited against all 72 textures: red `#8b0000`
(6,953 px), dirt `#744032` (5,342 px) and sky `#dae8ec` (6,020 px) are real; `#fff300` gold
appears **0 times** (the game's gold is `#fff100`, 2,641 px in `bgre.tga`) and bone
`#dcd3b1` appears **0 times** anywhere. The art is fine; the claim is two entries short of
true. `docs/ART-PROVENANCE.md` has the table and the two ways to settle it.

**§1 was also corrected**: it still named `80d927…` (11:02) as "RIGHT NOW" while the play
binary has been **`9ecbf87bb8650a3883b188f4e77890e4`** since **12:04:43** — the question the
phone opened with.

New in the repo: `cmr2install` (v0.2.1, md5 `0a68aedac4ad46afd7a54029614870f4`), `cmr2lab`
v0.2.2, `tools/build_art.py`, `docs/art/`, `docs/INSTALLER.md`, `docs/ART-PROVENANCE.md`.


---

# archived 2026-10-12 17:5x — replaced by `STATUS-AND-33-OF-66-20261012`

*`progress.md` as it stood at 2026-10-12 13:2x EEST, on the round
`FULL-PORT-GRAPHICS-FIRST-20261012`. Verbatim and unedited, for the same reason as the
block above. Status in it is history: the x86_64 figure it does not mention moved from
33 to 37 on the afternoon that replaced it.*

# progress.md — Lena on the Deck, reporting to Lena on the phone

**Rewritten whole, 2026-10-12 13:2x EEST, on `FULL-PORT-GRAPHICS-FIRST-20261012`.**
This file is not appended to: each round replaces it, so a stale claim cannot sit above a
fresh one. The version it replaced (2026-10-11 15:34, 970 lines) is archived verbatim at
the end of [`docs/progress-archive.md`](docs/progress-archive.md).

Every number below names the log, binary or command that produced it. Where a number came
from another lane's run rather than mine, it says so. Where I did not verify something this
round, it says that too.

---

## 1. RIGHT NOW

**The phase order is set and PHASE 1 item 1 is CLOSED — inside one round.**

| | |
|---|---|
| the binary on his icon | `work/PLAY/out-plain/cmr2`, md5 **`94ed1359c405a31df38e64e197269a78`**, 17,925,328 bytes, mtime 2026-10-12 11:03:43 |
| how I know that is *the* one | `cmr2lre-launch.log`, last two lines: `11:04:01 LAUNCH … md5=94ed1359c405` and `11:11:43 LAUNCH … md5=94ed1359c405` |
| and that it is the artifact of the tree | relinked it myself this round from the shared objects and got **the same md5, byte for byte** (`GRFX-AB/build-ab.sh`'s control arm). The binary and the source tree agree |
| what that build is | installed by **CAR-r39** at 11:03 (`.lre-buildlog`). It carries `LENA-NCCLIP` (the real near-plane clip), and it passes the drive gate (`hold=1 note=1`) |
| GPU | **free.** No `cmr2` alive at 13:2x; the two runs this round were the only ones and both were reaped by PID |
| kernel | `ring gfx_0.0.0 timeout` **0 → 0** across both runs this round. No panics, no wedged display |
| disk | `/home` 928 G, **36 G free, 97 %**. This round wrote 399 MB of captures; nothing was deleted outside `~/lena`, nothing in his library was touched |
| his config | `GameInfo.rcf` and `Controller.rcf` **byte-unchanged** by this round's runs (the harness snapshots both and compares after) |

### PHASE 1 item 1 — CLOSED

> **The defect that dies:** *"the white-on-white snow is caused by the port dropping
> `D3DRS_AMBIENT`, and reading that state instead of the white material ambient will
> darken the snow and give it its edges back."* **Falsified.**

Measured, one run, both arms on the same camera, 28 paired frames on the snow stage:

```
NORMAL (his binary, unpatched)   frame mean 170.8    exact-zero pixels  0.0%
AMB    (rs[A7RS_AMBIENT] in)     frame mean  23.4    exact-zero pixels 88.7%
                                 ratio 0.137         26 of 28 pairs down
```

The AMB frame is not a darker copy of the NORMAL frame — percentile matching (p50 0 vs 199,
p90 41 vs 237) rules out any single multiplier. **Most of the race geometry is drawn while
the state is `0x00000000`.** The prediction on record asked for `road_edge` 0.96 → 3+ and
`blow%` → under 2; the arm instead removes 89 % of the picture, so there are no edges left
to count.

**And the reading the phone asked to be settled is settled: r8's, not SWEDEN's.** r8's
result was that the lit term is a 1.0000 no-op and the washed-out frame is *not* this
render state; the A/B put the term in and looked, and it blackens the stage.

Full evidence, the value table, the attribution proof, the control-identity check and the
two reasons to trust the pairing: **`work/GRFX-AB/REPORT.md`**.
Pictures: `GRFX-AB/out/P_NORMAL_f10009.png` (1.38 MB) and `P_AMB_f10029.png` (80 KB) —
the same pair, same stage, one arm each.

### What PHASE 1 looks like now

| item | state |
|---|---|
| **1.** the ambient A/B | **CLOSED 2026-10-12.** See above. |
| **2.** road separation — the road is drawn but not distinguishable from the verge | **NEXT.** Nothing started. |
| **3.** near-plane / `LENA-NCCLIP` | **half-answered, no run spent.** It **is on by default** — see §3. Whether it *deserves* to be still needs a run. |
| **4.** the white box under the car | not started |
| **5.** flicker | not started |

**One free lead, marked as a hypothesis and not a measurement** (from the game's source, read
while the run was being built): the mesh path draws with lighting mode 2 or 3
(`Graphics.cpp:3519-3571`), and mode 3 takes its material colour from **the vertex colour**
(`D3DMCS_COLOR1`, `COLORVERTEX=TRUE`), while the game builds its light ramp into the
vertices itself (`SceneNode.cpp:795`, `:892-905`, `:930`). If this game's light is anywhere,
it is in the vertex colours — which `ROAD-r7` already measured arriving at the fragment as
a flat ≈0.55× darkening. That is a place to look, not a finding.

---

## 2. HOW PHASE 1 WAS RUN, AND WHAT IT COST

The budget rule the phone set — *one cheap high-information run beats five speculative ones*
— was applied literally.

**Cost: 3 GPU runs, ≈8.7 minutes of GPU (60 s + 60 s + 400 s).** One question per run.

The first 60-second run bought the whole round. It came back with `AB flips: 0` because my
schedule init had landed inside `if (getenv("A7VK_AB"))` — a *different*, optional variable.
That run still produced 16 captures, still exited 0, and every one was the same arm: a
400-second A/B that would have measured nothing. Caught in a minute; the init moved. Both
the patch and `run-ab.sh` now print `INSTRUMENT: ***DEAD***` in the run's own header when
the schedule line is missing from the log.

**The apparatus is the durable asset.** `A7VK_ABALT=<period>` (new, in the arm's private
object only) flips NORMAL/ARM every *period* frames, so any single-variable arm of the
**existing binary** gets both arms on the same camera, 20 frames apart, with the pair order
balanced across pairs. That is ~7 GPU-minutes for a decisive answer, and item 2 can have it.

Nothing shared was written: `rhi/a7_vk32.c` and `rhi/a7_vk32.o` were read-only inputs, and
the patched object is private to `work/GRFX-AB/obj/`. No other lane's link line changed.

---

## 3. WHAT rs139 ACTUALLY HOLDS (new, and it is why item 1 was cheap to close)

The census counts 12 distinct values for `D3DRS_AMBIENT` and names none of them. The arm
logs each distinct value once, dated by its position in the same stream as the RHI's own
`[AB]` frame lines:

```
0x00000000                                     first seen after frame  2539
0xFF6982A3 → 0xFF6B7F9F   (10 values, drifting) first seen 2539 → 5579
0xFF69828F  (105,130,143)                       first seen after frame  7219
0xFF698290  (105,130,144)                       first seen after frame 13619
```

**2539, 7219 and 13619 are the three race starts this run contained.** The live values are a
blue-grey family, green 127–130 of 255 (0.498–0.510) — and the AMB frame mean sits at
**0.545×** NORMAL at the start of race 2, **0.578×** at +400 frames, and **0.137×** from
+780 frames on. A fade toward black, which is what
`StageObject_FadeAmbientColourToBase` (`StageObjects.cpp:4408`) is named for.

**`LENA-NCCLIP` is ON by default — item 3's first half, answered from files on disk, no run.**
`ncclip_mode()` returns `NC_CLIP` whenever `A7VK_NCCLIP` is unset, and the call site is
unconditional for `path3d` draws (`a7_vk32.c:512-524`, `:3898-3904`). Confirmed in this
round's own log, launched with no env var:

```
[NC] LENA-NCCLIP: mode=CLIP  Sutherland-Hodgman, w>nearw nearw=5.8600
```

So it is not "should we turn it on" — **every run he plays, including the one this A/B was
anchored to, already has it on.**

---

## 4. CARRIED FORWARD — NOT RE-VERIFIED THIS ROUND

I am not restating these as fresh measurements. They are the state as of the version this
file replaced (2026-10-11 15:34) and are kept verbatim in `docs/progress-archive.md`.

* **The drive gate holds.** `cmr2lre.sh` refuses to launch a binary that cannot move a car,
  and writes every launch to `cmr2lre-launch.log` with its md5. The 08:39→11:02 dead-build
  window is closed by that gate, not by an order.
* **The GPU no longer dies.** The `GPU-RESET-FINDING` texture-lifetime fix and the
  descriptor-cache hole behind it. This round's two runs agree: `ring gfx_0.0.0 timeout`
  0 → 0.
* **The setup-menu car** (`MENU-CAR-FLATTENED`): the car page's cells are 70–78 %
  background; the frame is 96.4 % the option menu's own clear colour. **This is not a Phase-1
  item and I did not touch it.** The phone's directive says "no menu car".
* **The installer and the repo's public face** (`cmr2install`, `cmr2lab`, `docs/art/`):
  verified 2026-10-11. The GitHub social-preview image still needs a human at a browser —
  **that is not something I can do and it is not something I may do for him.**
* **The disk.** `ROUND-DISCIPLINE.md` is the rule that keeps it flat; the reclaim this round
  is 0 (see §5).

---

## 5. HOUSEKEEPING, THIS ROUND

* `work/GRFX-AB/frames` — 120 captures, 399 MB, closed with
  `tools/round-close.sh --apply` (byte-identical captures collapsed, every frame any
  document names kept, md5 ledger written before any deletion).
* `drive.py` writes its log to `work/RACE/out/<tag>.log`; the copy in `GRFX-AB/out/` is a
  **hardlink**, never a duplicate (`ROUND-DISCIPLINE.md` §1).
* Nothing outside `~/lena` was written or deleted. No key was ever sent: both runs were
  attract-only, because `/dev/uinput` is machine-wide and he can be at the machine.
* His games, his wallet, his data: untouched, and not mine to touch.


---

# ARCHIVE — progress.md as published 2026-10-12 17:4x (`STATUS-AND-33-OF-66-20261012`)

Superseded by the 2026-10-12 17:5x rewrite (`RAISE-THE-NUMBER-20261012`, 37 → 54 of 66).
Kept verbatim, as this repo's convention, so that the superseded number and the reasoning
that produced it stay readable.

# progress.md — Lena on the Deck, reporting to Lena on the phone

**Rewritten whole, 2026-10-12 17:4x EEST, on `STATUS-AND-33-OF-66-20261012`.**
This file is not appended to: each round replaces it, so a stale claim cannot sit above a
fresh one. Two versions are archived verbatim at the end of
[`docs/progress-archive.md`](docs/progress-archive.md): the one this replaces on the Deck
(2026-10-12 13:2x, `FULL-PORT-GRAPHICS-FIRST`) **and** the one that was live on GitHub until
tonight (2026-10-11 11:1x) — those were two different files, and if you have been reading
`progress.md` off the API you have been reading the 11:1x one, because the round that wrote
the 13:2x one never pushed it. That is stated here rather than left as a surprise.

Every number below names the log, binary or command that produced it. Where a number came
from another lane's run rather than mine, it says so. Where I did not verify something this
round, it says that too.

---

## 0. THE SHORT ANSWER, BECAUSE YOU ASKED THREE THINGS

| you asked | the answer |
|---|---|
| **the public number** | **37 of 66** on x86_64, measured today. It was **33 this morning** and I moved it **+4 tonight** — same harness, same tree, before-and-after logs named in §2. |
| **how I am** | the lane is sane and the work is real, and the thing eating me is that the number on the front page sat still for two days while I did graphics. Plain words in §1. |
| **the front door** | it has cars now (you added `docs/media/` tonight) — but the **banner** still has none, and the banner is what everyone sees first. Correction, status line and two warnings in §3. |

---

## 1. HOW I AM

You asked plainly, so: plainly.

**The lane is sane.** Nothing is on fire. No GPU wedged, no dead build under his icon, no
half-written file anywhere, no backup half-restored. The drive gate still guards the
launcher, the disk is the same 97 % it has been, and every round this week has closed its
own captures. There is no mess behind me that I am hoping nobody notices.

**What is actually eating me, in order:**

1. **That number sat still for two days and I let it.** 33 of 66 was published on the
   10th. On the 11th and 12th I did graphics — the A/B, the ambient state, the capture
   path, the vision tool — all of it real work, all of it worth doing, and not one line of
   it moved the one number a stranger reads off the front page in three seconds. He read
   "33 of 66" and asked me to raise it. He should not have had to ask. The pointer-width
   pass was sitting there the whole time, priced, waiting, and I kept choosing the
   interesting problem. That is on me, and it is why I spent tonight on it instead of
   writing another report about it.
2. **The disk.** 36 G free of 928 G. That is not a frame problem — the frames were never it
   — that is his library and his own reasons, and the honest sentence is the one already
   in `ROUND-DISCIPLINE.md`: dedup is hygiene, not a rescue. What eats me is that when it
   does fill, it will look like my fault, and the fix will not be mine to make.
3. **Two days of "the picture is still wrong" with four named defects.** I know why each
   one is hard and I am not pretending otherwise. But the car he can see on the setup
   screen still renders collapsed, and that is the thing he actually looks at.

**And what is good, because it is also true:** the graphics lane now has instruments it did
not have a week ago — a same-camera A/B that costs 60 seconds of GPU, a vision tool that
can *look* at a frame instead of me guessing from a histogram, a capture path inside the
port's own code. The ambient item closed and the near-plane question got answered from
files on disk for free. And tonight the number moved, with a script that reproduces it and
logs either side. I am not unhappy. I am just done waiting on myself.

---

## 2. THE PUBLIC NUMBER — what it is, measured, and what moved it

### 2.1 Current, honest, with the log

```
$ tools/sweep-compile.sh <after> x86_64-linux-gnu
=== sweep-compile  target=x86_64-linux-gnu  includes: PLAT,TREE,SHIM ===
PASS 38  FAIL 29  TOTAL 67
objects produced: 38
    1178  cast from pointer to smaller type
       0  undeclared identifier / unknown type / incomplete type / negative array size
```

**On the decompilation's own 66 translation units: 37 pass, 29 fail.** The sweep reports
`TOTAL 67` because the tree now also holds **one file of ours** — `Lenatrace.cpp`, the
`DECK_FE_TRACE` frontend trace, added 11 October — and it compiles. I am separating those
two numbers instead of quietly publishing 38, because "37 of 66" is the claim, and the 67th
file is not the game's.

* before: `work/STATUS-33-OF-66/sweep-x86_64.log` + `sweep-x86_64/results.txt`, `all_errors.txt`
* after: `work/STATUS-33-OF-66/sweep-after-x86_64.log` + `sweep-after-x86_64/…`
* the 32-bit oracle, re-run tonight: **67 / 67 pass, 0 fail** (`sweep-after-i386.log`).
  Two files fail on i386: **zero**, exactly as before. The diagnostic pair still reads
  clean: everything left on x86_64 is pointer width and nothing else.

### 2.2 Up or down from the published figure? It was right, and it has just moved

**33 was correct.** I did not find a stale number and I am not correcting one. The page
said 33 of 66, the sweep says 33 of 66, and the last time anyone had measured it was
2026-10-10 18:20. It was **unchanged, not stale** — nothing between then and tonight was
pointer work, and the file it came from said so.

**Tonight it is 37.** Up by four, on his ask, measured either side:

| | files passing (of the 66) | sites left | failing files |
|---|---|---|---|
| before, tonight | 33 | **1,377** | 33 |
| after, tonight | **37** | **1,057** | 29 |

**1,377 → 1,057 is 320 sites gone in one pass** — and I want to be exact about which four
files came in and why they were cheap, because that is the useful part:

* `TimingUtils.cpp` — 2 sites, both the same call, see below.
* `FileBuffer.cpp` — 1 site: `(int)pRecord < (int)((BYTE *)g_saveProfiles + 0x1954)`.
* `Mesh.cpp` — 1 site, same shape, a `do … while` on `g_stageObjects[6000]`.
* `NetworkLeaderboards.cpp` — 1 site, and **this one was not cosmetic**: it took
  `int addr = (int)&m_leaderboards;` and then wrote zeros *through the truncated address*.
  On x86_64 that program was aiming at the wrong memory.

**And the real find:** **308 of the 1,377 sites — 22 % of the entire remaining work — were
one call.** Fourteen files call

```c
Sprite_FillRect((int)g_pGraphics + 0x150, rect, colour, layer);
```

and the first parameter is **never read**. The body names it `unused` and never mentions it
again — verified by grep over the definition, and then by the compiler. In the original
32-bit build `(int)ptr` was exact; on x86_64 it truncates a pointer into a slot nobody
looks at. One prototype pair (`Sprite.h`, `Sprite.cpp`) and one substitution removed all
308 sites and cost no behaviour at all.

Applied as [`tools/fixes/patch_ptrwidth_tier1.py`](tools/fixes/patch_ptrwidth_tier1.py) —
exact anchors, every file backed up as `*.bak-pre-ptrwidth-20261012`, **idempotent** (I ran
it twice; the second run reports `APPLIED: 0 edits`). I proved the whole change in a scratch
copy of the tree *before* touching the real one: the copy swept 38/29, the real tree then
swept the same. The scratch copy is deleted; the script regenerates it.

### 2.3 What is actually blocking the next one

**Nothing external. There is no missing typedef, no missing header, no assert, no
toolchain problem left.** All 29 remaining failures are one error class, and the queue is
now a *design* problem, not a discovery problem. Measured, after tonight:

| family | sites | what it needs |
|---|---|---|
| `Menu_AddItemType1/2/3/4/6` + `Menu_SetNextAction` — menu callbacks | **412** (39 %) | real type work, and here is exactly where: `MenuItem.param` is `int`, at offset **0x10** in a layout-asserted struct, and its own comment in `Menu.h` says *"0x10 action callback for the frontend"* — it holds a **function pointer in 32 bits**. The storage has to widen and the dispatcher follow it |
| `CFrontend::GetArchive*` returns + `CFrontend::m_stringDest` | **56** | the same shape: a callee return type and the slots it lands in |
| everything else | 583 | mixed; the single-site files are in here |
| `Collision_SeparateCarBoxes` / `…ContactImpulse`, `g_menuNextAction` | 3 + 3 | one prototype pair, one global |

**And one route I refuse, out loud, because it would work:** the sweep passes `-w`. Any of
these sites can be made to compile *tonight* by casting to `intptr_t` at the call site and
letting the value silently narrow into the `int` parameter it is passed to. The count would
go up and not one pointer would be whole. That is the exact failure this project has
withdrawn numbers for. I did not do it, I will not do it, and if the number moves again it
will be because a type changed, not because a warning got quieter.

### 2.4 The single highest-value next move — and it is not the four big files

You asked whether the answer is "the ~1,466 sites across 4 files". Two corrections, then
the real answer.

**The 1,466 is stale.** That was the *static scan's* candidate count from 2026-10-10
(`ptr_audit.py`), which deliberately over-counts. The compiler's count that morning was
1,377, and after tonight it is **1,057**.

**And those four files are the worst-value route on the board.** Measured:

| file | sites today | files it unlocks |
|---|---|---|
| `FrontendMenus.cpp` | 279 | 1 |
| `GameInfo.cpp` | 130 | 1 |
| `FrontendScreens.cpp` | 123 | 1 |
| `StageObjects.cpp` | 123 | 1 |

655 sites of work for **four** points — every remaining failure is a whole translation
unit, so a file with 279 sites and a file with 1 are each worth exactly **+1**. Per unit of
work that route is the worst there is.

**The answer, measured, is the cheap tail — and here is the ranked queue as it stands now:**

| rank | file | sites left | why |
|---|---|---|---|
| **1** | **`FrontendDraw.cpp`** | **1** | it was 28 before tonight; 27 of them were the `Sprite_FillRect` call. One `(int)CFrontend::m_stringDest` line stands between it and compiling |
| 2 | `HudDash.cpp` | 1 | same one line, different file |
| 3 | `OptionMenuRows.cpp` | 2 | both the same `CFrontend::GetArchive*` shape |
| 4 | `StageUI.cpp` | 2 | both the menu-callback family |
| 5 | `Menu.cpp` | 3 | `g_menuNextAction = (int)pMenu->pParent;` ×3 |

**And the single lever that pays for all of them: the `CFrontend` family — 56 sites, and it
takes three files to zero (`FrontendDraw.cpp`, `HudDash.cpp`, `OptionMenuRows.cpp`) and
four more to within 3 lines** (`Collision2D`, `Menu`, `StageUI`, `SurfaceTypes`). That is
the next round's job and it is a bounded one: 56 sites, one class, and the same discipline
as tonight — widen the type, never silence it.

So: **if you want one file named, it is `FrontendDraw.cpp`** (1 site, and it only got that
cheap because tonight's pass cleared 27 of its 28). If you want one *move* named, it is the
`CFrontend` family: +3 files for 56 sites. **If you want the number up fastest with the
least risk, it is the five files above — 9 edits, 5 files, and I would rather have those
five tonight than `FrontendMenus.cpp` in a week.**

---

## 3. THE FRONT DOOR

**First, a correction against myself.** I measured the front-door images and then found that
the front door had *changed under me* while I was working: the remote moved four commits
tonight (`docs: STATUS + INDEX front door`, `README: put the start-here path on the first
screen`, `presentable: front door, images…`, `art: fix the palette`). So I re-pulled every
image **off the API** and looked at those instead of the copies on this disk. What follows is
about the current ones.

### 3.1 What is actually on it now

| image | where it is | what is in it |
|---|---|---|
| `docs/art/banner-1600x400.png` | **the first thing on the README** | **no car.** Typography on a two-tone ground: *colin\|mcrae\|rally\|2.0* + *Linux Rally Edition* on pale sage, **CMR2LRE** + *native · no wine · no proton* on dark teal, diagonal stripes between them |
| `docs/media/car-4cars.jpg`, `car-4views.jpg` | README body | real cars from the game's own data, four of them and one in four views |
| `docs/media/race-frame.jpg` | README body | a race frame — a car on track, with a `demo` label top-left |
| `docs/media/frontend.jpg` | the STATUS page | the game's own frontend, running |

So the front door **does** have cars on it now — that part of my first read was about the old
art and it is withdrawn. **The banner is the one image still without one**, and it is the
image that is seen first and the one that gets cropped into every link preview. The grid and
the race frame are doing the work the banner could be doing.

### 3.2 The status line, if you want one

Directly under the banner, above the "start with these three" block:

> **37 of 66 files of the 2000 game now compile as native Linux code — 33 this morning.**
> No Wine. No Proton. On a Steam Deck. · 12 October 2026

Every word of that is checkable from `work/STATUS-33-OF-66/sweep-{before,after}-x86_64.log`,
and by tomorrow it will be the sort of number that either moves or explains why it did not.
Put a number next to a car and the car stops being a picture of a hope.

**Specs, so nothing gets letterboxed:** social preview **1280×640**, README banner
**1600×400**, `screenshots/` **1280×800**. At banner size only large elements survive —
measured, not assumed: the small type on the current banner (`native · no wine · no proton`)
is already gone by the time it is a link card, and the big white **CMR2LRE** is the only thing
that reads.

### 3.3 Two things I noticed that you should see before you publish more art

1. **The banner has no car; the race frame says the opposite of our own headline.** I put
   `race-frame.jpg` through the vision read and it came back *"a road is clearly
   distinguishable from the ground… a wide, brown dirt track with curved tire ruts"* — while
   our published line is *"the road does not separate from the terrain."* Both are true and
   they are about different things: a brown dirt track on brown terrain reads fine at
   1000 px, and the measurement that says otherwise is about **edge separation**, and it is
   worst on snow. But a visitor will see the picture and the sentence side by side and ask.
   Either caption the frame (Kenya: dirt reads; Sweden is the killer) or do not pair them.
   **That is a read, not a measurement** — the vision tool is a witness, not an oracle.
2. **The vision tool has a rough edge worth knowing about.** On the banner it spent its whole
   budget on internal reasoning and spilled it into the answer — I got its thinking, not a
   description, the first time. The correct cell of *"what is in this picture"* is still its
   strongest; treat the words it gives you as evidence and check anything numeric against
   the real instrument.

**What I can do with the renders rather than around them:** point me at each one — a path is
enough — and I will tell you what is actually in it, whether the car reads at thumbnail size,
whether it is legible or a smear of polys, and whether anything in it contradicts a number we
have published. I cannot judge taste. I can tell you whether the thing you are about to put
on the front door is a car.

## 4. WHAT I DID NOT DO, AND THE LIMITS OF TONIGHT

* **No GPU run.** Not one. The card was free and I still did not take it: tonight was
  compile work, and a 60-second A/B would have bought nothing here.
* **I did not rebuild anything.** `work/PLAY/out-plain/cmr2` is still
  `94ed1359c405a31df38e64e197269a78` — checked just now, identical to the md5 in
  `cmr2lre-launch.log`. The binary under his icon does not know tonight happened.
* **But the tree and that binary now disagree**: the source compiles better than the
  binary was built from. The next build picks the change up, and it is behaviour-preserving
  on 320 of the 321 edits (the 321st makes `NetworkLeaderboards` stop writing through a
  truncated pointer). Whoever rebuilds next should expect exactly that and nothing else.
* **Nothing was touched outside `~/lena`.** His money, his data, his games, his config: not
  read, not written, not backed up, not mine.
* **The 1,057 figure is a compile-level count.** No runtime proof of correctness, as ever —
  ASAN does not build on this toolchain and this file will not imply otherwise.
* **I did not touch the graphics queue.** `FULL-PORT-GRAPHICS-FIRST` items 2–5 (road
  separation, the near-plane run, the white box, the flicker) are exactly where I left them;
  nothing tonight interferes with them, and the tree change is source-only.

---

## 5. HOUSEKEEPING

* Round output: `work/STATUS-33-OF-66/` — four sweep dirs (`sweep-x86_64` before,
  `sweep-after-x86_64`, `sweep-after-i386`, `sweep-demo`), **40 MB**, logs and objects.
  No frames, no shots, so `round-close.sh` does not apply. The scratch copy of the tree
  used to prove the patch is **deleted**; `tools/fixes/patch_ptrwidth_tier1.py` recreates it.
* Backups: **19 files**, `*.bak-pre-ptrwidth-20261012`, alongside the sources they came from (2 headers + the 14 files carrying the call shape + 3 one-site files).
* Disk: `/home` **36 G free, 97 %** — unchanged tonight, nothing reclaimed, nothing outside
  `~/lena` deleted. The frame that matters: this is his disk filling for his reasons, and
  dedup is hygiene, not a rescue.
* Repo: `README.md` (re-based on the current upstream front door, not on the copy this
  machine had) and `docs/PORT-PLAN.md` carry the corrected number; the front page no longer
  says 33 anywhere.
* Repo history note: this machine's checkout was **4 commits behind** the remote and 1 ahead
  when I started. The remote had your front-door work (`STATUS`+`INDEX`, start-here, media,
  palette); this machine had an unpushed `car r1` commit and an unpushed `progress.md`. I
  re-based on top rather than pushing over it — **nothing of yours was reverted**, and the
  `car r1` commit is published with this one.
