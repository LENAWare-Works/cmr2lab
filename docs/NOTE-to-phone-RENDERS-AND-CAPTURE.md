# RENDERS AND CAPTURE — the shopfront answer (2026-10-11 13:1x EEST)

CAME FROM: lena-on-the-phone, 2026-10-11 12:20 EEST — Miami's words, after he read the
README: *"possibly could use some more renders from the game and if any recorded my
gameplay for graphics display purposes."*

**THE LINE YOU ASKED FOR, now measured four ways: I can take in-game STILLS cheaply and
honestly, and I cannot produce a watchable recording — the capture that exists eats ~0.5 s
of the frame it lands on.** Details and numbers below; every one of them came off this box
in the last 20 minutes.

Binary under test throughout: `work/PLAY/out-plain/cmr2`, md5
`9ecbf87bb8650a3883b188f4e77890e4` (passes `cmr2_drives`), game root as cwd,
one `Enter` at t=12–14 s, stage up by ~t=50 s.

---

## 1. REAL IN-GAME STILLS: TWO PATHS, BOTH VERIFIED

### 1a. The compositor — RECOMMENDED, and it was not known to work here before today

`spectacle -b -n -f -o shot.png` during the stage, two runs:

| moment | file | bytes |
|---|---|---|
| t≈60 s | `docs/capture-20261011/ingame-stage_20261011-1306_compositor.png` | 2,105,881 |
| t≈72 s | `docs/capture-20261011/ingame-stage_20261011-1307_compositor.png` | 2,012,458 |

**It is the game's own pixels, not a wallpaper.** Checked against the renderer's own
capture of the same moment, channel statistics over the frame:

| | renderer (`A7VK_SNAP`, asked at t=70) | compositor (`spectacle`, t≈72) |
|---|---|---|
| mean luma | 78.8 | 78.9 |
| near-white (all three channels > 235) | 1.7% | 1.8% |
| warm (R ≥ G+16) | 81.9% | 80.4% |
| distinct 4-bit colours | 343 | 325 |

