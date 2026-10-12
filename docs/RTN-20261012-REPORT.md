# RAISE-THE-NUMBER-20261012 — x86_64 goes **37 → 54 of 66**

Round: `RAISE-THE-NUMBER-20261012`. Lane: the port's public count. Every number below
names the log or command that produced it. Nothing here is projected.

**The number: 54 of 66 game translation units compile for `x86_64-linux-gnu`.**
It was **37** when this round started. It is unchanged at **66 of 66 on i386**.
The raw sweep prints `PASS 55 FAIL 12 TOTAL 67` — the 67th file is our own
`Lenatrace.cpp`, not the game's, and it passes.

```
$ bash work/RTN-20261012/sweep.sh work/RTN-20261012/sweep-final x86_64-linux-gnu
=== sweep  target=x86_64-linux-gnu  includes: PLAT,ROOT,SHIM ===
PASS 55  FAIL 12  TOTAL 67
objects produced: 55
     12  cast from pointer to smaller type 'X' loses information
```

* before: `work/RTN-20261012/sweep-before.log` (`PASS 38 FAIL 29 TOTAL 67`, 1,178 sites)
* after:  `work/RTN-20261012/sweep-final.log` (`PASS 55 FAIL 12 TOTAL 67`, 385 sites)
* i386:   `work/RTN-20261012/sweep-final-i386.log` (`PASS 67 FAIL 0 TOTAL 67`)
* the whole editable history of the round: `sweep-s1 … sweep-s5`, `sweep-final`

**Answer to the question as asked.** Miami said "33 of 66". I measured first, as
instructed: the tree was **not** at 33, it was at **37** — the tier-1 pointer pass had
already taken it there at 17:39 tonight (`sweep-before.log`, re-run from scratch, 9.2 s,
`PASS 38 FAIL 29 TOTAL 67`). So: not 33, and not a stale published figure either. **37 was
correct when I started and 54 is correct now.**

---

## 1. The 17 files that came in

`collision2d, frontend, frontenddraw, frontendmenus, gamemenus, graphics, huddash, input,
menu, netplayers, optionmenurows, rallytiming, sound, sprite, stageui, surfacetypes,
vehiclephysics` — 17 files, **793 pointer-width sites gone** (1,178 → 385). Zero
regressions: `comm -23` of the before/after pass lists is empty.

**Plan step 2 — P3 (`platform_types.h`, `LONG`/`ULONG` → `int32_t`/`uint32_t`): already in
the tree**, lines 33–34, landed 2026-10-10 (`docs/P3-P1-REPORT.md`). Not re-done; nothing
to re-do. It was never a count win anyway — P3's own report says so: "It unlocks nothing by
itself."

**Plan step 3, changed.** The plan priced a single mechanical pass over "~1,466 sites,
~900 of them in four files". That is not what the measured tree looks like, and I say so
rather than nod at it: the failing set was **1,178 sites in 29 files**, led by
`FrontendMenus.cpp` 279, `GameInfo.cpp` 130, `StageObjects.cpp` 123, `FrontendScreens.cpp`
123, `StageTiming.cpp` 108. One error class only — `cast from pointer to smaller type`.
What I did instead of one blind pass:

1. **Cheapest files first.** The count is per file, so a one-site file is worth the same as
   a 279-site file. 13 of the first fixes were under 10 sites each.
2. **Fix the type, never the cast.** Every edit widened a container — a parameter, a field,
   a global, an array, a local — so the cast became lossless. The one thing I refused to do
   is the thing that would inflate this number: writing `(intptr_t)` on a cast whose result
   still lands in an `int`. `tools/sweep-compile.sh` passes `-w`, so that *compiles* and
   raises the count without making a single pointer whole. §4 is how I proved I didn't.
3. **Let the compiler hold the pencil.** Every cast that changed was changed at the exact
   `(file, line, column)` clang named, never by regex over a file.

### What each cluster actually was

