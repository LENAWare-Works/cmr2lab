# FRAMES — start here

Miami: every frame published so far, in one place, with exact filenames. All are
**1280×800 PNG, full size, no crop, no downscale**. Open them directly — nothing here
needs describing by me, and nothing is a mock-up.

Ticket: `CAPTURE-FRAMES-NOW-20261012-2210`.

---

## OPEN THESE FOUR FIRST

If you only look at four, look at these — they are the regression question, both sides:

| # | file | what you are looking at |
|---|---|---|
| 1 | `20261012-2210/B-0927-demo-f3500.png` | **the 09:27 build** — the one you called *"amazing"*. Attract demo, car mid-slide on an S-curve. This is the closest frame to "a real stage with real surfaces". |
| 2 | `20261012-2210/A-tonight-race-f6000.png` | **tonight's build**, in-race, HUD live. |
| 3 | `20261012-2300/miami-session-225944.png` | **your own session**, 22:59:44 — you, in a stage, playing. Not a harness. |
| 4 | `20261012-2210/B-0927-mainmenu-f2600.png` | the frontend on the 09:27 build. Its pair is `A-tonight-mainmenu-f2600.png` — see below. |

---

## THE ONE CONTROLLED COMPARISON (and its answer)

`B-0927-mainmenu-f2600.png` vs `A-tonight-mainmenu-f2600.png` — same screen, same frame
number, two builds:

```
differing pixels :      480 of 1,024,000   (0.047 %)
max channel delta:       71
mean abs delta   :        0.01
```

Those 480 pixels are **the frame counter**: `Time 00:00.28`. The other 480 are its
shadow. Everything else is identical.

**So the frontend is not the regression.** Whatever "worse than before" is, it is not
the menu. Verified by eye, twice: I looked at both files and they are the same picture —
same flat sage-grey backdrop, same `drivers | rally | arcade | network | options |
credits | quit` bar with `rally` lit, same spiral of letters.

**After frame 2600 the two runs diverge** (different route, different flags, a
wall-clock attract timer), so nothing below frame 2900 is a controlled pair. Those are
single frames with provenance given, not halves of an A/B.

---

## WHAT THE FRAMES SHOW, AND WHAT THEY REFUSE TO SHOW

**The stage defects are on BOTH sides.** I looked at the two stage frames myself:

- `B-0927-race-f5500.png` (the build you called amazing): long white horizontal smears
  across the road, textures streaked and stretched, the car reading as **a flat dark
  shape with torn geometry**, and a dark forested band across the lower foreground.
- `A-tonight-race-f6000.png` (tonight): long white horizontal smears on the road, the
  tree line torn white-and-yellow, missing geometry below the road edge, the car as a
  **flat dark mass**.

**That is the same symptom list on both sides.** The car body missing at race entry
(`B-0927-raceentry-f5000.png` vs `A-tonight-race-f5000-fxd.png`) — where you see grass
through where the car should be — is also on both sides. If "worse than before" was
about the car, this pair is counter-evidence, not support.

**The hard horizontal seam with a duplicated dark band under it is NOT called a game
defect here.** It appears on different builds, different runs, and — as of tonight — it
is visible in frames from *his own* session too. That is what a capture path reading a
swapchain buffer mid-write looks like, at least as much as any renderer bug. It needs a
second, independent capture method before anyone blames the renderer.

**`tree-fixed-f2600.png` is a MAIN MENU, not a stage.** Checked by eye. It proves the
tree build reached frame 2600 (586,844 draws in) without the record-map crash — it does
**not** show a stage rendering. Do not read it as "the crash is fixed on screen".

---

## WHAT DOES NOT EXIST, AND WHY NOT

**There are no frames of the binary you were actually on** (`3afeedbe77e5`, built 20:19).
You launched from the Desktop icon, the icon does not set `A7VK_SNAP`, so your two
sessions (21:51, 21:53) wrote a coredump and a log line and no picture. That binary
**SIGSEGVs on stage entry** — i.e. after the frontend and before the first stage frame —
so the only moments it could ever have been photographed are the frontend and the
stage-load instant.

**The "last frame before death" you asked for does not exist on this disk.** I did not
manufacture one and I did not take the GPU to make one. `20261012-2210/grab-his-build.sh`
is the run that fills exactly that gap — frontend, stage-load, last frame before death,
one ~6-minute run, it refuses to start if the card is not free, injects no keys, and runs
the golden copy from `work/PLAY/gold/`.

**Why no GPU run in this round:** the rule is no GPU runs while you are on the machine,
and the other lane (`ALIGN2218` / `FIXBOTH`) owned the card on and off all evening. At
23:12 this round, `drive.py` was actively running `out/cmr2` — so the newest frames in
`~/lena/eyes/` are **that lane's run, not yours**, and they are deliberately not published
here as if they were your session.

---

## EVERY FILE, FULL LIST

### `20261012-2210/` — both sides of the regression claim
`MANIFEST.txt` has md5 + size; all 12 files verify.

**B = the 09:27 build, the one you called amazing**
- `B-0927-mainmenu-f2600.png` — Main Menu (half of the controlled pair)
- `B-0927-mainmenu-plus-f2900.png` — still the Main Menu at 2900
- `B-0927-demo-f3000.png` — attract demo, real stage, car body complete with livery
- `B-0927-demo-f3500.png` — same demo, car mid-slide, S-curve ← closest to "amazing"
- `B-0927-demo-f4000.png` — same demo, car into the distance
- `B-0927-raceentry-f5000.png` — car body **absent**: roof, mirrors, rear wheels only
- `B-0927-race-f5500.png` — in-race, car middle still missing, road smeared

**A = tonight's tree build (94ed1359c405, 11:03)**
- `A-tonight-mainmenu-f2600.png` — Main Menu (other half of the pair)
- `A-tonight-demo-f3000.png` — attract demo, top-down camera, white vein geometry
- `A-tonight-setupmenu-f4000.png` — the setup screen: `Information | Set Up | Repair | Race | Quit`
- `A-tonight-raceentry-f5000.png` — in-race, car a shattered mass of black shards
- `A-tonight-race-f6000.png` — in-race, HUD live, terrain large areas blank white
- `A-tonight-race-f5000-fxd.png` — second sample, different run, car reads as dark slab

### `20261012-2300/` — the crash in the tree, and your own session
- `tree-fixed-f2600.png` — **Main Menu** of a build from the fixed tree. Past the
  record-map crash; not a stage. See the caveat above.
- `miami-session-225134.png` — **your session**, 22:51:34, in a stage
- `miami-session-225944.png` — **your session**, 22:59:44, still in a stage, process
  alive ~14 minutes on `94ed1359c405` with no fatal signal

Both of your session frames read **`KMH 000`**. That may be you parked, paused, or on a
start line — a still cannot tell. Flagged, not interpreted.

If you would rather your own session frames were not in a public repo, say so and this
directory gets deleted; nothing else refers to them.

---

## HOW THIS WAS TAKEN

Nothing here was rendered for the camera. Every frame is either a snapshot from a harness
run (`A7VK_SNAP`) or a `spectacle` capture of the screen from `~/lena/lena-eyes.sh`.
PPM → PNG with `work/RACE/ppm2png.py`, which decodes its own output back and refuses to
write a file whose pixels do not round-trip. Full size throughout.

**Disk hygiene:** `~/lena/work/ROUND-DISCIPLINE.md` applies. `cmr2lab-publish/frames` is
published output and is never swept or deduped.
