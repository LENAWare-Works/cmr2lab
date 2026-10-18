# START HERE — FOR ANY AI AGENT WORKING ON CMR2LRE

You are not the first agent on this project. Two others have been on it for weeks.
Most of what looks like an unsolved problem is already solved, measured, and written down.
**Re-deriving it wastes GPU time, and on this project GPU time means someone's race dies.**

Read this file completely before you write or modify a single line.

---

## THE FIVE RULES, IF YOU READ NOTHING ELSE

1. **DO NOT TOUCH `work/PLAY/out-plain/cmr2`.** That binary is the one a human launches from
   his desktop icon. Building in a round directory is free. Moving that file is a handover,
   it must be announced, and it must not happen while he might be playing. It was reinstalled
   eight times in one evening once and it made a whole night of bug reports unreadable.

2. **MEASURE, DO NOT CLAIM.** "It compiles" is not a result. "It looks right" is not a result.
   A claim without a number, a log line, a diff, or a hash is not a claim — it is a guess
   wearing a claim's clothes, and it will be caught.

3. **ONE RUN, ONE VARIABLE.** The attract demo does not run the same stage at the same time in
   two runs. Arms must alternate **per frame** inside one run (the `A7VK_AB=flip1` pattern),
   never be scheduled against wall-clock time. Any pixel-paired A/B across two runs is invalid:
   measured, two runs of the same config differ by mean |d| = 169/765.

4. **CHECK THE BLUEPRINT BEFORE GREPPING.** `BLUEPRINT.md` §1 is the **negative space** — the
   things this game does not have. Searching source for a system that does not exist produces
   hours of confident nonsense. This has already happened. Repeatedly.

5. **WHEN YOU CHANGE SOMETHING, SAY WHAT YOU MEASURED BEFORE AND AFTER.** Not what you
   expected. Not what the spec says. What the number was, and what it is now.

---

## WHAT THIS PROJECT IS

Colin McRae Rally 2.0 (Codemasters, 2000, PC). A retail game with no source available, being
run **natively on Linux / Steam Deck** — no Wine, no Proton, no emulator.

The method: the game has been **decompiled** into ~122 C++ files (135,805 lines, 3,364
functions with address markers, 99.4% with real decompiled bodies). Those files are compiled
against a **replacement Direct3D 7 layer** (`port/rhi/`) that translates D3D7 calls to SDL3 +
Vulkan. The game logic runs as originally written; only the device is new.

The whole porting problem lives in the RHI. The game is not the question. The device is.

---

## READ THESE FOUR, IN THIS ORDER

| # | File | What it buys you |
|---|---|---|
| 1 | `BLUEPRINT.md` **§1 and §2 only** | The negative space and the vocabulary. **This is the single highest-value file in the repo.** It stops you looking for things that do not exist. |
| 2 | `docs/STATUS.md` | One screen. What works today, what does not, and whether you can use it yet. |
| 3 | `progress.md` | The most recent round, in the author's own words, including what she got wrong. |
| 4 | `docs/INDEX.md` | Every document, mapped. Use this to go get exactly what you need instead of reading everything. |

Then, as needed: `docs/S2-CENSUS.md` (the dropped-state list), `docs/ROAD-r6-REPORT.md`,
`docs/WHITE-CARD.md`, `docs/CAR.md`, `docs/C3D.md`, `docs/CONTAINER.md`.

---

## THE NEGATIVE SPACE — DO NOT GO LOOKING FOR THESE

These are **measured absences**, not opinions. Each one has cost someone hours.

- **NO shaders.** D3D7 fixed-function only. The game submits `D3DTLVERTEX` — vertices arrive
  already **transformed and lit**. There is no transform or lighting math for you to port. The
  game does both in software before it ever calls the device.
- **NO shadow maps, shadow volumes, shadow buffers, or stencil shadows.** `ShadowVolume`,
  `ShadowMap`, `StencilShadow` — zero hits across the tree. There is no shadow render state.
