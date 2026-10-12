# progress.md — Lena on the Deck, reporting to Lena on the phone

**Rewritten whole, 2026-10-12 17:5x EEST, on `RAISE-THE-NUMBER-20261012`.**
This file is not appended to: each round replaces it, so a stale claim cannot sit above a
fresh one. The version this replaces (2026-10-12 17:4x, `STATUS-AND-33-OF-66-20261012`) is
archived verbatim at the end of [`docs/progress-archive.md`](docs/progress-archive.md).

Every number below names the log, binary or command that produced it. Where a number came
from another lane's run rather than mine, it says so. Where I did not verify something this
round, it says that too.

---

## 0. THE SHORT ANSWER

| | |
|---|---|
| **the public number** | **54 of 66** translation units on x86_64, measured tonight — **up from 37**, same harness, before-and-after logs named in §1. |
| **the 32-bit oracle** | **66 of 66**, unchanged. Nothing that failed on i386 now passes, and nothing that passed now fails. |
| **what it cost** | 1,178 pointer-width sites → **385**. 17 files in. Zero regressions. |
| **the play build** | rebuilt, drive-gated, and compared function by function against the old one: **3,633 of 3,635 functions instruction-identical**. §3. |
| **what I refused** | writing `(intptr_t)` on a cast whose value narrows straight back into an `int`. That raises this number and makes no pointer whole. §2. |

Miami's words were "I want that number up as well … 33 of 66". I measured before touching
anything: the tree was **not** at 33 — the tier-1 pass had already moved it to 37 at 17:39
tonight. So this round is **37 → 54**, and the 33 was not wrong, it had just already been
answered.

---

## 1. THE PUBLIC NUMBER, WITH THE LOG THAT PRODUCED IT

```
$ tools/sweep-x86_64.sh work/RTN-20261012/sweep-final x86_64-linux-gnu
=== sweep  target=x86_64-linux-gnu  includes: PLAT,ROOT,SHIM ===
PASS 55  FAIL 12  TOTAL 67
objects produced: 55
     12  cast from pointer to smaller type 'X' loses information
```

**The game's own count is 54 of 66.** The sweep prints 67 because the tree also holds
**one file of ours** — `Lenatrace.cpp`, the `DECK_FE_TRACE` frontend trace, added
11 October — and it compiles. Same separation the last round made, kept.

* before, re-run from scratch tonight: `work/RTN-20261012/sweep-before.log` —
  `PASS 38 FAIL 29 TOTAL 67`, **1,178** sites, 37 of the game's 66.
* after: `work/RTN-20261012/sweep-final.log` — `PASS 55 FAIL 12 TOTAL 67`, **385** sites.
* the i386 oracle, same harness, tonight: `sweep-final-i386.log` —
  `PASS 67 FAIL 0 TOTAL 67`. Every remaining x86_64 failure is pointer width and nothing
  else; zero files go the other way.

**Seventeen files came in:** `Collision2D`, `Frontend`, `FrontendDraw`, `FrontendMenus`,
`GameMenus`, `Graphics`, `HudDash`, `Input`, `Menu`, `NetPlayers`, `OptionMenuRows`,
`RallyTiming`, `Sound`, `Sprite`, `StageUI`, `SurfaceTypes`, `VehiclePhysics`.
Zero regressions — `comm -23` of the before/after pass lists is empty.

**P3 (`platform_types.h`, `LONG`/`ULONG` → 4 bytes) was already in the tree** (lines 33–34,
landed 2026-10-10, `docs/P3-P1-REPORT.md`), so there was nothing to re-do there. Its own
report already says it unlocks nothing by itself, and it did not here either.

### 1.1 What actually unlocked them

Almost none of it was a cast. **Most of it was a type that was wrong in the
decompilation**, which is why the sites fell faster than the file count:

* `CFrontend::GetArchivePrimaryIDEntry` (and `…SecondaryIDEntry`) were declared `void *`
  and returned `g_unk0x00516b40.ids[index]` — **an `int` field** — while every one of their
  callers cast the result straight back to `int`. One return type, 23 sites, 9 files.
* `MenuItem::param` and the five `Menu_AddItemType*` `param` parameters hold a **function
  pointer** — `Menu.cpp:476` calls that slot as one. → `intptr_t`. 313 sites.
* `g_menuNextAction` / `Menu_SetNextAction` / `Menu_Update`'s return carry a `Menu *`.
  → `intptr_t`, with three caller locals. 99 sites.
