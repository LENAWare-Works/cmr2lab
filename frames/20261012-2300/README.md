# frames/20261012-2300 — the stage-load crash, its four fixes, and his own session

Published 2026-10-12 ~23:35 by the round `SUSPECT-CORRECTED-THE-ALIGN-20261012-2218`.
Full size, 1280x800, no crop, no re-encode. `MANIFEST.txt` carries the md5 and size of
every file.

## The six frames

| file | what it is |
|---|---|
| `tree-fixed-f2600.png` | frame 2600 (Main Menu) of the **first tree build** to get past the record-map crash — 586,844 draws in, then it died in a second defect |
| `tree-build-stage-f3200.png` | **the tree build driving a stage** — attract demo, frame 3200, after 788,352 draws / 3,864,576 triangles, `clampHits=0`. The "demo" label is the attract route, which draws no HUD |
| `tree-build-stage-f4500.png` | same build, frame 4500: 1,192,719 draws / 11,552,344 triangles, still `clampHits=0` |
| `miami-session-225134.png` | **Miami's own session**, 22:51:34, from the eyes loop: leaderboard (`2 ERIKSON 01:57.21`, `3 AAA 01:57.63`), turn arrow, timer, tachometer |
| `miami-session-225944.png` | the same session, 22:59:44 — process up 17 minutes, no fatal signal, build `94ed1359c405` |
| `menu-diff-vs-his-build.png` | the **amplified pixel difference** between his build's Main Menu and the tree build's, at the same frame. It is the animated letter-ribbon's phase and nothing else — same title, same clock, same menu bar — which is what makes the tree build's frontend trustworthy without a GPU run |

These are the first frames published from a game he is actually playing, and the first from
a tree build that reaches a stage *and drives through it*. They are of the game screen only.
If he would rather his session frames were not in a public repo, delete those two and say so.

## What the frames prove, and what they do not

**Prove:** the record-map bug is gone from the binary; a build of the tree loads a stage,
renders it and drives (2,078 race frames, 1,969 in `state=8`, 11.5 M triangles, `clamps=0`,
ring-timeout delta 0, no kernel GPU event); his session on the older binary is healthy for
17 minutes; the tree build's menu is the same picture as his.

**Do not prove:** that the tree is ready to install. **It is not.** That same 200 s run died
at *stage end* — SIGSEGV in `StageObject_FreeAll` (`Mesh.cpp:416`) under
`RallyData_FreeChallengeSceneObjects` → `CGame::UnwindCallbacks` → `Race_ReleaseFrameResources`
→ `Race_HandleStageReplayViewTransitions`. That is the fifth defect tonight and it is why
`out-plain/cmr2` was **not** replaced: he stays on `94ed1359c405`, which is verified.

**The rendering defects are not tonight's bug, and they are in both builds:** long white
horizontal smears across the grass, star-shaped white polygon shards, the car flattened, and
a detached dark band along the very bottom edge — identical in his frames and in the tree
build's. The near-clip is ON in all of them, and **a clip-OFF control has never been run**, so
these frames claim neither that the clip causes them nor that it would cure them.

Two of his stills, eight minutes apart, read `KMH 000`. Parked, paused or start line — a
still cannot say, and it is flagged rather than interpreted.
