# CHECKPOINT — the crash that stopped the game at 16 s, and what is on screen

Lane: `work/PLAY`. Written 2026-10-10 ~22:55 EEST, on the Deck.
Task: `HOc6a6a7`, the continuation of Miami's *"open up the game lets test it out"*.

**One line: the game used to die on a sanitizer panic about 16 seconds in, every
run. It now runs — 30 s and 55 s runs, no panic — renders a real screen, and
takes input. It is not yet a game you can drive: it gets past the legal notice
and has not been seen to reach a stage.**

---

## 1. THE BUG THAT WAS KILLING IT, AND WHY IT LOOKED LIKE A DECOMPILER BUG

```
thread 406176 panic: index 6484 out of bounds for type 'BYTE[6464]'
CMR2Decomp/FileBuffer.cpp:397 in Profile_AssignAvailableCategory
CMR2Decomp/FrontendScreens.cpp:6270 in FrontendProfile_SetupNextPlayer
```

`cmr2` is 32-bit and built with `zig c++` at **-O0, which is Zig's Debug mode**:
clang's `-fsanitize=array-bounds` is on and the binary links **Zig's ubsan
runtime, which PANICS instead of printing a diagnostic**. So the game dies the
first time the decompiled source forms a pointer past the end of a declared
array — and the decompiled source does that on purpose, because that is what the
original MSVC6 output does.

**Measured on this toolchain** (`/tmp/ub5.c`, `/tmp/ub6.c`, `/tmp/ub7.c`):

| expression, `char G[4]` | result |
|---|---|
| `G + 4` (one past the end) | **allowed** — index == size is legal C |
| `G + 5` | panic: `index 5 out of bounds for type 'char[4]'` |
| `(char *)G + 5` | **allowed** — a cast is pointer arithmetic, not a subscript |

That single measured line decides the fix: **only a strictly-past-the-end array
SUBSCRIPT traps, and only the subscript form is instrumented.**

The decompiler wrote every "walk one field of each record" scan as
`p = RECORDS + firstField; p < RECORDS + (size + firstField)`. For
`g_saveProfiles` (4 × 0x650 = 0x1940) the sentinel is **+0x1954**: record + 0x14
of a fifth record that does not exist. It is only ever *compared* — the last
address actually read is +0x1304 — but the subscript form of it is fatal.

## 2. WHAT CHANGED ON DISK

| file | change |
|---|---|
| `CMR2Decomp/RallyData.cpp` | 2 sentinels cast to `(BYTE *)`; 1 to `(int *)` (`g_unk0x00536ff0 + 25`, element 25 of 24); long comment above `g_saveProfiles` explaining all of it |
| `CMR2Decomp/FileBuffer.cpp` | 3 sentinels cast; pointer to the comment above the `extern`s |
| `CMR2Decomp/FrontendScreens.cpp` | 1 sentinel cast (`g_saveCarRecords + 0x62c`, 12 bytes past an 8×0xc4 array) |

Seven sites, three files. **No loop bound, iteration count or write offset
changed** — only the way a pointer 12/20/4 bytes past an array is spelled.
Backups: `*.bak-pre-bounds-sentinels-20261010-224434` beside each file. Applied
once, anchored on exact strings, refusing to run if the source has drifted:
`work/PLAY/patch_bounds_sentinels.py` (dry-run by default, `--apply` to write).

Found by `work/PLAY/bounds_scan.py`, which walks every declared array in the
tree and reports `ARRAY + CONST` with `CONST > size`: **56 hits, of which 7 are
real** (the other 49 are locals with common names — `a`, `value`, `record`,
`pParts` — matched against unrelated declarations). Three of the seven are in
code a stage run will reach and would have died the same way.

Rebuilt: `FileBuffer.o`, `RallyData.o`, `FrontendScreens.o` into
`~/lena/work/CMR2/sw18/obj` (old ones kept as `*.pre-bounds-20261010`), then
`OUT=/home/deck/lena/work/PLAY/out sh link32.sh` → **link exit=0**, 32.7 MB
(SDL3 linked), with debug info.

## 3. THE RUNS — WHAT IS ACTUALLY TRUE NOW

`work/PLAY/run-play.sh <secs> [--snap] [--census]`, always from the game root.

| run | length | result |
|---|---|---|
| before the fix | 16 s | panic, `FileBuffer.cpp:397`, every time |
| `play1.log` | 32 s | alive at the end, no panic, no MSGBOX storm |
| `run-snapshot.log` | 30 s | alive, 1 swapchain frame captured, no panic |
| `run-with-keyinjection.log` | 55 s | no panic, 4 frames, screen **changed** after keys |

**The frame rate is real**: in the last run the RHI reported frame 243 at t+6 s
(≈40 fps including startup), 876 at ≈t+17 s, 1568 at ≈t+27 s → **~60 fps** once
up. An earlier 30 s run that only reached frame 120 was fighting the *other*
worker's game process for the GPU (see §6), not slow by itself.

### What is on the screen (swapchain captures, `evidence/frame-*.png`)

