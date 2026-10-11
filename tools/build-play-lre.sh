#!/bin/sh
# build-play-lre.sh -- rebuild ~/lena/work/PLAY/out-plain/cmr2 and PROVE it drives
#                      before it is allowed to replace anything.
#
# WHY THIS EXISTS (2026-10-11, Lena-on-the-Deck, launcher lane)
#
#   ~/lena/cmr2lre.sh -- the Desktop icon Miami actually clicks -- takes the
#   first of three paths that EXISTS, not the first that WORKS:
#       work/PLAY/out-plain/cmr2   <- 08:53, DEAD since the 08:39:06 racelink
#       work/PLAY/out/cmr2            (UBSan CHECKED build: dies on benign UB)
#       work/RACE/out-race/cmr2       (04:19)
#   So between 08:53 and now the icon launched a world where no car can be driven
#   (he did exactly that at 10:03; see NOTE-to-phone-DEMO-DRIVE-CRASH-4.md).
#
#   The object of this script is not "an incremental build". It is: out-plain is
#   the PLAY-named build, so it must never again be a binary nobody has checked.
#   The check is the same one work/DEMO-DRIVE-CRASH/loopcheck.sh uses, applied to
#   the LINKED artefact before it is installed:
#
#       does Race_UpdatePlayerViewAndDrivenCars actually call
#       Physics_UpdateRateHold and Car_UpdateEngineNoteFalloff and store the
#       loop bound to g_unk0x00538124?
#
#   If it does not, this script leaves out-plain exactly as it found it and exits
#   non-zero. A dead build never becomes the first pick again.
#
# NOT DONE HERE, on purpose:
#   * the platform objects (:work/PLAY/out/obj) and the rhi object
#     (port/rhi/deck_dd7.o) are SHARED with every other lane's link line. This
#     script does not recompile them -- touching them would change other lanes'
#     controls mid-round. Whatever is there is what gets linked, same as
#     build-plain.sh.
#   * nothing is launched, no window, no GPU. Compile + link + static check only.
#
# Usage: ./build-play-lre.sh            (safe to re-run; recompiles only stale TUs)
set -u

. /home/deck/lena/toolchain/env.sh
export ZIG_GLOBAL_CACHE_DIR=/home/deck/lena/state/zigcache

ROOT=/home/deck/lena/.lena_cmr2/port/tree/CMR2Decomp
PLAT=/home/deck/lena/.lena_cmr2/port/platform
SHIM=/home/deck/lena/.lena_cmr2/port/tree/third_party/dx7sdk-7001/include
OBJ=/home/deck/lena/work/PLAY/obj-plain
OUT=/home/deck/lena/work/PLAY/out-plain
PLATOBJ=/home/deck/lena/work/PLAY/out/obj
PORT=/home/deck/lena/.lena_cmr2/port
SDL3=$PORT/third_party/sdl3-i386
TARGET=x86-linux-gnu
TMP="$OUT/.cmr2.new.$$"
STAMP=$(date +%Y%m%d-%H%M%S)

cleanup() { rm -f "$TMP"; }
trap cleanup EXIT INT TERM

