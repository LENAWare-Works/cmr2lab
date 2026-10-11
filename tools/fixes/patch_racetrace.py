#!/usr/bin/env python3
"""patch_racetrace.py -- DECK_RACE_TRACE: the per-frame physics/rate trace and
the attract-driver trace, for the DEMO-DRIVE-CRASH round.

WHY THIS EXISTS
  Miami: "she can't drive for shit in the demo mode where the car goes around
  the track, keeps crashing over and over again." The demo driver is real code
  and it is in the tree:

      AI_UpdateAttractDrivingControls()   StageObjects.cpp   CMR2 0x0047d330

  It is a BANG-BANG controller. Four thresholds on four numbers and nothing
  else:

      state[0]  < 0x320000  -> throttle
      state[0]  > 0x460000  -> brake
      state[7]  >  0x50000  -> full right
      state[7]  < -0x50000  -> full left
      |state[0xe]| > 0x5a0000 -> one of six recovery modes (full lock + brake)

  There is no proportional term and no adaptive term anywhere in it. A
  controller shaped like that is only stable at the step size it was tuned at.
  So the FIRST question is not "is the AI wrong", it is "is the AI being handed
  the numbers and the time step it was tuned for". This patch makes both
  answerable from one run.

WHAT IT ADDS -- TWO READ-ONLY LINES

  [RT F] one per frame, from Race_UpdatePlayerViewAndDrivenCars():
         the clock (frame count, ms), the three frame-rate-derived values the
         game computes (fps, and both physics-scale pairs), the car-loop bound,
         and the race state code.

  [RT A] one per attract-driver call, from AI_UpdateAttractDrivingControls():
         the four state values the controller branches on, the branch it took,
         the four input bytes it wrote, and where the car actually is.

  A and F share `f=` (g_frameCount), so the two can be joined afterwards.

ENV GATE
  DECK_RACE_TRACE unset  -> zero lines, and that is MEASURED, not assumed.
  DECK_RACE_TRACE=1      -> [RT F] only   (cheap; the frame/rate question)
  DECK_RACE_TRACE=2      -> [RT F] + [RT A]  (the driver question)

  Read once per process by LenaTrace on the existing DECK_FE_TRACE helper, so
  the gate costs one getenv on the first call and nothing after it.

SAFETY
  Every added statement is a printf of values that are already in registers or
  already in memory at that point. Nothing is written to game memory. Nothing
  is reordered. Nothing is called that the game does not already call on the
  same path except RallyData_GetRouteNodeGroundPosition (the split-bar function
  calls it three times per frame a few instructions earlier) and
  RallyData_GetActiveCarRaceRecordField14 (called by the driver itself).

Usage:  python3 patch_racetrace.py            # dry run, prints the diff
        python3 patch_racetrace.py --apply    # write it
"""
import shutil
import sys
import os
import time

ROOT = "/home/deck/lena/.lena_cmr2/port/tree/CMR2Decomp"
RACE = os.path.join(ROOT, "Race.cpp")
STAGE = os.path.join(ROOT, "StageObjects.cpp")
STAMP = "bak-pre-racetrace-" + time.strftime("%Y%m%d-%H%M%S")

APPLY = "--apply" in sys.argv

# ---------------------------------------------------------------------------
# 1. the frame/rate line, in Race.cpp
# ---------------------------------------------------------------------------
F_ANCHOR = """    Physics_UpdateRateHold();
    g_unk0x00538124 = Car_UpdateEngineNoteFalloff(&g_unk0x00537f60);
"""

F_BLOCK = """    /*LENA-RACETRACE*/
    if (LenaRaceTrace() >= 1) {
        extern int g_frameCount;
        extern float g_frameScale;
        extern int g_physicsScale, g_physicsTimeStep;
        extern int g_unk0x0051bd40, g_unk0x0051bd3c;
        extern BYTE g_unk0x00537f08;
        extern int g_unk0x00537f24;
        {
            int rc_rs = RallyDataState() & 0xff;
            Car *rc0 = Car_Get(0);
            LenaRaceLog("[RT F] t=%u f=%d fps=%.4f psc=%d pts=%d os=%d ot=%d "
                      "steps=%d f08=%d f24=%d state=%d n=%d ord=%d "
                      "c0x=%d c0z=%d c0sp=%d\\n",
                      (unsigned)timeGetTime(), (int)g_frameCount,
                      (double)g_frameScale, (int)g_physicsScale,
                      (int)g_physicsTimeStep, (int)g_unk0x0051bd40,
                      (int)g_unk0x0051bd3c, (int)g_unk0x00538124,
                      (int)g_unk0x00537f08, (int)g_unk0x00537f24,
                      (int)g_unk0x00537fb8, (int)rc_rs,
                      (int)Car_GetOrderCount(),
                      (int)rc0->position.x, (int)rc0->position.z,
                      (int)rc0->speed);
        }
    }
/*LENA-RACETRACE-END*/
# --- LENA FIX 2026-10-11 (work/DEMO-DRIVE-CRASH round 3) ------------------
# THE ANCHOR IS GAME CODE. It must survive the replacement.
# As written, F_BLOCK did not contain F_ANCHOR, so `text.replace(anchor,
# block, 1)` DELETED the two statements -- and with them the bound of the
# per-car drive loop, so no car could be driven and the physics never
# stepped, in every binary linked after 08:39:07 on 2026-10-11.
# Restored in the tree; kept here so a re-run cannot delete it again.
"""
assert F_ANCHOR.strip() and "Physics_UpdateRateHold" in F_ANCHOR
F_BLOCK = F_BLOCK + F_ANCHOR

