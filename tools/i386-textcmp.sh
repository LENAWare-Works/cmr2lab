#!/bin/bash
# textnow.sh <name> -- compile the CURRENT file for i386 at its canonical path and
# compare .text against the object built at 17:38 from the UNTOUCHED tree
# (i386-before/).  Identical path, identical flags -> only the content can differ.
set -u
. /home/deck/lena/toolchain/env.sh
export ZIG_GLOBAL_CACHE_DIR=/home/deck/lena/toolchain/zcache-local
ROOT=/home/deck/lena/.lena_cmr2/port/tree/CMR2Decomp
PLAT=/home/deck/lena/.lena_cmr2/port/platform
SHIM=/home/deck/lena/.lena_cmr2/port/tree/third_party/dx7sdk-7001/include
W=/home/deck/lena/work/RTN-20261012/tc-now; mkdir -p $W
n=$1
zig c++ -target x86-linux-gnu -O0 -w -Wno-c++11-narrowing -std=c++17 -DCMR2_NATIVE=1 \
  -include "$PLAT/platform_types.h" -I"$PLAT" -I"$ROOT" -I"$SHIM" -c "$ROOT/$n.cpp" -o $W/$n.o || { echo "FAIL NOW $n"; exit 3; }
objcopy -O binary --only-section=.text /home/deck/lena/work/RTN-20261012/i386-before/$n.o $W/$n.b.text
objcopy -O binary --only-section=.text $W/$n.o $W/$n.a.text
if cmp -s $W/$n.b.text $W/$n.a.text; then echo "SAME TEXT  $n.cpp  (i386 .text $(stat -c%s $W/$n.a.text) bytes, before 17:38 vs now)"
else echo "TEXT DIFF  $n.cpp  $(cmp -l $W/$n.b.text $W/$n.a.text | wc -l) bytes differ"; fi
