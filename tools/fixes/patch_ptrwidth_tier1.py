#!/usr/bin/env python3
"""patch_ptrwidth_tier1.py -- the first tier of the pointer-width pass.

WHY THIS EXISTS
---------------
Every remaining x86_64 compile failure in the decomp tree is one class:
`cast from pointer to smaller type 'int' loses information`. The published
census (2026-10-12, tools/sweep-compile.sh) is 1,377 distinct sites across
33 files. This script does the cheapest tier of that work and nothing else.

WHAT IT CHANGES, AND WHY EACH ONE IS FAITHFUL

1. `Sprite_FillRect(int unused, short *pRect, BYTE *pColour, int layer)`
   -- 308 call sites across 14 files pass `(int)g_pGraphics + 0x150` into the
   FIRST parameter, and the function body never reads it (verified: the
   identifier `unused` appears exactly once in the definition, in the
   signature). In the original 32-bit build, `(int)ptr` was exact; on x86_64
   it truncates. Widening the parameter to `intptr_t` and the call sites to
   `(intptr_t)` restores the original meaning and changes no behaviour,
   because nothing reads the value.

2. `FileBuffer.cpp` -- `(int)pRecord < (int)((BYTE *)g_saveProfiles + 0x1954)`.
   A pointer comparison through truncated ints. Both operands point into the
   same object, so comparing them as `intptr_t` is the original comparison.

3. `Mesh.cpp` -- `} while ((int)pSlot < (int)&g_stageObjects[6000]);`  same
   shape, same fix.

4. `NetworkLeaderboards.cpp` -- `int addr = (int)&m_leaderboards;` and then
   `*(BYTE*)addr = 0;` inside the loop. This one is not cosmetic: on x86_64
   the address is truncated and the zeros are written somewhere else. The
   fix makes the pointer whole.

Every edit is anchored on an exact string, every file is backed up before it
is touched, and the script is idempotent: running it twice changes nothing.

USAGE
    python3 patch_ptrwidth_tier1.py /path/to/CMR2Decomp [--dry-run]
"""

import argparse
import os
import re
import shutil
import sys

STAMP = "ptrwidth-20261012"

# exact-anchor edits: (filename, old, new, required_count)
EXACT = [
    ("Sprite.h", "int Sprite_FillRect(int unused, short *pRect, BYTE *pColour, int layer);",
                 "int Sprite_FillRect(intptr_t unused, short *pRect, BYTE *pColour, int layer);", 1),
    ("Sprite.cpp", "int Sprite_FillRect(int unused, short *pRect, BYTE *pColour, int layer)",
                   "int Sprite_FillRect(intptr_t unused, short *pRect, BYTE *pColour, int layer)", 1),
    ("FileBuffer.cpp",
     "(int)pRecord < (int)((BYTE *)g_saveProfiles + 0x1954)",
     "(intptr_t)pRecord < (intptr_t)((BYTE *)g_saveProfiles + 0x1954)", 1),
    ("Mesh.cpp",
     "} while ((int)pSlot < (int)&g_stageObjects[6000]);",
     "} while ((intptr_t)pSlot < (intptr_t)&g_stageObjects[6000]);", 1),
    ("NetworkLeaderboards.cpp",
     "int addr = (int)&m_leaderboards;",
     "intptr_t addr = (intptr_t)&m_leaderboards;", 1),
    ("NetworkLeaderboards.cpp",
     "int endAddr = addr + sizeof(m_leaderboards);",
     "intptr_t endAddr = addr + sizeof(m_leaderboards);", 1),
]

# the one repeated call shape (308 sites, 14 files)
REGEX = (re.compile(r"\(int\)g_pGraphics \+ 0x150"),
         "(intptr_t)g_pGraphics + 0x150")


def backup(path):
    bak = "%s.bak-pre-%s" % (path, STAMP)
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    return bak


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tree")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    tree = os.path.abspath(a.tree)
    if not os.path.isdir(tree):
        sys.exit("not a directory: %s" % tree)

    edits = 0
    # 1. the repeated call shape, every .cpp in the tree
    for name in sorted(os.listdir(tree)):
        if not name.endswith(".cpp"):
            continue
        p = os.path.join(tree, name)
        src = open(p, encoding="utf-8", errors="surrogateescape").read()
        new, n = REGEX[0].subn(REGEX[1], src)
        if n:
            print("  %-24s %3d x  (int)g_pGraphics + 0x150" % (name, n))
            if not a.dry_run:
                backup(p)
                open(p, "w", encoding="utf-8", errors="surrogateescape").write(new)
            edits += n

    # 2. the exact-anchor edits
    for name, old, new, want in EXACT:
        p = os.path.join(tree, name)
        src = open(p, encoding="utf-8", errors="surrogateescape").read()
        got = src.count(old)
        if new in src and got == 0:
            print("  %-24s already applied" % name)
            continue
        if got != want:
            sys.exit("  ANCHOR PROBLEM in %s: found %d, expected %d\n    %s"
                     % (name, got, want, old))
        print("  %-24s   1 x  %s" % (name, old[:60]))
        if not a.dry_run:
            backup(p)
            open(p, "w", encoding="utf-8", errors="surrogateescape").write(src.replace(old, new))
        edits += 1

    print("\n%s: %d edits across the tree" % ("DRY RUN" if a.dry_run else "APPLIED", edits))
    if not a.dry_run:
        print("backups: *.bak-pre-%s" % STAMP)


if __name__ == "__main__":
    main()
