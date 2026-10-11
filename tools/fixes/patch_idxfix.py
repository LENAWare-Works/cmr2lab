#!/usr/bin/env python3
"""patch_idxfix.py -- the INDEX BASE, switchable, so it can be A/B'd in one build.

Measured by patch_idxtrace.py in a full run (work/RACE/out/idxtrace_race.log):

    draws with startVert != 0 : 404,000
    relOk  (every RAW index inside [0,numVerts))  : 404,000   (100.00 %)
    absOk  (every SUBTRACTED index inside range)   :       0   (  0.00 %)
    indices: raw in range 15,969,393 / 15,969,393 ; subtracted in range 349,174

so `idxScratch[i] = idx[i] - startVert` re-bases an array that is already
relative, and the base shift in the same call undoes it: the vertex actually
read is `data + idx*stride` instead of `data + (startVert + idx)*stride`.

DEFAULT IS UNCHANGED -- this patch only adds the switch, so the behaviour every
number in this lane was measured against stays the default:

    (unset)            -> subtract (today's behaviour)
    A7VK_IDXBASE=raw   -> do not subtract (the fixed behaviour)

Idempotent.
"""
import os
import shutil
import sys
import time

SRC = "/home/deck/lena/.lena_cmr2/port/rhi/deck_dd7.cpp"
TS = time.strftime("%Y%m%d-%H%M%S")

DECL_ANCHOR = """/* --- LENA-IDXTRACE (work/RACE/patch_idxtrace.py): off unless DECK_IDXTRACE --- */"""
DECL_ADD = """/* --- LENA-IDXFIX (work/RACE/patch_idxfix.py): A7VK_IDXBASE=raw -> do not
 * re-base indices that Mesh_BuildParts already rebased (see the report). --- */
static int ib_raw = -1;
static int ib_is_raw(void)
{
    if (ib_raw < 0) { const char *e = getenv("A7VK_IDXBASE"); ib_raw = (e && e[0] == 'r') ? 1 : 0; }
    return ib_raw;
}

""" + DECL_ANCHOR

OLD = """    if (startVert) {
        if (numIdx > idxScratchCap) {
"""
NEW = """    if (startVert && !ib_is_raw()) {
        if (numIdx > idxScratchCap) {
"""


def main():
    src = open(SRC, encoding="utf-8", errors="surrogateescape").read()
    if "LENA-IDXFIX" in src:
        print("skip (already applied)")
        return 0
    if src.count(DECL_ANCHOR) != 1 or src.count(OLD) != 1:
        print("FAIL anchors x%d / x%d" % (src.count(DECL_ANCHOR), src.count(OLD)))
        return 1
    src = src.replace(DECL_ANCHOR, DECL_ADD, 1).replace(OLD, NEW, 1)
    shutil.copy2(SRC, SRC + ".bak-pre-idxfix-" + TS)
    open(SRC, "w", encoding="utf-8", errors="surrogateescape").write(src)
    print("applied, backup:", SRC + ".bak-pre-idxfix-" + TS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