# ---------------------------------------------------------------- 1. compile --
PASS=0; FAIL=0; SKIP=0
for f in "$ROOT"/*.cpp; do
  n=$(basename "$f"); b=${n%.cpp}
  case "$n" in
    Zlib*) STD="-std=gnu++14"; EXTRA="-I$ROOT/zlib" ;;
    *)     STD="-std=c++17";   EXTRA="" ;;
  esac
  o="$OBJ/$b.o"
  if [ -f "$o" ] && [ "$o" -nt "$f" ] && [ -f "$o.plain" ]; then SKIP=$((SKIP+1)); continue; fi
  if zig c++ -target $TARGET -O0 -fno-sanitize=undefined -w -Wno-c++11-narrowing $STD -DCMR2_NATIVE=1 \
       -include "$PLAT/platform_types.h" \
       -I"$PLAT" -I"$ROOT" -I"$SHIM" $EXTRA \
       -c "$f" -o "$o" 2>/tmp/bpl_$n.txt; then
    touch "$o.plain"; PASS=$((PASS+1)); echo "  compile OK   $n"
  else
    FAIL=$((FAIL+1)); echo "  compile FAIL $n :: $(grep -m1 'error:' /tmp/bpl_$n.txt)"
  fi
done
echo "game objects: $PASS compiled, $SKIP already current, $FAIL failed"
[ "$FAIL" -ne 0 ] && { echo "REFUSING: $FAIL translation unit(s) failed. out-plain untouched."; exit 1; }

# ------------------------------------------------------------------- 2. link --
SDL_LIB=""
[ -f "$SDL3/lib/libSDL3.a" ] && SDL_LIB="$SDL3/lib/libSDL3.a"
echo "linking $TMP ..."
# shellcheck disable=SC2086
zig c++ -target x86-linux-gnu.2.43 -o "$TMP" \
  "$OBJ"/*.o "$PLATOBJ"/*.o "$PORT/rhi/deck_dd7.o" "$PORT/rhi/a7_vk32.o" \
  -L/usr/lib32 -L/usr/lib64 $SDL_LIB -lX11 -lX11-xcb -lxcb -lvulkan -ldl -lpthread -lm \
  -Wl,--allow-shlib-undefined > /tmp/bpl_link.log 2>&1
rc=$?
if [ $rc -ne 0 ]; then
  echo "REFUSING: link exit=$rc. out-plain untouched."
  grep -o 'undefined symbol: [^ ]*' /tmp/bpl_link.log | sort -u | head -20
  exit 1
fi
chmod +x "$TMP"

# --------------------------------------------------- 3. is it a build that DRIVES?
# Race_UpdatePlayerViewAndDrivenCars, and the three things the drive-bound block
# puts back inside it. Read out of the linked file, not out of the source.
a=$(nm "$TMP" 2>/dev/null | awk '/_Z34Race_UpdatePlayerViewAndDrivenCarshi/{print $1; exit}')
if [ -z "$a" ]; then
  echo "REFUSING: no Race_UpdatePlayerViewAndDrivenCars symbol in the link output."
  exit 1
fi
s=$((0x$a)); e=$((s + 0x900))
dis=$(objdump -d -M intel --start-address=$s --stop-address=$e "$TMP" 2>/dev/null)
nhold=$(printf '%s\n' "$dis" | grep -c 'Physics_UpdateRateHoldv')
nnote=$(printf '%s\n' "$dis" | grep -c 'Car_UpdateEngineNoteFalloff')
nbnd=$(printf '%s\n' "$dis"  | grep -c '538124')
echo "drive-bound check: Physics_UpdateRateHold=$nhold  Car_UpdateEngineNoteFalloff=$nnote  (store-0x538124 text: $nbnd -- informational)"
# The gate is the two restored STATEMENTS, and it is the same one loopcheck.sh uses
# (it tests only the first of them). Calibrated against the workspace itself, not
# against an opinion: out-rt3 and PLAY/out read hold=1 note=1 and drive; the 08:39
# regression reads hold=0 note=0. A grep for the literal '538124' in this window
# reads 0 for EVERY binary here -- good and dead alike -- so it is printed and not
# gated on. Measured 2026-10-11 11:0x, four binaries, both arms.
if [ "$nhold" -lt 1 ] || [ "$nnote" -lt 1 ]; then
  echo "REFUSING: this link is a DEAD BUILD (the 08:39:06 regression). out-plain untouched."
  exit 2
fi

# ------------------------------------------------------------- 4. install it ---
old=$(md5sum "$OUT/cmr2" 2>/dev/null | cut -c1-12)
if [ -f "$OUT/cmr2" ]; then
  cp -a "$OUT/cmr2" "$OUT/cmr2.bak-dead-pre-lre-$STAMP" 2>/dev/null
fi
mv -f "$TMP" "$OUT/cmr2"
trap - EXIT INT TERM
new=$(md5sum "$OUT/cmr2" | cut -c1-12)
echo "installed: $OUT/cmr2"
echo "  was  $old   (kept as cmr2.bak-dead-pre-lre-$STAMP)"
echo "  now  $new"
echo "  $(date "+%Y-%m-%d %H:%M:%S")  $new  hold=$nhold note=$nnote  built by build-play-lre.sh" >> "$OUT/.lre-buildlog"
# provenance: which source revisions this binary is a snapshot of
{ echo "--- $STAMP  md5=$new"
  for f in "$ROOT"/*.cpp; do stat -c '%y %s %n' "$f"; done
} >> "$OUT/.lre-source-stamp-$STAMP"
echo "source stamp: $OUT/.lre-source-stamp-$STAMP"
echo "NOTE: not launched, not tested on the GPU -- the static drive-bound check above"
echo "      is the gate; a live run belongs to whoever next holds the GPU."
exit 0
