# DECK-UI CONSTRAINT — the operational form of charter item 23

Written 2026-10-11 on the Deck. This is the *checkable* version of Miami's
requirement, because "Steam Deck compatible" is a sentence and a build needs a
list. `CHARTER-REVIEW.md` sits next to this file and holds the architecture read;
this file holds the gates.

His words, verbatim, 2026-10-11: **"add in the CHARTER. UI must be Steam Deck
compatible."** Filed by the phone as open_question 23 in
`~/.lena_projects/cmr2-native.json`, and his scope fix on the theme in the same
breath: **"The Installer CMR2.0LRE I mean not the actual game."** So the object is
OURS: the installer / modkit / wrapper. The game keeps its own look and keeps its
own frontend question (item 15).

---

## 1. The two acceptance tests. Nothing else counts as "compatible".

**T1 — CONTROLS, with the mouse and keyboard unreachable.**
Every control in the UI is reachable and operable with: left stick + d-pad,
A (confirm), B (back), and the shoulders (page/tab or scroll). Nothing may
require: a pointer hover, a right-click, a drag, a scroll wheel, a double-click,
a text field typed into with a hardware keyboard, or a keyboard shortcut.

**T2 — LEGIBILITY at 1280x800, on a 7-inch panel, at arm's length.**

| element | floor | why this number |
|---|---|---|
| body / list text | **20 px** | 1280 px across ~151 mm = 8.5 px/mm, so 20 px ~ 2.4 mm of glyph. Below that it is a squint at handheld distance. |
| headings | 32 px | it has to be findable without reading |
| tap targets / rows | 48 px tall | a row you can hit with a stick is a row you can hit with a thumb when Steam Input flips to touch |
| contrast | 4.5:1 | the panel is glossy and he plays in daylight |

**The launch default is fixed: 1280x800, borderless, fullscreen.** No resolution
picker, no "first run wizard", no window-size memory. A resolution choice before
the tool can be used is item 23's `NOT_THIS` verbatim.

---

## 2. Audit of the UI we ALREADY ship (2026-10-11, measured)

The installer is not written yet, so the only UI this project owns today is the
launcher wrapper. It is worth auditing now, because a constraint nobody applies
to the thing that already exists is decoration.

### 2.1 FINDING — there are THREE launch surfaces called CMR2, and only ONE is gated

| surface | what it runs | gated? |
|---|---|---|
| `/home/deck/Desktop/CMR2LRE.desktop` → `Exec=/home/deck/lena/cmr2lre.sh` | **the game.** Refuses if a copy is already running, refuses if the binary cannot drive a car, logs what it started. | **yes** — this is the one he clicked at 11:06:03 |
| `~/.local/share/applications/cmr2-native.desktop` → `Exec=/home/deck/lena/cmr2deck/run.sh` | **the asset viewer** (`cmr2deck/build/cmr2deck`, default car `205a1N`). Not the game. | **no** |
| Steam shortcuts (`userdata/180595232`) → `/home/deck/lena/.lena_cmr2/game/CMR2.exe` | the dead Wine route from before the native port | **no** |

Measured by reading the three files. **Why item 23 cares:** the failure this
project spent a day on was "the icon took the first path that EXISTED, not the
first that WORKED" — and there are still two other icons on this machine that can
hand him something that is not the game, with no gate and no logging. Not a bug
in the wrapper; a bug in the set of doors. Cheap to fix once the installer exists
(the installer is the door) and cheap to state now: **one name, one door.**

### 2.2 FINDING — the wrapper's failure path is a modal dialog, which is the exact mouse-only class item 23 names

`cmr2lre.sh` says things through `say()`:

```
kdialog --error  ->  zenity --error  ->  notify-send  ->  stderr
```

Measured: all three of those binaries exist (`/usr/bin/kdialog`,
`/usr/bin/zenity`, `/usr/bin/notify-send`). Measured: in this desktop session
`org.freedesktop.Notifications` is owned by `plasmashell` (pid 501695), so
notifications work *here*.

Not measured, and I am not going to pretend otherwise: **Game Mode.** In a Steam
Game Mode session plasmashell is not the session shell, so my reading is that
`notify-send` is the one path that goes silent and the dialog is a desktop window
sitting over gamescope with no guaranteed focus. Whether a Deck gamepad's A/B
reach a raw KDE dialog there is **untested**. It needs a Game Mode test, and until
it has one this is a live instance of the thing item 23 forbids: *a UI that cannot
be used without deciding something we did not design.*

**The fix is structural, not a tweak:** the wrapper's messages are the first
screen a user meets and they belong to US, not to KDE. When the installer binary
exists, `say()` becomes a screen in our own window — 1280x800, dismissible with
A/B, drawn in the CMR2.0 identity like everything else. A dialog we did not draw
is a UI we cannot promise anything about.

### 2.3 GOOD NEWS, MEASURED — the wrapper's decisions have a headless seam

`CMR2LRE_NOGUI=1` (stderr only, no dialogs) and `CMR2LRE_DRYRUN=1` (decide, log,
print, do not exec) exist, and I ran the pair:

```
$ CMR2LRE_NOGUI=1 CMR2LRE_DRYRUN=1 sh ./cmr2lre.sh
CMR2LRE: Colin McRae Rally 2.0 is already running (pid 3923265).
Starting a second copy wedges the display -- so this one did not start.
Close the other one first.
exit=1
```

Two things proven at once: the "do not stack two copies" guard fires correctly —
a lane process (`work/MENU-CAR-FLATTENED/out-md2/cmr2`) held the machine and the
launcher refused to add a second — **and** it does this with no GUI and no GPU.
So T1 can be tested on the wrapper without opening a window and without stealing
the card from another lane. That is the shape the installer needs too: every
decision reachable and assertable headlessly, the window being only presentation.

---

## 3. The gate for the installer round

The installer is not "Deck compatible" until every line below is true, and each
line is checked by doing it, not by reading the source:

- [ ] One file. Launched from Game Mode (non-Steam shortcut) with no terminal.
- [ ] First screen is drawn by us and is legible at 1280x800 with no window
      manager, no decoration, no resolution prompt.
- [ ] Every control reachable with stick/d-pad + A/B + shoulders. Unplug or
      ignore the keyboard and mouse for the whole pass.
- [ ] Lists (cars, tracks, files) scroll with the stick/shoulder **and** have a
      visible focus that survives a 360-degree stick sweep without getting lost.
- [ ] No text entry. If a path must be chosen, choose it from a list; if one is
      unavoidable, it comes up with the system on-screen keyboard and states that
      it can be typed with the Deck's own keyboard — never "type the path".
- [ ] Failure states are OUR screens, in the same identity, dismissible with B.
      No kdialog, no zenity, no notify-send, no silent exit.
- [ ] The theme comes from the game's own data (`res1024.bfl` / `common.bfl`:
      `livery1/2/3.tga`, `cmr2.tga`) — item 22, installer only, game untouched.
- [ ] Verified in **Game Mode** by Miami, without him asking me how to run it.

## 4. What this file is for

A rule is real when it can fail something. This file is the thing that fails a
UI round: if an installer round comes back and any box above is unticked, the
round is not done, no matter how good the screenshot is. It is also the reason
the non-GPU lane exists — see `NOTE-to-phone-UI-DECK-CONSTRAINT.md` next door.
