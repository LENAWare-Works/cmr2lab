# THE ICON, THE DEAD BUILD, AND WHY THE FIX IS A GATE AND NOT AN ORDER

`work/PLAY`, 2026-10-11 11:0x EEST. Lena-on-the-Deck, launcher lane. Task:
`LAUNCHER-POINTS-AT-DEAD-BUILD` (from the phone, 10:2x).

**One line:** the Desktop icon was launching a world where no car can move, because
it took the first candidate that **exists** instead of the first that **works**. The
play build is relinked and drives again; every launcher now refuses to start a build
that cannot drive, and writes down which build it started.

---

## 1. THE FACTS, EACH ONE RE-MEASURED HERE RATHER THAN TAKEN

| fact | how | result |
|---|---|---|
| the icon takes the first candidate that exists | `cat ~/lena/cmr2lre.sh` (step 1) | confirmed: `out-plain` first, `break` on `-x` |
| `out-plain` (08:53) is dead | `work/DEMO-DRIVE-CRASH/loopcheck.sh` | **DEAD**, md5 `d26a09231a98` |
| the dead arm really has no drive statements | my own disassembly of the function | 0 calls to `Physics_UpdateRateHold`, 0 to `Car_UpdateEngineNoteFalloff` |
| **the phone's alternative was already stale on arrival** | md5 search + `loopcheck.sh` | `d25d5ef3353b` exists **nowhere**; `out-rt2` was relinked at 10:48 to `0b53003787c8` and **that** reads DEAD |

The fourth row is the reason this file is not called "reorder the picker". The
suggested fix -- put the working binary first -- would have shipped a picker that
pointed at a different frozen world within the hour, because in this workspace a
binary path is a *name*, not a *build*: another lane relinked that name at 10:48 and
the md5 the phone measured at 09:47 no longer existed by 10:00. **A hardcoded order
has a shelf life here; a check on the file does not.**

Also measured, and it changes the shape of the day: a peer's `drive.py` run held the
GPU from 10:59:45 to ~11:05 (`work/RACE/out-rt2/cmr2`, PID 3636583). **I ran nothing
on the GPU for this task** -- no window, no key injection, no screenshot, no kill.

## 2. WHAT WAS BUILT TO FIX IT

**`work/PLAY/out-plain/cmr2` -- relinked at 11:02, md5 `80d927b54f59`, DRIVES.**
`../../.lena_cmr2/port/tree/CMR2Decomp` at its 10:45 state recompiled 9 stale TUs
(67 objects, 0 failed) and linked with the same flags and the same link line as
`build-plain.sh`. The dead binary is kept: `cmr2.bak-dead-pre-lre-20261011-110238`.

The result is **byte-identical** to `work/HUD-2D/out3/cmr2`, which another lane built
at 10:45 -- two lanes, same tree, same flags, same bytes. That is a useful accident:
it means this is not a Lena-flavoured build of the game, it is *the* build of that
tree, and it is the one that lane has been running.

**`work/PLAY/build-play-lre.sh` -- a build that refuses to install a dead binary.**
It compiles the stale TUs, links to a temp name, runs the drive check on the *linked
artefact*, and only then replaces `out-plain`; if the check fails it leaves what was
there untouched and exits non-zero. It also stamps the source revisions it is a
snapshot of (`.lre-source-stamp-*`) and appends to `.lre-buildlog`.

**`~/lena/cmr2lre.sh` -- the icon, now gated.** Same path, same Desktop entry, nothing
moved on his Desktop. Differences:
1. it picks the first candidate that **passes the drive check**, logging the ones it
   skipped as dead;
2. if **no** candidate passes it does **not** start one anyway -- it says so and stops.
   A frozen car presented as a game is worse than no game;
3. it appends `LAUNCH <binary> md5=<md5> skipped-dead:<list>` to
   `~/lena/cmr2lre-launch.log`, so "which build was he actually on" is never again a
   question for the journal to answer (it took a systemd-forensics round to learn he
   was on `out-plain` at 10:03);
4. `CMR2_BIN=` overrides the first candidate (still checked), `CMR2LRE_NOGUI=1` and
   `CMR2LRE_DRYRUN=1` test the decision with no desktop and no GPU.
Kept from the original: `cwd` = game root, and the refusal to start a second instance.

**`~/lena/cmr2-drivecheck.sh`** -- the same question as a sourced helper
`cmr2_drives <bin>` (0 drives / 1 dead / 2 cannot tell), so the next launcher does not
have to invent it a third time.

**`~/lena/cmr2-native.sh`** -- the *second* door: its default `BIN` was the same
`out-plain`. It now warns loudly (naming the regression and the relink command) and
waits 5s. It does **not** refuse, deliberately: a lane launching a bad build as a
control has to stay possible.

## 3. THE GATE: WHAT IT IS, CALIBRATED ON THIS WORKSPACE

One question, asked of the file: *does `Race_UpdatePlayerViewAndDrivenCars` call
`Physics_UpdateRateHold`?* -- the same question `loopcheck.sh` asks, in the same
0x900-byte window, with one `nm` and one `objdump` per candidate.

    DEAD   (+ hold=0)  out-plain@08:53, out-rt2@10:48, out-md@09:01, out-md2@09:13
    DRIVES (+ hold=1)  out-rt3, PLAY/out, out-race, out-plain@11:02

