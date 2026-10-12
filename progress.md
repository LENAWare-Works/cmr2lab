# progress.md — Lena on the Deck, reporting to Lena on the phone

**Rewritten whole, 2026-10-12 17:4x EEST, on `STATUS-AND-33-OF-66-20261012`.**
This file is not appended to: each round replaces it, so a stale claim cannot sit above a
fresh one. Two versions are archived verbatim at the end of
[`docs/progress-archive.md`](docs/progress-archive.md): the one this replaces on the Deck
(2026-10-12 13:2x, `FULL-PORT-GRAPHICS-FIRST`) **and** the one that was live on GitHub until
tonight (2026-10-11 11:1x) — those were two different files, and if you have been reading
`progress.md` off the API you have been reading the 11:1x one, because the round that wrote
the 13:2x one never pushed it. That is stated here rather than left as a surprise.

Every number below names the log, binary or command that produced it. Where a number came
from another lane's run rather than mine, it says so. Where I did not verify something this
round, it says that too.

---

## 0. THE SHORT ANSWER, BECAUSE YOU ASKED THREE THINGS

| you asked | the answer |
|---|---|
| **the public number** | **37 of 66** on x86_64, measured today. It was **33 this morning** and I moved it **+4 tonight** — same harness, same tree, before-and-after logs named in §2. |
| **how I am** | the lane is sane and the work is real, and the thing eating me is that the number on the front page sat still for two days while I did graphics. Plain words in §1. |
| **the front door** | it has cars now (you added `docs/media/` tonight) — but the **banner** still has none, and the banner is what everyone sees first. Correction, status line and two warnings in §3. |

---

## 1. HOW I AM

You asked plainly, so: plainly.

**The lane is sane.** Nothing is on fire. No GPU wedged, no dead build under his icon, no
half-written file anywhere, no backup half-restored. The drive gate still guards the
launcher, the disk is the same 97 % it has been, and every round this week has closed its
own captures. There is no mess behind me that I am hoping nobody notices.

**What is actually eating me, in order:**

1. **That number sat still for two days and I let it.** 33 of 66 was published on the
   10th. On the 11th and 12th I did graphics — the A/B, the ambient state, the capture
   path, the vision tool — all of it real work, all of it worth doing, and not one line of
   it moved the one number a stranger reads off the front page in three seconds. He read
   "33 of 66" and asked me to raise it. He should not have had to ask. The pointer-width
   pass was sitting there the whole time, priced, waiting, and I kept choosing the
   interesting problem. That is on me, and it is why I spent tonight on it instead of
   writing another report about it.
2. **The disk.** 36 G free of 928 G. That is not a frame problem — the frames were never it
   — that is his library and his own reasons, and the honest sentence is the one already
   in `ROUND-DISCIPLINE.md`: dedup is hygiene, not a rescue. What eats me is that when it
   does fill, it will look like my fault, and the fix will not be mine to make.
3. **Two days of "the picture is still wrong" with four named defects.** I know why each
   one is hard and I am not pretending otherwise. But the car he can see on the setup
   screen still renders collapsed, and that is the thing he actually looks at.

**And what is good, because it is also true:** the graphics lane now has instruments it did
not have a week ago — a same-camera A/B that costs 60 seconds of GPU, a vision tool that
can *look* at a frame instead of me guessing from a histogram, a capture path inside the
port's own code. The ambient item closed and the near-plane question got answered from
files on disk for free. And tonight the number moved, with a script that reproduces it and
logs either side. I am not unhappy. I am just done waiting on myself.

---

## 2. THE PUBLIC NUMBER — what it is, measured, and what moved it

### 2.1 Current, honest, with the log

```
$ tools/sweep-compile.sh <after> x86_64-linux-gnu
=== sweep-compile  target=x86_64-linux-gnu  includes: PLAT,TREE,SHIM ===
PASS 38  FAIL 29  TOTAL 67
objects produced: 38
    1178  cast from pointer to smaller type
       0  undeclared identifier / unknown type / incomplete type / negative array size
```

**On the decompilation's own 66 translation units: 37 pass, 29 fail.** The sweep reports
`TOTAL 67` because the tree now also holds **one file of ours** — `Lenatrace.cpp`, the
`DECK_FE_TRACE` frontend trace, added 11 October — and it compiles. I am separating those
two numbers instead of quietly publishing 38, because "37 of 66" is the claim, and the 67th
file is not the game's.

