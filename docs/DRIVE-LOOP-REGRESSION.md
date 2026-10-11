# ROUND 3 — THE CAR COULD NOT BE DRIVEN, AND THE REASON WAS OURS

`work/DEMO-DRIVE-CRASH`, 2026-10-11 ~09:46-10:1x EEST. Task `DEMO-DRIVE-CRASH`,
round 3. Companion to `RUNS-AND-THE-ZERO.md` (round 2) and
`REPLAY-FILES-MEASURED.md`. Evidence: `out/rt5.log`, `out-rt/rt5.drive.out`,
`loopcheck.out`, `Race.cpp.bak-pre-drivebound-20261011-0946`.

---

## 0. THE ONE PARAGRAPH

The bound of the per-car driving loop in `Race_UpdatePlayerViewAndDrivenCars` was
never assigned, so the loop never ran one iteration, no car was ever given an
input, and the physics never stepped. **The port always had the two statements
that assign it. They were deleted at 08:39:06 by `patch_racetrace.py` — round 2's
own instrumentation — because they were its `str.replace` ANCHOR.** I restored
them, rebuilt, and re-ran the pure-idle attract case: the loop now iterates 3650
times in 220 s, the physics steps at ~24 Hz, and car 0 accelerates to speed
101958 and travels across the world. Miami's "she can't drive for shit" was
measured on builds from **before** 08:39, when the code was intact; everything
measured **after** 08:39 — including round 2's rt2/rt3 — was measured on a build
where nothing could be driven at all.

---

## 1. HOW THE TWO STATEMENTS GOT DELETED

`work/RACE/patch_racetrace.py`, as written:

```python
F_ANCHOR = """    Physics_UpdateRateHold();
    g_unk0x00538124 = Car_UpdateEngineNoteFalloff(&g_unk0x00537f60);
"""

F_BLOCK = """    /*LENA-RACETRACE*/
    if (LenaRaceTrace() >= 1) { ... }
/*LENA-RACETRACE-END*/
"""
```

and then a plain `text.replace(F_ANCHOR, F_BLOCK)`. The anchor is not a comment,
not a marker — **it is the game code itself**, and the block does not contain it,
so applying the patch deletes it. Two statements. No diff review, because the
diff *is* the tool's output and the tool says the change is safe
("Nothing is written to game memory. Nothing is reordered." — true, and beside
the point: something was *removed*).

The proof is a diff between two backups the tool itself left in the tree:

```
$ diff -u Race.cpp.bak-pre-racetrace-20261011-083906 \
          Race.cpp.bak-pre-drivebound-20261011-0946
@@ -5295,8 +5298,32 @@
     second = StageTiming_ConsumeDashRefreshLatch();
-    Physics_UpdateRateHold();
-    g_unk0x00538124 = Car_UpdateEngineNoteFalloff(&g_unk0x00537f60);
+    /*LENA-RACETRACE*/
+    if (LenaRaceTrace() >= 1) { ... the [RT F] printf ... }
+/*LENA-RACETRACE-END*/
     g_unk0x00537f0c[4] = 0;
```

`md5 ae4a118c0b8f0fe9c7c499d696ec98bb` (08:38:50) and `…98bb` (08:39:06) are
identical: the two backups are the same file, taken twice, immediately before the
patch. The file written at 08:39:07 is the first one without the statements.

The port has these statements in `upstream/CMR2Decomp/Race.cpp:5205`,
`decomp2/…:5227`, and in every tree backup from 2026-10-09 23:33 up to
08:39:06. **They were never missing. Round 2's §3 — "the port never assigns
`g_unk0x00538124`" — was true of the file it was reading and false of the port.**

---

## 2. WHY THE FIX IS CORRECT, BY CONSTRUCTION AND BY THE ORIGINAL

* `g_unk0x00538124` has exactly one writer in the whole port: the restored line.
  (`grep -rn g_unk0x00538124` → declaration, three trace reads, my comment, my
  assignment, the loop. Nothing else.) So `steps ≠ 0` cannot have any other cause.
* The original writes it once, at `0x41c5eb`, exactly where I put it —
  `call 0x42b790` (`Physics_UpdateRateHold`), `push 0x537f60` /
  `call 0x42c890` (`Car_UpdateEngineNoteFalloff`), `mov ds:0x538124,eax`,
  `mov ds:0x537f1c,ebp`, `jle`.
* **Round 2's target for this fix was wrong.** It said "in
  `Replay_LoadSelectedRun`". `Replay_LoadSelectedRun` is `0x41c510..0x41c594` and
  ends with `ret`; the tail belongs to the *next* function, `0x41c5a0`, which the
  port already carries as `Race_UpdatePlayerViewAndDrivenCars`. Putting it in
  `Replay_LoadSelectedRun` would have been both wrong and ineffective.
