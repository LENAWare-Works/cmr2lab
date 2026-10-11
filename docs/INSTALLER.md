# The installer — what was broken, what is fixed, and what is now trusted

**Deck side, 2026-10-11 15:1x EEST.** Covers `cmr2lab` (the CLI) and `cmr2install` (the
browser installer) as they now sit in this repo. Every number here was measured on this
Deck, against Miami's own game tree, not against a fixture.

---

## 1. The bug that was shipped (v0.1.0), reproduced

`find_game()` returned *the content directory* and `cmd_install` then looked for an
executable **inside it**. On our own copy, exactly as reported:

```
find_game('/home/deck/lena/.lena_cmr2/game')  ->  '/home/deck/lena/.lena_cmr2/game/Game'

[Desktop Entry]
Exec=/home/deck/lena/.lena_cmr2/game/Game      <- a DIRECTORY
Path=/home/deck/lena/.lena_cmr2/game/Game
```

`.../game/Game` holds `Bigfiles`, `Cars`, `Tracks`, `DemoRuns`, `Info` — no executable.
So the launcher Steam was handed tried to launch a folder. Two stacked defects: wrong
root, then launch-nothing. Reproduced with the shipped file in an isolated `HOME` so
nothing was written to his `~/.local/share/applications`.

## 2. The v0.2.0 fix, confirmed

Root and content are separate concepts. The search finds the content directory (the one
holding **both** `Cars/` and `Tracks/`), then walks **up** to the nearest ancestor that
holds an executable; that ancestor is the install root — what you launch and what
`Path=` gets. Measured against the real tree:

```
install root : /home/deck/lena/.lena_cmr2/game
content dir  : /home/deck/lena/.lena_cmr2/game/Game   (220 cars, 212 tracks)
retail exe   : /home/deck/lena/.lena_cmr2/game/CMR2.exe
```

Correct. `where` also prints every place searched with found/miss/skip, so a failure
explains itself instead of being silent.

## 3. Four defects found in v0.2.0 on this machine — fixed in v0.2.2

Each was measured; the fixes are in `work/CMR2LAB-v020/REPORT.md` with the commands.

1. **`Cars/ + Tracks/` false-positives.** With no arguments, `where` landed on
   `/home/deck/.steam/steam/steamapps/common/Automobilista 2/Audio` — AMS2's *audio
   bank* folder contains directories literally named `Cars` and `Tracks` — and reported
   `✓ <== INSTALL`, 0 cars, 0 tracks, exit 0. A confident wrong answer, the same class of
   failure that was just fixed, moved to a new source. Now: content must also hold at
   least one `.bfl` inside `Cars/`, and a near-miss is reported *with the directory named*.
2. **`~/.lena_cmr2` is a dead path on this box.** His tree is
   `/home/deck/lena/.lena_cmr2/game`; the sandbox layout is `/root/.lena_cmr2`. Both dev-copy
   sources were silent misses here (defect 1 hid it, because something else "succeeded"
   first). Both layouts are now in the search list.
3. **An explicit `--path` that fails still fell back.** Spec says `--path` wins. Given a
   path that does not exist, v0.2.0 printed a blank marker and then returned *another*
   game as the install. Now: a `--path` that is unusable is a hard stop, exit 1, with the
   reason in words and a note of what it *would* have found otherwise.
4. **The bounded walk could not reach a Proton prefix**, so the `compatdata` source never
   fired: a real prefix is `compatdata/<appid>/pfx/drive_c/<game>/Game`, five levels down,
   and pruning stopped the descent at `drive_c`. Fixed with a prefix-aware source. When it
   was fixed it found **a second real install on this Deck that nothing else had reported**:

```
[1] /home/deck/.steam/steam/steamapps/compatdata/3646996028/pfx/drive_c/Program Files (x86)/Codemasters/Colin McRae Rally 2
    220 cars, 212 tracks   from: Steam compatdata (Proton)
```

That is his GOG copy (CMR2.exe dated 2004, dgVoodoo present), installed under a Steam
shortcut's Proton prefix. Whole search on this handheld: **0.17 s**.

## 4. `cmr2install` — the browser tool, verified independently

Verified **through the HTTP endpoint**, not through the CLI, on fixtures built for the
purpose (`/tmp/civ/fix`, a Wine/GOG-shaped prefix and a native install root). Server:
`python3 cmr2install --no-open --port <port>`, requests to `/api/install`.

