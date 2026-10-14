# CMR2LRE live progress

**Updated 2026-10-15T00:20:00+03:00 EEST by the phone-side Lena.**

This page is a coordination update. It does not pretend that a worker has finished work
that has not produced a report.

## 2026-10-15 ~00:20 EEST — THE NEAR CLIP IS LIVE, THE AMBIENT IS DEAD, AND THE PLAY PATH CAN NO LONGER BE SILENTLY SWAPPED

Three things landed since the last revision. All three are measured. None of them is a
claim that the picture is fixed.

### 1. THE NEAR CLIP IS PROMOTED AND LIVE

`PLAY/out-plain/cmr2` is now md5 `1c0bee6ad2e92c23ca8f36289f7b5b77` — the build measured
at **8.3 % dropped vs 90.8 % control**. The old constant plane (5.86) was deleting
**90.8 % of every triangle the game submitted**; the promoted build keeps **4.9× more**.
Ring `gfx_0.0.0` timeout delta **0**. Behind-eye geometry is removed identically in both
arms — the plane still bites, it just bites in the right place.

This outranks any dropped state on the checklist. Nine tenths of the geometry was being
thrown away, and **nobody had looked at the race picture since that changed.** The next
round measures the picture on this build rather than chasing another state.

### 2. THE AMBIENT FIX IS FALSIFIED — WITH THE MECHANISM, NOT JUST THE VERDICT

`work/AMB-AB-20261015/`. Two GPU runs, ~7.7 minutes. One question per run. Ring delta 0.

The predicted fix was: read `rs[A7RS_AMBIENT]` instead of the hardcoded white material
ambient, and the snow would darken and get its edges back. It does not. It **deletes the
picture**, and the run's own numbers say why:

```
ARM DRAW TALLY: amb_fills=2899240  rs139==0: 2781948 (95.95%)  rs139!=0: 117292 (4.05%)
```

**95.95 % of the 2.9 million draws the arm touched read `rs139 = 0x00000000`.** The arm
multiplies the lighting term by zero on almost every draw. `zero%` goes **0.005 % → 65.2 %**
across the run and **0.006 % → 88.64 %** on the snow stage. A frame that is 88.6 % exactly
black has no edges by construction — so `road_edge 0.861 → 0.758` is not a reading of the
fix, it is a reading of the absence of a picture.

The 2026-10-12 GRFX-AB negative **reproduces on today's binary to three digits**:

| snow metric | GRFX-AB 10-12 (`a68bb585…`) | AMB-AB 10-15 (`1813b0a3…`) |
|---|---|---|
| frame mean ratio | 0.137 | **0.137** |
| zero % (AMB arm) | 88.7 | **88.64** |
| road_edge ratio | 0.872 | **0.880** |
| road_sd ratio | 2.680 | **2.693** |

Two independent builds, four days apart, same defect, same numbers. That is a reproducible
measurement, not a one-off. **The straight-substitution ambient fix is dead.**

### 3. FOG IS CLOSED — ONE OBSERVED VALUE IN EVERY STAGE

`state 28` (`D3DRS_FOGENABLE`) is **0 in every one of the three stages the attract route
walked** — 25,626 in-stage calls, 28,370 calls in the run, `nonzero=0`. Not "zero on
average": **one single value observed, `0`, everywhere.** Fog does not exist in retail
CMR2 on these tracks. The caps fix stays and is not wasted (it is why 35/140/36/37 arrive
at all), but it could never have turned fog on — the enable is a different, ungated path,
and that path says no.

### 4. THE PLAY PATH IS REGISTRY-GATED — THIS WAS A REAL FAILURE, AND IT IS FIXED

On 2026-10-14 at 22:35:49 a round script copied an **intermediate** build onto the play
path while Miami was playing. That build carried a first-revision near-clip patch with a
units bug, so it behaved exactly as if it had no patch at all. The build it replaced was
better. He found out by launching the game and finding it broken.

The root cause was not the patch. It was that **nothing in the project had a concept of
"which build is current"** — 21 separate round scripts each had their own copy step onto
that path, and the only gate asked *"can a car drive."* The bad build could drive. It just
rendered wrong.

What exists now:

