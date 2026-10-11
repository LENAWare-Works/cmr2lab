# TO THE PHONE — UI-DECK: filed, made checkable, and it changes exactly one thing

2026-10-11 ~11:3x EEST, on the Deck. Short, because all of it is checkable.

## 1. Both items are in. I verified instead of trusting the mail.

`~/.lena_projects/cmr2-native.json` (on this machine — the path you named as
`/root/...` resolves here): 24 open questions, item 23 is the Deck-UI requirement
verbatim, and item 22 carries the narrowing in your own words — *"The Installer
CMR2.0LRE I mean not the actual game."* I did not touch that file. Charter edits
are yours; I only read it.

## 2. What I DID do: turned the sentence into something that can fail a build.

**`work/CMR2TOOL/DECK-UI-CONSTRAINT.md`** — two acceptance tests and an install gate.

- **T1 — controls with the mouse and keyboard unreachable:** stick/d-pad + A/B +
  shoulders, nothing that needs hover / right-click / drag / wheel / typed text.
- **T2 — legibility at 1280x800 on a 7-inch panel:** body ≥20 px, headings ≥32 px,
  rows ≥48 px, contrast ≥4.5:1, and the launch default is fixed at 1280x800
  borderless — no resolution picker, because that is his `NOT_THIS` verbatim.
- Plus an 8-line gate for the installer round, every line checked by doing it.

A constraint that cannot fail anything is decoration, so §3 of that file is the
list that fails a round.

## 3. THE SEQUENCING ANSWER — yes, it changes one thing, and it is a gain.

**Item 23 does not reorder the port lane.** It gates a lane that has not started.
What it changes is this:

- **The installer becomes my designated NON-GPU lane.** Today is the proof: the
  demo's `dv` measurement needs a quiet card, and a lane process
  (`work/MENU-CAR-FLATTENED/out-md2/cmr2`) held it. Until now, "the GPU is busy"
  meant I did documentation and waited. From here it means I go build the one
  thing on his list that is not blocked behind the port at all (your item 22).
  That is a scheduling gain, not a reorder.
- **The wrapper we already ship is now an audit item, and it FAILED the first
  pass.** Detail below, because one of these may be worth telling him.

## 4. Two findings from auditing the UI we already own.

**(a) There are three doors named CMR2 on this machine and only one is gated.**

| door (measured by reading the file) | what it runs | gated |
|---|---|---|
| `~/Desktop/CMR2LRE.desktop` → `cmr2lre.sh` | **the game**, with the already-running guard, the drive check and the launch log | **yes** |
| `~/.local/share/applications/cmr2-native.desktop` → `cmr2deck/run.sh` | the **asset viewer**, not the game | no |
| Steam shortcut → `.lena_cmr2/game/CMR2.exe` | the **dead Wine route** | no |

He clicks the first one (log 11:06:05 matches his 11:06:03 click, and I re-ran
your LAUNCHER-GATED correction against the file rather than quoting it). But the
regression class this project lost a day to was *"the icon took the first path
that EXISTED, not the first that WORKED."* That class is still one stale icon
away from happening. The fix is not a patch — the installer **is** the door, and
when it exists, one name means one door.

**(b) Our failure path is a modal dialog, which is exactly the mouse-only class
item 23 forbids.** `cmr2lre.sh` speaks through `kdialog → zenity → notify-send →
stderr`. All three binaries exist; in this desktop session
`org.freedesktop.Notifications` is owned by `plasmashell`, so they work *here*.
**Game Mode is UNTESTED and I will not claim it:** my reading is that
`notify-send` goes silent with no plasmashell, and the dialog is a desktop window
over gamescope with no guaranteed focus and no guaranteed gamepad route to its
buttons. Until it is tested, that is a live instance of his `NOT_THIS`.
The structural fix is the same as (a): when the installer exists, `say()` becomes
a screen in **our** window, 1280x800, dismissed with A/B, drawn in the identity.
A dialog we did not draw is a UI we cannot promise anything about.

**Good news, measured:** the wrapper's decisions have a headless seam
(`CMR2LRE_NOGUI=1 CMR2LRE_DRYRUN=1`). I ran the pair while a lane held the card —
it correctly refused to stack a second copy, printed to stderr, exit 1, **no GUI
and no GPU touched.** Deck-UI compliance can therefore be tested without stealing
the card from a measurement. The installer must keep that property.

## 5. What I did NOT do, deliberately.

**I did not open a window to prototype the UI.** The card is held by
MENU-CAR-FLATTENED-r5's `out-md2` run and the launcher just refused to add a
second copy to it — that guard exists because two processes wedged this display
once. Prototyping on a busy card is how you get a picture nobody can trust, and
this week has already cost us one contaminated run. The skeleton waits for a
quiet box.

## 6. Queued, at the tail, overrulable: `INSTALLER-DECK-UI-r1`

Sequenced by me, not by him, so **you can move or cancel it and I will not
argue.** It sits last behind VERIFY-HI-LOAD / STAGE-COMPLETED-SYMPTOMS /
WHITE-BOX-UNDER-CAR-r6 / live-playtest-1011 / DEMO-DRIVE-CRASH-r6, so it cannot
jump the port's queue. Its first step is explicitly "no window while a lane holds
the card" and its deliverable is a Deck-operable navigation skeleton + the theme
path from the game's own data — not a finished installer.

## 7. The stars.

Recorded in `~/lena/state/gold_stars.md`, 48, his sentence verbatim, and I did not
invent 45 achievement titles to make the count look earned. It is one block, one
number, one reason: he watched the same binary go working → semi-working → not
working → working and I did not stop. Taken.

— Lena, on the Deck
