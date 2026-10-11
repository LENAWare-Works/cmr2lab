# to Lena-on-the-phone, from the MENU-CAR-EVIDENCE-VISION seat. 2026-10-11 ~10:2x EEST.
## round 4. the A/B is run. your test came back, and it came back inverted.

Your five pixel observations were used as constraints and they did their job. Here is what
the two conventions do on that screen, measured inside each run's own option-screen window
(the window is the frame range where the camera is `eye=(0.14 -0.09 -5.00)`; coverage is
`A7VK_OWNER`'s per-frame count of the 64x40 grid cells any 3D triangle reached):

| arm | run | window | covered | triangles | car textures bound |
|---|---|---|---|---|---|
| **shipped default** | md_raw f7900 | 7675-8050 | **23.4 % of frame** | 2,099 | 8 |
| **shipped default** | md_geo f3450 | 3350-3525 | **23.2 % of frame** | 2,073 | 8 |
| **sub (old re-base)** | md_sub4 f6950 | 6650-7225 | **1.1 % of frame** | **48** | 8 |

Credit where it is due: the coverage A/B is the peer worker's — commit `229c886` already has
23.4 / 23.1 / 17.6 % vs <=1.1 %. What I added is the check that those numbers were taken
while the screen's own camera was up (they were), the patch's size in % of frame (the
number that meets your estimate), and the capture audit below.

Two independent default runs, three hours and thousands of frames apart, agree to 0.2 % of
frame area. `sub` is a factor of ~21 down in covered area and 43 down in triangles.

**And `sub`'s patch measures 10.9 % of the width by 10.0 % of the height, 1.1 % of the
frame area, holding 48 triangles of the car's own livery, in one compact block.** Your
patch: "roughly 10-15 % of screen width and height", car's own paint, flat, no
silhouette. That is `sub`, to your own error bars.

**So: the menu path does not need the old re-base. The old re-base is what draws your
photo.** Scoping it to the menu draw path would install your picture onto his screen. The
corrected default stays, globally, and nothing needs to be path-scoped.

On the default arm the same screen is a car, measured, in one frame where the screen and
the geometry trace were on together (f3480): object-space box **4.2 x 1.2 x 1.8 units**,
NDC box x[-0.81..0.74] y[-0.42..0.46], `part=0`, `behind=0`, `nonfinite=0`,
`draw_alloff=0`. That is your constraint five — "nothing shooting off-screen" — as a
measured zero on the arm you wanted to reject.

## the one thing you should not accept from me
Your patch is "roughly on the horizontal centre line". `sub`'s patch is at 64.8-66.4 %
across — right of centre, not on it. Your vertical reading ("just below centre") matches
(67.5 % down in two of the three samples). One axis agrees, one does not, and I am not
smoothing that over. I have not identified your photo; I have matched its size and shape
to an arm.

## why nothing here ever photographed that screen (I counted it)
Every capture this ticket has ever taken:
* md_raw: window 7675-8050, 7 captures, first is 8264 — **0 inside**.
* md_geo: window 3350-3525, 19 captures, first is 3955 — **0 inside**.
* md_sub4: window 6650-7225, 15 captures, one at 7023 — **1 inside**, and it is 48 frames
  after the car stopped being drawn (33 distinct colours, 99.233 % one grey). That is the
  "FLAT" picture from the ticket: true of the picture, silent about the arm.

The car's 3D lives for 1-2 seconds per visit. Everything the ticket said about "the
default frame has no car" was a capture fired a few seconds too late.

## your optional text item
Answered in the report and unchanged: font atlases load on both screens, the
`Font_DrawText -> DrawPrimitive(TLVERTEX)` path is implemented and runs 1.66-1.87 M times
per run, and on the option screen itself the 2D path drew 19,691 sprites in the one frame
I have. So "no text" cannot be a missing path. Still unverified — and I am still not
chasing it beyond that.

## the ask, and it is one line
Send one full-resolution capture of that screen, taken **while the car is up**, on his
current default build. That one frame settles both this ticket and the text question. And
if you have the two photos you sent me, put them in `work/RACE/fromlenaphone/` — they are
not on this machine, so your measurements are the only ones that exist.

## housekeeping
No GPU run by me this round: the card was held by the peer's menu-car run and then, from
10:03, by the death lane (`PLAY/out-plain/cmr2`). The display death kept its place at the
front of the queue — I never contended for the card.
