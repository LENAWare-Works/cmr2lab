#!/bin/bash
# sweep.sh -- x86_64 compile census, same flags/harness as tools/sweep-compile.sh.
# Usage: sweep.sh OUTDIR [target]
set -u
. /home/deck/lena/toolchain/env.sh
export ZIG_GLOBAL_CACHE_DIR=/home/deck/lena/toolchain/zcache-local
export ZIG_LOCAL_CACHE_DIR=/home/deck/lena/toolchain/zcache-local-local
mkdir -p "$ZIG_GLOBAL_CACHE_DIR" "$ZIG_LOCAL_CACHE_DIR"
ROOT=/home/deck/lena/.lena_cmr2/port/tree/CMR2Decomp
PLAT=/home/deck/lena/.lena_cmr2/port/platform
SHIM=/home/deck/lena/.lena_cmr2/port/tree/third_party/dx7sdk-7001/include
OUT=${1:?outdir}
TARGET=${2:-x86_64-linux-gnu}
mkdir -p "$OUT/obj" "$OUT/log"
: > "$OUT/results.txt"; : > "$OUT/all_errors.txt"
PASS=0; FAIL=0
for f in "$ROOT"/*.cpp; do
  n=$(basename "$f"); b=${n%.cpp}
  case "$n" in Zlib*) STD="-std=gnu++14"; EXTRA="-I$ROOT/zlib" ;; *) STD="-std=c++17"; EXTRA="" ;; esac
  if zig c++ -target $TARGET -w -Wno-c++11-narrowing -ferror-limit=0 $STD -DCMR2_NATIVE=1 \
       -include "$PLAT/platform_types.h" -I"$PLAT" -I"$ROOT" -I"$SHIM" $EXTRA \
       -c "$f" -o "$OUT/obj/$b.o" > "$OUT/log/$n.log" 2>&1; then
    echo "PASS $n" >> "$OUT/results.txt"; PASS=$((PASS+1))
  else
    FAIL=$((FAIL+1))
    e=$(grep -m1 -E 'error:' "$OUT/log/$n.log" | sed 's/^.*error: //' | cut -c1-110)
    echo "FAIL $n :: $e" >> "$OUT/results.txt"
    grep -E 'error:' "$OUT/log/$n.log" | sed "s|^.*/CMR2Decomp/||" >> "$OUT/all_errors.txt"
  fi
done
echo "=== sweep  target=$TARGET  includes: PLAT,ROOT,SHIM ==="
echo "PASS $PASS  FAIL $FAIL  TOTAL $((PASS+FAIL))"
echo "objects produced: $(ls "$OUT/obj" 2>/dev/null | wc -l)"
echo
echo "=== ranked failure REASONS (first error per file) ==="
grep '^FAIL' "$OUT/results.txt" | sed 's/^FAIL [^:]*:: //' | sed -E "s/'[^']*'/'X'/g; s/\"[^\"]*\"/\"X\"/g" | sort | uniq -c | sort -rn | head -20
echo
echo "=== the failures ==="
grep '^FAIL' "$OUT/results.txt"
