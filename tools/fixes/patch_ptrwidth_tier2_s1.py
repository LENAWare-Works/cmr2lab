#!/usr/bin/env python3
"""patch_s1.py -- RAISE-THE-NUMBER stage 1.

Driven ENTIRELY by the compiler's own error list (file,line,col) from the
x86_64 sweep, plus a small table of exact-string type corrections.

Every edit is one of:
  DECL  widening a declaration or field that holds a pointer (int -> intptr_t,
        void*->int where the value really is an int field).  On i386 intptr_t
        IS int, so nothing here can change the 32-bit play build.
  SITE  replacing (int)ptr / (unsigned int)ptr with (intptr_t)prt at a column the
        compiler itself pointed at.
Nothing else is touched.  Sites that no rule claims are PRINTED, not guessed at.
"""
import os, re, sys, shutil, datetime, collections

ROOT = "/home/deck/lena/.lena_cmr2/port/tree/CMR2Decomp"
LOG  = "/home/deck/lena/work/RTN-20261012/sweep-before/log"
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
DRY = "--apply" not in sys.argv

def rd(p): return open(os.path.join(ROOT, p), errors="replace").read()
def wr(p, s):
    full = os.path.join(ROOT, p)
    if not DRY:
        if not os.path.exists(full + ".bak-pre-rtn-" + STAMP):
            shutil.copy2(full, full + ".bak-pre-rtn-" + STAMP)
    if DRY: return
    open(full, "w").write(s)

