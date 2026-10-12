# the five fixes, as scripts

These are the actual patch scripts that fixed the five things this project found in
the port between 2026-10-10 22:44 and 2026-10-11 11:02. They are here because a fix
that only exists in a commit message is not on the record; each one is idempotent,
backs up before it writes, and refuses to run if the source it is anchored on has
drifted.

They edit a **port tree that is not in this repository** (the native port's copy of
the decompiled game plus its RHI, `port/rhi/a7_vk32.c` and `port/rhi/deck_dd7.cpp`),
so they will not run against a fresh clone of `cmr2lab`. They are published as the
record of the change, not as a tool you can point at your own checkout — and the
matching prose is `docs/`, linked per row.

| script | what it fixed | the number that says so | written up in |
|---|---|---|---|
| `patch_gpu_lifetime.py` | a texture's Vulkan memory was freed while an in-flight frame could still be sampling it, and the upload path re-recorded **the frame's own command buffer** while it was in the queue — 6 edits in `rhi/a7_vk32.c` | every run died at ~30 s with a kernel ring timeout; after: 3 runs, **0 ring timeouts**, one of them 165 s / 8,124 frames / 3,299,876 triangles | `docs/GPU-LIFETIME-FIX.md` |
| `patch_combo_views.py` | the **second hole** in the same class: the descriptor-set cache was keyed on the texture id, so a draw could be handed a set naming an image view that had just been destroyed. 12 edits: key on the view, free the stale sets | the mechanism fired **710 times** in one 360 s run; that run: 20,662 frames, **6,344,401 mesh-FVF draws**, 72.7 M triangles, **0 GPU resets, 0 page faults** — previous rounds all published **0** mesh draws | `docs/DEATH-AND-LIGHT.md` §1 |
| `patch_dxt_blt.py` + `patch_dxt_exact.py` | the stage's textures are DXT5 and `DeckSurface7::Blt` was copying the **compressed blocks** into a 32-bit surface as if they were pixels; the blit now decodes, and `surface_fill_desc` reports a compressed surface as compressed (`DDSD_LINEARSIZE`) | ground band before: mean `(142,171,159)` — noise. After: `(115,90,15)`, against the terrain texture's own `(116,89,17)` | `docs/DXT-COPY-PATH.md` |
| `patch_idxfix.py` | `DeckDevice7::DrawIndexedPrimitiveVB` subtracted a vertex base that `Mesh_BuildParts` had **already** subtracted, so for any part whose base was not 0 the two cancelled and `startVert` was lost | of **404,000** indexed draws with a non-zero base, **404,000 (100.00 %)** fit the game's convention and **0** fit the port's; road texture `RD_GA` went `0.0` → **347,599.57 screens** of coverage | `docs/ROAD-TEXTURE-OWNER.md` |
| `patch_racetrace.py` | **our own mistake, and the reason this directory has a `loopcheck.sh` next to it.** Round 2's instrumentation used two real statements of game code as its `str.replace` ANCHOR, and its replacement block did not contain them — so applying it deleted the call that assigns the per-car driving loop's bound. Every binary linked after 08:39:06 could not move a car | restored: the loop iterates **3,650** times in 220 s, the physics steps at **~24 Hz**, car 0 accelerates to speed **101,958** and travels across the world. Before the restore: `steps=0`, car 0 speed `0`, for every run | `docs/DRIVE-LOOP-REGRESSION.md` |

## the two checks that keep the last one from happening again

| script | what it asks | how it answers |
|---|---|---|
| `tools/loopcheck.sh` | *which binaries in this workspace can drive a car?* | for every `cmr2` under `~/lena/work`: does `Race_UpdatePlayerViewAndDrivenCars` call `Physics_UpdateRateHold`? One `nm`, one `objdump`, per binary |
| `tools/drivecheck.sh` | *can **this** binary drive a car?* | the same question as a sourced helper, `cmr2_drives <bin>`: `0` drives / `1` dead / `2` cannot tell. It is what the Desktop icon now asks **before** it starts anything — and if no candidate passes, it starts nothing |
| `tools/build-play-lre.sh` | *may this build be installed?* | recompiles the stale translation units, links to a temp name, runs the drive check on the **linked artefact**, and refuses to replace the working binary if it fails |

A binary path in this workspace is a **name, not a build** — during one hour of
2026-10-11 another lane relinked the same path twice — which is why the gate asks the
file rather than trusting a hardcoded order or an md5 measured an hour ago. That is
measured, not stylistic: `docs/LAUNCHER-DEAD-BUILD.md` §1.

## the pointer-width passes (the count, not a bug)

These are a different species from the five above: they do not fix a symptom anyone saw on
screen, they **raise how much of the game compiles natively**. They are here for the same
reason — a number in a README is worth nothing without the edits that produced it.

| script | what it did | the number | written up in |
|---|---|---|---|
| `patch_ptrwidth_tier1.py` | 320 pointer-width sites, four files. 308 of them were one call shape — `Sprite_FillRect((int)g_pGraphics + 0x150, …)` in 14 files, into a parameter the function never reads | x86_64: **33 → 37 of 66**; sites 1,377 → 1,057 | `docs/PORT-PLAN.md` §3 |
| `patch_ptrwidth_tier2_s1.py` … `…_s4.py` | the five stages of the 12 October evening pass. `s1` corrects types that were wrong in the decompilation (`GetArchivePrimaryIDEntry` returning an `int` field through a `void *`; `MenuItem::param` holding a function pointer); `s2`, `s3b`, `s4` widen the interfaces (`ApplyTextureStageChange`, `Font_Unused`, `Collision_*`, `Sound_NoOpMusicCallback`, the ACM callbacks); `s3` is the bulk engine — it rewrites every remaining site and then **reverts, whole, every line the audit faults** | x86_64: **37 → 54 of 66**, 17 files, 1,178 → 385 sites | `docs/PORT-PLAN.md` §3, `docs/RTN-20261012-REPORT.md` |
| `tools/sweep-x86_64.sh` | the harness, same flags as `tools/sweep-compile.sh`, so any published count can be re-produced from the tree | `PASS 55 FAIL 12 TOTAL 67` (54 of the game's 66; the 67th unit is our `Lenatrace.cpp`) | — |
| `tools/ptrwidth-audit.sh` | **the guard.** Recompiles every unit with no `-w` and `-Wshorten-64-to-32`, so any 64-bit value landing in a 32-bit container is named with a file and a line. This is what stops a `(intptr_t)` cast from being used to inflate the count while narrowing straight back into an `int` | warnings on the tree **36 → 25** across the tier-2 pass; every reverted line came from this | `docs/RTN-20261012-REPORT.md` §4 |
| `tools/binfunctions.sh` + `tools/i386-textcmp.sh` | the two checks that say the 32-bit play build was not disturbed: one compares two linked binaries function by function with addresses normalised, the other compares a file's i386 `.text` before and after | **3,633 of 3,635** functions identical; `.text` byte-identical in all 18 files measured | `docs/RTN-20261012-REPORT.md` §2 |

They are driven by the compiler's own `(file, line, column)` error list — never by a regex
over a source file — and the ones that write back up before they write.