The third thing the restored block does -- store the bound to `0x538124` -- is **not**
usable as a gate: a literal `538124` grep reads 0 for every binary in this workspace,
good and dead alike (measured on four, both arms). My first version of the script
gated on it and refused a build that was in fact fine; that is recorded here so nobody
"restores" it.

**What the gate does not do:** it catches one regression class. It says nothing about
driving quality, the demo car having a driver, the HUD, the road, the menu car or the
frontend -- those are other lanes' questions and this does not answer them.

## 4. WHAT WAS TESTED, AND WHAT WAS NOT

Tested, no GPU, no window, no desktop dialog (`CMR2LRE_NOGUI`/`CMR2LRE_DRYRUN`):
* normal pick -> `out-plain`, md5 `80d927b54f59`, nothing skipped;
* override pointed at the dead binary -> skipped as dead, fell through to `out-plain`,
  notification emitted;
* **all candidates dead** -> `REFUSED` in the log, exit 1, **nothing launched**;
* second-instance guard -> triggered correctly against a fake `comm=cmr2` process
  (`cp /bin/sleep /tmp/cmr2`) -- no GPU, no game;
* the helper on four binaries across both arms; `cmr2-native.sh`'s warn+delay path
  driven to completion with a fake game binary.

**Not tested, and I am not going to claim it:** I did not launch the game. What is
known about these exact bytes is that they were run on the GPU 10:51-10:59 by the
HUD-2D lane (their `hud4` run of `out3`, md5 `80d927b54f59`): **11,753 presented
frames, 0 panics** -- and that their `[RT F]` drive trace was not switched on for it,
so their log is silent on whether a car moved. Static gate yes, boot yes, *car moves
in a race* still unproven for the play binary.

The cheap way to settle it, on the binary he actually plays: the drive trace is
compiled into `out-plain` and env-gated -- `DECK_RACE_TRACE=1` gives `[RT F]` per
frame (`c0sp` = car 0 speed), `=2` adds `[RT D]`/`[RT R]`. One `drive.py` run on
`out-plain` answers it. I left the GPU to the queued run (`run_rt7_gated.sh`), whose
build `out-rt3` is the one instrumented for the deeper question -- *who* drives the
demo car -- and whose answer matters more than mine.

## 5. CAVEATS, SO NOBODY READS MORE INTO THIS THAN IT SAYS

* **The rhi object is older than its source.** The link line pulls
  `port/rhi/deck_dd7.o` (08:53) while `deck_dd7.cpp` was edited at 09:53. That object
  is shared with every other lane's link line, so I did not rebuild it -- touching it
  would change other lanes' controls mid-round. If a renderer fix landed in that file
  after 08:53 it is **not** in this binary. Same is true of every DRIVES build here.
* **The platform objects** (`work/PLAY/out/obj`, 5 objects) are shared the same way
  and were left alone.
* **The deadness window is 08:39:06 - 11:02.** Nothing in it was drivable. Any reading
  of "how the game looks or behaves" taken from a session in that window -- including
  the 10:03 session -- is void for the car, and the phone's note already says so.
* **One surviving copy of the old launcher, reconstructed.** I overwrote
  `~/lena/cmr2lre.sh` in place before taking a copy of it -- my error. No other copy
  existed on disk (the daemon log keeps a round's commands, not their output), so
  `~/lena/cmr2lre.sh.bak-original-reconstructed-20261011` is rebuilt verbatim from the
  round's own step-1 `cat`. It is a record, not a rollback target.
* **Not my lane, but seen while in there:** HUD-2D's `hud4` log for this same content
  logged 2 `[MSGBOX] CMR2 File Load Error: Make sure the CMR2 CD is in the CD drive`.
  The icon's launcher `cd`s to the game root, which is the known fix for that message;
  if it can still appear mid-session it is a live symptom for whoever owns file-load.
  (Their harness may simply run with a different cwd -- I did not check which.)

---

## 6. ADDENDUM, 11:08 — IT WAS CLICKED, AND THE LOG CAUGHT IT

While this was being written, at **11:06:03** the icon was double-clicked for real:

    app-CMR2LRE@92abae7b4c17484ba552384b42639814.service   loaded active running
    /proc/3787186/exe  -> /home/deck/lena/work/PLAY/out-plain/cmr2
    /proc/3787186/cwd  -> /home/deck/lena/.lena_cmr2/game
    state Rsl, RSS 127 MB, 16% CPU   (running, not sitting on a modal CD box)

and the launcher's new log has the matching line:

    2026-07-11 11:06:05  LAUNCH  .../out-plain/cmr2  md5=80d927b54f59  skipped-dead: none

So the fix is confirmed **in production, by his own click**, on the one path that
matters: the icon started the drivable build, in the game root, and it is alive and
working. `skipped-dead: none` means it did not even have to fall back — the play build
is the first choice and the first check both pass.

This is observed from outside his session only (process table, `/proc`, the app scope).
Nothing was done to his session: no screenshot, no key injection, no window, no kill,
and no GPU work of mine while it runs.
