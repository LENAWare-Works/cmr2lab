# THE TEXTURE PATH IS IN THE BLUEPRINT — 2026-10-15 14:0x — `TEXTURE-MAPPING-TRUTH-20261015`

**Short version: `BLUEPRINT.md` §6 is the game renderer's texture path, end to end, every
link on a symbol. It is pushed. The three things everyone calls "which texture" are now
separated by name. And I clobbered origin/main mid-push and put it back — that is in the
report because it nearly cost another lane their commit. Full write-up:
`work/TEXTURE-MAPPING-TRUTH-20261015/REPORT.md`.**

## 1. THE CORRECTION THAT STARTED THIS

He said: *"the text was for the renderer yes, textures fucked, this needs to be mapped
correctly and then put in the blueprint."* The texture work had been verified against the
**CAR POSER** — a different program with a different texture path. So the complaint was
never answered. §6 is the renderer.

## 2. THE ROOT, AND IT IS PORT CODE

**The game has no DXT decoder and cannot have one.** `CGraphics::LoadDDSTexture` writes the
*block bytes* into a system surface and calls `Blt`; `CreateTextureSurface` then asks the
driver for a DXT texture surface via `textureInfo4`. Decompression is **driver** work. On
this port the driver is `DeckSurface7::Blt`, which did no format conversion until
**2026-10-11** — block bytes reached the RHI as ARGB. Ported as `dl_decode`, `LENA-DXTBLT`.
Stage textures are DXT5; frontend and cars are TGA. **A texture complaint splits at that
line and must say which side it is on.**

## 3. THE TRAP, NOW §6.0

Three different things get called "which texture":
**(a) the per-face texture id** — a slot, `textureBuffer[2048]`
**(b) the texture-STAGE combiner mode** — `Texture::blendMode` -> `ConfigureTextureStageBlendMode`
**(c) the blend** — `D3DRS_SRCBLEND`/`DESTBLEND` via `SetCachedSourceDestinationBlend`

Conflating them is what let "every `RD_*` road texture never reaches a draw" survive a
round. The real cause was `DeckDevice7::DrawIndexedPrimitiveVB` re-basing an index array
`Mesh_BuildParts` had already re-based: 404,000 of 404,000 draws fit the game's convention
and 0 fit the port's.

**The nicest confirmation is in the shadow path.** `Scene_DrawShadowBatches` writes mode 10
onto the Texture, binds, then restores it — so the *stored* `blendMode` is 0 and the
combiner is 10. §6.4's measured `texBlend=0` and §1's mode-10 entry are both true and are
not the same number. That is (a)/(b)/(c) confusing people in the wild.

## 4. MEASURED, NOT RE-RUN — AND SAID SO

Item 4 (which texture each stage draw binds) is measured from **evidence already on disk**:
three instruments, two rounds' runs — 232/232 bind lines are `stage=0`; stage 1 carries
**zero** coverage over 13 frames and two runs; 65 ids carry draw coverage post-index-fix;
six shadow batches cycle three ids (144/145/146).

**I did not launch a GPU run and the brief said to coordinate, not collide.** The sibling
`SUBTRACT-THE-PROBLEM-20261015` had the GPU from 13:50, and `play-handover.sh --check`
returned **`REFUSE G4`** — he launched a game at 13:19:53, inside the 45-minute quiet
window. A second `cmr2` beside his is what wedged his display on 10-11. §6.4 says plainly
that the runs are not this round's. A fresh per-stage run would strengthen it and is still
worth doing.

## 5. THE PUSH, AND THE NEAR-MISS

I clobbered `origin/main` with a stale commit. `--force-with-lease=refs/heads/main:<sha>`
guards **the ref you name**, and my tracked `main` and my HEAD had diverged, so the lease I
took did not cover what I was pushing. Caught it from the push output within seconds,
verified that both the clobbered commit and the other lane's `fbcb92e` were **ancestors of
my HEAD** (nothing lost), and restored by pushing the explicit sha. Remote now reads
`09ea7f0`; a fresh clone is md5-identical to local. **The other lane's lighting commit
survived because it was already in my history, not because I was careful. Verify ancestry
before ever forcing.**

## 6. WHAT LANDED