| files | sites | what it was | the fix |
|---|---|---|---|
| 9 | ~23 | `CFrontend::GetArchivePrimaryIDEntry` / `…SecondaryIDEntry` declared `void *` but returning `g_unk0x00516b40.ids[index]` — **an `int` field**. The decomp mistyped an int table as a pointer table; every caller cast it back. | return type → `int` (header, definition, and `Car.cpp`'s own redeclaration) |
| 8 | 313 | `Menu_AddItemType1/2/3/4/6(…, (int)SomeCallback, …)` — the callback slot of a menu item | `MenuItem::param` and the five `param` parameters → `intptr_t`, matching `Menu.cpp:476` which calls that slot as a function pointer |
| 7 | 99 | `Menu_SetNextAction((int)&g_menu0x…)` — a `Menu *` in an `int` global | `g_menuNextAction`, the parameter, `Menu_Update`'s return and 3 caller locals → `intptr_t` |
| 4 | 21 | `Collision_SeparateCarBoxes((int)pCarA, (int)pCarB)`, `Font_Unused`, `FrontendProfile_Set{Return,Rename,Completion}Menu`, `Frontend_MergeBest*Option`, `GameMenus_FormatModeName`, `Sound_NoOpMusicCallback` | parameters widened to `intptr_t` — every one of them is used as a pointer (or a function pointer) inside |
| 3 | 19 | `CGraphics::ApplyTextureStageChange(0, (int)pTexture)` incl. the `QUAD2D_SET_STATE` macro (15 macro sites off one line) and `m_unk0x0065fa38`, the stage cache | `param2` and the cache → `intptr_t` |
| 5 | ~30 | `g_sceneLightState[30]`, `g_sceneLightState2[10]`, `g_unk0x00591948`, `Quad2D::flags`, `Sound_NoOpMusicCallback`, the two ACM callbacks' `dwInstance` | arrays/fields/globals widened; `dwInstance` matched to the shim's own `DWORD_PTR` typedef and the `(DWORD)&find` casts corrected to `(DWORD_PTR)` |
| rest | ~200 | `while ((int)p < (int)end)`, `*(BYTE *)((int)g_pCurrentCar + 0xb45)`, `(unsigned int)ptr & 0xffff` — pure address arithmetic and comparison | `intptr_t`/`uintptr_t`, which is the same value on 32-bit and the whole address on 64-bit |

Four sites needed a written reason rather than a rule, and they are in the scripts with
their reasons attached: `(DWORD)(uintptr_t)pTexture` inside a branch where `pTexture == NULL`
(the value is 0 either way), and
`pDevice->field_0x10 = (int)(intptr_t)m_keyboardDelay + now` in `Input.cpp` — the delay is a
small integer carried in a `PVOID`, which is the idiom that file already uses at line 732.

## 2. The play binary — rebuilt, gated, and compared function by function

The 32-bit `work/PLAY/out-plain/cmr2` is the binary Miami actually launches. It was rebuilt
with its own script, which refuses to install a link that cannot drive:

```
$ sh work/PLAY/build-play-lre.sh
game objects: 34 compiled, 33 already current, 0 failed
linking …/.cmr2.new.748495 …
drive-bound check: Physics_UpdateRateHold=1  Car_UpdateEngineNoteFalloff=1
installed: /home/deck/lena/work/PLAY/out-plain/cmr2
  was  94ed1359c405   (kept as cmr2.bak-dead-pre-lre-20261012-175330)
  now  2da6ed2ca1d2
$ . /home/deck/lena/cmr2-drivecheck.sh && cmr2_drives work/PLAY/out-plain/cmr2   →  0 (drives)
```

Then the stronger question — *did the code change at all* — asked of the two linked
binaries, not of my intentions. Every function symbol common to both, disassembled and
normalised (addresses and relocations blanked), compared one by one:

* **3,635 functions compared. 3,633 identical instruction for instruction.**
* The 2 that differ are `CFrontend::GetArchivePrimaryIDEntry` and
  `…SecondaryIDEntry` — the two accessors §1 changed the return type of. They differ in
  *which register holds the GOT base* and one dead reload; the value returned is loaded by
  the identical `mov (%eax,%edx,4),%eax` and returned in `%eax` in both. Zero observable
  difference.

And the mechanism, measured rather than asserted: the file-set compiled for i386 from the
untouched tree at 17:38 and again now, `.text` compared byte for byte —

```
SAME TEXT  Menu.cpp Frontend.cpp FrontendMenus.cpp FrontendScreens.cpp GameInfo.cpp
           GameMenus.cpp Car.cpp RallyData.cpp StageObjects.cpp StageTiming.cpp
           SurfaceTypes.cpp RallyTiming.cpp NetPlayers.cpp HudDash.cpp
           OptionMenuRows.cpp FrontendDraw.cpp Collision2D.cpp StageUI.cpp
```

18 files, all identical (`work/RTN-20261012/textnow.sh`). `int` and `intptr_t` are the same
type on i386 — the DWARF string in the touched objects literally reads
`'intptr_t' (aka 'int')` — so this was never going to be anything else, and now it is not
an argument. For the files outside that eighteen, the same comparison against their
pre-stage-3 state reads `SAME TEXT` for all of them (`textcmp2.sh`).

One trap worth recording for whoever does this next: compiling a file *under a different
filename* changes its `__FILE__`, and `GameInfo.cpp` bakes its filename into a diagnostic
string, which moves the GOT and shifts `.text` by three bytes. It cost me twenty minutes to
prove that was my test and not my edit (`textcmp.sh` vs `textcmp2.sh`). Hold the name
constant or the comparison lies.

## 3. What is still 12 files, and the honest price of each

385 sites left, all one class. Not one of them is blocked by the *class*; each is blocked by
a distinct piece of real work:

| file | sites | what it is |
|---|---|---|
| `StageObjects.cpp` | 78 | ~70 are `*(int *)(pRecord + 0xNN) = (int)ptr` — raw slots inside game records whose 32-bit layout the game itself reads. Widening the store without widening the record desynchronises the record. |
| `StageTiming.cpp` | 74 | the particle-effect texture handles: `LOAD_EFFECT_TEXTURE()` (15 macro sites) feeds 16 `int` globals that go straight into `ParticleType::field0x38…0x4c`. Widening the globals alone leaves a narrowing at the callee. |
| `GameInfo.cpp` | 65 | ~32 `g_unk0x… = (int)SomeLookup()` — globals that hold pointers and must become pointer-wide *together with* every reader. |
| `Car.cpp` | 36 | `pCar = (int)Race_GetPlayerRecordPointer(i)` and friends: `int` locals and `int` arrays of car records. |
| `RallyData.cpp` | 32 | same shape, `SceneNode_FindByType` / record-table handles. |
| `Sector.cpp`, `Game.cpp` | 23 + 23 | `Graphics_AccumulateCounterOrInitialize((int)pNodes)`, `Game_DrawSceneViewport(…, (int)g_viewNodes[view], …)` and a dozen similar one-shot call interfaces. |
| `FrontendScreens.cpp` | 17 | save-slot iteration `(int)pRecord < (int)(g_saveSlots + 0x300)` plus a few record-handle stores. |
| `NetRace.cpp`, `Race.cpp`, `CarEffects.cpp` | 13 + 10 + 10 | `Network_SendPlayerMessage(0, 1, (int)&msg, 1)` and `Sector_BuildC3DModelScene((unsigned int)pBuffer, …)` — small interfaces, each a header edit plus its call sites. |
| `SceneNode.cpp` | 4 | **the one place I stopped on purpose.** `pHeader[2] = (int)p` stores a pointer into an array whose *other* elements are read as 32-bit counts (`p += pHeader[1] * 0x30`). Widening that array does not just widen a pointer, it changes what the surrounding ints *mean*. That is a data-layout decision about a structure the game reads, not a cast fix, and I am not making it by grep. |

None of these is unknown work; each is priced above. **No number here assumes any of them
compiles.**

## 4. How I kept the number honest

The failure mode this round could have had is easy and would have looked like success:
write `(intptr_t)` on every cast, let the value narrow back into the `int` it is stored in,
and publish a bigger number. The sweep passes `-w`, so nothing complains. So I built the
instrument that does complain, and it is the gate the edits had to pass:

* `work/RTN-20261012/audit.sh` compiles every TU with **no `-w`** and with
  `-Wshorten-64-to-32 -ferror-limit=0`, so every place a 64-bit value lands in a 32-bit
  container is *named with a file and a line*.
* `patch_s3.py rewrite` widened every remaining site; `patch_s3.py revert` then put back,
  whole, **every line the audit complained about**. 346 of 529 rewritten lines were reverted
  that way in the first pass and 331 of 347 in the second. What stands is only what the
  audit could not fault.
* Baseline (untouched tree): **36** such warnings. Now: **25**. The count went *down*,
  because widening removed real truncations; none of the 25 sits on a line this round
  widened.

`-w` also means a *new* error class can hide behind an old one. One did: widening the two
ACM callbacks' `dwInstance` to `DWORD_PTR` first produced
`no matching function for call to 'acmFormatEnum'`, because the callbacks' own parameter
types disagreed with the shim's `ACMFORMATENUMCB`. Fixed at the callback signature, and the
sweep was re-run rather than read twice from memory.

**What a passing file does and does not mean.** It means that TU *compiles* for x86_64. It
does not mean the port is correct: `CGraphics::ApplyTextureStageChange` now compiles, and
inside it `*(int *)(param2 + 0x114)` still reads four bytes of what is a `pSurface`
pointer on a 64-bit build. That is a runtime defect the compiler cannot see, and it is the
next lane's work, not a number.

## 5. Also found, and not mine to clean

**`/tmp` is a 7.3 G tmpfs at 81 % (5.8 G used).** My own 17-file scratch filled it and two
compiles died with `Disk quota exceeded`; I moved all scratch under `~/lena/work/RTN-20261012/`
and left `/tmp` exactly as I found it (`ROUND-DISCIPLINE` §2: report, never clean). The
frames and `.bmp`s that are actually holding it are other lanes'. This is the same disk
picture the phone already has, now measured on `/tmp` as well as on `/`.

## 6. Files

* scripts, all in `work/RTN-20261012/`: `sweep.sh` (the harness, same flags as
  `tools/sweep-compile.sh`), `audit.sh` (the truncation oracle), `patch_s1.py`,
  `patch_s2.py`, `patch_s3.py` (rewrite/revert), `patch_s3b.py`, `patch_s4.py`,
  `textnow.sh` / `textcmp2.sh` (the i386 `.text` comparisons), `binfuncs.sh` (the linked-
  binary function diff), `census.py` / `shapes2.py` / `callees_s1.py` (the site censuses).
* the published copies are in the repo at `tools/fixes/patch_ptrwidth_tier2.py` (stages
  1+2) and `tools/fixes/patch_ptrwidth_tier2_bulk.py` (stage 3, rewrite/revert) with
  `tools/ptrwidth-audit.sh`.
* source backups in the tree: `*.S1-STATE-NOT-PRE` (note: that name is **wrong** — the
  first patch run wrote them after it had already edited the files once, so they are the
  post-stage-1 state, not the pre-state; the real pre-round state for the 18 files above is
  the object set in `i386-before/` plus the untouched `.bak-pre-ptrwidth-20261012` files),
  `*.bak-S2-*`, `*.bak-S3-*`, `*.bak-S3B-*`, `*.bak-S4-*`.

**One of my own mistakes, on the record.** `patch_s1.py` was run once without `--apply` and
printed `DRY RUN` — and wrote anyway, because the write call was not behind the dry-run
flag. It cost no correctness (the edits it applied are the ones I then went on to verify and
sweep), but it cost the round a clean pre-image of stage 1, and the backups it labelled
`bak-pre-rtn-*` are therefore misnamed. Fixed in the script, renamed in the tree, and stated
here rather than discovered later.
