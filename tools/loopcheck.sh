#!/bin/sh
# loopcheck.sh -- which cmr2 binaries in this workspace have a DEAD DRIVE LOOP?
#
# WHY
#   At 08:39:06 the DEMO-DRIVE-CRASH instrumentation (patch_racetrace.py)
#   replaced two real statements in Race_UpdatePlayerViewAndDrivenCars --
#       Physics_UpdateRateHold();
#       g_unk0x00538124 = Car_UpdateEngineNoteFalloff(&g_unk0x00537f60);
#   -- with its own trace block, because they were its str.replace ANCHOR.
#   With them gone the per-car loop's bound is never assigned, so the loop
#   never runs, no car is ever given an input, and the physics never steps.
#
#   Every binary linked from that tree AFTER 08:39:07 therefore cannot drive.
#   This script says which ones, by looking at the code, not at timestamps:
#   it finds Race_UpdatePlayerViewAndDrivenCars and asks whether that function
#   calls Physics_UpdateRateHold.
#
# Usage: ./loopcheck.sh            (read only; nothing is run, nothing is opened)
set -u
for b in $(find /home/deck/lena -name cmr2 -type f -perm -u+x 2>/dev/null | sort); do
    sz=$(stat -c %s "$b")
    [ "$sz" -gt 1000000 ] || continue
    a=$(nm "$b" 2>/dev/null | awk '/_Z34Race_UpdatePlayerViewAndDrivenCarshi/{print $1; exit}')
    if [ -z "$a" ]; then
        echo "NO-SYM   $(stat -c %y "$b" | cut -d. -f1)  $b"
        continue
    fi
    s=$((0x$a)); e=$((s + 0x900))
    n=$(objdump -d -M intel --start-address=$s --stop-address=$e "$b" 2>/dev/null \
        | grep -c "Physics_UpdateRateHoldv")
    if [ "$n" -gt 0 ]; then v="DRIVES  "; else v="DEAD    "; fi
    printf "%s %s  md5=%s  %s\n" "$v" "$(stat -c %y "$b" | cut -d. -f1)" "$(md5sum "$b" | cut -c1-12)" "$b"
done