| frame | what it is |
|---|---|
| `frame-000/001.png` | the legal notice: `© 2000 The Codemasters Software Company Limited` etc., 9 small lines, plus two blocks of big text. 17 colours, 40,778 bright pixels, all inside x86-974 y336-680, the rest of the screen black. **Identical at t+1 and t+6 s** — it sits there waiting. |
| `frame-002/003.png` | **after the key presses**: full-screen layout, ~32,000 bright pixels spread across x3-1257 y43-749 — a header block top-left and top-right, sparse text down the middle, and a wide tabular band at y636-744 with separate cells. 92,856 pixels differ from frame 000. |

So it boots, holds the notice, and **advances when a key arrives**.

Input is proven end to end, not assumed: `inject-key.py` creates a synthetic
keyboard on `/dev/uinput` (deck has write access) and the port's own trace
answers:

```
[DIN +64194.037] scancode 0x1c DIK_key DOWN     <- injected evdev 28 -> DIK_RETURN
[DIN +64194.453] scancode 0x39 DIK_key DOWN     <- injected evdev 57 -> DIK_SPACE
```

### Where the frames come from

**Not** from an X screenshot. `ffmpeg -f x11grab :0` returns an **all-black
frame on this session whether the game is running or not** (measured twice,
including with nothing else on screen) — XWayland's root is not the composited
desktop. Every pixel claim above is the RHI's own swapchain capture
(`A7VK_SNAP=120,600,1500:/tmp/playframe.ppm` or the `A7VK_SNAP_TRIGGER` file
handshake). A screenshot taken the other way would have "proved" the game
renders nothing.

## 4. TOOLS LEFT BEHIND, ALL REUSABLE

* `run-play.sh <secs> [--snap] [--census]` — one measured run, correct cwd, INT
  not KILL, snapshot/census optional.
* `inject-key.py enter space up a` — synthetic key press; `--list` for names.
  The way to answer "does the game see input" without a human at the device.
* `bounds_scan.py` — the array-overrun detector above. Run it before blaming
  the renderer for something that is an address.
* `patch_bounds_sentinels.py` — the fix, idempotent, refuses on drift.
* `evidence/` — the raw runs, the four frames as PNG and the notice screen as
  the raw PPM, so every claim here can be re-made rather than believed.

## 5. THE LAUNCHER MIAMI ASKS FOR

`~/lena/cmr2-native.sh` — the native port, from the game root, taking the
desktop session out of plasmashell's environment. `--log` keeps the output in
`evidence/last-run.log`. Stop it with `pkill -x cmr2`.

`~/lena/cmr2-play.sh` and `cmr2-play-x11.sh` are **Proton** launchers for the
original `CMR2.exe` — a different thing on purpose. Don't confuse the two.

## 6. THE OTHER WORKER — READ THIS BEFORE TRUSTING A MEASUREMENT

There is a **second daemon worker running the same continuation task**
(`HO712b55`, started 22:46:15) while this one (`HOc6a6a7`) was mid-run. Two
`cmr2` processes on one GPU corrupt each other's frame timings, and its
`pkill -x cmr2` kills my run mid-capture.

Its first test at 22:45 ran `cd ~/lena/work/PLAY/out && ./cmr2` — **from the
binary's directory, not the game root** — and got 200,000 message-box dialogs
("the game is spinning, not running"). That is a wrong-cwd artefact, not a
regression: from the game root the same binary shows three CD-load dialogs (the
Bink intro path, non-fatal) and runs. `work/PLAY/READ-ME-FIRST-two-workers.md`
says this, and says its `pf.ppm.*` captures and mine are of the same binary.

## 7. OPEN

1. **The legal notice is gated on a key, and the port's Bink is a stub** — the
   intro movie (`FrontEnd/Videos/intro.bik`, present) cannot play, which is why
   the notice sits there. Whether the frontend would have advanced on its own
   after the movie, and whether the CD-load dialogs are only that stub talking,
   is worth one run with `DECK_MSGBOX_MAX` high and the paths traced.
2. **The screens after the notice have not been identified.** The frames are
   there; reading them (header text, the tabular band at y636-744) is the next
   ten minutes and it is what tells us whether this is a menu or a records
   table.
3. **No stage has ever been reached** — S2's standing item, unchanged. The
   notice-to-menu transition is now known to work, which is further than S2b
   got, but `0 of 205,714 draws carried the mesh FVF` is still the number that
   matters and nothing here touched it.
4. **The frame captures are the RHI's, so they show the swapchain, not the
   window.** If a future round needs "what does the desktop see", that method
   has to be found first — x11grab is not it.


---

## 8. SECOND FATAL TRIP, AND THE TWO-BUILD ANSWER (23:0x)

The array-bounds fix was necessary but not sufficient. A later run died on a
**different** UBSan check, again in decompiled code, again on something this CPU
does for free:

```
thread 411989 panic: load of misaligned address 0x11cd97e for type 'int *',
                         which requires 4 byte alignment
CMR2Decomp/GameInfo.cpp:1966 in OptionMenu_LoadRallyRecords
```

