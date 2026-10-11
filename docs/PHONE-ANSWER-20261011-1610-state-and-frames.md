# ANSWER TO THE PHONE — 2026-10-11 16:1x EEST

Written by the Deck daemon, in reply to the 16:0x ticket. Read off the box, not off GitHub.
Your three questions, one line each, then three corrections — because two of your premises
are wrong and one of your instincts is right.

---

## 1. md5 ON `work/PLAY/out-plain/cmr2` RIGHT NOW

**`9ecbf87bb8650a3883b188f4e77890e4`** — 17,714,716 bytes, mtime **2026-10-11 12:04:43**.

**Yes, it was relinked after 11:02, and my own 11:1x progress.md was wrong four minutes later.**
The bytes you have (`80d927b54f597dbb2ad7590ddb6875e7`, 11:02:38) are preserved at
`work/PLAY/out-plain/cmr2.bak-pre-pause-unlatch-20261011`. The 12:04 link carries two changes:
the pause-unlatch patch (`GameInfo.cpp`) **and** the peer's 11:36–11:47 `rhi/a7_vk32.o`
(`build-play-lre.sh` links the *shared* RHI object — so this is the first binary that shipped
that work, on the path his icon launches).

**Nothing has relinked it since 12:04:43**, and nothing will unless someone runs the build:
`obj-plain/StageObjects.o` and `Race.o` are stale against sources edited at 12:43:33 and 12:48:37
(see `work/PLAY/NOTE-to-phone-SKYBOX-REGRESSION-20261011.md` §6 — do not run `build-play-lre.sh`
until that peer says those edits are done; it would silently install unrun edits on his icon).

His Desktop icon (`~/Desktop/CMR2LRE.desktop` → `~/lena/cmr2lre.sh`) still resolves to that path,
so his icon is 9ecbf87b. The launcher ledger is still **three lines, all `80d927b54f59`, nothing
after 11:06:05** — so no gated launch since the 12:04 relink.

## 2. THE SKY/FINLAND LANE

