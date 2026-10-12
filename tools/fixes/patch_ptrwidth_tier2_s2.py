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
LOG  = "/home/deck/lena/work/RTN-20261012/sweep-s1/log"
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
DRY = "--apply" not in sys.argv

def rd(p): return open(os.path.join(ROOT, p), errors="replace").read()
def wr(p, s):
    full = os.path.join(ROOT, p)
    if not DRY:
        if not os.path.exists(full + ".bak-S2-" + STAMP):
            shutil.copy2(full, full + ".bak-S2-" + STAMP)
    if DRY: return
    open(full, "w").write(s)

DECL = [
 # --- Font_Unused: takes the caller's string pointer (3 sites) ---------------
 ("Font.h",
  "int Font_Unused(int unused1, int unused2);",
  "int Font_Unused(intptr_t unused1, int unused2);",
  "callers pass CFrontend::m_stringDest (FrontendDraw, FrontendScreens, GameInfo)"),
 ("Font.cpp",
  "int Font_Unused(int unused1, int unused2)",
  "int Font_Unused(intptr_t unused1, int unused2)",
  "definition"),
 # --- Collision2D: the two car records are pointers -------------------------
 ("Collision2D.cpp",
  "int Collision_SeparateCarBoxes(int param_1, int param_2);",
  "int Collision_SeparateCarBoxes(intptr_t param_1, intptr_t param_2);",
  "the body does (param_1 + 0x2e8): pointer arithmetic"),
 ("Collision2D.cpp",
  "int Collision_SeparateCarBoxes(int param_1, int param_2)",
  "int Collision_SeparateCarBoxes(intptr_t param_1, intptr_t param_2)",
  "definition"),
 ("Collision2D.cpp",
  "void Collision_ResolveCarContactImpulse(int param_1, int param_2);",
  "void Collision_ResolveCarContactImpulse(intptr_t param_1, intptr_t param_2);",
  "called with Car* and used as one"),
 ("Collision2D.cpp",
  "void Collision_ResolveCarContactImpulse(int param_1, int param_2)",
  "void Collision_ResolveCarContactImpulse(intptr_t param_1, intptr_t param_2)",
  "definition"),
 # --- Frontend_MergeBest*Option: pBlock is a BYTE* block --------------------
 ("Frontend.cpp", "BYTE Frontend_MergeBestDeviceStageOption(int index, int pBlock)", "BYTE Frontend_MergeBestDeviceStageOption(int index, intptr_t pBlock)", "used as (pBlock + 0x150 + ...)"),
 ("Frontend.cpp", "BYTE Frontend_MergeBestDeviceButtonOption(int index, int pBlock)", "BYTE Frontend_MergeBestDeviceButtonOption(int index, intptr_t pBlock)", "same"),
 ("Frontend.cpp", "BYTE Frontend_MergeBestPlayerStageOption(int index, int pBlock)", "BYTE Frontend_MergeBestPlayerStageOption(int index, intptr_t pBlock)", "same"),
 ("Frontend.cpp", "BYTE Frontend_MergeBestSecondaryPlayerOption(int index, int pBlock)", "BYTE Frontend_MergeBestSecondaryPlayerOption(int index, intptr_t pBlock)", "same"),
 ("GameMenus.cpp", "BYTE Frontend_MergeBestDeviceStageOption(int index, int pBlock);", "BYTE Frontend_MergeBestDeviceStageOption(int index, intptr_t pBlock);", "this file's declaration"),
 ("GameMenus.cpp", "BYTE Frontend_MergeBestDeviceButtonOption(int index, int pBlock);", "BYTE Frontend_MergeBestDeviceButtonOption(int index, intptr_t pBlock);", "this file's declaration"),
 ("GameMenus.cpp", "BYTE Frontend_MergeBestPlayerStageOption(int index, int pBlock);", "BYTE Frontend_MergeBestPlayerStageOption(int index, intptr_t pBlock);", "this file's declaration"),
 ("GameMenus.cpp", "BYTE Frontend_MergeBestSecondaryPlayerOption(int index, int pBlock);", "BYTE Frontend_MergeBestSecondaryPlayerOption(int index, intptr_t pBlock);", "this file's declaration"),
 # --- GameMenus_FormatModeName ---------------------------------------------
 ("GameMenus.cpp", "void GameMenus_FormatModeName(int unused, int mode);", "void GameMenus_FormatModeName(intptr_t unused, int mode);", "caller passes CFrontend::m_stringDest"),
 ("GameMenus.cpp", "void GameMenus_FormatModeName(int unused, int mode)", "void GameMenus_FormatModeName(intptr_t unused, int mode)", "definition"),
 # --- FrontendProfile_Set*/Get*Menu: the slots hold Menu* --------------------
 ("FrontendScreens.cpp", "int g_unk0x00819030;", "intptr_t g_unk0x00819030;", "holds the profile rename Menu*"),
 ("FrontendScreens.cpp", "int g_unk0x00819124;", "intptr_t g_unk0x00819124;", "holds the completion Menu*"),
 ("FrontendScreens.cpp", "int g_unk0x00819870;", "intptr_t g_unk0x00819870;", "holds the return Menu*"),
 ("FrontendScreens.cpp", "int FrontendProfile_GetRenameMenu(void);", "intptr_t FrontendProfile_GetRenameMenu(void);", "getter; value goes straight into Menu_SetNextAction"),
 ("FrontendScreens.cpp", "int FrontendProfile_GetRenameMenu(void)", "intptr_t FrontendProfile_GetRenameMenu(void)", "definition"),
 ("FrontendScreens.cpp", "void FrontendProfile_SetRenameMenu(int value)", "void FrontendProfile_SetRenameMenu(intptr_t value)", "definition"),
 ("FrontendScreens.cpp", "int FrontendProfile_GetCompletionMenu(void);", "intptr_t FrontendProfile_GetCompletionMenu(void);", "getter"),
 ("FrontendScreens.cpp", "int FrontendProfile_GetCompletionMenu(void)", "intptr_t FrontendProfile_GetCompletionMenu(void)", "definition"),
 ("FrontendScreens.cpp", "void FrontendProfile_SetCompletionMenu(int value)", "void FrontendProfile_SetCompletionMenu(intptr_t value)", "definition"),
 ("FrontendScreens.cpp", "void FrontendProfile_SetReturnMenu(int value)", "void FrontendProfile_SetReturnMenu(intptr_t value)", "definition"),
 ("FrontendMenus.cpp", "void FrontendProfile_SetReturnMenu(int value);", "void FrontendProfile_SetReturnMenu(intptr_t value);", "this file's declaration"),
]
# --------------------------------------------------------------- SITE rules --