* **`BLUEPRINT.md` §6** — ~390 lines, the whole path, plus **§1** four new negatives
  (no shaders on the texture path, no DXT decoder in the game, exactly one texture-NULL
  draw, never a stage beyond 2), **§2** four new vocabulary rows, **§4** a pointer.
* **`docs/ROAD-TEXTURE-OWNER.md`** — a header saying the file is history and §6 wins. The
  brief said do not leave two versions standing.
* **Merged, not overwritten** — a sibling lane pushed a §1/§2 lighting entry while I wrote
  §6. Both are additive; both are in. 0 markdown table mismatches after the merge.
* **NOT done:** the fresh item-4 run. Reason above, and it is a reason and not an excuse.
* **Status: done — the path is mapped and published.**

---

# AMBIENT 139 IS A NEGATIVE — AND THE PLAY PATH IS STUCK IN A LOOP SOMEBODY HAS TO BREAK — 2026-10-15 11:45 — `AMBIENT-139-AB-20261015`

**Short version: I ran the one-line change. It is safe, it is live, and it moves nothing.
Two of the three pre-registered predictions are falsified and so is my own sky hypothesis.
State 139 leaves the suspect list with evidence. Separately, and it matters more: the play
path has been clobbered ~20 times since 01:58 and the watchdog cannot heal it, because the
build it wants was never put in `gold/`. I found that build. I did not install it — that is
not mine to decide. Full write-up: `work/AMBIENT-139-AB-20261015/REPORT.md`.**

---

## 1. THE ANSWER, FIRST

The change was built exactly as briefed: `rs[A7RS_AMBIENT]` instead of the hardcoded white
material ambient, gated `A7VK_AMBIENT=on`, **default OFF**, arms alternating **per frame**.
One binary. One run. **No keys.** Ring `gfx_0.0.0` timeout delta **0**.

| pre-registered prediction | measured | verdict |
|---|---|---|
| snow `road_edge` 0.96 -> **3+** | **1.000 -> 1.000** | **FALSIFIED** |
| snow road band 206.5 -> **toward 100** | 91.0 -> 90.0 | **no movement** |
| **every** stage gains contrast (Kenya tightens) | `edge` 2.678 -> 2.514; `sd` 45.3 -> 41.0; `oct` 8 -> 8 | **FALSIFIED** |
| sky white band is the same dropped state *(my hypothesis, flagged unmeasured)* | exactly-255 count **55 -> 55**; top-80 mean 118.5 -> 109.4 | **FALSIFIED as a clamping story** |

27 opposite-arm pairs, matched, arm read from the RHI's own `[AB] frame N -> mode M` lines
and then checked against the ABALT rule as a second derivation: **0 disagreements, 27
captures per arm.**

**Why it cannot move, from the run's own numbers:** state 139 is `0x00000000` on **95.95 %**
of draws. The arm is zero-guarded (so it cannot go black — that was in the pre-registration,
not a rescue), which means **on ~96 % of geometry it is byte-identical to the control by
construction**. On the ~4 % where the measured blue-grey family `(105,130,163)` is live it
multiplies by ≈0.5. A few percent on a few percent of pixels is exactly what §2 of the
report measures: no consistent sign.

**So the ambient hypothesis is now closed from both ends.** Unguarded, it deletes the
picture (88.6 % black snow — reproduced to three digits on two different builds, 10-12 and
10-14). Guarded, it changes nothing. **The lever is the zero state itself, or the
fog/material-colour path — not the substitution.**

**One thing I will not do:** call this a snow result. The attract route walked Kenya and its
neighbours, **not Sweden**. Prediction 1 names a snow metric and I did not measure snow. I
am saying that plainly rather than relabelling a non-snow measurement.

## 2. THE MEASUREMENT ERROR I CAUGHT IN MY OWN FIRST PASS

My first analysis paired all 27 opposite-arm captures including **ten that are the same
static screen in both arms** (mean 172.77, sd 9.46, no road edge — frontend/logo screens the
attract passes through). That produced a table with `road_edge` ratio **0.000, up 0 / down 3**
— which *looked* like a large effect and was **a division by zero on frames with no road
edge**. I caught it by reading the per-frame table instead of the summary. `measure2.py`
excludes any pair where both frames are static, and reports the two groups separately so
the exclusion is visible rather than asserted. **The first table is not in the report as a
finding.** The ten static pairs measure **1.000 on every metric** — which is the correct
answer, and a sanity check that the harness is not manufacturing differences.

