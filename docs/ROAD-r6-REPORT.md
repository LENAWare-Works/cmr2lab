# ROAD-r6 — the MENUTEX-style instrument, run against the RACE's 3D draws

2026-10-11, 21:47–22:0x EEST. Round of the item I wrote at the end of ROAD-r5 §9.
**Two GPU runs, both with `ring gfx_0.0.0 timeout` delta = 0.**

---

## 1. THE ANSWER, FIRST

**The road is not invisible because the port misdraws it. The road is invisible because
the fragment colour IS the texture, every terrain texture in use is in one colour family,
and the one per-vertex input that could have separated road from verge never reaches the
shader.**

Measured, on the race's own indexed 3D draws (FVF 0x2d2, 4.3 M draws, no keys):

| question | instrument reading |
|---|---|
| do the stage's terrain draws bind textures at all? | **yes — 100%.** 93,999 of 93,999 in the first window; `tex0bound == draws` in **every** window of both runs; `noTex0=0` throughout |
| a second texture (shadow/cube)? | **never.** `tex1bound=0`, `stage1on=0` in every window, both runs |
| the stage ops and args | **one signature:** `s0(op=4 MODULATE, a1=1 TEXTURE, a2=2 DIFFUSE)`, `a0(op=4, a1=1, a2=2)`, `s1(op=4)` — 4,124,4121 twice, nothing else |
| the material diffuse | **`0xffffffff` for every single draw** (93,999/93,999 … 556,382/556,382, 24 windows). With `MODULATE(TEXTURE, DIFFUSE)` this means the combiner's diffuse argument contributes *nothing*: the fragment colour is the texel |
| the vertex diffuse | **rich and unused.** 258,554+ distinct values in one window (e.g. `ffacbac7`, `ffa3b1c0`, `ff6a81a1` — cool blue-greys). It is what the game's own pre-lit terrain vertices carry |
| the port's combiner prediction | `predM = texel × material diffuse` → warm olive-brown: `7b731b` `946521` `945d1e` `916320` `817626`. `predV = texel × vertex diffuse` → dark: `2c230c` `333a11` `764d19` `5d4819` |
| which one is on the screen | **predM.** See §4 — the framebuffer's terrain field measures **(116,89,28) / (124,91,29)**; the census's own texture `745a12` means **(116,90,18)**; the predV family (44,35,12 / 51,58,17) is not there |
| uv0 | clean: `nan=0 out[0,1]=0 u[0,1] v[0,1]` — 14.9 M vertex samples across the run, zero exceptions |
| projective texture transform | **not wanted by the game.** `s0/t24` (TEXTURETRANSFORMFLAGS) = 4,745,057 calls, `last=0` (D3DTTFF_DISABLE). The port's unimplemented projective path is a real gap but it is *not* this bug |
| texcoord set | `s0/t11` (TEXCOORDINDEX) = 4,745,057 calls, `last=0` → stage 0 wants coord set 0, which is what the port uses |

And the piece of state that makes the whole thing land:

```
[CENSUS] DROPPED render states: ... 141:287595(last=1/0x1) 145:287595(last=0/0x0)
```
`141 = D3DRENDERSTATE_COLORVERTEX` — **the game asks for vertex colours 287,595 times** and
sets it TRUE. `145 = D3DRENDERSTATE_DIFFUSEMATERIALSOURCE` — set to `D3DMCS_MATERIAL (0)`,
which is the *lighting* source, not the combiner's. **The port maps neither state** (both are
in its DROPPED list), and `a7vk3d.vert` hardcodes `flags.w = 0` = "material diffuse"
(`a7_vk32.c:2752`, `b->flags[3] = (g_ab_mode == AB_VCOL || AB_VCOLOP) ? 1.0f : 0.0f;`).

So `D3DTA_DIFFUSE` in the port is a global white, not the vertex colour D3D would have
supplied. That is the measured mechanism behind "one uninterrupted warm field": every
terrain triangle gets texel × white, and the game's own per-vertex shading — the thing that
separates road from verge, sunlit from shadowed — is discarded before the rasteriser.

---

## 2. THE CONTROLS (they are the reason the above is a proof and not a story)

Both in run 1, inside the same race, frame-labelled by the port's own counter:

| arm | frames | what the swapchain showed |
|---|---|---|
| `skip3d` (all 3D batches dropped at submission) | 2900–4300, snaps 3100 / 3600 | **100.00% a single colour, `0x9cb4ac`, 1 distinct colour** — the game's own clear colour and *nothing else*. The race picture is 100% 3D content: no 2D, no HUD, no backdrop art of its own |
| `notex` (textures unbound on the 3D path, t0 = white) | 4300–5700, snaps 4600 / 5200 | **99.77% `f7f7f7` / 100.00% `ffffff`**; row means (247,247,247) and (255,255,255) |
| `notex`, second run, different stage | run 2 frame 5790 | **100.0% white, `uniq_sample=1`, row means (255,255,255)** — replicated |

With `MODULATE(texel, diffuse=white)`, unbinding the texture *must* yield white — and it
does, on two different stages in two different runs, over the whole frame. That is the
independent confirmation that the terrain's colour is the texture and that the terrain
covers the frame.

**Honest correction to my own pre-run expectation.** I wrote in the checkpoint that the
census would show the arms (`hasTex0=0` in a notex window). **It cannot, and I was wrong**:
the deck-level census counts draws *before* the RHI builds batches, so `AB_SKIP3D` and
`AB_NOTEX` are invisible to it — every window counts the same draws with tex0 bound. The
arms are labelled by the port's own frame numbers (`[AB] frame N -> mode M`) and by the
frame-numbered captures, which is how the table above is built.

---

## 3. THE CENSUS, as the port printed it

One summary per 500 frames; the race windows of run 1 (the stage the road question is
about — warm olive-brown family) and of run 2 (a *different* stage, olive-green family, same
structure):

```
run 1 windows 1..7   frames 2719..6263   (the warm stage)
  draws 93999 188625 212435 202991 220637 128550 79043      tex0bound == draws, noTex0=0
  light 68763 143151 159181 151831 166540  94619 57565     (73% of draws)
  zwrite == light, blend == draws, atest == draws, fog = 0, oor = 0
  ops: s0(op=4,a1=1,a2=2) + s1(op=4) + a0(op=4,a1=1,a2=2)  [two signatures, 41244120 / 41244121]
  matdiff: ffffffff:<all of them>
  tex0 (top, with each texture's own upload-time mean):
     163 256x256 mean=41421b   158 256x256 mean=343520   95 128x128 mean=745a12
     157 128x128 mean=6a3a16   155 128x128 mean=643413   159 256x256 mean=52391d
     162 128x128 mean=443908   161 256x256 mean=43430d   160 256x256 mean=614306
  -> one family, B lowest in all nine, R,G within 0x34..0x74
  uv0 281997..661911 samples per window, nan=0, out[0,1]=0
```

```
run 2 windows 9..16  frames 7000..11000  (a DIFFERENT stage, olive-green)
  draws 480972 603522 513580 581935 628200 582966 474010 556382   tex0bound == draws
  same ops, same matdiff=ffffffff, same uv0 nan=0/out=0, light ≈ 78%
  tex0: 480 128x256 mean=535531  479 mean=5f6531  481 mean=585f42  486 mean=6b5e36
        487 mean=807f34  485 mean=736329  470 mean=514c30
  -> again one family (G≈R, B lowest), a completely different texture set, same structure
```

```
(census whole run, run 1, from the backend's own counters)
  device draws=4312153  backend draws=6371511  tris=86717822  textureUploads=662
  xformSets=1994697  lightSets=464061  clamps=0  refusedFvf=0
```

**The whole-run TOTAL block never printed** — `drive.py` kills the game and my `atexit`
handler went with it. The per-window summaries cover the same ground and are what §1–§3
quote; §7 records it as a known gap in the instrument, not a silent one.

---

## 4. THE PREDICTION vs WHAT LANDS IN THE FRAMEBUFFER

The row means of the frames, against the census's own predicted palette (no new run — the
frames are the swapchain's, the palette is `a7_eval_texop`'s):