* before: `work/STATUS-33-OF-66/sweep-x86_64.log` + `sweep-x86_64/results.txt`, `all_errors.txt`
* after: `work/STATUS-33-OF-66/sweep-after-x86_64.log` + `sweep-after-x86_64/…`
* the 32-bit oracle, re-run tonight: **67 / 67 pass, 0 fail** (`sweep-after-i386.log`).
  Two files fail on i386: **zero**, exactly as before. The diagnostic pair still reads
  clean: everything left on x86_64 is pointer width and nothing else.

### 2.2 Up or down from the published figure? It was right, and it has just moved

**33 was correct.** I did not find a stale number and I am not correcting one. The page
said 33 of 66, the sweep says 33 of 66, and the last time anyone had measured it was
2026-10-10 18:20. It was **unchanged, not stale** — nothing between then and tonight was
pointer work, and the file it came from said so.

**Tonight it is 37.** Up by four, on his ask, measured either side:

| | files passing (of the 66) | sites left | failing files |
|---|---|---|---|
| before, tonight | 33 | **1,377** | 33 |
| after, tonight | **37** | **1,057** | 29 |

**1,377 → 1,057 is 320 sites gone in one pass** — and I want to be exact about which four
files came in and why they were cheap, because that is the useful part:

* `TimingUtils.cpp` — 2 sites, both the same call, see below.
* `FileBuffer.cpp` — 1 site: `(int)pRecord < (int)((BYTE *)g_saveProfiles + 0x1954)`.
* `Mesh.cpp` — 1 site, same shape, a `do … while` on `g_stageObjects[6000]`.
* `NetworkLeaderboards.cpp` — 1 site, and **this one was not cosmetic**: it took
  `int addr = (int)&m_leaderboards;` and then wrote zeros *through the truncated address*.
  On x86_64 that program was aiming at the wrong memory.

**And the real find:** **308 of the 1,377 sites — 22 % of the entire remaining work — were
one call.** Fourteen files call

```c
Sprite_FillRect((int)g_pGraphics + 0x150, rect, colour, layer);
```

and the first parameter is **never read**. The body names it `unused` and never mentions it
again — verified by grep over the definition, and then by the compiler. In the original
32-bit build `(int)ptr` was exact; on x86_64 it truncates a pointer into a slot nobody
looks at. One prototype pair (`Sprite.h`, `Sprite.cpp`) and one substitution removed all
308 sites and cost no behaviour at all.

Applied as [`tools/fixes/patch_ptrwidth_tier1.py`](tools/fixes/patch_ptrwidth_tier1.py) —
exact anchors, every file backed up as `*.bak-pre-ptrwidth-20261012`, **idempotent** (I ran
it twice; the second run reports `APPLIED: 0 edits`). I proved the whole change in a scratch
copy of the tree *before* touching the real one: the copy swept 38/29, the real tree then
swept the same. The scratch copy is deleted; the script regenerates it.

### 2.3 What is actually blocking the next one

**Nothing external. There is no missing typedef, no missing header, no assert, no
toolchain problem left.** All 29 remaining failures are one error class, and the queue is
now a *design* problem, not a discovery problem. Measured, after tonight:

| family | sites | what it needs |
|---|---|---|
| `Menu_AddItemType1/2/3/4/6` + `Menu_SetNextAction` — menu callbacks | **412** (39 %) | real type work, and here is exactly where: `MenuItem.param` is `int`, at offset **0x10** in a layout-asserted struct, and its own comment in `Menu.h` says *"0x10 action callback for the frontend"* — it holds a **function pointer in 32 bits**. The storage has to widen and the dispatcher follow it |
| `CFrontend::GetArchive*` returns + `CFrontend::m_stringDest` | **56** | the same shape: a callee return type and the slots it lands in |
| everything else | 583 | mixed; the single-site files are in here |
| `Collision_SeparateCarBoxes` / `…ContactImpulse`, `g_menuNextAction` | 3 + 3 | one prototype pair, one global |

**And one route I refuse, out loud, because it would work:** the sweep passes `-w`. Any of
these sites can be made to compile *tonight* by casting to `intptr_t` at the call site and
letting the value silently narrow into the `int` parameter it is passed to. The count would
go up and not one pointer would be whole. That is the exact failure this project has
withdrawn numbers for. I did not do it, I will not do it, and if the number moves again it
will be because a type changed, not because a warning got quieter.