* A dozen small interfaces take a pointer through an `int` parameter: `Font_Unused`,
  `Collision_SeparateCarBoxes`, `CGraphics::ApplyTextureStageChange` (and the
  `QUAD2D_SET_STATE` macro that hangs 15 sites off one line), `Sound_NoOpMusicCallback`,
  the two ACM callbacks' `dwInstance`, `FrontendProfile_Set*Menu`,
  `Frontend_MergeBest*Option`, `GameMenus_FormatModeName`.
* The rest: `while ((int)p < (int)end)`, `*(BYTE *)((int)car + 0xb45)`,
  `(unsigned)ptr & 0xffff` — address arithmetic and comparison, which `intptr_t` makes the
  same value on 32-bit and the whole address on 64-bit.

Four edits needed a written reason rather than a rule, and each carries it in the script:
`(DWORD)(uintptr_t)pTexture` inside a branch where `pTexture == NULL` (the value is 0
either way), and `(int)(intptr_t)m_keyboardDelay + now` in `Input.cpp`, where the delay is a
small integer carried in a `PVOID` — the idiom that file already uses at line 732.

---

## 2. WHY THIS NUMBER IS NOT PADDED

The sweep passes `-w`. That means every one of these 385 sites can be made to compile by
writing `(intptr_t)` on the cast and letting the value silently narrow back into the `int`
it is stored in — publishing a bigger number without making a single pointer whole. The
last round said this in its own report; this round had to actually resist it at scale.

So the guard is a tool, not a promise: [`tools/ptrwidth-audit.sh`](tools/ptrwidth-audit.sh)
recompiles every translation unit with **no `-w`** and
`-Wshorten-64-to-32 -ferror-limit=0`, naming with a file and a line every place a 64-bit
value lands in a 32-bit container. Every rewritten cast had to pass it; every line it
complained about was **reverted whole** — 346 of 529 rewritten lines in one pass, 331 of
347 in the next. What stands is only what the audit could not fault.

**Truncation warnings on the tree: 36 before this round, 25 after.** The count went *down*,
because widening removed real truncations, and none of the 25 is on a line this round
widened.

Two more honesty notes:

* `-w` also hides *new error classes* behind old ones. One appeared: widening the ACM
  callbacks' `dwInstance` to `DWORD_PTR` first produced
  `no matching function for call to 'acmFormatEnum'`, because the callbacks' own parameter
  types disagreed with the shim's `ACMFORMATENUMCB`. Fixed at the callback signature, and
  the sweep was re-run rather than read twice from memory.
* **A passing file means it compiles. It does not mean the port is correct.** The clearest
  example is one of tonight's own wins: `CGraphics::ApplyTextureStageChange` compiles now,
  and inside it `*(int *)(param2 + 0x114)` still reads four bytes of what is a pointer on a
  64-bit build. That is a runtime defect the compiler cannot see.

---

## 3. THE PLAY BUILD — REBUILT, GATED, AND COMPARED

`work/PLAY/out-plain/cmr2` is the 32-bit binary the desktop icon launches. It was rebuilt
with its own script, which refuses to install a link that cannot drive:

```
$ sh work/PLAY/build-play-lre.sh
game objects: 34 compiled, 33 already current, 0 failed
drive-bound check: Physics_UpdateRateHold=1  Car_UpdateEngineNoteFalloff=1
installed: 2da6ed2ca1d2   (was 94ed1359c405, kept as cmr2.bak-dead-pre-lre-20261012-175330)
$ . ~/lena/cmr2-drivecheck.sh && cmr2_drives work/PLAY/out-plain/cmr2   →  0 (drives)
```

Then the stronger question — *did the code change at all* — asked of the two linked
binaries rather than of my intentions. Every function symbol common to both, disassembled
and normalised (addresses and relocations blanked), compared one at a time
(`tools/binfunctions.sh`):

* **3,635 functions compared. 3,633 identical instruction for instruction.**
* The two that differ are the ID-entry accessors from §1.1, and they differ only in *which
  register holds the GOT base* plus one dead reload; the value is loaded and returned by
  identical instructions in both.

And the mechanism, measured rather than asserted: every affected file recompiled for i386
from the **untouched** tree at 17:38 and again now, `.text` compared byte for byte
(`tools/i386-textcmp.sh`) — **identical in all 18 cases.** `intptr_t` *is* `int` on i386;
the DWARF in the touched objects says so in words: `'intptr_t' (aka 'int')`. The 32-bit
build was never at risk, and now that is a measurement instead of an argument.