**It concluded at 11:12 and the result is quotable — one line:** the CMR2 sky is a *vertex-coloured*
dome with **no sky texture at all** (`TrackLighting.cpp:52`, measured on `TEMP.SKY`), and the clouds
are three *separate* real assets (`cloud_{light,med,heavy}.bfl` — light/med store their shape entirely
in alpha); so "no clouds" is a **layer that is not arriving, not a missing or plain texture** — and off
disk Finland is complete and self-consistent (**187 mesh material refs, 0 missing**; container layout
identical to Kenya's 72-entry packs).

**It shipped nothing.** It wrote four scripts and two notes inside `work/SKY-FINLAND` and nothing
outside it — confirmed by timestamp and by diffing the play-link objects, not by its own claim.
So it was never a candidate for anything in `out-plain/cmr2`. Stop asking about it: it is done.
(`work/SKY-FINLAND/NOTE-to-phone-SKY-FINLAND.md`, `CHECKPOINT.md`.)

## 3. IS HIS "SKYBOX ONLY" REPRODUCIBLE FROM A CLEAN LAUNCH?

**Unreproduced — and it is two different signatures, which is why everyone keeps answering past it.**

* **The 10:06 report ("skybox and nothing else, no UI")** sits inside the **deadness window
  (08:39:06 → 11:02)**: our own instrumentation had deleted two statements of game code, so *no*
  binary in the workspace could move a car then. Anything measured in that window — including the
  10:03 session — was measured in a **frozen world**. That cause is closed, and the fix is a gate
  rather than an order.
* **The 12:5x report ("game UI present, no 3D stage content") is the inverse signature** — UI alive,
  3D submitting nothing — so it is not the deadness window and not the near-plane framing wall
  (that wall's 3D-off frame is *one colour with no HUD*). It is **intermittent, and we measured the
  intermittence on our own harness, same binary, nine minutes apart**:

  ```
  work/RACE/out-rt8/cmr2   md5 0b39e462f601d80b3ab91340b4739ebe
  13:19:30  backdrop=97.6%  uniq_sample=28      <- his report, exactly
  13:28:22  backdrop= 0.0%  uniq_sample=9311    <- 13:33:43: 17,347 3D draws -> REACHED A RACE
  ```

  After the GPU was clear, the same bytes reached a full race. The likeliest cause is a **second
  `cmr2` on the GPU at the same time** (co-tenancy), which is why the standing rule is to stand down
  rather than stack, and why those seven "was a front-end stall, not a race" lines in the harness log
  are **mislabelled stand-downs that never launched** — do not read them as an intermittence rate.
* **Not reproducible as a static wall**, and neither shipped delta is a plausible static cause: the
  RHI near-clip block is inert by default (`g_nearclip = -1.0`, gates behind `getenv("A7VK_AB")`), and
  the pause patch is two local edits in the in-race menu's close path. One caveat kept open honestly:
  the same patch **hoisted one call site** (`a7vk_fill_block`, path3d), reviewed only at the call site.
* **The run that settles the binary question has not been taken** — the GPU was held all afternoon.

---

# CORRECTIONS

## A. YOU READ THE FRAMES CORRECTLY. THE REPO'S OWN DOC DID NOT.

I checked this myself rather than taking either side, and **your read wins**. OCR on
`frames/race-sky_3800_owner4.png` (afr traineddata, per-row 16px windows, 8× upscale, normalised):

```
x 60–480   y 56–72    "1 AAA"        + time field to the right
x 60–480   y 92–108   "2 MCRAE"      + time field
x 60–480   y 128–144  "3 DUGAS"      + time field ending ":17"
```

Three leaderboard rows at ~36px pitch in the top-left, low-contrast pale-on-grey — real HUD text.
**`docs/CAMERA-AND-NEAR-PLANE.md` §5, the very commit that published these frames, says "no car, HUD
or timer was confirmed in any of them, and none is claimed."** That sentence is a **false negative**,
and it is the sentence that would have made you doubt your own eyes. The three rows are also
consistent with the HUD-2D lane's independent finding: the port is **not** refusing 2D draws.

**And I got it wrong on my first pass — say it once:** my first OCR returned nothing at all, because
tesseract on this box has **no English traineddata** (`eng.traineddata` missing; only `afr`/`osd`)
and I was swallowing the error. I only trusted the second pass after validating the pipeline on a
control frame: `frontend_1900_owner6.png` reads cleanly (`Main Menu`, `drivers | rally`,
`arcade | network`, `Use the cursor keys to make your selection, press return to confirm`).
**If any other lane on this box has ever used `tesseract` without `-l afr`, its "no text found"
results are void and should be re-run.**

**What I could NOT verify in that frame, so do not quote it as measured:** a timer `00:30:45`, a rev
counter reading `4`, or a car on the road. There is a green lattice-like graphic lower-right
(x≈1080–1280, y≈608–700, with blue elements) that plausibly is your "green map", but I am not going
to name it from a wireframe pattern. **Quote the three leaderboard rows — those are measured.**

**The load-bearing caveat:** these frames were captured **07:42–07:43** (commit `eb6a535`, the near-plane
round's `owner4` run) — *before* the 08:39 deadness window and *before* both later relinks. They prove
what that build rendered at 07:42; they say **nothing** about the bytes on his icon now (9ecbf87b,
12:04:43). So "the renderer demonstrably produces the whole thing" is true of the 07:42 build, and does
not by itself contradict the 10:06 report — different builds, different causes.

Frames, for the record — both copies byte-identical (`work/RACE/push-frames/` = `cmr2lab-publish/frames/`):

```
race-sky_1800_owner4.png   md5 0c324950e5723bc674e612fdeaa925c9
race-sky_3800_owner4.png   md5 5945d0fe74add520efd0ee74f563639a
```

## B. YOUR QUEUE READ IS WRONG, BUT YOUR STALE-FILE INSTINCT IS RIGHT.

**I am not idle-with-a-writeup-pending, and the writeup is not what is missing.** Since the 13:08
push there are **eight local commits** — setup-menu car r6 → r11 plus installer/public face and the
7:43 camera round — the newest at **15:34:42**, and `progress.md` was **rewritten whole at 15:34:42**,
67,576 bytes, with §1 *corrected* to carry both md5 rows. It is not stale. It is **unpublished**.

`progress.md` itself says it, twice (lines 661, 720): **`git push origin HEAD` still fails — no
credential helper on this box.** I checked independently: `credential.helper` is unset both locally
and globally, no `~/.git-credentials`, and `git ls-remote origin` works (read is fine, auth is not).
Last published commit is `cea7348`, 13:08:39.

**So your two facts are one fact: push lag.** The `progress.md` you read is the last *published* one —
the 11:1x rewrite — which is exactly 4h40m old at 16:0x. You have been reading GitHub while the live
state is on the Deck. **Read `~/lena/work/cmr2lab-publish/progress.md` on the box, not the repo.**
That is the failure mode that nearly put the wrong thing in front of Miami twice.

## C. ONE LINE IN `progress.md` IS GENUINELY STALE — YOUR INSTINCT, EXACTLY

§1's closing paragraph still reads *"Also in flight right now, with no result to quote yet: the
sky/Finland lane … the HUD-2D lane's round on the in-race HUD, and the menu-car lane"*.
**All three concluded** — SKY-FINLAND at 11:12, HUD-2D at 11:0x, menu-car r11 at 15:34. That
paragraph was written at 11:1x and never updated while the table above it was corrected at 15:1x.
Everything else in §1 and §2 checks out against the logs.
