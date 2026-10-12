# frames/20261013-0025 — the tree build racing a whole stage (and where it dies)

One run, one binary, named. Captured 2026-10-12 23:54–23:56 off the RHI's own swapchain
(`A7VK_SNAP`), 1280x800 PPM, converted to PNG unchanged.

| | |
|---|---|
| binary | `/home/deck/lena/work/PLAY/out-plain/cmr2`? **no** — `work/SUSPECT-CORRECTED-THE-ALIGN-20261012-2218/out/cmr2` |
| md5 | `275dfde9089ca0b551c726f18f37c473` (a pinned copy of `FIX-BOTH-PROPERLY-20261012-2201/out/cmr2`) |
| what it is | the R7 stage-loader migration with faults 1–6 fixed (record stride 0x114→0x120, light-zone item copy, 0x5c chain links, fin-record chain link, and the fault-6 lifetime fix) |
| run | 400 s attract, no keys, clip ON, mips ON, `DECK_RACE_TRACE=1`, tag `align2` |
| result | **5,060 race frames, 4,885 in `state=8`, car moving on 4,812, max speed 97,526, `clampHits=0` at all 8 captures, `tl_misaligned=0`, clip `newv=120 deg=0 scrfail=0`, ring delta 0, no kernel GPU event — it drove a whole stage and survived the stage end (`state=9`, 168 frames). Then it died at the second stage transition on a bad `free()` (`munmap_chunk(): invalid pointer`), 332 s in.** |
| evidence | `work/RACE/out/align2.log`, `work/FIXBOTH-20261012/logs/align2.header`, verdict in `work/SUSPECT-CORRECTED-THE-ALIGN-20261012-2218/logs/verdict-align2.txt` |

## The frames

| file | what it is |
|---|---|
| `2600.png` | the main menu. The rotating ribbon of scrambled letters (`mcr aecolin…`) is the animated 3D text object, not a glitch; `rally` is the selected item. |
| `3500.png` | a stage, demo camera, car at centre |
| `4000.png` | the same stage from the demo camera |
| **`4500.png`** | **the tree build racing**: Ford Focus WRC, Valvoline/MoviStar livery, `Grist / McRae` on the rear quarter, `5` on the door, gravel wheels, `demo` watermark top-left |
| `5000.png` | back at the main menu — the demo cycle ended and the frontend came back |

## What is WRONG in these frames (nobody has fixed this, and it is not the clip)

In `4500.png` and `3500.png`, with the near clip ON and its own census reporting `deg=0`,
`scrfail=0`, `bad=0` in every measured run:

* the white road-edge geometry **draws on top of the car** — it crosses the front wheel, the sill
  and the rear wing, so the car appears to be behind the road markings;
* a detached white streak floats in the air to the left of the rear wing;
* the bottom of the frame is a flat, featureless brown band with no texture;
* there is no sky — the top of the frame is a dark blurred band.

`KMH 000` in Miami's own two stills (8 minutes apart) is also still unexplained. These are
rendering-layer faults, not the loader migration and not the near clip, and they need a control
run with the clip OFF that has not been done yet.
