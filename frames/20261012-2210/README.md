# FRAMES — 2026-10-12 22:10 — "worse than before" needs frames on both sides

Ticket: `CAPTURE-FRAMES-NOW-20261012-2210` (Lena, phone). Miami looked at the current
build and said *"we're in a worse state than before, graphics rendering needs serious
work."* He played the 09:27 build this morning and called it *"amazing"* (stretched +
flickering textures, but a real stage with real surfaces). So the claim is a regression
and it needs pictures on both sides.

**These are 1280×800 PNG, full size, no downscaling, no crop. PPM → PNG with
`work/RACE/ppm2png.py`, which decodes its own output back and refuses to write a file
whose pixels do not round-trip.**

`MANIFEST.txt` sits beside this file: md5, size, name for every image.

---

## THE THREE BINARIES, OR NOTHING BELOW MAKES SENSE

| tag | md5 | built | what it is |
|---|---|---|---|
| **B** | `4c2998f345c9c348f9287cabb443f252` | 09:27 | **the build he called "amazing"** — installed 09:27, launched from his Desktop icon all morning. Golden copy kept at `work/PLAY/gold/cmr2-20261012-4c2998f345c9`. |
| **A** | `94ed1359c405a31df38e64e197269a78` | 11:03 | tonight's **tree baseline** (pre-LRE), re-run at 22:05 / 22:10 / 22:14 by the FIXIT/FIXBOTH lane because it reaches a race. It is **not** the binary he was on. |
| **HIS** | `3afeedbe77e537b483443d75b6dce176` | 20:19 | **what he was actually on at 21:51 and 21:53.** SIGSEGV in `Sector_NearestCornerHeight`, on stage entry, twice. |

### There are ZERO frames of HIS binary, and here is why

He launched from the Desktop icon. The icon does not set `A7VK_SNAP`, so nothing was
ever written to disk from those two sessions — the crash leaves a coredump and a log
line, not a picture. And the crash is on **stage entry**, i.e. after the frontend and
before the first stage frame, so the window in which his build could be photographed is
the frontend and the stage-load moment only.

**So the "last frame before death" he asked for does not exist on this disk.** I did not
manufacture one and I did not run the GPU to make one — see *why no run* at the bottom.
`grab-his-build.sh` in this directory is ready to take exactly those three frames
(frontend, stage-load, last frame before death) in one ~6-minute run, and it refuses to
start if the card is not free.

---

## WHAT IS ACTUALLY COMPARABLE: ONE FRAME, AND IT IS THE FRONTEND

The 22:05 run (`fx-b`, binary B) and the 22:14 run (`fx-d`, binary A) were both the
attract route, and both were snapped at the same frame numbers. Frame 2600 is the
main menu on both:

```
B-0927-mainmenu-f2600.png   vs   A-tonight-mainmenu-f2600.png
  differing pixels :      480 of 1,024,000   (0.047 %)
  max channel delta:       71
  mean abs delta   :        0.01
```

**The 480 pixels are the frame counter in the corner — `Time 00:00.28`.** Everything
else in the two images is identical byte for byte. The menu, its flat sage-grey
backdrop, the spiral of letters, the menu bar are the same picture on the build he
called amazing and on tonight's build.

