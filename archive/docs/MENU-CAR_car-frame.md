# The menu car, round 5: the A/B on the car page, and the capture that was missing

**From:** `MENU-CAR-FLATTENED`, round 5, 2026-10-11 11:2x EEST.
**Runs used:** `out/md_car_raw.log` (default arm), `out/md_car_sub2.log` (`A7VK_IDXBASE=sub`),
`out/md_car_sub4.log` — binary `out-md2/cmr2`, md5 `cfd9cb7980dff26a5e56649467845432`, the only
change between arms is the one environment variable.
**Supersedes:** nothing. This adds to `MENU-CAR-opt-preview_car-frame.md` (round 4).

## 1. The A/B the ticket asked for, on the car page itself

`md_car_sub2` (finished 10:32, unread until now) reached the option camera at t=73.6 s with
3 injected keys and landed on the **car page** — the same page as the default arm's frame 8517,
identified by its per-part object boxes (0.365–0.833 units wide, versus the stage page's ±80/±100).

| | default (`md_car_raw`) | `sub` (`md_car_sub2`) |
|---|---|---|
| indexed draws parsed | 3,012 | 3,036 |
| `idxInRange=NO` | **0** | **2,778 (91.5 %)** |
| indices as received | `2,1,0,3,2,0`, largest 44 | `65506,65505,65504,…` (= −30, −31 as int16) |
| `zeroBase=yes` | 336 | 258 — the only in-range draws |
| `[GEO]` mesh NDC box | x=[−0.811 0.741] y=[−0.422 0.460] | **x=[−76577.33 3.60] y=[−92242.79 20664.31]** |
| owner-map coverage | 463–658 cells, 2,073 tris, 18–25 % | 21 cells, 48 tris, 0.8 % |

**So: the menu car's indices are part-local/relative, exactly like the race path's, and the
old re-base (`sub`) is the thing that produces a mangled, blown-up sheet.** The phone's
hypothesis — that the frontend needs the old convention — is dead on the screen it was written
about, by measurement this time rather than by reading ten call sites. Nothing needs scoping;
reverting the fix would create the symptom, not cure it.

## 2. The capture that was missing, and what it shows

`frames/md_car_raw.000.ppm` is run frame **8517**, taken with **1,377 car draws in flight**
(`pickcap.py`), inside the car page's own draw window (owner map: 8500–8575). Measured
(`scan.py`, `grid.py`):

* **96.417 % of the frame is one colour, `(140,150,158)`; 232 distinct colours in the whole frame.**
* The car's own owner cells — rows **r14–r27**, cols **c8–c53** of the 64×40 map, i.e.
  **x 160–1080, y 280–560 px** (`out/md_car_raw.log` frames 8500/8575, `tex=37 39 40 41 44 …`) —
  contain **nothing that differs from the backdrop**. The only content is the 2D chrome.
* Same run, same frames, `[GEO]`: `3D draws=1377 verts=78183 tex=1377 notex=0 lit=1326`,
  obj box `x=[-2.1 2.1] y=[-0.5 0.7] z=[-0.9 0.9]`, `w=[4.076 6.157]`,
  `ndc x=[-0.811 0.741] y=[-0.422 0.460]`, `behind=0 nonfinite=0 draw_behind=0 draw_alloff=0`.

**The car is submitted, textured, correctly transformed, and paints nothing.** That is now a
measured sentence about the default arm, not an inference.

## 3. The picture in this repo

`frames/opt-preview-car_where-engine-says-vs-what-screen-shows_f8517.png`
(md5 `9471b0235b178b1ba43a2529566549f5`), made by `owner_overlay.py` from
`frames/md_car_raw.000.ppm`: the capture, with the owner map's car cells tinted magenta and
ringed in red — **25.16 % of the frame (257,600 px)**. It is the clearest one-image statement of
the bug we have: the engine says the car is here, the screen says the screen is empty.

## 4. What is still not claimed

No cause. The remaining candidates are all "after submission": fragments discarded by alpha
test, cull/winding, or a dead texture binding — or written in the backdrop colour. The render
state line (`rs z=0 zw=0 zf=4 ablend=1 cull=3 shade=2 light=0 fog=0 atest=1 viewport=1280x800`)
is identical on the car page, on frames with no 3D, and on the stage page, so it is a
frame-level snapshot and **not** a per-draw discriminator; the per-draw histogram
(`63:120 159:60 191:1440`) is suggestive and not decisive. Next instrument: `A7VK_TEXDUMP` on
the car's texIds checking their alpha, or one run with alpha test forced off.
