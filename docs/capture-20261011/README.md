# capture-20261011 — real in-game pictures, and what each one actually is

These were taken while answering Miami's request of 2026-10-11 12:20 EEST (*"possibly could
use some more renders from the game and if any recorded my gameplay for graphics display
purposes"*). The finding is in [`../NOTE-to-phone-RENDERS-AND-CAPTURE.md`](../NOTE-to-phone-RENDERS-AND-CAPTURE.md);
this file is the provenance of the four files, because a picture with no provenance is a
claim.

**Nothing here is staged, retouched, upscaled or rendered from the offline viewer.** Every
file is a frame of the game's own race path running on a Steam Deck, saved exactly as the
capture path produced it.

Binary: `work/PLAY/out-plain/cmr2`, md5 `9ecbf87bb8650a3883b188f4e77890e4` — the default
play binary on 2026-10-11 13:0x, the same bytes that pass the `cmr2_drives` gate.
Run procedure: game root as cwd, one `Enter` at t≈13 s, stage up by t≈50 s, no driving
input. `work/RACE/gpu-guard.sh` consulted before every launch (one launch was refused —
a peer lane's game held the GPU, which is correct).

| file | what it is | how it was made |
|---|---|---|
| `ingame-stage_20261011-1306_compositor.png` | the game's window at t≈60 s of the run (renderer frame asked for at t=58) | `spectacle -b -n -f -o …` — a KWin compositor screenshot of the desktop, which contains the game window. **Real game pixels: verified against the renderer's own capture at the same moment (mean luma 93.0 vs 97.5, warm 58.8% vs 56.2%, 348 distinct 4-bit colours in both).** 1280×800, 2,105,881 B |
| `ingame-stage_20261011-1307_compositor.png` | the same window at t≈72 s of the run (renderer frame asked for at t=70) | same method. 1280×800, 2,012,458 B |
| `ingame-stage_20261011-1307_renderer-readback.png` | the renderer's own frame of the same moment as the still above — the trigger fires on the next present, then Spectacle runs, so the two are ≈2 s apart | `A7VK_SNAP` trigger, asked for at t=70 — the RHI re-records the current batch list offscreen and reads it back off the GPU (P6 PPM → PNG with `tools/ppm2png.py`, round-trip verified pixel-exact). 1280×800, 2,599,070 B |
| `cmr2-stage-burst_20261011-frames2710-2804.mp4` | **1.68 s of gameplay, and it is a burst, not a demo** | overlaid frames 2710→2804, i.e. 48 consecutive presented frames sampled every other present, encoded true-speed at 28.5 fps (h264, 5.7 MB). It took 26 s of wall clock to capture because a capture costs ≈0.5 s of the frame it lands on — a control run presented the same stage at 57.2 fps with the capture left alone |

## Read this before using any of them

- **The lighting is broken, visibly.** In these stills 80–92% of the frame is one warm hue at
  mean luma 79–93; earlier in the same stage (renderer frames 1104/1176) **48.6% of the frame
  was blown-out near-white**. That is the unfixed defect in `docs/DEATH-AND-LIGHT.md`, and
  the README already says so in its honesty table.
- **Frames 1104/1176 of the frontend show 73% flat clear colour and 11–45 distinct sampled
  colours.** The frontend accepts input and draws; it is not a screenshot anyone would pick
  on purpose.
- **Do not caption the mp4 as "gameplay footage"** without the word *burst*. It is 1.68 s
  long because that is all that can be captured in a reasonable wall-clock budget at ≈2
  captured frames per second.
- The two compositor stills include the game window **as composited on the desktop**. If a
  window decoration or a panel edge is visible in one, that is why — it is not part of the
  game's render.