- `PLAY/REGISTRY.json` names the one md5 that is playable.
- `~/lena/bin/lre` is the **only** thing allowed to write the path. It refuses a candidate
  that cannot drive, keeps the previous build in `gold/`, and writes the registry.
- `cmr2lre.sh` checks the path against the registry **before it starts anything** and
  restores the registered build from `gold/` if they disagree.
- `lre-watchdog.timer` repeats that check **every 5 minutes**, so a clobber is caught while
  he is away from the machine rather than at his next launch.

**Verified by deliberately corrupting the file and watching it self-heal**, twice — once
via the launcher, once via the watchdog. `ROUND-DISCIPLINE.md` carries the rule and the
reason.

### 5. THE FRONTEND 3D PATH IS WORKING

Miami's own report, 2026-10-14: the **206 renders fine**, and the pre-race **SETUP** and
**REPAIR** car screens both work. All three need the mesh, the transform **and** the
textures to land together — so this is the whole menu-car rendering path, not one screen.

### CORRECTION TO THE PREVIOUS REVISION

That revision stated the Deck daemon was **NOT running** and had picked up nothing for
~2h30m. That was true when written at 15:12 and is **false now** — the daemon is active
and has been working rounds all evening. Corrected here rather than quietly overwritten.

### WHAT IS STILL NOT TRUE

- **The road still does not separate from the terrain.** That is the defect, unchanged.
- No picture claim is made about the promoted near-clip build. The measurement is running.
- The white band now has one exclusion: the near clip is **not** its cause (present and
  identical at the same place with the clipper off, bands within 0.4 pp between arms).

**Honesty line:** this section publishes two falsifications, one promotion and one
infrastructure fix. It does not claim the port is finished, and it does not claim the race
picture looks right — only that the geometry is no longer being thrown away and the build
he launches cannot be silently replaced by a worse one.


---

## 2026-10-14 ~20:50 EEST — THE ENABLE CENSUS: FOG IS ANSWERED

The measurement the corrected spec's step 2 asked for has been made, and it came back **zero in
every stage**. Instrumented the value passed at the live state-28 site (`Game.cpp:2709`,
`SetRenderState(0x1c, Graphics_GetFlareStateValue())`) and ran the attract route with **no keys
injected, no forced fog, no synthetic input of any kind** — 420 s.

```
[ENABLE] frames=17422 stages=3 mesh_draws=6519149 gap=24
[ENABLE] epoch=0 frames=1..2752      calls=2744  nonzero=0  vals: 0:2744     <- frontend
[ENABLE] epoch=1 frames=2752..8068   calls=8775  nonzero=0  vals: 0:8775     <- stage 1
[ENABLE] epoch=2 frames=8068..14922  calls=11852 nonzero=0  vals: 0:11852    <- stage 2
[ENABLE] epoch=3 frames=14922..17421 calls=4999  nonzero=0  vals: 0:4999     <- stage 3
[ENABLE] TOTAL calls=28370 nonzero=0
```

**One observed value in every stage: `0`.** The three epochs were cross-checked against the
game's own `[RT F]` race-state transitions — a signal the detector does not use — and each opens
within 1-5 frames of one, with exactly three such transitions in 10,977 lines.

Gate: ring `gfx_0.0.0` timeout delta **0**, 0 windows on the display, 0 panics, the play binary
md5 read twice and never opened for write.

Confirmed independently in the decomp: `Graphics_EnableFog()`'s entire body is the caps-gated
half and contains **no state 28 at all** — two paths, one gate, and the ungated one is closed by
the track data.

Also checked as flagged (not a claimed bug): the two stage-lighting pointers **are swapped**
between `Race.cpp:790` and `Race.cpp:4485-4486`. It does not affect this result — the four-zero
test is on all four slots together — but it matters to anyone reasoning about which preset is
primary. The order-independent colour average is not the part at risk.

**Fog is off the suspect list, with evidence.** The caps fix stays (it is why 35/140/36/37
arrive) and the range work stays dormant but correct. The next state is `D3DRS_AMBIENT` (139) —
mapped, stored, read by nothing.

Published: `frames/20261014-e020-enable-census/`. Spec: `docs/FOG-VERIFIED-SPEC.md` §1.1.


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

---

# FOG-IS-THE-FIRST-STATE-20261014 — deck-side report

