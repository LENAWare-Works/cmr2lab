# archive/ — moved out of the active tree, not deleted

Created 15 October 2026 at Miami's instruction: *"stale files that aren't used, don't have
any instructions or anything further project to aid us, make em gone — if you're afraid of
deleting them, archive them."*

**Nothing here was deleted.** Every file still exists, byte for byte, and every file is
still reachable by its original content. What changed is that it is no longer sitting in
`docs/` competing for attention with documents that are current.

## The rule that decided what moved

A file moved here if it was **all three** of:

1. a round-by-round working log, a delivered agent-to-agent note, a completed checkpoint,
   or a note about a single capture file;
2. not referenced by `README.md`, `docs/STATUS.md`, `docs/INDEX.md` or `progress.md`;
3. not the only record of anything still in force.

A file stayed if it was an entry point, a format reference, a report about something that
shipped or is still open, or a plan.

## What is here, and why each one

| file | why it moved |
|---|---|
| `docs/CAR-r1-REPORT.md` | round 1 of a ticket whose rounds 7–14 superseded it; the findings live on in the later car rounds |
| `docs/DEPENDENCY-MAP-CHECKPOINT.md` | opens with "Round complete". The map it belongs to is `docs/DEPENDENCY-MAP.md`, which stayed |
| `docs/FRAME-FEEDBACK.md` | Miami's three 10 October facts chased to numbers; superseded by the later `ROAD-*` rounds |
| `docs/MENU-CAR-ROUND2.md` | round 2 of the menu-car ticket |
| `docs/MENU-CAR_car-frame.md` | round 5 of the same ticket |
| `docs/MENU-CAR_car-page-round6.md` | round 6 of the same ticket |
| `docs/MENU-CAR-opt-preview_car-frame.md` | round 4 of the same ticket |
| `docs/MENU-CAR_round9_engine-vs-screen.md` | round 9 of the same ticket |
| `docs/MENU-CAR_opt-preview-capture.md` | a note about one PNG |
| `docs/NOTE-to-phone-CAR-r1.md` | a note between two agents. It was delivered; its content is in `CAR-r1-REPORT.md` |
| `docs/ONE-WHEEL-FRAME.md` | a refutation of a claim about a photograph that is not on this machine — it reaches a dead end by its own account |
| `docs/PHONE-STATUS-20261014.md` | a status snapshot with a timestamp in its own title. `docs/STATUS.md` is the live one |
| `docs/ROAD-r5-REPORT.md` | superseded by `docs/ROAD-r6-REPORT.md`, which is what `README.md` cites |
| `frames/20261013-0025/` | captures of a **superseded build** (`275dfde9`). Its `README.md` is a good record and came with it — nothing cites it |
| `tools/build_car_tiles.py` | rebuilt the README car tiles. `tools/render/make_assets.py` does that now, and does it correctly |
| `tools/bfl-rw.py` | `.bfl` read/write. Superseded by the `cmr2lab` CLI, which is the supported path |
| `tools/relay-analyze.py`, `tools/relay-filter.py` | instruments for the WINEDEBUG dependency-map round. That round is complete (`docs/DEPENDENCY-MAP.md`); nothing calls these |

**The menu-car ticket is NOT closed.** It is still an open defect in `README.md`'s honest
table. The canonical documents stayed in `docs/` — [`MENU-CAR.md`](../docs/MENU-CAR.md)
(round 1, plus the correction header that supersedes its own §0.1) and
[`MENU-CAR-EVIDENCE.md`](../docs/MENU-CAR-EVIDENCE.md) (the round that corrected it). Only
the intermediate rounds moved.

## Byte-identical duplicates removed

`frames/20261014-1750-fog-first-state/` stored 25 PNGs of which **10 were byte-identical
duplicates of another file** — a capture pair is two frames apart, so consecutive pairs
share a frame and the same bytes were saved under two names. Verified with `cmp` before
removal, one file per distinct md5 kept, and the whole thing recorded in
`frames/20261014-1750-fog-first-state/DUPLICATE-LEDGER.json` (kept path, removed path,
md5). **21.1 MB reclaimed, no frame lost.** No document cites an individual pair filename,
so no citation broke.

This is the same rule the Deck's frame prune used: prove duplicates by content, never
judge by staleness.

## Recovering something

Every file can be moved back with a single `git mv`. Nothing was rewritten on the way in —
these are the same bytes that were published, so `git log --follow` works on all of them.
