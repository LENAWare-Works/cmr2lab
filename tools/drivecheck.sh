#!/bin/sh
# cmr2-drivecheck.sh -- "can this cmr2 binary drive a car?" asked of the FILE.
#
# Sourced, not run:  . /home/deck/lena/cmr2-drivecheck.sh
#
#   cmr2_drives <binary>   0 = drives   1 = dead   2 = cannot tell
#
# WHY (2026-10-11, launcher lane)
#
#   A tool of ours deleted two statements out of Race_UpdatePlayerViewAndDrivenCars
#   at 08:39:06 (patch_racetrace.py used them as a str.replace anchor). The second
#   one assigns the bound of the per-car drive loop, so with it gone no car is ever
#   given an input and every car sits frozen -- while the binary still boots, still
#   presents frames, and still looks like a game. Four binaries in this workspace
#   are in that state; for a while the Desktop icon was launching one of them.
#
#   The check is static: find the function in the symbol table, then ask the code
#   whether it calls Physics_UpdateRateHold. That is the same question
#   work/DEMO-DRIVE-CRASH/loopcheck.sh asks of every binary in the workspace, and
#   it is calibrated against this workspace's own two arms (read 2026-10-11 11:0x):
#
#     DEAD   (+ hold=0) PLAY/out-plain/cmr2 @08:53, RACE/out-rt2/cmr2 @10:48,
#                       MENU-CAR-FLATTENED/out-md @09:01, out-md2 @09:13
#     DRIVES (+ hold=1) RACE/out-rt3, PLAY/out, RACE/out-race, PLAY/out-plain @11:02
#
#   A `grep 538124` for the store -- the third thing the restored block does -- reads
#   0 for EVERY binary here, good and dead alike, so it is not usable as a gate and
#   is not used. Do not "fix" this by adding it back.
#
# LIMITS, stated so nobody reads more into it than it says:
#   * it catches ONE regression class: a link from a tree whose drive loop was
#     damaged. A binary that passes can still be wrong in every other way.
#   * it says nothing about driving QUALITY, the demo car having a driver, the HUD,
#     the road, or the menu car. Those are other lanes' questions.
#   * the window is 0x900 bytes from the function's entry, the same window
#     loopcheck.sh uses. If the function ever grows past it, widen both.
#   * no nm/objdump on the box -> returns 2, and callers are expected to treat that
#     as "carry on as before", never as "refuse to start the game".
#
# Read-only. Opens nothing, starts nothing, needs no GPU.

cmr2_drives() {
    command -v nm >/dev/null 2>&1 || return 2
    command -v objdump >/dev/null 2>&1 || return 2
    [ -f "$1" ] || return 1
    _a=$(nm "$1" 2>/dev/null | awk '/_Z34Race_UpdatePlayerViewAndDrivenCarshi/{print $1; exit}')
    [ -n "$_a" ] || return 1          # no symbol: not a binary we can vouch for
    _s=$((0x$_a)); _e=$((_s + 0x900))
    _n=$(objdump -d -M intel --start-address=$_s --stop-address=$_e "$1" 2>/dev/null \
         | grep -c 'Physics_UpdateRateHoldv')
    [ "$_n" -gt 0 ] && return 0
    return 1
}