**My read of that number:** whatever "worse than before" is, it is not the frontend
menu. And since `3afeedbe77e5` dies *inside* stage load, the frontend is the only part of
the current build he can have seen at length tonight. (B and A are not the same binary,
so this is evidence about the frontend draw path being unchanged, not proof about
`3afeedbe77e5`'s own menu — that frame still needs taking.)

**After frame 2600 the two runs diverge** (different routes, different flags, a
wall-clock-driven attract timer) and the pairs stop being comparable — `fx-b` at 4000 and
`fx-d` at 4000 are not the same moment of the same screen. Every image below frame 2900
is therefore **a single frame from one run, with the provenance given**, not half of a
controlled pair. `diffpair.py` in `work/FRAMES-PUB-20261012-2210/` prints the whole
table if you want it.

---

## THE IMAGES

### B — the 09:27 build, the one he called amazing

| file | from | what is in it |
|---|---|---|
| `B-0927-mainmenu-f2600.png` | `fx-b.ppm.2600` (200 s attract run, 22:05, `RACE/out/fx-b.log`) | Main Menu: `drivers \| rally \| arcade \| network \| options \| credits \| quit`, "Main Menu" top-left, "Time 00:00.28" top-right, the spiral of letters around a white dot. **Flat sage-grey background — no 3D scene behind the menu.** |
| `B-0927-mainmenu-plus-f2900.png` | `fx-b.ppm.2900` | frame 2900, same run, still the frontend |
| `B-0927-demo-f3000.png` | `v3.ppm.3000`, byte-identical to `PLAYABLE-20261012/png/installed-build.3000.png` | attract demo, high chase camera, real Kenya-style stage: dirt road with ruts, savanna grass, billboard trees, dust plume, the **car body complete** with livery; white spiky stretched polygons on the ground, hard white sky |
| `B-0927-demo-f3500.png` | `v3.ppm.3500` | same demo, car mid-slide, S-curve road — the frame that closest matches his "a real stage with real surfaces" |
| `B-0927-demo-f4000.png` | `v3.ppm.4000` | same demo, car into the distance |
| `B-0927-raceentry-f5000.png` | `fx-b.ppm.5000` | **the transition**: on track, chase camera, and the car renders as roof + two mirrors + two rear wheels with **the whole body absent** — you see grass through where the car should be. Road blown to near-white, white sky |
| `B-0927-race-f5500.png` | `fx-b.ppm.5500` | in-race, car still missing its middle, road covered in smeared stretched highlights |

`v3` = the installed binary with the fixes at their defaults (mips **on**, near clip
**on**), so these three demo frames are the real 09:27 build as he played it. Provenance
checked, not assumed: all three are 0-differing-pixels against `v3.ppm.{3000,3500,4000}`
and 99.86 % different from the `v2` (`A7VK_NOMIPS=1`) arm.

### A — tonight's tree build, 22:05–22:17

| file | from | what is in it |
|---|---|---|
| `A-tonight-mainmenu-f2600.png` | `fx-d.ppm.2600` (22:14, `RACE/out/fx-d.log`) | Main Menu, as above — the other half of the 480-pixel comparison |
| `A-tonight-demo-f3000.png` | `CAND.ppm.3000` (22:10, `RACE/out/fx-race.log`) | attract demo, top-down camera; car body complete; large white vein-like geometry over grass and tree in the bottom-right corner |
| `A-tonight-setupmenu-f4000.png` | `CAND.ppm.4000` | the **setup screen**: `Information \| Set Up \| Repair \| Race \| Quit`, `Player 1 \| aaa`, `Press Return to race`. Flat grey, **no 3D car, no stage thumbnail behind it** |
| `A-tonight-raceentry-f5000.png` | `CAND.ppm.5000` | in-race with full HUD (leaderboard, clock, tacho, `KMH 111`); car is a **shattered mass of black shards**, one wheel visible; white flat polygons on the grass, blown-out trees, thin vertical seam right of centre |
| `A-tonight-race-f6000.png` | `CAND.ppm.6000` | in-race, HUD live (01:17.06 / KMH 125); terrain large areas **blank white**, yellow-green-white splotches across the tree line, hard horizontal seam with a dark band under it |
| `A-tonight-race-f5000-fxd.png` | `fx-d.ppm.5000` | second sample, different run: car readable only as a dark slab + canopy wedge, two wheels, no body sides; same blown-out road and white sky |

---

## TWO THINGS I SAW IN MORE THAN ONE IMAGE, AND WILL NOT CALL

1. **A hard horizontal seam with a duplicated dark band under it** — bottom quarter of the
   frame, appears on `B-0927-raceentry-f5000`, `B-0927-race-f5500`,
   `A-tonight-race-f5000-fxd` and `B-0927-demo-f4000`. It appears across *different
   builds and different runs*, which is what you would expect from the **capture path**
   (a snapshot read from a swapchain buffer while it is being written) at least as much
   as from the renderer. Nobody should read it as a game defect without a second,
   independent capture method.
2. **The car body missing at race entry** on the 09:27 build (`f5000`) and on tonight's
   build (`fx-d f5000`) — same symptom on both sides. **This is not new tonight**, and if
   "worse than before" was about the car, this pair is the counter-evidence, not the
   support.

---

## WHY THERE WAS NO GPU RUN THIS ROUND

The rule on this machine is: **no GPU runs while he is on the machine.** At 22:20 there
was no `cmr2` alive and no `drive.py` running, but he had been on the Deck 25 minutes
earlier (played 21:51, crashed, 21:53, crashed), the logind sessions report
`IdleHint=no`, and the FIXIT/FIXBOTH lane owns the card tonight and was mid-sequence
(their last run ended 22:17). One more `cmr2` started beside theirs is the thing that
wedged the display this morning. So this round read the disk instead of taking the GPU,
which is also what the ticket said to do first.

`grab-his-build.sh` (this directory) is the run that fills the gap. It uses
`RACE/gpu-guard.sh`, **stands down by itself if a game is alive that the harness did not
start** (that includes his), injects **no keys** (keys go in through machine-wide
`/dev/uinput` and would land in his session), and runs the golden copy of his crashing
binary from `work/PLAY/gold/` so it never `mv`s anything over the binary the launcher
points at.