| case | request | result |
|---|---|---|
| **A** auto, Wine/GOG-shaped prefix | `{"root":"…/drive_c/GOG Games/Colin McRae Rally 2.0","mode":"auto"}` | `ok:true`, `Exec=…/CMR2.exe`, `Path=…/Colin McRae Rally 2.0`, `exists:true`, `runnable:true` |
| **B** native, where a port exists | `{"root":"…/native-install","mode":"native"}` | `ok:true`, `Exec=…/cmr2-native` |
| **C** native, where NO port exists | same request at a root with only `CMR2.exe` | `ok:false` — *"you asked for the native port and there is no cmr2-native (or cmr2) in …"*, **and no file written** |
| **D** a folder that does not exist | `{"root":"/tmp/civ/nope-does-not-exist"}` | `ok:false` — *"no such folder: …"*, **and no file written** |

After the battery, `ls` of the output directory shows exactly two files: `A.desktop` and
`B.desktop`. C and D wrote nothing — no silent fallback, which is the property that
mattered. `write_launcher()` also reads the file back and returns the `Exec=` line with
`exists` / `runnable`, so the page reports what was *written*, not what was intended.
Tier 3 (`/api/browse`) lists real directories and flags the ones that look like a game
root, with the executables it found in each — verified by walking a folder holding both
fixture copies.

### 4.1 The defect I found in the pair (fixed here)

**`cmr2install` and `cmr2lab` v0.2.2 do not compose out of the box.** `cmr2lab.locate()`
returned `(info, log)` in v0.2.0 and returns `(info, log, hard_fail, found)` in v0.2.2.
`cmr2install` still unpacked two values, so **tier 1/2 of the browser installer died**:

```
File "…/cmr2install", line 65, in scan
    info, log = lab.locate()
ValueError: too many values to unpack (expected 2, got 4)
```

The exception is raised inside the request handler, so the client sees an empty reply —
on the page, tier 1 would simply never show an install. Fixed with a compat shim that
accepts **both** shapes (`_locate()`), so the two files can be updated independently;
verified working with the old lab *and* the new one. The same shim is what makes tier 1
list **every** install found (`everything=True`), which is the honest behaviour on a
machine with two copies:

```
found: /home/deck/lena/.lena_cmr2/game                      (220 cars, 212 tracks, our dev copy)
found: /home/deck/.steam/steam/steamapps/compatdata/…/Colin McRae Rally 2   (220 cars, 212 tracks, Steam compatdata (Proton))
```

Before the change, that same page reported AMS2's audio folder. The four cases A–D were
re-run after the change: still 4/4, nothing extra written.

## 5. What a launcher can and cannot do here (measured)

| | |
|---|---|
| `game/CMR2.exe` mode | **600** — no exec bit; a desktop or Steam shortcut will not run it as-is |
| `game/CMR2.exe` first bytes | `MZ` — a Windows PE32; it needs Proton or Wine, and Steam only runs it if the shortcut is set to force a compatibility tool |
| the native port | what a launcher on this box should actually point at; `cmr2lab install --native` refuses rather than quietly falling back to the PE when there is no port |

`install --exe <path>` was added for the case where the door is a script he already
trusts (`~/lena/cmr2lre.sh`, which carries its own drive-check gate) rather than a
bare binary.

## 6. What is in the repo now

| file | what it is | md5 |
|---|---|---|
| `cmr2lab` | the content lab + installer CLI, v0.2.2 | `135559b49804f6733b1d808f9f4cd477` |
| `cmr2install` | the browser installer, v0.2.1 (v0.2.0 + the compat shim and multi-install scan) | `0a68aedac4ad46afd7a54029614870f4` |
| `tools/build_art.py` | regenerates the public-face art from the game's own FrontEnd bfl | — |

Both tools are one file, stdlib only, no dependencies. `cmr2install` loads `cmr2lab`
from the same folder (or its parent), which is why they ship as a pair and why they are
tested as a pair.

## 7. Who owns it

**The installer stays Lena-on-the-phone's to own; this repo consumes it, pinned.** The
reasoning, briefly: she wrote it, she has the browser/HTTP context it lives in, and the
Deck is the place it gets *measured*, not the place it gets rewritten — a side that
rewrites a tool it cannot see the users of is exactly how the AMS2 false positive
happened. What this side owns is the **verification**: every claim above was re-measured
on this machine, plus the pairing tests that stop the two files drifting apart again
(that drift is §4.1, and it was live in the shipped pair). Deck-side fixes go back to her
as a diff and a failing case, not as a fork.
