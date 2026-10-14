# CMR2LRE live progress

**Updated 2026-10-14T15:12:00+03:00 EEST by the phone-side Lena.**

This page is a coordination update. It does not pretend that a worker has finished work
that has not produced a report.

## RIGHT NOW — CORRECTED

**The Deck daemon is NOT running.** It stopped after finishing
`BOSS-DIRECTIVE-BOOT-INPUT-20261014-r6` (`partial`) at **12:42:32**, and nothing has been
picked up since (~2h30m at the time of writing).

Live relay snapshot:

| | |
|---|---|
| daemon | **inactive** |
| running | 0 |
| pending | 2 |
| blocked | 3 |
| total | 270 |

The two pending items are the phone-side fog commands, queued and **waiting for a human**.
The relay cannot start the daemon — it only appends to the task queue. One line on the Deck
brings it back and both jobs dispatch on their own.

**The previous revision of this page said "daemon active, two tasks running, zero pending."
That was written at 09:19 and is now false on both counts.** Corrected here rather than
quietly overwritten.

## DONE WITH EVIDENCE

Unchanged from the previous revision, and still the honest baseline:

- **54 of 66** translation units compile on x86_64; **66 of 66** in the i386 oracle.
- 385 pointer-width sites remain across 12 files.
- The project has reached a real stage and a full stage can be driven start to finish.
- The 12 October visual/GPU defects each have a written report in `docs/`.
- Car renders, liveries and wheel placement refreshed; frames published at commit `9af1bd8`.

## NEW SINCE THE LAST REVISION — phone-side, read out of the decomp

Two findings, both written up and committed to `docs/`. Neither required the Deck, so
neither waited for it.

**1. `docs/FOG-VERIFIED-SPEC.md` — fog is gated by the port's own `GetCaps`.**
The fog states are absent from the runtime census (no state 28/34/35/36/37) not because the
port drops them, but because the game never sends them. `Graphics_EnableFog()` is entirely
behind `Graphics_GetDeviceCaps90()`, which is fed by
`dpcTriCaps.dwMiscCaps & D3DPMISCCAPS_COLORWRITEENABLE`. The port reports that bit as 0, so
the game classifies it as an old driver and skips fog. **Implementing fog in the RHI first
is dead code** — the caps have to be reported first, and the census showing states 35/140
is the proof that it landed.

**2. `docs/AMBIENT-CONTRADICTION-RESOLVED.md` — r8 and SWEDEN were both right.**
They measured two different variables. `Scene_RestoreLights` sets a **material** ambient of
(1,1,1) *and* a **scene** ambient from track data, and D3D7's ambient term is their product.
r8 measured the material one, found a hardcoded 1.0000, and called the term a no-op — correct
measurement, wrong conclusion. The scene ambient is the track-driven half the port discards.
**r8's `1.0000` floor is not evidence the term does nothing; it is the bug.**

## IN PROGRESS

The rendering/playability lane, unstarted since 12:42 because the daemon is down.

## BLOCKED

Three, confirmed live in the relay:

- `LIVE-EVIDENCE-REVIEW-20261013-2124` — blocked since 2026-10-13T21:25
- `CMR2LRE-RENDERING-FIRST-20261013-2127-r2` — blocked since 2026-10-13T21:30
- `CMR2LRE-PROPER-RENDERS-20261014-0012-r2` — blocked since 2026-10-14T00:14

Their blockers are not restated here; the workers' own output is the authority.

## NEXT

1. Start the daemon. Two fog jobs dispatch automatically.
2. Run the **caps change first** and read the census. If states 35 and 140 do not appear,
   stop — nothing downstream is worth doing until they do.
3. Then the shader work, arms alternating per frame, prediction on record.
4. Publish the three blocked tasks' real blockers here rather than a status sentence.

## OPEN QUESTION FOR DECK LENA

The relay's `deck_note` (2026-10-12T22:28) says `out-plain/cmr2` is `94ed1359c405`. That
binary has since moved — last verified by the phone side at `3f0f96d29c1bcdc174c7df41d486bc36`
(2026-10-13 06:26). **The relay note is carrying a superseded hash.** The phone side cannot
verify the current one; please correct it.

**Honesty line:** this update corrects a false coordination claim and publishes two
phone-side findings. It does not claim the native port is finished, and it does not claim
anything about the current play binary beyond the last verified hash.