# ---------------------------------------------------------------- DECL edits --
# (file, exact old text, exact new text, why)
DECL = [
 ("Frontend.h",
  "    static void *GetArchivePrimaryIDEntry(int index);",
  "    static int GetArchivePrimaryIDEntry(int index);",
  "returns g_unk0x00516b40.ids[index], an int; every one of its 20+ callers casts it back to int"),
 ("Frontend.h",
  "    static void *GetArchiveSecondaryIDEntry(int index);",
  "    static int GetArchiveSecondaryIDEntry(int index);",
  "same table, ids[index+22]"),
 ("Frontend.cpp",
  "void *CFrontend::GetArchivePrimaryIDEntry(int index)\n{\n    return (void *)g_unk0x00516b40.ids[index];\n}",
  "int CFrontend::GetArchivePrimaryIDEntry(int index)\n{\n    return g_unk0x00516b40.ids[index];\n}",
  "definition"),
 ("Frontend.cpp",
  "void *CFrontend::GetArchiveSecondaryIDEntry(int index)\n{\n    return (void *)g_unk0x00516b40.ids[index + 22];\n}",
  "int CFrontend::GetArchiveSecondaryIDEntry(int index)\n{\n    return g_unk0x00516b40.ids[index + 22];\n}",
  "definition"),
 ("Car.cpp",
  "    static void *GetArchivePrimaryIDEntry(int index);",
  "    static int GetArchivePrimaryIDEntry(int index);",
  "this file's own redeclaration of the same function"),
 # --- Menu: the callback slot is a pointer slot -----------------------------
 ("Menu.h",
  "    int param;              // 0x10 action callback for the frontend",
  "    intptr_t param;         // 0x10 action callback for the frontend (pointer-wide)",
  "MenuItem::param holds a function pointer; Menu.cpp calls it as one"),
 ("Menu.h",
  "void Menu_AddItemType3(Menu *pMenu, int stringId, short id, BYTE min, BYTE max, BYTE flag2, int unused, int param, short value);",
  "void Menu_AddItemType3(Menu *pMenu, int stringId, short id, BYTE min, BYTE max, BYTE flag2, int unused, intptr_t param, short value);",
  "callback parameter"),
 ("Menu.h",
  "void Menu_AddItemType6(Menu *pMenu, int stringId, short id, BYTE min, BYTE max, BYTE flag2, int unused, int param, short value);",
  "void Menu_AddItemType6(Menu *pMenu, int stringId, short id, BYTE min, BYTE max, BYTE flag2, int unused, intptr_t param, short value);",
  "callback parameter"),
 ("Menu.h",
  "void Menu_AddItemType4(Menu *pMenu, int stringId, short id, int param, short value);",
  "void Menu_AddItemType4(Menu *pMenu, int stringId, short id, intptr_t param, short value);",
  "callback parameter"),
 ("Menu.h",
  "void Menu_AddItemType1(Menu *pMenu, int stringId, short id, int param, short value);",
  "void Menu_AddItemType1(Menu *pMenu, int stringId, short id, intptr_t param, short value);",
  "callback parameter"),
 ("Menu.h",
  "void Menu_AddItemType2(Menu *pMenu, int stringId, short id, Menu *pSubMenu, int param, short value);",
  "void Menu_AddItemType2(Menu *pMenu, int stringId, short id, Menu *pSubMenu, intptr_t param, short value);",
  "callback parameter"),
 ("Menu.h",
  "void Menu_SetNextAction(int action);",
  "void Menu_SetNextAction(intptr_t action);",
  "action is a Menu* -- Menu_SetNextAction((int)&g_menu0x...) is the 99-site form"),
 ("Menu.h",
  "int Menu_Update(Menu *pMenu, unsigned int input);",
  "intptr_t Menu_Update(Menu *pMenu, unsigned int input);",
  "its return value is used as a Menu* by 3 callers"),
 ("Menu.cpp",
  "int g_menuNextAction;",
  "intptr_t g_menuNextAction;",
  "holds a Menu* (Menu.cpp:467,480,518) and is handed back as the next menu"),
 ("Menu.cpp",
  "void Menu_AddItemType3(Menu *pMenu, int stringId, short id, BYTE min, BYTE max, BYTE flag2, int unused, int param, short value)",
  "void Menu_AddItemType3(Menu *pMenu, int stringId, short id, BYTE min, BYTE max, BYTE flag2, int unused, intptr_t param, short value)",
  "definition"),
 ("Menu.cpp",
  "void Menu_AddItemType6(Menu *pMenu, int stringId, short id, BYTE min, BYTE max, BYTE flag2, int unused, int param, short value)",
  "void Menu_AddItemType6(Menu *pMenu, int stringId, short id, BYTE min, BYTE max, BYTE flag2, int unused, intptr_t param, short value)",
  "definition"),
 ("Menu.cpp",
  "void Menu_AddItemType4(Menu *pMenu, int stringId, short id, int param, short value)",
  "void Menu_AddItemType4(Menu *pMenu, int stringId, short id, intptr_t param, short value)",
  "definition"),
 ("Menu.cpp",
  "void Menu_AddItemType1(Menu *pMenu, int stringId, short id, int param, short value)",
  "void Menu_AddItemType1(Menu *pMenu, int stringId, short id, intptr_t param, short value)",
  "definition"),
 ("Menu.cpp",
  "void Menu_AddItemType2(Menu *pMenu, int stringId, short id, Menu *pSubMenu, int param, short value)",
  "void Menu_AddItemType2(Menu *pMenu, int stringId, short id, Menu *pSubMenu, intptr_t param, short value)",
  "definition"),
 ("Menu.cpp",
  "void Menu_SetNextAction(int action)",
  "void Menu_SetNextAction(intptr_t action)",
  "definition"),
 ("Menu.cpp",
  "int Menu_Update(Menu *pMenu, unsigned int input)",
  "intptr_t Menu_Update(Menu *pMenu, unsigned int input)",
  "definition"),
 ("Menu.cpp",
  "    MenuItem *pItem;\n    int action;",
  "    MenuItem *pItem;\n    intptr_t action;",
  "the action that Menu_Update returns"),
 # --- locals that hold a pointer (no ABI effect anywhere: they are locals) ---
 ("Frontend.cpp",
  "    int base;\n    unsigned int *pDevice;",
  "    intptr_t base;\n    unsigned int *pDevice;",
  "base holds the pointer from RallyData_GetAvailableCategorySaveRecord and is used for arithmetic"),
 ("GameInfo.cpp",
  "    int result;",
  "    intptr_t result;",
  "GameInfo.cpp:4800 stores Menu_Update's return (a Menu*) here -- applied to every 'int result;' in this file, 2 of them, both pointer/clamped mixes: SEE REPORT"),
 ("GameMenus.cpp",
  "    int action;",
  "    intptr_t action;",
  "GameMenus.cpp:3930 stores Menu_Update's return (a Menu*) here"),
 ("StageUI.cpp",
  "    int next;",
  "    intptr_t next;",
  "StageUI.cpp:1011 stores Menu_Update's return (a Menu*) here"),
]

