# CMR2LRE

![CMR2LRE](assets/hero.png)

**Colin McRae Rally 2.0 — Linux Rally Edition.**
A 2000 PC rally game, running natively on a Steam Deck. No Wine. No Proton. No emulator.
The actual engine, recompiled for Linux.

---

### The cars below are not screenshots. We rendered them.

The game's own `.c3d` geometry and `.bfl` liveries, decoded and rasterised by a renderer
written from scratch in this repo (`assets/` — regenerated from scratch, no 3D engine, no
game process, no GPU).

| | | | |
|---|---|---|---|
| ![Subaru Impreza WRC](assets/car-subaru.png) | ![Ford Focus WRC](assets/car-focus.png) | ![Peugeot 205 T16](assets/car-205.png) | ![MG Metro 6R4](assets/car-6r4.png) |
| **Subaru Impreza WRC** | **Ford Focus WRC** | **Peugeot 205 T16** | **MG Metro 6R4** |
| read off the retail disc | real livery, real UVs | our own rasteriser | no engine, no emulator |


> ### New here? Start with these three.
>
> | | |
> |---|---|
> | **[`docs/STATUS.md`](docs/STATUS.md)** | **One screen. Can I use this yet? Read this first.** |
> | [`docs/INDEX.md`](docs/INDEX.md) | Every document in this repo, mapped and explained |
> | [`docs/GLOSSARY.md`](docs/GLOSSARY.md) | Every unfamiliar term, in plain English |
>
> Then come back here — the rest of this page is the detail behind those three.

---

> **11 October 2026.** The game boots its own frontend, loads a real Kenya stage off
> disk, and drives a car with the game's own physics — on this project's renderer, on a
> Steam Deck. **Four things that were broken are fixed and measured as of today** (see
> *Recent fixes*): the stage's textures were never decoded, the GPU was being reset by
> our own code every thirty seconds, the road was drawn from the wrong vertices, and one
> of our own tools had quietly deleted the two lines that make a car drivable.
>
> **A full stage has been driven start to finish** on this renderer, on a Deck. It is
> still not *right*: the road does not separate from the terrain — one continuous warm
> field, white-on-white on snow stages — because the port drops the game's per-vertex
> colours (measured in `docs/ROAD-r6-REPORT.md`). The setup-screen car also renders
> collapsed.
>
> **If you want to know whether to download anything today:** the file tools below work
> perfectly right now. The port is a laboratory, not a game.

---

## What is this, in plain words

In 2000, Colin McRae Rally 2.0 came out on PC. It only ever ran on Windows. Twenty-six
years later it still only runs on Windows — or through Wine and Proton, which are
translators that pretend to be Windows so the game doesn't have to change.

This project is the other route: **change the game so it speaks Linux directly.**