| frame | top 20% (sky) | mid band 320–480 | bottom 40% |
|---|---|---|---|
| `R5SHIP.01_t60` (shipped binary, warm stage) | (146,153,157) | **(116,89,28)** | **(124,91,29)** |
| `R5SHIP.03_t100` | (123,102,83) | (111,84,52) | (122,73,23) |
| run-2 `05_t160` (olive-green stage) | (138,147,176) | (122,115,64) | (175,166,148) |
| **`notex` control** `r6.ppm.4600` | (247,247,247) | (247,247,247) | (247,247,247) |
| **`notex` control** run-2 `03_t100` | (255,255,255) | (255,255,255) | (255,255,255) |

* census texture `745a12` = **(116,90,18)** → the shipped binary's terrain field is
  **(116,89,28)** → *identical in R and G, 10/255 apart in B*.
* census predM top = `7b731b`=(123,115,27), `946521`=(148,101,33), `817626`=(129,118,38) →
  the same band as (116,89,28) / (124,91,29).
* census predV top = `2c230c`=(44,35,12), `333a11`=(51,58,17), `5d4819`=(93,72,25) →
  **dark, and the field is not dark.**

Exact-value counts are 0 px for every palette entry, and that is expected rather than
troubling: `pred` is a per-vertex value from a colour snapshot, while the framebuffer is
bilinear-filtered across a mip chain. The claim here is a band/mean claim, and it is the
honest one to make at this scale — the *unlit* combiner prediction (the vertex shader
multiplies `base` by its `lit` term for 73–78% of race draws) cannot be a pixel-exact
prediction anyway.

---

## 5. WHAT THIS SETTLES, AND WHAT IT DOES NOT

**Settled at fragment-input level (nothing upstream of the fragment is left implicated):**

* the terrain draws are textured, correctly, with UVs in the unit square and no projective
  transform requested or needed — the "textures are not sampled / UVs are wrong / the
  projective path is missing" family of hypotheses is dead for stage 0;
* stage 1 (the shadow/cube sampler) is never enabled in a race;
* the material diffuse is white, so the combiner is a pass-through of the texel;
* the fragment's diffuse argument is the material, not the vertex colour, and the game sets
  `D3DRS_COLORVERTEX=1` 287,595 times for the port to ignore;
* every terrain texture in use is inside one colour family — so "the road does not differ
  from the terrain it runs through" is, at input level, **true by construction**: there is no
  second colour family on screen to be a road.

**Not settled:**

* **the `lit` term.** 73–78% of race draws have `D3DRS_LIGHTING=1`; `a7vk3d.vert` does
  `base.rgb *= (ambient + emissive + Σ lightDiffuse·NdotL)` and that term has never been
  measured on this box. It is the last unmeasured input between the prediction and the pixel.
  It is also the standing explanation for one thing the census now makes sharp: two of run
  1's most-used terrain textures (`163` mean `41421b`=(65,66,27), `158` mean `343520`=(52,53,32))
  have **G ≥ R**, i.e. they should read as green, and the frames of that stage read
  **green = 0.0–0.5%**. A warm `lit` would convert exactly that. Run 2's olive-green stage
  does show green (19–26% in its frames), so this is stage-specific and unresolved, not a
  contradiction.
* **a `vcol` race frame.** See §6 — my schedule missed it by ~400 frames.
* the near-plane blow-up (ROAD-r5 §7 item 2), untouched.
* a player race (still only the attract demo).

---

## 6. MY OWN ERRORS THIS ROUND, STATED PLAINLY

1. **The arm schedule in run 1 was mis-timed, and it cost the `vcol` race frame.** I placed
   `2900:skip3d, 4300:notex, 5700:vcol` on the assumption that the race occupied
   ~2900–7100 frames. The race in that run was frames **2719–6263**, so `skip3d` and `notex`
   between them covered it and `vcol` (5700–7100) landed on the tail of the race and the
   return to the frontend. I got two decisive controls *because* of the mistake and missed
   the one arm that speaks to the fix. The `vcol` race capture `work/WHITE-BOX-UNDER-CAR`
   recorded as missing at 12:1x is **still missing**.
2. **Run 2's arms landed on a different phase of the loop** (`vcol` 4000–5400, `notex`
   5400–6200 hit a stage, captured at frame 5790 and useful as the notex replication; the
   olive-green stage then ran from 7000 with no arm on it and no frames captured there).
