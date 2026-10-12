# frames/20261012-2300 — the stage-load crash, its fix, and his own session

Published 2026-10-12 ~23:00 by the round `SUSPECT-CORRECTED-THE-ALIGN-20261012-2218`.
Full size, 1280x800, no crop, no downscale. `MANIFEST.txt` has the md5 and byte size of
every file and nothing is re-encoded.

## The three frames

| file | what it is |
|---|---|
| `tree-fixed-f2600.png` | **frame 2600 of a build made from the fixed tree** — the first tree build that ever got past the record-map crash. 586,844 draws / 1,210,912 triangles had already gone to the GPU on this frame. It is a *build* frame, not a run: the build died 114 frames later, in a **second** defect behind the first (see below). |
| `miami-session-225134.png` | **Miami's own session**, 22:51:34, from the eyes loop. He pressed the Desktop icon at 22:46:38 and this is him in a stage: leaderboard top-left (`2 ERIKSON 01:57.21`, `3 AAA 01:57.63`), turn arrow top-centre, timer + progress bar top-right, tachometer bottom-right. |
| `miami-session-225944.png` | the same session, 22:59:44 — still alive, still in a stage. By 23:00 the process had been up ~14 minutes with no fatal signal, on build `94ed1359c405`. |

These are **the first frames ever published from a game he is actually playing** rather than
from a harness run. They are of the game screen only. If he would rather they were not in a
public repo, delete this directory and say so — nothing else refers to them.

## What the frames do and do not prove

**Prove:** a stage loads and renders, the HUD is live, the game survives past stage entry
(14 minutes and counting), and the near-clip + mips + per-draw TL align are all in the build
he is on.

**Do not prove:** that the tree is fixed. The tree build in `tree-fixed-f2600.png` is not the
build in his session, and it did not finish its run.

**The rendering defects are visible in his frames and they are real, not compression:**
long white horizontal smears across the road and terrain on the right, and the bottom third
of the frame carrying a separate dark forest texture that does not connect to the road above
it. The car reads as a flattened dark mass. All three are present **with the near-clip ON**.
**A clip-OFF control has never been run**, so this set claims neither that the clip causes
them nor that it would cure them. That control is the named next experiment.

Two stills eight minutes apart (`22:51:34` and `22:59:44`) both read **`KMH 000`**. That may
be him parked, paused, or at a start line — a still cannot tell. It is flagged here rather
than interpreted, because if his car will not move it is a different bug from any in this
directory.