That is a big job and it is going well. The game's source code has been recovered from
the shipped `.exe` — 122 files, 135,805 lines of C++ — and more than half of it compiles
natively on a Steam Deck (**54 of 66 translation units on x86_64, 66 of 66 on 32-bit**;
compile-level counts, and this repo labels them as such, because there is still no
runtime proof of the port's correctness). The x86_64 figure was **33 at the start of
12 October and 54 by the end of it** — 21 files, and the sites it is counted in fell from
1,377 to 385. Every edit is named in a script, stage by stage:
[`tools/fixes/patch_ptrwidth_tier1.py`](tools/fixes/patch_ptrwidth_tier1.py) for the first
pass, and `tools/fixes/patch_ptrwidth_tier2_s1.py` … `…_s4.py` for tonight's — driven by
the compiler's own `(file, line, column)` list, never by a regex over a file.

It also draws, and that sentence has to be exact. The game's data files produce a real
car, rendered on a Deck through Vulkan — but the **data** is the game's and the **draw
code** is this project's own viewer. That viewer is not the game.

| Four cars, built from the retail files | One car, four angles |
|---|---|
| ![Four cars from Colin McRae Rally 2.0, drawn by this project's viewer](docs/media/car-4cars.jpg) | ![A single car model shown from four angles](docs/media/car-4views.jpg) |

*Both images are the project's **viewer**, not the game — the geometry and textures are
CMR2's, the renderer is ours.*

Separately, the game's **own** 3D path now draws: it loads a stage, builds its own car
list, runs its own race loop, and the physics steps at 24 Hz with a car accelerating
across the world.

![A race frame from the native port](docs/media/race-frame.jpg)

*The game's own renderer running a stage on a Steam Deck. The road does not separate
from the terrain yet — that is the open lighting bug, named in
[`docs/ROAD-r6-REPORT.md`](docs/ROAD-r6-REPORT.md).*

Nothing here is a mock-up and nothing here is a rendering of what we hope it will look
like. Where a number appears in this repository, the log, tool or command that produced
it is named next to it — and where a claim turned out to be wrong, it was withdrawn in
public rather than deleted (`docs/ROAD-TEXTURE-OWNER.md` §3 and
`docs/README-ARCHIVE.md` both do this).

---

## Can I use it? (the honest table)

| What you want to do | Works today? | Where |
|---|---|---|
| **Look inside the game's data files** | ✅ **Yes, right now** | `./cmr2lab` |
| **Pull out a car's textures as normal images** | ✅ **Yes, right now** | `./cmr2lab unpack` |
| **Edit a texture and put it back in the game** | ✅ **Yes, right now** | `./cmr2lab pack` |
| **Be sure the rebuilt file is byte-identical to the original** | ✅ 581 / 581 containers | `./cmr2lab repack` |
| **Read the game's 3D model format** | ✅ Documented | `docs/C3D.md` |
| **See a car from the game drawn natively** | ⚠️ Yes — this is a *viewer*, not the game | `src/port/` |
| **Watch the game's own code run on Linux** | ⚠️ Yes — boots to its frontend, loads a stage, runs the race loop | `docs/PLAY-CHECKPOINT.md` |
| **A session that lasts longer than two minutes** | ✅ **Yes, since 11 Oct** — the GPU bug that ended every run is fixed | `docs/GPU-LIFETIME-FIX.md` |
| **A car you can actually drive** | ⚠️ **Yes again since 11 Oct 11:02** — our own tool had broken it for 2½ hours | `docs/DRIVE-LOOP-REGRESSION.md` |
| **Lighting that looks like the original** | ❌ No — the road's per-vertex shading is dropped | `docs/ROAD-r6-REPORT.md` |
| **The car in the setup screen** | ❌ No — it renders collapsed | `docs/MENU-CAR-EVIDENCE.md` |
| **More than half the game's code compiling for Linux** | ✅ 54 of 66 files (compile-level) | `docs/PORT-PLAN.md` |
| **The rest compiling** | ❌ Not yet — pointer-width work, 385 sites left in 12 files | `docs/PORT-PLAN.md` |

**Full current status, rewritten whole each round so it cannot contain a stale claim
above a fresh one: [`progress.md`](progress.md).**

## Recent fixes

Four bugs were found and killed on 10–11 October, each with a number that says it
worked — the stage's textures were never being decoded, the GPU was being reset by our
own code every thirty seconds, the road was drawn from the wrong vertices, and one of our
own tools had quietly deleted the two lines that make a car drivable.

**Full write-up, with the measurements:** [`docs/FIXES-20261011.md`](docs/FIXES-20261011.md)

---

---

## Track 1 — "I just want to look inside the game"

You need: a PC or a Steam Deck, your own copy of Colin McRae Rally 2.0 (the 2000 PC
release), and Python 3. Nothing else — no compiler, no dependencies, no install.

```
git clone https://github.com/LENAWare-Works/cmr2lab && cd cmr2lab
./cmr2lab status   /path/to/Colin\ McRae\ Rally\ 2.0
./cmr2lab list     /path/to/game cars
./cmr2lab unpack   /path/to/game/Game/Cars/205a1.bfl /tmp/205
ls /tmp/205          # 27 real textures, ready to open in anything
./cmr2lab pack     /tmp/205 205a1.bfl       # put your edited version back
./cmr2lab repack   /path/to/game            # prove every file still rebuilds exactly
```

```
cmr2lab status              what's here, what's possible
cmr2lab list cars|tracks    enumerate content
cmr2lab info   <file.bfl>   entries, magic, breakdown
cmr2lab unpack <in> <dir>   extract a container
cmr2lab pack   <dir> <out>  rebuild one
cmr2lab repack <file|dir>   round-trip and VERIFY byte-identical
cmr2lab tabs                show the CMR2 / CMR3 content tabs
cmr2lab install             write a Steam launcher entry
```

**The guarantee:** every `.bfl` in the retail game round-trips **byte-identical**.

```
$ ./cmr2lab repack /path/to/Colin\ McRae\ Rally\ 2.0
repack VERIFY: 581/581 byte-identical   (skipped 1 non-container)
```

581 containers, 417 MB of container data, zero failures — re-run on a Deck on 11 October
2026 in **8.4 seconds**. If a container rebuilds to the exact original bytes, then a
*modified* container is structurally indistinguishable from something the game shipped.
That's the whole safety argument for editing your own copy.

(An earlier version of this page quoted the install at 2.26 GB. It is not: **2.26 GB was
three copies of the disc image in a download folder.** A real retail install measures 907
files, **638 MB** on disk, and the 582 `.bfl` files inside it are 417 MB. The withdrawal
is recorded in `docs/README-ARCHIVE.md` rather than quietly edited away.)

---

## The installer (new, 11 October)

Two doors, both one file, no dependencies:

```
cmr2lab where                 # every place searched, found/miss/skip, then the install
cmr2lab install --native      # write the launcher; refuses if there is no native port
python3 cmr2install           # the same thing in a browser, for people who do not want a terminal
```

The bug that made "the installer" do nothing is fixed and written up with the measurements
in [`docs/INSTALLER.md`](docs/INSTALLER.md): it used to hand Steam a **folder** to launch.
It now finds the content directory (`Cars/` **and** `Tracks/`), walks up to the ancestor
that actually holds an executable, and puts *that* in `Exec=`. On this Deck the search
finds **two** real installs — a dev copy and a GOG copy inside a Steam Proton prefix — in
0.17 s, and lists both rather than picking for you. A `--path` you give is a hard stop if
it is wrong: no silent fallback.

## Track 2 — "I want to build the native port"

Read [`docs/PORT-PLAN.md`](docs/PORT-PLAN.md) first. It has the measurement method, the
error census, and an explicit list of numbers this project published before running them
and then had to withdraw. Read that list before you quote anything.

The decompiled source is **not in this repository.** It is a separate, public,
GPL-licensed matching decompilation; this repo ships only the tools used to measure it,
the fixes that came out of it, and the numbers.

**What compiles today:** **54 of 66** translation units on `x86_64-linux-gnu`; 66 of 66 on
`i386-linux-gnu` — the second only with `-Wno-c++11-narrowing`, the flag that build
actually uses. The i386 build is kept deliberately as a **diagnostic oracle**: a file that
fails on x86_64 but passes on i386 is blocked by pointer width and nothing else, which is
all 12 of them. Every remaining error is one class — a pointer cast into a smaller integer
type — at **385 sites**, down from 1,377 on the morning of 12 October. Both counts
reproduce with `tools/sweep-compile.sh`.

**How the first four came in (12 October, tier 1).** The 33 failures were not evenly priced. Three
were a single line each; one was a program that truncated a pointer and then wrote silently
through the truncated value. And 308 of the 1,377 sites — 22% of the entire remaining work
— were the *same call*: `Sprite_FillRect((int)g_pGraphics + 0x150, …)`, across 14 files,
into a parameter the function never reads. One prototype pair and one substitution removed
all 308. The script is
[`tools/fixes/patch_ptrwidth_tier1.py`](tools/fixes/patch_ptrwidth_tier1.py) — idempotent,
every file backed up before it is touched. **And a warning for whoever does the next one:
the sweep passes `-w`, so any of these sites can be made to compile by casting to
`intptr_t` and letting the value silently narrow into the `int` it is passed to. That
raises this number without making a single pointer whole. Every edit above widened a
type.**

**How the next seventeen came in (12 October, tier 2 — 37 → 54).** Held to the same rule:
1,178 sites became 385, and not one edit is a cast papering over a narrowing. Most of the work
was not casts at all but **wrong types in the decomp**, which is why the sites fell faster
than the file count: `CFrontend::GetArchivePrimaryIDEntry` was declared `void *` while
returning an `int` field of `g_unk0x00516b40.ids[]` — one return type corrected 23 sites in
9 files; `MenuItem::param` and the five `Menu_AddItemType*` parameters hold a function
pointer (the code calls it as one) — 313 sites; `g_menuNextAction` holds a `Menu *` — 99
sites; a dozen small interfaces (`Font_Unused`, `Collision_SeparateCarBoxes`,
`CGraphics::ApplyTextureStageChange`, `Sound_NoOpMusicCallback`, the ACM callbacks'
`dwInstance`, …) each take a pointer through an `int` parameter.

Because the temptation is now bigger, so is the check:
[`tools/ptrwidth-audit.sh`](tools/ptrwidth-audit.sh) recompiles every translation unit with
**no `-w`** and `-Wshorten-64-to-32`, naming with a file and a line every place a 64-bit
value lands in a 32-bit container; every rewritten cast had to pass it, and every line it
complained about was reverted whole. Truncation warnings on the tree went **36 → 25** — down,
because widening removed real ones, and none of the 25 is on a line tier 2 touched.

**And the play build was checked, not assumed.** `work/PLAY/out-plain/cmr2` — the 32-bit
binary the desktop icon launches — was rebuilt and passes its own drive gate, and then the
two links were compared function by function with addresses normalised: **3,635 functions,
3,633 identical instruction for instruction**, the two exceptions being the ID-entry
accessors, which differ only in which register holds the GOT base. Every affected file
recompiled for i386 from the untouched tree has a **byte-identical `.text`**. `intptr_t` is
`int` on i386; that is measured here, not assumed.

**These are compile-level numbers.** ASAN does not build on this toolchain, so there is no
runtime evidence about the port's correctness, and this repository will not imply there
is.

**The entire remaining Windows surface:**

```
278  Direct3D 7 call sites, 20 methods — 256 state, 22 draws
 45  files that include <windows.h>
 36  __asm occurrences — 0 visible to a non-MSVC compiler
```

81% of the D3D7 surface is in `Graphics.cpp` alone. The ratio matters more than the
total: **22 draws against 256 pieces of state** is the architectural problem, because
modern graphics APIs have no equivalent of "set this state, now draw" — you declare the
whole state up front and get a pipeline handle back. That means a state tracker, which is
the real mountain.

**One genuinely good discovery:** the game is Direct3D 7 **fixed-function** and submits
`D3DTLVERTEX` — transformed, lit, screen-space triangles. There are no shaders to port.
The game already does its own transform and lighting math in software. The renderer's job
is "fill screen-space textured triangles", which is close to the most portable shape 3D
code can have.

**Toolchain on a Deck (rootless, no sudo):** `zig cc` with standalone cmake and ninja, or
a distrobox container. `zig` defaults to musl — you must pass `-target x86_64-linux-gnu`.
Note the trap that cost this project a day: `zig cc` at `-O0` is Zig's **Debug** mode, so
clang's array-bounds sanitiser is live and its runtime **panics** instead of printing —
on decompiled code that forms pointers past the end of arrays on purpose. See
[`docs/PLAY-CHECKPOINT.md`](docs/PLAY-CHECKPOINT.md) §1.

**The five fixes are published as scripts** — idempotent, backed up, anchored on exact
strings — in [`tools/fixes/`](tools/fixes/), with the checks that stop the launcher from
ever again starting a build that cannot drive (`tools/drivecheck.sh`,
`tools/loopcheck.sh`).

---

## Where this is going

In rough order, and every item here is a real plan rather than a wish:

1. **Make the picture right** — the lighting defects (§2 of
   `docs/DEATH-AND-LIGHT.md`), then the near-plane blow-up that owns the frame.
2. **The GUI installer** — one download, one click, no terminal. The destination.
3. **Controller support finished** — analogue triggers that behave progressively, because
   a rally game with on/off throttle isn't a rally game. The axes are delivered; the
   engine's pedal axis is fed by nothing today.
4. **A championship builder** — Classic mode or Custom: any number of tracks, reversed or
   not, stages per track, repairs on or off. The game's own championship screens are in
   the decomp already; the custom rules are new.
5. **Damage on a slider** — the game already deforms real mesh vertices on impact.
6. **Multiplayer** — and the good news is that rally is asynchronous. Cars race the clock,
   not each other, so this needs a shared championship file and submitted stage times, not
   lockstep netcode.
7. **CMR3 content** — opens once the `PP_F` record layout is parsed for its own files.

---

## Where everything lives

| path | what |
|---|---|
| `cmr2lab` | the container tool **and the installer CLI** — one file, no dependencies (`where`, `install`) |
| `cmr2install` | the **browser installer** — three tiers: the usual places, an automatic search under them, then a real folder browser. Needs `cmr2lab` beside it |
| `src/port/` | the native renderer: C + SDL3 + Vulkan |
| `docs/DXT-COPY-PATH.md` | why the stage's textures were invisible (fix 1) |
| `docs/GPU-LIFETIME-FIX.md` | the ring timeout that killed every run (fix 2) |
| `docs/DEATH-AND-LIGHT.md` | the second GPU hole, and the lighting, measured (fix 2 + open) |
| `docs/ROAD-TEXTURE-OWNER.md` | the road drawn from the wrong vertices (fix 3) |
| `docs/DRIVE-LOOP-REGRESSION.md` | our own tool deleting the drive loop (fix 4) |
| `docs/LAUNCHER-DEAD-BUILD.md` | why the launcher asks the file instead of an order |
| `docs/PLAY-CHECKPOINT.md` | the game booting, the sanitiser panics, the two-build answer |
| `docs/MENU-CAR-EVIDENCE.md` | the setup-screen car, and what it is not |
| `docs/CONTAINER.md` | the `.bfl` container format |
| `docs/C3D.md` | the `PP_F` 3D geometry format |
| `docs/PORT.md`, `docs/PORT-PLAN.md` | the native port: overview, error census, withdrawn numbers |
| `docs/GLOSSARY.md` | **every term in this repo, in plain English** |
| `docs/progress-archive.md` | the dated append-log, mistakes included, kept verbatim |
| `tools/` | the analysis scripts behind the numbers |
| `tools/build_art.py` | regenerates the public-face art from the game's own FrontEnd textures — nothing drawn by hand |
| `docs/INSTALLER.md` | what the installer got wrong, what is verified now, and the one defect found in the pair |
| `docs/ART-PROVENANCE.md` | the old social preview measured, the new one measured, and an audit of which palette entries really come from the game |
| `tools/fixes/` | the five fixes, as runnable patch scripts |
| `progress.md` | the live status page — rewritten whole each round |

**Still reading? [`docs/INDEX.md`](docs/INDEX.md) maps every document in this repo —
reference first, then the engineering journal.** If a word in this README was unfamiliar, it's
defined there — D3D7, RHI, translation unit, triangle list, byte-identical, all of it.

---

## A note on the name

The repository is called `cmr2lab` because it started as a container-inspection lab. The
project it now serves is **CMR2LRE**. The old name stuck to the URL; the project outgrew
it.

---

## Legal

This repository contains **no game data.** No textures, no models, no audio — not one byte
from Colin McRae Rally 2.0 or 3. It is a tool.

Bring your own copy of the game. Reverse engineering for interoperability is established
practice; redistributing the assets is not, and this project does not do it. The same rule
that keeps decompilation projects alive for decades is the rule here: **ship the code, let
the user supply the files.**

Everything in this repository is code and documentation, and the geometry, container and
texture work was derived from data the user already owns.

MIT licensed — see [`LICENSE`](LICENSE).

---

## Who builds this

Miami owns it. The work is done by agents, two of them most days — one on a Steam Deck,
one on a phone — which is why the commit history has an unusual shape. The Deck one does
the port work; the phone one does the archaeology and writes things down.

Both of them read the actual files rather than remembering what's in them, which sounds
like a low bar until you watch how often it matters. The four fixes in this README are
what that produces — including the fourth one, which was ours.

