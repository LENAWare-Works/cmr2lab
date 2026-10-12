#!/bin/bash
# audit.sh OUTDIR -- compile every TU with -ferror-limit=0 and NO -w, with
# -Wshorten-64-to-32 on, purely to see WHERE a 64-bit value lands in a 32-bit
# container. Errors and warnings are both emitted for the whole TU.
set -u
. /home/deck/lena/toolchain/env.sh
export ZIG_GLOBAL_CACHE_DIR=/home/deck/lena/toolchain/zcache-local
ROOT=/home/deck/lena/.lena_cmr2/port/tree/CMR2Decomp
PLAT=/home/deck/lena/.lena_cmr2/port/platform
SHIM=/home/deck/lena/.lena_cmr2/port/tree/third_party/dx7sdk-7001/include
OUT=$1; mkdir -p "$OUT"
for f in "$ROOT"/*.cpp; do
  n=$(basename "$f"); b=${n%.cpp}
  case "$n" in Zlib*) STD="-std=gnu++14"; EXTRA="-I$ROOT/zlib" ;; *) STD="-std=c++17"; EXTRA="" ;; esac
  zig c++ -target x86_64-linux-gnu -Wshorten-64-to-32 -Wno-everything -Wshorten-64-to-32 \
      -ferror-limit=0 $STD -DCMR2_NATIVE=1 \
      -include "$PLAT/platform_types.h" -I"$PLAT" -I"$ROOT" -I"$SHIM" $EXTRA \
      -c "$f" -o /dev/null > "$OUT/$n.log" 2>&1
done