# ---------------------------------------------------------------------------
# 2. the attract-driver line, in StageObjects.cpp
# ---------------------------------------------------------------------------
A_ANCHOR = """apply:
    if (preview != 0)
        return 1;
"""

A_BLOCK = """apply:
    /*LENA-RACETRACE-A*/
    if (LenaRaceTrace() >= 2) {
        extern int g_frameCount;
        FixVector rcNode;
        int rcRs = RallyData_GetRouteStateValue();
        RallyData_GetRouteNodeGroundPosition((int)node, (int *)&rcNode);
        LenaRaceLog("[RT A] f=%d car=%d node=%d rs=%d s0=%d s7=%d sd=%d se=%d "
                  "s13=%d s14=%d s1=%d pre=%d mode=%d L=%d R=%d T=%d B=%d Hb=%d "
                  "sp=%d px=%d pz=%d rx=%d rz=%d hx=%d hz=%d nx=%d nz=%d\\n",
                  (int)g_frameCount, (int)car, (int)node, (int)rcRs,
                  (int)state[0], (int)state[7], (int)state[0xd], (int)state[0xe],
                  (int)state[0x13], (int)state[0x14], (int)state[1],
                  (int)preview, (int)mode,
                  (int)left, (int)right, (int)throttle, (int)brake,
                  (int)handbrake, (int)pCar->speed,
                  (int)pCar->position.x, (int)pCar->position.z,
                  (int)pCar->right.x, (int)pCar->right.z,
                  (int)pCar->velocity.x, (int)pCar->velocity.z,
                  (int)rcNode.x, (int)rcNode.z);
    }
/*LENA-RACETRACE-A-END*/
    if (preview != 0)
        return 1;
"""

EARLY_ANCHOR = """    pCar = Car_Get(car);
    node = (unsigned short)RallyData_GetActiveCarRaceRecordField14((BYTE *)pCar);
    if (node + 5 > (unsigned int)RallyData_GetRouteStateValue())
        return 0;
"""

EARLY_BLOCK = """    pCar = Car_Get(car);
    node = (unsigned short)RallyData_GetActiveCarRaceRecordField14((BYTE *)pCar);
    /*LENA-RACETRACE-E*/
    if (LenaRaceTrace() >= 2) {
        extern int g_frameCount;
        LenaRaceLog("[RT E] f=%d car=%d node=%d rs=%d\\n",
                  (int)g_frameCount, (int)car, (int)node,
                  (int)RallyData_GetRouteStateValue());
    }
/*LENA-RACETRACE-E-END*/
    if (node + 5 > (unsigned int)RallyData_GetRouteStateValue())
        return 0;
"""

# The trace helper is declared in Lenatrace.cpp; StageObjects.cpp and Race.cpp
# need to see it. One prototype, added once, at the top of each file's body.
DECL = ("int LenaRaceTrace(void);\n"
        "void LenaRaceLog(const char *fmt, ...);\n")


MARKER = {"F": "/*LENA-RACETRACE*/", "A": "/*LENA-RACETRACE-A*/",
          "E": "/*LENA-RACETRACE-E*/"}


def insert_once(text, anchor, block, name, path):
    if MARKER[name] in text:
        print("  [%s] already present -- skipping" % name)
        return text, False
    if anchor not in text:
        print("  [%s] ANCHOR NOT FOUND in %s -- refusing" % (name, path))
        sys.exit(2)
    if text.count(anchor) != 1:
        print("  [%s] anchor is ambiguous (%d hits) -- refusing"
              % (name, text.count(anchor)))
        sys.exit(2)
    print("  [%s] anchor ok, +%d lines" % (name, block.count("\n")))
    return text.replace(anchor, block, 1), True


def add_decl(text):
    """Put the LenaRaceTrace prototype after the last #include at the top."""
    if DECL in text:
        return text, False
    lines = text.split("\n")
    last = 0
    for i, ln in enumerate(lines[:80]):
        if ln.startswith("#include"):
            last = i
    lines.insert(last + 1, DECL)
    return "\n".join(lines), True


def main():
    print("patch_racetrace.py  (apply=%s)" % APPLY)
    changed = []

    for path, edits in ((RACE, [("F", F_ANCHOR, F_BLOCK)]),
                        (STAGE, [("A", A_ANCHOR, A_BLOCK),
                                 ("E", EARLY_ANCHOR, EARLY_BLOCK)])):
        text = open(path).read()
        orig = text
        text, d = add_decl(text)
        if d:
            print("  [%s] +1 prototype" % os.path.basename(path))
        for name, anchor, block in edits:
            text, _ = insert_once(text, anchor, block, name, path)
        if text != orig:
            changed.append(path)
            if APPLY:
                shutil.copy2(path, path + "." + STAMP)
                open(path, "w").write(text)
    if not changed:
        print("nothing to do -- tree already patched")
        return
    print("files changed: %d" % len(changed))
    for p in changed:
        print("   %s" % p)
    if APPLY:
        print("backups written with suffix .%s" % STAMP)
    else:
        print("DRY RUN -- nothing written. Re-run with --apply.")


main()
