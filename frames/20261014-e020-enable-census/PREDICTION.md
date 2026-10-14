# PREDICTION — THE ENABLE CENSUS. WRITTEN BEFORE THE RUN.

Round: FOG-IS-THE-FIRST-STATE-20261014, continuation.
Task: instrument the value passed at `Game.cpp:2709` (the live state-28 site) per
frame and run the **attract route with NO KEYS**. No forced fog, no synthetic
input, no new recipe.

---

## THE CLAIM UNDER TEST

> Does state 28 (`D3DRS_FOGENABLE`, `0x1c`) ever go **NON-ZERO**, in **ANY**
> stage?

This is PATH A of the corrected spec: the enable. It is **not** caps-gated — there
is no `GetDeviceCaps` call anywhere in that chain. It is a **stage-data property**
read from the track's lighting preset: `StageObjects.cpp` fills `[0x25]/[0x26]`
from `pPrimary` and `[0x52]/[0x53]` from `pSecondary`, and when all four are zero
the game writes enable 0, otherwise 1 (`StageObjects.cpp:5301-5309`).

So this is separable from the range work, and the previous round's measurement —
state 28 at 24369 calls, `uniq=1`, value 0 across a full race stage — is ONE
stage, not all of them.

---

## MY PREDICTION (pre-registered so it can be wrong)

**I predict state 28 is ZERO in every stage.**

Reasons, stated so the failure mode is visible rather than implied:

1. CMR2 shipped fog as a **driver-capability** feature. The `GetDeviceCaps` gate
   on the range path (PATH B) is the shape of a studio deciding at runtime
   whether the driver can do it at all. That is a feature you ship *off*, not one
   you drive from track data on a 1999 disc.
2. The four coefficients are **all-zero in every stage measured so far**, and the
   previous round's race measurement is one stage that says no. If the format
   carried a real range, at least the summary statistics of one of the three
   countries on the attract route would be expected to be non-zero.
3. The stages the attract route walks are **clear weather**. Fog's job in this
   game would be to hide the draw-distance cut on a hazy stage; there is no
   evidence any shipped stage here is hazy.

**If it comes back non-zero somewhere, that is the better result and it beats my
prediction.** It would mean the enable is real, that ONE stage is the only place
the range matters, and that stage is where the term is worth watching land. I
would rather publish that than my prediction.

---

## WHAT WOULD MAKE THIS ROUND MEANINGLESS (the falsifier of the METHOD, not the claim)

- **Zero in-stage epochs.** If the run never reaches a stage, "state 28 is 0"
  is a statement about the menus and the whole round answers nothing. The dump
  prints `IN-STAGE (epoch>=1) stages=N` and a `VERDICT: NO STAGE WAS MEASURED`
  line precisely so this cannot be misread as the answer.
- **Epochs that are not stages.** The epoch opens on the first MESH draw
  (FVF `0x2d2`) after ≥24 frames with none. If the attract route passes through a
  loading screen that draws meshes, epochs will over-count. Cross-check: the
  epoch count is printed beside the raw frame numbers and must be reconcilable
  with the `[RT F] state=` transitions in the same run log. If it is not, the
  per-stage attribution is wrong and only the run total may be quoted.
- **A run that does not complete the route.** The brief says Kenya → Sweden →
  Greece in about five minutes. If the log shows fewer than three stage loads,
  the answer is "these stages", not "all stages".

---

## WHAT IS EXPLICITLY NOT BEING DONE

- **The forced-fog experiment is not re-run.** It answered its question and the
  term is measured working (fogC vs fogD: cross-arm signed mean delta +11.74 luma
  forced vs −1.07 unforced, an 18× difference; ring delta 0). Re-running it would
  be motion, not evidence.
- **No keys are injected.** No `inject-key.py`, no pad synthesis, no forced menu
  navigation. The attract route drives itself.
- **No pixels are compared.** This round decides whether fog MATTERS. A visual
  result is a later round's job, and only if the enable turns out to be non-zero.

## THE GATE

- ring `gfx_0.0.0` timeout delta must be **0**
- 0 windows on his display
- 0 panics / signal 11
- `PLAY/out-plain/cmr2` untouched (md5 before and after)