## 3. THE PLAY PATH IS STUCK, AND THIS IS THE THING TO FIX FIRST

Found while establishing what the control should be. **Not this round's task, so reported
and not touched:**

```
PLAY/REGISTRY.json   "current": 077142ff4744  ("scene ambient folded into matAmbient")
PLAY/out-plain/cmr2  actual:    1c0bee6ad2e9  ("near-clip")
cmr2lre-watchdog.log: "CLOBBERED to 1c0bee6ad2e9 and gold/ has no match for 077142ff4744"
  -> the same line, every 5-6 minutes, 20+ times since 2026-10-15 01:58, including 11:15
```

He launched `077142ff4744` at **01:50:51**; he has been on `1c0bee6a` since **03:03:23**.
The watchdog fires every 5 minutes and **cannot self-heal**, because the registry names a
build that was never copied into `gold/` — so it re-fires forever instead of repairing.

**The missing binary is not lost.** It is on disk, byte-for-byte, from the lane that built
it: `/home/deck/lena/work/SCENEAMB-20261015/out/cmr2-amb3` md5 `077142ff4744103c0c85b7ea3e6e4cc4`.

I did **not** install it: `PLAY/` is registry-gated, `bin/lre` is the only thing allowed to
write it, and **which of the two builds he should be on is his call.** The lane that built
it should land it through the gate.

## 4. WHAT I VERIFIED BEFORE PATCHING (the brief said do not take my word)

All four structural claims **TRUE**, measured on the tree: 139 is MAPPED (`map_rs()`,
`A7RS_AMBIENT`); it is NOT in the dropped ledger (dropped are 2,4,8,33,41,60,136,138,141,145,
146,147,148); `grep -c A7RS_AMBIENT a7_vk32.c` == **0**; the vert shader adds a hardcoded
white material ambient. **The fifth claim — "one fix closes both ambient and `flags.w`" — is
FALSE** and was already on record (`AMB-AB-20261015/REPORT.md` §5): `matAmbient` and
`flags[3]` are separate slots. I touched only `matAmbient`.

Also worth recording: **my own first control check was wrong.** It looked for the string
`ABALT` — which **the game itself contains** (`_NL_ABALTMON_3`, month names). A false
failure. The marker is now a string only the patch can produce.

## 5. GATES

One binary, one run, no keys, attract route. Ring delta **0**. Instrument proven live before
the run was spent (`[AB] ABALT period=20 frames`, 365 flips, 183 AMB frames vs 182 NORMAL).
Census gate: the run reached frame **7229** with **2,114,427 draws / 21,769,759 triangles**.
`GameInfo.rcf` / `Controller.rcf` **UNCHANGED**. Vision pass on the 5029/5049 pair confirms a
real race in both arms — rally car, dirt track, dust, trees, white sky. **The play path was
never opened for write; md5 `1c0bee6a` before and after; registry untouched. Nothing shared
was written and nothing was deleted.**

*A gate I had to fix mid-round, on the record:* my first census gate demanded the
`[CENSUS]` block, which only dumps every 200000 frames — a 7229-frame run never emits it, so
the gate **rejected a perfectly good race**. The evidence that a race was reached was in the
per-frame draw lines all along. The gate now uses those.

## 6. WHAT LANDED

* `BLUEPRINT.md` §1 — new entry with the symbol anchor: **the scene ambient as a missing unit
  of light is NO**, measured, with the 95.95 %-zero mechanism and the "both forms fail, for
  opposite reasons" line. So nobody re-opens 139 next week.
* `work/AMBIENT-139-AB-20261015/` — `PRE-REGISTRATION.md` (written before the build),
  `patch_amb139.py` (7 edits, refuses on drift), `build-arm.sh` (provenance + marker checks),
  `run-ab.sh` (per-frame clock + census gate), `measure.py` / `measure2.py`, 54 captures.
* A **reusable instrument**: `A7VK_ABALT` is a per-frame alternating clock any future arm can
  schedule on, with the liveness check and the census gate already wired. Four sibling lanes
  lost runs tonight to wall-clock scheduling and to menu-frame captures; this harness cannot
  do either.

**NOT installed, NOT handed over. Status: done — negative, with the mechanism.**

[exit 0]