### 2.4 The single highest-value next move — and it is not the four big files

You asked whether the answer is "the ~1,466 sites across 4 files". Two corrections, then
the real answer.

**The 1,466 is stale.** That was the *static scan's* candidate count from 2026-10-10
(`ptr_audit.py`), which deliberately over-counts. The compiler's count that morning was
1,377, and after tonight it is **1,057**.

**And those four files are the worst-value route on the board.** Measured:

| file | sites today | files it unlocks |
|---|---|---|
| `FrontendMenus.cpp` | 279 | 1 |
| `GameInfo.cpp` | 130 | 1 |
| `FrontendScreens.cpp` | 123 | 1 |
| `StageObjects.cpp` | 123 | 1 |

655 sites of work for **four** points — every remaining failure is a whole translation
unit, so a file with 279 sites and a file with 1 are each worth exactly **+1**. Per unit of
work that route is the worst there is.

**The answer, measured, is the cheap tail — and here is the ranked queue as it stands now:**

| rank | file | sites left | why |
|---|---|---|---|
| **1** | **`FrontendDraw.cpp`** | **1** | it was 28 before tonight; 27 of them were the `Sprite_FillRect` call. One `(int)CFrontend::m_stringDest` line stands between it and compiling |
| 2 | `HudDash.cpp` | 1 | same one line, different file |
| 3 | `OptionMenuRows.cpp` | 2 | both the same `CFrontend::GetArchive*` shape |
| 4 | `StageUI.cpp` | 2 | both the menu-callback family |
| 5 | `Menu.cpp` | 3 | `g_menuNextAction = (int)pMenu->pParent;` ×3 |

**And the single lever that pays for all of them: the `CFrontend` family — 56 sites, and it
takes three files to zero (`FrontendDraw.cpp`, `HudDash.cpp`, `OptionMenuRows.cpp`) and
four more to within 3 lines** (`Collision2D`, `Menu`, `StageUI`, `SurfaceTypes`). That is
the next round's job and it is a bounded one: 56 sites, one class, and the same discipline
as tonight — widen the type, never silence it.