So the fatal set is not one bug class, it is *"any UB the original binary was
allowed to rely on"* — and on decompiled code that is unbounded. Chasing it site
by site is a treadmill, and it is **not** what "open up the game and test it"
needs.

**Answer: two builds, on purpose.**

| binary | UBSan | role | measured |
|---|---|---|---|
| `out-plain/cmr2` (**the launcher's default**) | **off** (`-fno-sanitize=undefined`, `build-plain.sh`) | playing | 66/66 objects, link 0, **0 ubsan handlers left in the game objects**; 16 s and 14 s runs, no panic |
| `out/cmr2` | on (`link32.sh`) | finding defects | found the 7 array-bounds sites; dies on the misaligned load |

The platform layer (`platform/*.cpp`) stays checked in **both** — it is
hand-written, so a misalignment there is a real bug, not an artefact. Only the
decompiled game objects lose the checks.

**Do not read "UBSan off" as "the fix didn't matter".** The array-bounds fix is
in the *source* and every future build carries it; the plain build just stops
paying for a checker that cannot distinguish a decompiler artefact from a bug.

## 9. AN UNEXPLAINED COLOUR DIFFERENCE — MEASURED, NOT EXPLAINED

Back-to-back runs, same game root, same frame number, only the binary differing:

```
frame 240, checked build : [('000000', 970741), ('ffffff', 17664), ('808080', 5730)]
frame 240, plain build   : [('9cb4ac', 970741), ('ffffff', 17664), ('cedad6', 5730)]
                           1006336 of 1024000 pixels differ
```

Identical geometry and identical rank counts, so it is the *same screen*; the
plain build's copy is the checked one faded toward white. The map is exactly
affine per channel and solves to a white blend:

```
out = (1-t)*in + t*255      t = 0.61 (R), 0.71 (G), 0.68 (B)
0 -> 9cb4ac   40 -> b5c7c1   80 -> cedad6   bf -> e6ecea    ff -> ffffff
```

Two candidate causes, and I could not separate them before the box became
unusable for long runs (§10): a real render-state difference between the builds
(which would be extraordinary but is what the A/B says), or a capture that
caught a different game state — the notice screen fades, and the RHI's `frames`
counter counts presents, not game frames.

**It is the same screen either way, and it is the checked build's frame that
matches the other captures.** Whoever owns the frontend-draw question should
settle it with one A/B at a fixed frame: it is one command from here. Do not
"fix" a colour that turns out to be a capture artefact.

## 10. WHY §9 IS NOT SETTLED: THE BOX WAS TAKEN

Two workers are on this task (§6 of `READ-ME-FIRST-two-workers.md`). From 22:53
on, `cmr2` was repeatedly **SIGKILLed mid-run** by the other worker's cleanup
(`pkill -x cmr2`), including two runs I needed: `exit=137`, no panic line, log
cut off at startup, capture never written. Four runs died that way.

That is not a defect in the port and it is not in the counts above. It is why
§9's A/B is a single measurement rather than three, and why the plain build's
long-run claim rests on 16 s and 14 s runs rather than a 60 s one.

**One file collision, worth knowing:** both workers used `/tmp/snapnow` and
`/tmp/trig.ppm.NNN` — the RHI's fixed trigger paths. A frame I read as mine at
22:55 was the other worker's. `run-play.sh` no longer deletes or writes those
paths, and a unique trigger name per worker is the fix.

---

## 11. THE ICON WAS LAUNCHING A DEAD BUILD — GATED, 11:0x 2026-10-11

`~/lena/cmr2lre.sh` took the first candidate that **existed**; `out-plain/cmr2`
(08:53) was dead, so the Desktop icon launched a world with no drive loop — he did
exactly that at 10:03. Fixed at the source and at the door:

* `out-plain/cmr2` relinked 11:02, md5 **`80d927b54f59`**, DRIVES (byte-identical to
  `work/HUD-2D/out3/cmr2`, another lane's build of the same 10:45 tree);
* `build-play-lre.sh` — recompiles stale TUs, links to a temp, **checks the linked
  artefact**, and refuses to install a build that cannot drive;
* the launcher picks the first candidate that passes that check, **refuses to start
  anything if none does**, and logs every launch with md5 to
  `~/lena/cmr2lre-launch.log`;
* same gate, warning only, in `~/lena/cmr2-native.sh` (the second door);
* the check itself: `~/lena/cmr2-drivecheck.sh` (`cmr2_drives <bin>`).

Tested with no GPU: pick / skip-dead / all-dead-refusal / second-instance / warn path.
**Not** tested: a live run — the car-moves proof is still owed, and `out-plain` carries
the env-gated `[RT F]`/`[RT D]`/`[RT R]` traces (`DECK_RACE_TRACE=1|2`) so one
`drive.py` run on it settles the question.

Full record: `LAUNCHER-DEAD-BUILD.md`. Note for the phone: `NOTE-to-phone-LAUNCHER-GATED.md`.
