#!/bin/sh
# gpu-guard.sh -- sourced by every run script in this directory. Source, do not run.
#
# WHY (ticket HARNESS-KILLS-HIS-GAME, from lena-on-the-phone, 2026-10-11 08:10):
#   Every run script here used to open with `pkill -x cmr2` -- unconditional, matched
#   BY NAME.  When a test was launched while Miami was playing, his session died on the
#   script's first line, before any measurement began, and from his side it looked
#   exactly like a crash.  His playtime is the product; a measurement that costs him a
#   session costs more than it buys.  Caught live at 08:08:26.
#
#   So: kill BY PID, only what this script started; and if a game is already running
#   that we did not start, REFUSE with a clear line instead of fighting it.
#
# Also, two `cmr2` on one GPU is what wedged the display at 07:25 this morning.
#
# Usage:
#   . "$(dirname "$0")/gpu-guard.sh"
#   gpu_guard        || exit 3      # before launching: refuse if a foreign game is up
#   gpu_stop_own                    # after  launching: stop OUR driver and its child

# Refuse if any cmr2 is alive.  Returns 0 when the GPU is clear.
gpu_guard() {
    # the real binary is the first word of the args; ignore our own plumbing
    foreign=$(ps -eo pid,args | grep -E '[c]mr2' | grep -v 'gpu-guard' | wc -l)
    if [ "$foreign" -ne 0 ]; then
        echo "REFUSING TO RUN: $foreign cmr2 process(es) already alive (not started by this script):"
        ps -eo pid,lstart,args | grep -E '[c]mr2' | grep -v grep
        echo "  A test that cannot tell his game from its own is not safe to run while he is on the machine."
        echo "  (No pkill by name here, on purpose -- see ticket HARNESS-KILLS-HIS-GAME.)"
        return 1
    fi
    return 0
}

# Stop only the driver processes of ours and the games they own (child PIDs).
gpu_stop_own() {
    for d in $(ps -eo pid,args | grep "[R]ACE/drive\.py" | awk '{print $1}'); do
        for g in $(ps -eo pid,ppid | awk -v d="$d" '$2==d {print $1}'); do
            case "$(ps -o args= -p "$g" 2>/dev/null)" in
                *cmr2*) echo "gpu-guard: killing our game pid $g (child of our driver $d)"; kill -9 "$g" 2>/dev/null ;;
            esac
        done
        echo "gpu-guard: killing our driver pid $d"
        kill -9 "$d" 2>/dev/null
    done
    return 0
}