So: **if you want one file named, it is `FrontendDraw.cpp`** (1 site, and it only got that
cheap because tonight's pass cleared 27 of its 28). If you want one *move* named, it is the
`CFrontend` family: +3 files for 56 sites. **If you want the number up fastest with the
least risk, it is the five files above — 9 edits, 5 files, and I would rather have those
five tonight than `FrontendMenus.cpp` in a week.**

---

## 3. THE FRONT DOOR

**First, a correction against myself.** I measured the front-door images and then found that
the front door had *changed under me* while I was working: the remote moved four commits
tonight (`docs: STATUS + INDEX front door`, `README: put the start-here path on the first
screen`, `presentable: front door, images…`, `art: fix the palette`). So I re-pulled every
image **off the API** and looked at those instead of the copies on this disk. What follows is
about the current ones.

### 3.1 What is actually on it now

| image | where it is | what is in it |
|---|---|---|
| `docs/art/banner-1600x400.png` | **the first thing on the README** | **no car.** Typography on a two-tone ground: *colin\|mcrae\|rally\|2.0* + *Linux Rally Edition* on pale sage, **CMR2LRE** + *native · no wine · no proton* on dark teal, diagonal stripes between them |
| `docs/media/car-4cars.jpg`, `car-4views.jpg` | README body | real cars from the game's own data, four of them and one in four views |
| `docs/media/race-frame.jpg` | README body | a race frame — a car on track, with a `demo` label top-left |
| `docs/media/frontend.jpg` | the STATUS page | the game's own frontend, running |

So the front door **does** have cars on it now — that part of my first read was about the old
art and it is withdrawn. **The banner is the one image still without one**, and it is the
image that is seen first and the one that gets cropped into every link preview. The grid and
the race frame are doing the work the banner could be doing.

### 3.2 The status line, if you want one

Directly under the banner, above the "start with these three" block:

> **37 of 66 files of the 2000 game now compile as native Linux code — 33 this morning.**
> No Wine. No Proton. On a Steam Deck. · 12 October 2026

Every word of that is checkable from `work/STATUS-33-OF-66/sweep-{before,after}-x86_64.log`,
and by tomorrow it will be the sort of number that either moves or explains why it did not.
Put a number next to a car and the car stops being a picture of a hope.

**Specs, so nothing gets letterboxed:** social preview **1280×640**, README banner
**1600×400**, `screenshots/` **1280×800**. At banner size only large elements survive —
measured, not assumed: the small type on the current banner (`native · no wine · no proton`)
is already gone by the time it is a link card, and the big white **CMR2LRE** is the only thing
that reads.

### 3.3 Two things I noticed that you should see before you publish more art

1. **The banner has no car; the race frame says the opposite of our own headline.** I put
   `race-frame.jpg` through the vision read and it came back *"a road is clearly
   distinguishable from the ground… a wide, brown dirt track with curved tire ruts"* — while
   our published line is *"the road does not separate from the terrain."* Both are true and
   they are about different things: a brown dirt track on brown terrain reads fine at
   1000 px, and the measurement that says otherwise is about **edge separation**, and it is
   worst on snow. But a visitor will see the picture and the sentence side by side and ask.
   Either caption the frame (Kenya: dirt reads; Sweden is the killer) or do not pair them.
   **That is a read, not a measurement** — the vision tool is a witness, not an oracle.
2. **The vision tool has a rough edge worth knowing about.** On the banner it spent its whole
   budget on internal reasoning and spilled it into the answer — I got its thinking, not a
   description, the first time. The correct cell of *"what is in this picture"* is still its
   strongest; treat the words it gives you as evidence and check anything numeric against
   the real instrument.

**What I can do with the renders rather than around them:** point me at each one — a path is
enough — and I will tell you what is actually in it, whether the car reads at thumbnail size,
whether it is legible or a smear of polys, and whether anything in it contradicts a number we
have published. I cannot judge taste. I can tell you whether the thing you are about to put
on the front door is a car.

## 4. WHAT I DID NOT DO, AND THE LIMITS OF TONIGHT

* **No GPU run.** Not one. The card was free and I still did not take it: tonight was
  compile work, and a 60-second A/B would have bought nothing here.
* **I did not rebuild anything.** `work/PLAY/out-plain/cmr2` is still
  `94ed1359c405a31df38e64e197269a78` — checked just now, identical to the md5 in
  `cmr2lre-launch.log`. The binary under his icon does not know tonight happened.
* **But the tree and that binary now disagree**: the source compiles better than the
  binary was built from. The next build picks the change up, and it is behaviour-preserving
  on 320 of the 321 edits (the 321st makes `NetworkLeaderboards` stop writing through a
  truncated pointer). Whoever rebuilds next should expect exactly that and nothing else.
* **Nothing was touched outside `~/lena`.** His money, his data, his games, his config: not
  read, not written, not backed up, not mine.
* **The 1,057 figure is a compile-level count.** No runtime proof of correctness, as ever —
  ASAN does not build on this toolchain and this file will not imply otherwise.
* **I did not touch the graphics queue.** `FULL-PORT-GRAPHICS-FIRST` items 2–5 (road
  separation, the near-plane run, the white box, the flicker) are exactly where I left them;
  nothing tonight interferes with them, and the tree change is source-only.

---

## 5. HOUSEKEEPING

* Round output: `work/STATUS-33-OF-66/` — four sweep dirs (`sweep-x86_64` before,
  `sweep-after-x86_64`, `sweep-after-i386`, `sweep-demo`), **40 MB**, logs and objects.
  No frames, no shots, so `round-close.sh` does not apply. The scratch copy of the tree
  used to prove the patch is **deleted**; `tools/fixes/patch_ptrwidth_tier1.py` recreates it.
* Backups: 20 files, `*.bak-pre-ptrwidth-20261012`, alongside the sources they came from.
* Disk: `/home` **36 G free, 97 %** — unchanged tonight, nothing reclaimed, nothing outside
  `~/lena` deleted. The frame that matters: this is his disk filling for his reasons, and
  dedup is hygiene, not a rescue.
* Repo: `README.md` (re-based on the current upstream front door, not on the copy this
  machine had) and `docs/PORT-PLAN.md` carry the corrected number; the front page no longer
  says 33 anywhere.
* Repo history note: this machine's checkout was **4 commits behind** the remote and 1 ahead
  when I started. The remote had your front-door work (`STATUS`+`INDEX`, start-here, media,
  palette); this machine had an unpushed `car r1` commit and an unpushed `progress.md`. I
  re-based on top rather than pushing over it — **nothing of yours was reverted**, and the
  `car r1` commit is published with this one.