Two independent paths, on the same scene two seconds apart, agreeing to within 2% on
every statistic: that is agreement about the scene. **And it costs the game nothing**: the compositor path does not touch the renderer,
so the game keeps its 57 fps while a still is taken. (`run-play.sh`'s note that "a WM grab
returns all black" is about gamescope, and it is not true in desktop mode.)

### 1b. The renderer's own swapchain — exact, but it stops the world for half a second

`A7VK_SNAP` (the RHI's `a7_capture()`: re-record the current batch list offscreen, read it
back off the GPU). 75 of 100 requested frames in one run, frames 300 → 1188, each a P6 PPM
1280×800 = 3,072,016 bytes. This is the one to use when the question is *what the renderer
drew this exact frame*; see §3 for its price.

## 2. A WATCHABLE RECORDING: NO — AND HERE IS THE MEASUREMENT THAT SETTLES IT

Two runs, same sequence, same stage window:

| run | what was asked of the renderer | what the game presented |
|---|---|---|
| control (13:05) | **3 captures in the whole run** | 571 frames in 10.0 s = **57.10 fps**, then 572 in 10.0 s = **57.20 fps** |
| capture (13:01) | one capture per present (triggered at 8 Hz) | 48 frames in 26 s = **1.85 fps** |

Same phase of the same stage: **57.2 fps with the renderer left alone, 1.85 fps with a
capture landing on every frame.** So the cost is the capture, not the game — and it is
about half a second per captured frame, on a scene of ~200,000 draws / ~900,000 triangles.

The consequence for a clip, stated plainly:

```
captures: frames 2710, 2712, 2714 … 2804      (48 files)
that is 94 presents of game time = 1.65 s at 57 fps
it took 26 s of wall clock to ask for them
=> "recorded gameplay" today is a 1.65-second BURST, or a slideshow at 1.9 fps.
   There is no version of this that is a trailer.
```

Assembled, true speed, in `docs/capture-20261011/`:
`cmr2-stage-burst_20261011-frames2710-2804.mp4` — 1280×800, 48 frames, 28.5 fps,
**1.68 s**, 5.7 MB, h264. Caption it as a burst or do not use it.

**There is no live-video path on this machine either** — checked, not assumed:

| path | result, measured today |
|---|---|
| `ffmpeg -f x11grab -i :0.0` | all-black 1280×800, 4,902 bytes (12:53). The game is an XWayland Vulkan client; nothing lands in the X root. |
| `spectacle -R s -b -o clip.mp4` | exits without writing a file (12:57, 12:58). Spectacle 6.7.3 recording is GUI/DBus-driven. |
| `wf-recorder` / `wl-screenrec` / `grim` / `gpu-screen-recorder` / `obs` | not installed |
| `ffmpeg -f kmsgrab` | needs root; `sudo -n` denied |

(A person *can* still press Spectacle's record button by hand — the GUI mode exists. That
is a hand action on his desktop, not something I can script, and I did not try it on his
screen.)

## 3. WHAT THE FRAMES ACTUALLY LOOK LIKE — before anyone promises him renders

- **Stage, earlier in (renderer frames 1104 / 1176):** near-white pixels (all channels
  > 235) = **48.6% / 48.5% of the whole frame** — edge-to-edge blown-out sky over warm
  ground. That is `docs/DEATH-AND-LIGHT.md` B1/B2 unfixed, and the README's own honesty
  table already says "Lighting that looks like the original ❌ No".
- **Stage, later in (frames 2710–2804, and the two compositor stills):** 80–92% of the
  frame one warm hue, mean luma 79–93, 325–551 distinct 4-bit colours. It is a real rally
  scene — terrain, road, structure — rendered flat.
- **Frontend:** 73% flat clear colour `0x9cb4ac` plus a few text rows, **11–45 distinct
  sampled colours**. The game's own UI, and not a menu anyone would screenshot on purpose.
- **Existing `frames/`:** none of them is shopfront-grade. `race-closeup_3100_owner6.png`
  is 91.5% one hue (a flat wash, 324 distinct colours); `race-sky_1800_owner4.png` is the
  best of them — a blue sky band with terrain and structure, but 24.4% pure white and from
  a pre-lighting-fix build — and it is the only thing in `frames/` I would put in front of
  a stranger, with its build named in the caption.

**So the premise of the request is the finding: more in-game renders today would make the
page look worse, not better.** The three model-viewer PNGs in `screenshots/` are the only
good-looking images this project owns, precisely because they are not the game.

## 4. WHAT I RECOMMEND

1. Tell him the truth in one sentence: *stills yes and cheap; video no.* He asked whether
   gameplay had been recorded — it has not, and today it cannot be, except as a 1.7 s
   burst.
2. If he wants a game picture on the page now: use a **compositor still** (§1a — it is his
   game's own pixels and costs nothing), with the caption naming the defect. That reads as
   *more* credible than a clean model-viewer raster dressed as gameplay, and the page
   already admits the lighting is broken.
3. Do not add the burst mp4 to the README. It is evidence, not a demo.
4. Order unchanged: road hole under the car, pause menu, lighting first. The shopfront is
   downstream of the picture being good enough to show, and it is not close.

## 5. THE FILES (also pushed to `github.com/LENAWare-Works/cmr2lab`)

```
docs/capture-20261011/ingame-stage_20261011-1306_compositor.png   compositor still, t=58 s
docs/capture-20261011/ingame-stage_20261011-1307_compositor.png   compositor still, t=70 s
docs/capture-20261011/cmr2-stage-burst_20261011-frames2710-2804.mp4  1.68 s burst
docs/capture-20261011/README.md                                   provenance for each
```

On this box, the full working set is `work/w1-capture/` (48-sequence `seq/`, `run2.log`,
`run3.log`, `run4.log`, the 3 control frames, the 75-frame run in `/tmp/w1-capture/`).

## 6. WHAT I DID NOT DO

No staged image, no model-viewer render dressed as the game, no invented caption, no frame
described that I did not capture. Four runs, all with `work/RACE/gpu-guard.sh` consulted
first — the second of them was correctly **refused** at 13:00 because a peer lane's game
(`out-rt4/cmr2`, pid 187017) held the GPU. I killed nothing by name (only the PIDs my own
scripts spawned, one of which a `dash` arithmetic error in my first harness had orphaned —
the game was running with no owner for about a minute; it was killed by PID at 13:05). No
personal data touched. No window was left open.
