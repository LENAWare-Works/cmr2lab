#!/bin/sh
# run_card.sh -- measure the WHITE CARD under the car, one run, A/B by frame.
#
# WHY THIS EXISTS (ticket WHITE-BOX-UNDER-CAR, 2026-10-11 07:45)
#   Miami: "again super janky and white box under the car".  Offline measurement
#   of the captures this project already holds found a specimen with no ambiguity:
#   out/death/control4.ppm.3000 is 99.6% the 2D backdrop colour 0x9cb4ac and 0.4%
#   a PURE #ffffff hard-edged quad, corners ~(583,382) (630,388) (576,450)
#   (523,441) -- i.e. the only thing on that screen that is not the backdrop.
#   In out/ab/abfix.ppm.3590 (A7VK_AB=notex) the WHOLE FRAME came out #ffffff,
#   single component, 1,024,000/1,024,000 px.  That is the signature of a
#   draw whose colour is not coming from its texture and not coming from its
#   vertices either -- it comes from the port's hardcoded material source
#   (a7_vk32.c:2623, flags.w == 0 == D3DMCS_MATERIAL, with
#   D3DRS_COLORVERTEX(141) and D3DRS_DIFFUSEMATERIALSOURCE(145) both in the
#   DROPPED state list -- measured, see out/death2.log).
#
#   The car's shadow is exactly such a draw: CarPhysics_DrawBodyWheelAndSkidShadows
#   (CarPhysics.cpp:451) queues a world-space fan through
#   Quad2D_QueueFixedTriangle(0, v0, v1, v2, NULL, (Quad2D*)10) -- TEXTURE NULL,
#   vertex colour BLACK, alpha 0x32..0xff.  Its only colour is in its vertices.
#   Give it the material instead and it comes out white.
#
# WHAT THIS RUN MEASURES
#   A7VK_AB switches the 3D path BY FRAME NUMBER, so a capture 10 frames either
#   side of a switch is the same scene with ONE variable changed.  Mode vcol =
#   the vertex diffuse is used instead of the material (A7VK_AB=vcol).
#   Eight captures, four pairs: normal|vcol, vcol|normal, normal|vcol, vcol|normal.
#   If the white card is a vertex-coloured draw rendered with the material, the
#   card must go DARK in the vcol frames and come back in the normal ones.
#   If it does not, the mechanism is wrong and this round says so.
#
# CO-EXISTENCE -- the box has two workers and two games on one GPU is what killed
#   Miami's display this morning.  This script NEVER runs `pkill -x cmr2`:
#   it kills only the driver it started, by PID, and if any cmr2 it did not start
#   is alive it REFUSES to run.  (Ticket HARNESS-KILLS-HIS-GAME, 08:10.)
#
# Usage: ./run_card.sh [tag]
set -u
TAG=${1:-card1}
BIN=${BIN:-/home/deck/lena/work/PLAY/out-plain/cmr2}
GAME=/home/deck/lena/.lena_cmr2/game
OUT=/home/deck/lena/work/RACE/out
LOG=$OUT/$TAG.log
MINE=$$

KT() { journalctl -k --no-pager 2>/dev/null; }
ring()  { KT | grep -c 'ring gfx_0.0.0 timeout'; }
ring1() { KT | grep -c 'ring gfx_0.1.0 timeout'; }
mode2() { KT | grep -c 'MODE2 reset'; }
tcp()   { KT | grep -c 'Faulty UTCL2 client ID: TCP'; }

# ---- 1. never kill anything we did not start --------------------------------
# Shared guard: refuses on ANY cmr2 that is already alive (his game and a peer's
# look the same from here), and never does `pkill -x cmr2`.
. "$(dirname "$0")/gpu-guard.sh"
gpu_guard || exit 3

mkdir -p "$OUT"
rm -f /tmp/card.ppm.*
echo "=== $TAG ==="
echo "binary : $BIN"
echo "md5    : $(md5sum "$BIN" | cut -d' ' -f1)"
echo "--- KERNEL BEFORE ---"
echo "ring0=$(ring) ring1=$(ring1) mode2=$(mode2) tcp=$(tcp)"

# frame 3000 is ~53 s in (calibrated in run_framing.sh: 3319 -> t=57.2 s)
SEQ=${SEQ:-"w14,k=enter,w6,k=enter,w6,k=enter,w60,w10"}

A7VK_AB="0:normal,3020:vcol,3060:normal,3100:vcol,3140:normal" \
A7VK_SNAP="3010,3030,3050,3070,3090,3110,3130,3150:/tmp/card.ppm" \
DECK_DD7_CENSUS=1 DECK_DD7_CENSUS_EVERY=6000 \
DECK_DIN_TRACE=2 \
  timeout 200 python3 /home/deck/lena/work/RACE/drive.py "$BIN" "$TAG" "$SEQ" \
  > "$OUT/$TAG.drive.out" 2>&1
echo "drive.py exit=$?"

echo "--- KERNEL AFTER ---"
echo "ring0=$(ring) ring1=$(ring1) mode2=$(mode2) tcp=$(tcp)"

mkdir -p "$OUT/card"
i=0
for f in /tmp/card.ppm.*; do
    [ -e "$f" ] || continue
    mv "$f" "$OUT/card/$TAG.ppm.$(echo "$f" | sed 's/.*card\.ppm\.//')"
    i=$((i+1))
done
echo "moved $i frames to $OUT/card/"
grep -E '\[AB\]' "$LOG" 2>/dev/null | head -8
grep -E 'draws by FVF|refusedFvf' "$LOG" 2>/dev/null | tail -2
ps -eo pid,args | grep -E '[c]mr2' | grep -v grep || echo "no cmr2 left running"