def rule_for(fname, linetext):
    for k in ("Font_Unused(", "Collision_SeparateCarBoxes(", "Collision_ResolveCarContactImpulse(",
              "Frontend_MergeBestDeviceStageOption(", "Frontend_MergeBestDeviceButtonOption(",
              "Frontend_MergeBestPlayerStageOption(", "Frontend_MergeBestSecondaryPlayerOption(",
              "GameMenus_FormatModeName(", "FrontendProfile_SetReturnMenu(", "FrontendProfile_SetRenameMenu(",
              "FrontendProfile_SetCompletionMenu(", "FrontendProfile_GetRenameMenu(", "FrontendProfile_GetCompletionMenu("):
        if k in linetext:
            return "widen callee/return type (" + k + ")"
    return None

ADDR = {
 ("Frontend.cpp", 1337), ("Menu.cpp", 467), ("Menu.cpp", 480), ("Menu.cpp", 518),
 ("FrontendMenus.cpp", 963), ("FrontendMenus.cpp", 1024),
}

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
open("/home/deck/lena/work/RTN-20261012/unclaimed_s2.txt", "w").write(
    "\n".join(f"{a}:{b}:{c}: {d}" for a, b, c, d in unclaimed))
print("\nDRY RUN" if DRY else "\nAPPLIED (backups: *.bak-S2-" + STAMP + ")")