* The `jle` needs no separate statement: `for (x = 0; x < bound; x++)` with
  `bound <= 0` is the same control flow.
* The reconstruction is now textually identical to upstream apart from the trace
  block sitting above the two statements.

---

## 3. THE MEASUREMENT (rt5) — ALL PREDICTIONS STATED BEFORE THE RUN

`BIN=out-rt2/cmr2 RACE_TRACE=3 ./run_rt.sh rt5 220 "w220"`
binary md5 `d25d5ef3353b0a96a3bfe65f08279647`, 13356 presented frames,
8760 `[RT F]`, 0 panics, `ring0=12 ring1=3 mode2=14 tcp=3` before and after.

| prediction | what happened |
|---|---|
| `steps=` becomes non-zero | **yes** — 3507 frames `steps=1`, 51×`2`, 12×`3`, 1×`5`, 5189×`0` |
| `[RT P]` becomes non-zero | **no — still 0** (see §4; not the instrument's fault) |
| `c0sp` leaves 0 and `c0x/c0z` change | **yes** — speed up to 101958; x 28472962→45951805, z 11118819→78463 |
| `os/ot` stop being 65525/65547 | **yes** — os 2621000 / 74883 / 154176 / 163812, ot 1638 / 57354 / 27857 |

Two internal consistency checks that make this hard to be wrong about:

* `f24` (`g_unk0x00537f24`, incremented once per iteration of the outer loop) ends
  at **3650**, which is exactly `3507·1 + 51·2 + 12·3 + 1·5`. The loop's own
  counter agrees with the loop's bound.
* `steps=1` on 40 % of frames at ~60 fps = **≈24 Hz**. That is the fixed rate the
  original was designed at (the attract replays are recorded at 25 fps), so the
  restored function is producing a *plausible* simulation rate, not a runaway.

Both scale pairs now respond: `os/ot` are `StageObject_SetPhysicsScaleAndReciprocal`
(StageObjects.cpp 0x00466630), which is called *only* from the restored
`Physics_UpdateRateHold`. The old constant `65525/65547` was the stage's
`Physics_SetScale(0x190000)` value, which is what round 2 misread as a mismatch —
it is a match: `FixMul(0xa3d,0x190000) = 1638400·2621>>16 = 65525`,
`FixDiv(0x10000,65525) = 65547`. (`Physics_SetScale` is the *other* pair,
Car.cpp 0x00433840.) Checkpoint item 3 closed, with the sign the other way round.

---

## 4. `[RT P]` = 0 — REAL, BUT NARROW. AND `[RT A]` IS ON THE WRONG FUNCTION

`Replay_DecodeCarControls` (the `[RT P]` hook) has exactly one caller:
`Replay_PlayStreamFrame`, StageObjects.cpp:14313, **inside
`if (p->pLaneSamples[p->lane] != 0)`**. So 0 means that branch never ran — it does
not prove the replay is dead, and it must not be quoted as if it did.

What it does say is that the motion in rt5 arrived by the other path:
`case 8 → CarInput_UpdateRaceOrderSlot → StageObject_DriveCPUOrderSlot →
AI_UpdateRouteDrivingControls`. Round 2's header claim that the attract car is
driven by decoding the recorded run is therefore **not** what is happening in
these runs, at least not through that branch. That reframes the phone's candidates
towards 2 and 3, and away from the replay decoder.

And a straight instrument bug, worth fixing before the next run: **`[RT A]` is
hooked to `AI_UpdateAttractDrivingControls` (StageObjects.cpp:15391), which runs
only in switch cases 9/10 with flag26 set.** rt5 was `state=8` on 8506 of 8760
frames. So `[RT A]` printed nothing for a reason that has nothing to do with the
driver — the driver that ran is `AI_UpdateRouteDrivingControls`
(StageObjects.cpp:13923), reached from `StageObject_DriveCPUOrderSlot`
(StageObjects.cpp:14068). **The next round should move that hook.**

---

## 5. WHAT THE CAR ACTUALLY DOES NOW — THE BRIEF'S QUESTION, FIRST LOOK

Straight off `[RT F]`, car 0, in one 220 s attract run:

| f | what car 0 is doing |
|---|---|
| 2763 | first movement (the demo starts) |
| 2763–4349 | **driving fast**: speed 60 000–101 958 (0.9–1.5 world units/frame) |
| 4349–6549 | **not going anywhere**: 0.08 world units of net travel in ≈2200 frames (≈36 s), x/z wobbling inside ±0.02 units, `c0sp` pinned at 6000–7500 (≈7 % of its driving speed) |
| ≈6749 | `state=9`, the demo ends |
| 8599 | a **second** demo starts, at a completely different place (x 3.1 M → 52.4 M in one frame) |
| 8599–13354 | drives again, with many short 5–55-frame stalls |

So she is not crash→restart-crash→restart in a tight loop. She drives out and then
**grinds in place with the throttle on for half a minute**, and after the reset the
next demo stutters in the same way. From a sofa, that is exactly "keeps crashing
over and over".

**What this does NOT settle:** whether the 36 s of no progress is scenery (a car
against a wall, wheels spinning) or an AI with the throttle on and nowhere to go
(a route it cannot follow). `[RT F]` cannot tell those apart — that is a question
for the driver, which is why §4's hook matters. Stated as an open question, not
as a finding.

---

## 6. WHICH BINARIES ARE AFFECTED (`loopcheck.sh`, `loopcheck.out`)

`loopcheck.sh` answers it from the code (`does Race_UpdatePlayerViewAndDrivenCars
call Physics_UpdateRateHold?`), not from timestamps:

```
DEAD   2026-10-11 08:49:00  RACE/out-rt/cmr2                  <- rt2, rt3, card3's pin
DEAD   2026-10-11 08:53:59  PLAY/out-plain/cmr2               <- THE ONE HE PLAYS
DEAD   2026-10-11 09:01:54  MENU-CAR-FLATTENED/out-md/cmr2
DEAD   2026-10-11 09:13:24  MENU-CAR-FLATTENED/out-md2/cmr2    (md_sub4 in flight)
DRIVES everything built 2026-10-10 and everything before 08:39 on 2026-10-11
       (deckbuild/out, deckbuild/outres, FIXBG, GAME2 r5b/r7, INPUTGEN×2, P3×3,
        PADTUNE×2, PLAY/out, RACE/out-ctl, out-death, out-geo, out-owner,
        out-race, out-tex, out-texreq, out-trace, S2)
```

The split is exactly on 08:39:07, which is the timestamp of the patch's write.
Nothing before it is affected; nothing after it can drive.

**Nobody's measurement is "wrong" for having been taken — but any result that
assumed a car could be driven, a car could be steered, or the physics could step,
on a binary linked after 08:39:07, is measuring a frozen world.** That includes
round 2's rt2/rt3 (which is how the zero was found) and any race-screen A/B taken
this morning after 08:39.

Not rebuilt, on purpose: `PLAY/out-plain/cmr2` is another workstream's artifact
and several scripts gate on its md5. The fix is in the tree, so the next build of
it picks it up; that decision belongs to whoever owns it.

---

## 7. WHAT I DID AND DID NOT TOUCH

* **Wrote:** `Race.cpp` (the two statements, `/*LENA-DRIVEBOUND*/`), with backups
  at `work/DEMO-DRIVE-CRASH/Race.cpp.bak-pre-drivebound-20261011-0946` and beside
  the original. New dirs `obj-rt2/`, `out-rt2/`, `obj-ctl/`, `out-ctl/`, all
  inside `~/lena/work`.
  Note: `~/.lena_cmr2/repo/CMR2Decomp/Race.cpp` is the **same inode** as
  `~/.lena_cmr2/port/tree/CMR2Decomp/Race.cpp`, so the edit shows in both. That is
  the tree's existing arrangement, not something I set up.
* **Did not touch:** `out-rt/cmr2` or its md5 pin; `PLAY/out-plain`; any peer's
  log, frames, binary or save; Miami's session, data or playtime. `gpu-guard.sh`
  was honoured throughout — one run stood down when a peer's game appeared, one
  stood down when his own `out-plain` was alive, and no process was ever killed by
  name.
* **Kernel ledger unmoved** across the only run: `ring0=12 ring1=3 mode2=14 tcp=3`.
* Two runs made, both with the GPU free: `rt4` (**void** — a peer's game appeared
  11 s in and the harness yielded at 675 frames, before the race view; 0 `[RT F]`)
  and `rt5` (the real one). `rt4` is kept only as the record of a yielded run.

## 8. WHAT I DID NOT DO

* No fixed-point work (phone's candidate 1) beyond noting that
  `Physics_UpdateRateHold` — now live for the first time — contains one of the
  five `fistp`-vs-truncate sites in its `(int)(rate * 65536.0f)`; that is a ≤1 LSB
  offset recomputed per frame, not an accumulating drift, so at *this* call site
  it does not match the "drifts a fraction per frame" shape the phone described.
* No frame-timing work (candidate 2) and no stage/route-data work (candidate 3) —
  candidate 3 is where §5's open question points, and it needs the re-hooked
  driver trace first.
* The `[RT A]` re-hook and its run: **the next round's item.**