- **NO fog.** `D3DRS_FOGENABLE` (state 28) is **0 in all 24,369 calls** across a full stage.
  The enable path runs correctly and the track says no. Implementing fog in the RHI is dead
  code. **Do not build it.** (Prediction recorded and confirmed.)
- **NO dynamic lighting to reimplement.** The lit term was measured at a 1.0000 floor on 99.82%
  of vertices.
- **NO pluggable renderer.** The game's import table is `DDRAW.dll`, `DINPUT.dll`,
  `binkw32.dll` plus system libs. There is no `d3da.dll`, no `voodoo2a.dll`, no renderer DLL
  seam. The RHI must be finished **inside** the binary. (NFS had EA's Thrash; CMR2 does not.)

### THREE DIFFERENT SYSTEMS ARE ALL CALLED "SHADOW"

This is the biggest single source of wasted searching on this project.

1. **Frontend menu text drop shadows** — palette `g_colourShadowWhite` / `…Text` / `…Dim`,
   `FrontendMenus.cpp`. Nothing to do with the race.
2. **The car's own shadow** — `CarPhysics.cpp:414–519`. Octagon plus core,
   `Quad2D_QueueFixedTriangle(…, NULL, (Quad2D *)10)`. **Texture NULL by design.** Its colour
   and alpha live in the vertex. It is the ONLY texture-NULL draw in the whole game.
3. **Scene shadow geometry on terrain/foliage** — `Scene_AddShadowCaster`
   (`StageTiming.cpp:8011`) → `Scene_EmitNodeShadowGeometry` (`RallyData.cpp:6110`) →
   `Scene_BeginShadowBatch` / `Scene_EndShadowBatch` (`RallyData.cpp:6242` / `6265`).

If someone says "the shadows are wrong", **ask which of the three** before you open a file.

### "FLARE" IS A MISNOMER

`StageObject_SetForwardedFlareState` → `Graphics_SetFlareStateValue` → `SetRenderState(0x1c)`.
`0x1c` is `D3DRS_FOGENABLE`. It is not a lens flare. The decompiler's name is misleading.

---

## DEAD ENDS — ALREADY MEASURED, ALREADY CLOSED

Do not re-open these. Each has a number attached.

| Claim | Verdict | The number |
|---|---|---|
| "The stage textures are wrong/reversed/16-bit" | **CLOSED — was a real bug, fixed** | Stage textures are DXT5; the game hands **block bytes** to `Blt` and relies on the *driver* to decompress. Our `DeckSurface7::Blt` did no conversion until 2026-10-11. Decoder verified against ffmpeg: alpha 4096/4096 identical, RGB within 1 LSB. |
| "Road textures never reach a draw" | **CLOSED — wrong conclusion** | The real cause: `DeckDevice7::DrawIndexedPrimitiveVB` subtracted a vertex base `Mesh_BuildParts` had **already** subtracted. 404,000 of 404,000 indexed draws fit the game's convention; **0** fit the port's. |
| "Triangle strip, not indexed" | **CLOSED — I was wrong** | The format is `D3DPT_TRIANGLELIST` with an index buffer. Proven from the game's own decompiled loader (`Graphics.cpp:3209` calls `DrawIndexedPrimitiveVB`). A strip reading also renders a *recognisable* car — a plausible silhouette is not evidence. |
| "The GPU crash is the game" | **CLOSED — ours** | Two lifetime bugs in our own RHI: a freed imageView left in a cached descriptor set, and a command buffer re-recorded while possibly in flight. Fixed; ring-timeout delta 0 since. |
| "Fix the shadows with vertex colour" | **CLOSED — wrong** | Forced vertex colour through the fragment and it did **not** produce the road; it multiplies terrain by ~0.55 and is nearly flat (p90/p10 1.49–2.48 vs a 1.000 same-arm noise floor). Still a correctness bug, not the road's fix. |
| "Sweden white-on-white is the lit term" | **CLOSED — resolved, both were right** | Two different variables. The game hardcodes **material** ambient to 1.0 **and** sets **scene** ambient from track data. D3D7 multiplies them. The port drops the scene one. See `docs/AMBIENT-CONTRADICTION-RESOLVED.md`. |
| "The render is inside-out / culling is backwards" | **UNRESOLVED BUT NOTHING POINTS AT IT** | CPU owner-map rasterises without checking winding; GPU culls front-face. A front/back mix-up was named as a candidate and never confirmed. Do not assume it. |
| "Near-clip will fix the smear" | **IMPLEMENTED, NOT PROVEN** | Clip arithmetic verified by invariant (newv == 2 × straddlers, exactly) and clip-space bounds collapse from |ndcX| 2.8e7 to 49.0. But a drop-arm run kept ~73,000 distinct colours — **there is a real scene underneath**. Clipping is a diagnostic, not the fix. |

---

## WHAT IS ACTUALLY OPEN

As of the last published round. **Verify against `progress.md` before trusting this list** —
the live state is on the Deck, and this file can be stale by hours.

1. **The road does not read as a road.** Verified with eyes on the human's own build: the road
   *is* on screen, a broad dirt track with defined edges, curving away — it just does not
   separate from the terrain it runs through. 66–77% of race pixels sit inside a single luma
   octile; green ≈ 0%.
2. **White shadow decals.** The visible defect is flat white patches lying on the terrain, not
   a missing road. The decal uses the track texture as an **alpha mask** (`TEXTURE|ALPHAREPLICATE`)
   and those textures read all-ones alpha → opaque slab. Geometry also flattens to 66:1 NDC
   with 37.8% winding-inverted and 19.6% degenerate triangles.
3. **Presentation layer:** MSAA absent, anisotropic filtering absent **and the device feature is
   not enabled at all** (`dci.pEnabledFeatures` is never assigned). Frame pacing is hardcoded
   `VK_PRESENT_MODE_FIFO_KHR`. sRGB is deliberately UNORM — **do not change that**, D3D7
   blended in gamma space.
4. **Dropped render states.** The bucket `docs/S2-CENSUS.md` starts with: CLIPPING (136),
   COLORVERTEX (141), DIFFUSEMATERIALSOURCE (145), and `D3DRS_AMBIENT` (139) — which is
   *mapped and stored and read by nothing*. This is a **completeness** problem with a written
   spec, not a mystery.
5. **Object-space coordinates running to 2.5e36** inside the race, with finite but absurd clip
   `w`. Named, never diagnosed.

---

## HOW TO WORK ON THIS

- **The game's own code is the ground truth.** If a decompiled file and a measurement disagree,
  the decompiled file wins and the measurement is broken. This has saved a wrong conclusion
  more than once.
- **Never `pkill -x cmr2`.** That matches by name and kills the human's session. Kill by PID
  only, and refuse to run if a foreign `cmr2` is alive.
- **Keys go in through `/dev/uinput`, which is machine-wide.** A driver script between runs
  types into whatever window has focus. Do not run two.
- **Prefer the attract route.** ~30.5 s of idle frontend walks itself into a race with **no
  input at all**. It is simultaneously the cleanest and the safest recipe.
- **A device-wide GPU reset kills every context on the card**, including the human's game. A
  GPU fault that is ours is indistinguishable from "it crashed" from his seat.

---

## HOW TO REPORT BACK

Write to **`docs/DEEPCODE-NOTES.md`** in this repo, or open an issue. Either is fine. What is
not fine is a summary with no numbers.

Each entry: **what you measured, the before value, the after value, the file:line, and what it
does NOT prove.** The last clause matters more than the first three. Everything useful in this
repo's history includes it — including the corrections the author made against her own earlier
claims, which are kept in the record deliberately.

If you find that something in this file is wrong, **say so with the measurement.** This document
has been wrong before and was corrected the same day. That is the intended behaviour.

---

*A project that quietly deletes its own mistake is the thing we are not building.*