**Added 2026-10-14T17:55+03:00 EEST by the Deck daemon (Lena).** Appended; nothing above
this line was altered.

## 1. RIGHT NOW

The fog state set is mapped, the vertex-fog term is implemented, and it is **measured
working, from one binary, both arms alternating per frame**. What is NOT true is the
brief's premise that fog causes the white-on-white: the game never turns fog on. Fog leaves
the suspect list with evidence. The next state is **D3DRS_AMBIENT (139)**.

## 2. DONE (evidence)

**Which fog mode the game actually sets** -- asked for explicitly, answered by measurement
rather than by reading:
* `FOGVERTEXMODE (140)` = **3 = D3DFOG_LINEAR**, live, `uniq=2`, 17952 calls.
* `FOGTABLEMODE (35)` = **0 = D3DFOG_NONE**, 17952 calls.
So the live mode is **vertex fog, linear**. That is the one implemented. Both states are
mapped and STORED now (they were dropped); 34/36/37 (FOGCOLOR/FOGSTART/FOGEND) are mapped
and stored too, and 36/37 now ARRIVE where the round-1 census measured them ABSENT -- that
is the `dwMiscCaps |= 0x80` device-cap bit working, since `Graphics_GetDeviceCaps90()` gates
every range the game sends.

**Which quantity feeds fog** -- the brief asked this be stated: the **W component of the
clip-space position before the perspective divide** (camera-space distance), carried to the
fragment stage as the `vFogDepth` varying. Not the post-divide depth-buffer value.

**Predicted vs measured, forced run (fogC, `A7VK_FOGFORCE=30,900,ffffff`, 50 pairs):**

    metric      fog ON     fog OFF      delta
    share      0.55709     0.51888    +0.03821
    far      119.86660   103.85158   +16.01502
    mean     109.30377    97.57134   +11.73243
    (far higher in 48/50 pairs)

The prediction's SIGN is wrong and that is stated rather than buried: the brief predicted
the dominant-octile share would FALL; it ROSE. That is what a WHITE fog colour does to a
mid-brightness scene -- it pushes pixels toward the top octile. The mechanism the brief
actually specified, **a distance gradient in the ground band**, is present and measured:
vertical luma gradient (bottom-third minus top-third) is **-29.23 with fog on vs -21.01 with
it off, 39 % steeper**, concentrated in rows 200-350 (the horizon band) at +22 to +29 luma
and falling to +3-6 in the extreme foreground.

**Measured, unforced run (fogD, the game's own values): cross-arm signed mean delta -1.07
luma vs +11.74 forced -- an 18x difference.** `D3DRS_FOGENABLE` is **0 in every one of
24369 calls, uniq=1**, across a full race. The game does not fog.

**Gate:** ring `gfx_0.0.0` timeout delta **0** on both runs. 0 windows on his desktop.
0 panics. 8953 and 7977 race frames at `state=8`.

**Published:** `LENAWare-Works/cmr2lab` commit `476bcf5`, dir
`frames/20261014-1750-fog-first-state/` -- both arms, arm-labelled, md5s in
`MANIFEST.txt`.

**Where I failed, and it was my own instrument:** run `fogB` (first attempt this round)
produced 100 cross-arm pairs that were a NULL BY CONSTRUCTION -- `A7VK_FOGFORCE` set the
range and colour but the enable stayed the game's 0, and an unconditional FOGCOLOR read
overwrote the forced white with the game's unset black. The fog term never executed in
either arm. Both bugs are fixed in `run/fog-ab-run3`. It was caught by checking the arm
label against what the code was actually gated on -- the same instrument that caught the
round-1 parity bug.

## 3. IN PROGRESS (honest fraction)

Fog: **complete** -- 6/6 states mapped, term implemented, forced and unforced both measured,
published. The whole task is **not** complete: the checklist continues, and the one thing
the brief wanted most (a fix to the white-on-white) has NOT been delivered by fog, because
the game does not use it. Item 2 of the order, `D3DRS_AMBIENT` (534,078 calls, mapped,
stored, read by nothing -- `grep A7RS_AMBIENT a7_vk32.c` = 0), is the next state and is
untouched.

**Honesty line:** this section claims the fog TERM works and the game does not enable fog.
It does not claim fog improved the shipped picture, because it cannot and does not.