3. **The attract demo does not run the same stage at the same time in two runs.** Run 1:
   warm stage 2719–6263, then a grey/light stage to 11000. Run 2: a grey/light stage
   2771–6974, then an olive-green stage 7000–11000. Run `R5SHIP` (no arms at all): warm
   stage from 2720 to at least 11400. Three runs, three different orders. **Any future arm
   schedule must be frame-labelled and census-classified, never wall-clock; and a
   "did we hit the race" check has to be the census's texture family, not the clock.**
4. I predicted the census would reveal the arms (§2). It does not.

---

## 7. PROVENANCE

```
instrument   work/ROAD-r6/patch_stgtex.py  -> port/rhi/deck_dd7.cpp  (LENA-STGTEX)
             backup deck_dd7.cpp.bak-pre-stgtex-20261011-214648
             object deck_dd7.o (was 08:53, kept as deck_dd7.o.bak-pre-stgtex-20261011-214634)
lab binary   work/ROAD-r6/out-r6/cmr2   md5 4fd46919fb5a004f8802c9627e4bb3a0  17798396 B
             = his link inputs (work/PLAY/obj-plain/*.o, work/PLAY/out/obj/*.o, rhi/a7_vk32.o)
               with ONLY rhi/deck_dd7.o rebuilt
his binary   work/PLAY/out-plain/cmr2    md5 9ecbf87bb8650a3883b188f4e77890e4
             strings check: the 08:53 object contains NONE of LENA_MENU*/LENA_STGTEX;
             the rebuilt one contains LENA_MENUDRAW/MENUTEX/MENUSKIP3D/MENUUNLIT (all
             env-gated, inert when unset) + LENA_STGTEX
gate         build-play-lre.sh's own drive-bound check on the lab binary:
             Physics_UpdateRateHold=1, Car_UpdateEngineNoteFalloff=1 (not the 08:39 dead build)

run 1        work/ROAD-r6/r6_run.sh  log work/ROAD-r6/r6_launch.log
             A7VK_AB="0:normal,2900:skip3d,4300:notex,5700:vcol,7100:normal"
             A7VK_SNAP=3100,3600,4600,5200,6000,6500,7400,7800,8400,9200
             keyless, r5's SEQ, timeout 300, exit 0
             ring gfx_0.0.0 timeout: 0 before, 0 after  (delta 0)
             frames work/ROAD-r6/frames/    instrument work/RACE/out/R6STG.log (1.3 MB)
run 2        work/ROAD-r6/r6b_run.sh  log work/ROAD-r6/r6b_launch.log
             A7VK_AB="0:normal,4000:vcol,5400:notex,6200:normal"
             A7VK_SNAP=3000,3600,4200,4700,5200,5600,6000,6500
             ring gfx_0.0.0 timeout: 0 before, 0 after  (delta 0)
             frames work/ROAD-r6/frames-b/   instrument work/RACE/out/R6B.log
tools        work/ROAD-r6/frames_cmp.py (r5's three road metrics), pred_vs_fb.py,
             stgtex_table.py  — pure bytes/collections, no numpy/PIL on this box
nothing was written into the game tree; no synthetic keys; no process killed that was not ours
```

## 8. THE SINGLE NEXT ITEM

**Make the game's own vertex colours reach the fragment, and capture a `vcol` race frame
from a run whose phase is read from the census.**

The instrument has now told us where the road went: the fragment gets `texel × white`, and
the game asks for `texel × vertex-colour` 287,595 times per run. The change is small and it
is already prototyped — `a7_vk32.c`'s `flags[3]` selects the vertex diffuse under
`A7VK_AB=vcol`, and the 12:07 frames show that arm repaints ~44% of the world and takes
green from 5% to 19%. What is missing is the one artifact that would make it a finding
rather than an arm: **a race frame on the vertex-colour path, framed against a normal frame
of the same stage**, plus the `lit` term measured (light colours, ambient, emissive) so the
prediction can be compared pixel-for-pixel instead of by band.

Design notes for whoever takes it, learned the hard way this round: schedule by *census
window*, not by wall clock; put the same stage in the same run at least twice
(normal → vcol → normal → notex), because the demo randomises the stage; and keep
`ring gfx_0.0.0 timeout` at delta 0 as the gate before any picture claim.