# --------------------------------------------------------------- SITE rules --
# lines the compiler flagged, and which rule claims them
def rule_for(fname, linetext):
    if "Menu_AddItemType" in linetext:
        return "menu-item callback arg -> intptr_t (param widened in Menu.h/Menu.cpp)"
    if "Menu_SetNextAction(" in linetext:
        return "Menu_SetNextAction arg -> intptr_t (param + g_menuNextAction widened)"
    if "GetArchivePrimaryIDEntry" in linetext or "GetArchiveSecondaryIDEntry" in linetext:
        return "already fixed by the return-type correction; cast becomes a no-op"
    return None

# sites I verified by hand are pure address context (compare / arithmetic):
ADDR = {
 ("RallyTiming.cpp", 109), ("RallyTiming.cpp", 209), ("RallyTiming.cpp", 279),
 ("NetPlayers.cpp", 139), ("NetPlayers.cpp", 697), ("NetPlayers.cpp", 978),
 ("SurfaceTypes.cpp", 350), ("SurfaceTypes.cpp", 745), ("SurfaceTypes.cpp", 1593),
 ("Frontend.cpp", 354), ("Frontend.cpp", 1696),
 ("Frontend.cpp", 1338), ("Frontend.cpp", 1554), ("Frontend.cpp", 1589),
 ("RallyTiming.cpp", 419), ("RallyTiming.cpp", 422),
 ("NetPlayers.cpp", 811), ("NetPlayers.cpp", 939), ("NetPlayers.cpp", 961),
 ("GameInfo.cpp", 931),
}
for k in list(ADDR):
    if k[0] in ("RallyTiming.cpp","NetPlayers.cpp","SurfaceTypes.cpp","Frontend.cpp"):
        pass
CASTRE = re.compile(r'\((unsigned\s+int|int)\)')

# ------------------------------------------------------------------- DECLs ---
print("=== DECL edits ===")
changed = collections.Counter()
for f, old, new, why in DECL:
    s = rd(f); n = s.count(old)
    if n == 0:
        print(f"  !! NOT FOUND in {f}: {old[:70]!r}")
        continue
    if n > 1 and "int result" in old:
        print(f"  ** {f}: '{old.strip()}' occurs {n}x -- applying to all, check each")
    wr(f, s.replace(old, new))
    changed[f] += n
    print(f"  {f}: {n}x  {old.splitlines()[0].strip()[:60]}   -- {why}")

# -------------------------------------------------------------------- SITEs --
print("\n=== SITE edits (from the compiler's own (file,line,col) list) ===")
persite = collections.defaultdict(collections.Counter)
unclaimed = []
for fn in sorted(os.listdir(LOG)):
    base = fn[:-4]                      # e.g. GameInfo.cpp
    txt = open(os.path.join(LOG, fn), errors="replace").read()
    hits = [(int(a), int(b)) for a, b in re.findall(r'\.cpp:(\d+):(\d+): error: cast from pointer to smaller type', txt)]
    if not hits: continue
    lines = rd(base).split("\n")
    for ln, col in sorted(hits, reverse=True):   # right-to-left so columns stay valid
        src = lines[ln-1]
        r = rule_for(base, src)
        if r is None and (base, ln) in ADDR:
            r = "address context (compare / pointer arithmetic) -> intptr_t"
        if r is None:
            unclaimed.append((base, ln, col, src.strip()))
            continue
        if "already fixed" in r:
            persite[base]["noop (decl fix)"] += 1
            continue
        m = CASTRE.match(src, col-1)
        if not m:
            persite[base]["col mismatch"] += 1
            unclaimed.append((base, ln, col, "COLUMN IS NOT A (int) CAST: " + src.strip()))
            continue
        new = src[:col-1] + "(intptr_t)" + src[col-1+len(m.group(0)):]
        lines[ln-1] = new
        persite[base][r] += 1
    wr(base, "\n".join(lines))

for f in sorted(persite):
    print(f"  {f}: " + ", ".join(f"{v}x {k}" for k, v in persite[f].items()))

print("\n=== sites no rule claimed (left alone deliberately) ===")
byfile = collections.Counter(u[0] for u in unclaimed)
for f, n in byfile.most_common():
    print(f"  {n:5d}  {f}")
print(f"  TOTAL unclaimed: {len(unclaimed)}")
open("/home/deck/lena/work/RTN-20261012/unclaimed_s1.txt", "w").write(
    "\n".join(f"{a}:{b}:{c}: {d}" for a, b, c, d in unclaimed))
print("\nDRY RUN" if DRY else "\nAPPLIED (backups: *.bak-pre-rtn-" + STAMP + ")")