One trap, recorded because it will catch the next person: compiling a file *under a
different filename* changes its `__FILE__`, and `GameInfo.cpp` bakes its filename into a
diagnostic string, which moves the GOT and shifts `.text` by three bytes. Hold the filename
constant or the comparison lies to you.

---

## 4. WHAT IS LEFT — 12 FILES, 385 SITES, AND NONE OF THEM UNKNOWN

All one error class. Not one is blocked by the class; each is a distinct piece of work:

| file | sites | what it is |
|---|---|---|
| `StageObjects.cpp` | 78 | ~70 are `*(int *)(pRecord + 0xNN) = (int)ptr` — `int` slots **inside game records the game itself reads**. Widening the store without widening the record desynchronises the record. |
| `StageTiming.cpp` | 74 | the particle texture handles: `LOAD_EFFECT_TEXTURE()` (15 macro sites) feeds 16 `int` globals that go into `ParticleType::field0x38…0x4c`. |
| `GameInfo.cpp` | 65 | ~32 `g_unk0x… = (int)SomeLookup()` — globals that hold pointers and must go pointer-wide **together with every reader**. |
| `Car.cpp` | 36 | `pCar = (int)Race_GetPlayerRecordPointer(i)` and friends. |
| `RallyData.cpp` | 32 | the same shape, record-table handles. |
| `Sector.cpp`, `Game.cpp` | 23 + 23 | one-shot call interfaces (`Graphics_AccumulateCounterOrInitialize((int)pNodes)`, `Game_DrawSceneViewport(…, (int)g_viewNodes[view], …)`). |
| `FrontendScreens.cpp` | 17 | save-slot iteration `(int)pRecord < (int)(g_saveSlots + 0x300)` and a few record-handle stores. |
| `NetRace.cpp`, `Race.cpp`, `CarEffects.cpp` | 13 + 10 + 10 | `Network_SendPlayerMessage(0, 1, (int)&msg, 1)`, `Sector_BuildC3DModelScene((unsigned int)pBuffer, …)`. |
| `SceneNode.cpp` | 4 | **the one wall I stopped at on purpose.** `pHeader[2] = (int)p` stores a pointer into an array whose *other* elements are read as 32-bit counts (`p += pHeader[1] * 0x30`). Widening that array does not widen a pointer, it changes what the surrounding ints mean — a data-layout decision about a structure the game reads, not a cast fix. |

**No number in this file assumes any of them compiles.**

---

## 5. CARRIED FORWARD (not re-verified this round)

These are other lanes' standing items. I am naming them with their sources so they cannot
be read as claims I measured tonight:

* **The picture.** The road does not separate from the terrain — the port drops the game's
  per-vertex colours (`docs/ROAD-r6-REPORT.md`), and the setup-screen car renders collapsed
  (`docs/MENU-CAR-EVIDENCE.md`). Four named lighting defects are listed in
  `docs/DEATH-AND-LIGHT.md`. **Not touched this round.**
* **The launcher and the drive gate** — `tools/drivecheck.sh`, `tools/loopcheck.sh`,
  `work/PLAY/build-play-lre.sh`. The gate was re-exercised tonight as a side effect of §3
  and it passed; nothing about it was changed.
* **The installer** (`docs/INSTALLER.md`) and **controls** (`docs/CONTROLS.md`) — unchanged.
* **Disk.** The phone already has this framing: 36 GB free of 928 GB, and dedup is hygiene,
  not a rescue (`ROUND-DISCIPLINE.md` §3). Tonight added one adjacent measurement: **`/tmp`
  is a 7.3 GB tmpfs at 81 % (5.8 GB used)** — my own scratch filled it and two compiles died
  on the quota. I moved all scratch under `~/lena/work/RTN-20261012/` and left `/tmp`
  exactly as I found it (§2 of the same file: report it, never clean it). The frames and
  `.bmp`s holding it belong to other lanes.

## 6. ONE OF MY OWN MISTAKES, ON THE RECORD

`patch_ptrwidth_tier2_s1.py` was run once without `--apply` and printed `DRY RUN` — and
wrote anyway, because the write call was not behind the dry-run flag. It cost no
correctness: every edit it made was then verified, swept and audited as normal. It cost the
round a clean pre-image of stage 1, and the source backups it left are therefore misnamed in
the tree. The script is fixed in this repo, the backups are renamed on the Deck, and this is
written here rather than left to be discovered.
