#!/bin/sh
# grab-his-build.sh -- take the three frames that do not exist yet:
#   frontend, stage-load, and THE LAST FRAME BEFORE DEATH, on the build he was
#   actually on (3afeedbe77e5, 20:19) -- the one that SIGSEGVs in
#   Sector_NearestCornerHeight on stage entry.
#
# Written 2026-10-12 22:2x by the CAPTURE-FRAMES-NOW-20261012-2210 round, which did
# NOT run it: he was on the machine and the fix lane held the card. This script is the
# run, ready, for whoever holds the GPU next.
#
# SAFETY, and it is the whole design:
#   * RACE/gpu-guard.sh is sourced. gpu_guard REFUSES if any game is alive that this
#     harness did not start -- his game, or another lane's. Exit 3, nothing launched.
#   * NO KEYS. No /dev/uinput, no key injection: that device is machine-wide and a
#     synthetic Return would land in HIS session. The route is wait-only (attract).
#   * the game is run from its GOLDEN COPY (work/PLAY/gold/), so nothing is moved
#     over /home/deck/lena/work/PLAY/out-plain/cmr2 and the launcher's target is
#     untouched. PLAY-HOLD stays exactly as it is.
#   * capture is into this directory. The card is stopped afterwards by PID, only if
#     this run started it.
#
# THE CRASH IS AT STAGE ENTRY, so the frames worth having are the last ones BEFORE
# it. The snap list below covers the frontend, the load, and the last presented
# frames; the driver is expected to die -- that is the measurement.
#
#   usage:  sh grab-his-build.sh          (BIN/SECS can be overridden by env)
set -u

W=/home/deck/lena/work/FRAMES-PUB-20261012-2210
BIN=${BIN:-/home/deck/lena/work/PLAY/gold/cmr2-20261012-3afeedbe77e5}
TAG=${TAG:-his}
SECS=${SECS:-330}
SHOTS=${SHOTS:-$W/shots-his}
mkdir -p "$SHOTS" "$W/logs"

[ -x "$BIN" ] || { echo "no golden binary at $BIN -- refusing to guess"; exit 2; }
echo "binary : $BIN"
echo "md5    : $(md5sum "$BIN" | cut -d' ' -f1)   (expect 3afeedbe77e537b483443d75b6dce176)"

. /home/deck/lena/work/RACE/gpu-guard.sh
LENA_RUN_ID="grabhis-$$"; export LENA_RUN_ID
gpu_reap
gpu_guard || { echo "STOOD DOWN: a game is alive that we did not start. His playtime wins."; exit 3; }

# frame numbers: frontend is presented for thousands of frames before stage entry,
# so 3/4/5k are frontend or load and 5.0-5.4k is the approach to the fault.
env A7_VSYNC=1 DECK_RACE_TRACE=1 DECK_DIN_TRACE=0 \
    A7VK_SNAP="3000,4000,4500,4800,5000,5100,5150,5200,5250,5300:$SHOTS/$TAG.ppm" \
    LENA_ZLINE=1 LENA_ZLINE_SNAP="$SHOTS/$TAG.zline.ppm" LENA_ZLINE_SNAPS=3 \
    timeout $((SECS+120)) python3 /home/deck/lena/work/RACE/drive.py \
            "$BIN" "$TAG" "w${SECS}" \
            > "$W/logs/$TAG.drive.out" 2>&1
echo "drive.py exit=$?  (a SIGSEGV here IS the expected result -- it is the fault)"
gpu_stop_own

echo "--- what the game said before it died ---"
G=/home/deck/lena/work/RACE/out/$TAG.log
[ -f "$G" ] && { grep -a '\[RT F\]' "$G" | tail -3; tail -5 "$G"; }
echo "--- and the pixels ---"
ls -la "$SHOTS"
echo
echo "next: convert the ones that show a screen --"
echo "  for f in $SHOTS/$TAG.ppm.*; do"
echo "    python3 /home/deck/lena/work/RACE/ppm2png.py \"\$f\" \"\$f.png\"; done"
