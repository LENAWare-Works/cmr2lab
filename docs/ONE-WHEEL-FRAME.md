# ONE-WHEEL-FRAME — the photo is not on this machine, and two of the three claims
# it carries do not survive contact with what is already measured here

`work/RACE`, 2026-10-11 08:4x EEST. Worker 2. Round: **the phone's one-wheel frame.**

**No game run. No GPU. No source edited, no binary built or copied, nothing of worker 1's
files touched.** Everything below is measured from the filesystem, the kernel/DRM state, the
already-captured frames in `out/`, and the traces already on disk. Worker 1 holds the GPU
(`WHITE-BOX-UNDER-CAR`), and the phone ranks the display death first.

Read with `FRAMING.md` (what a frame is), `../.lena_cmr2/port/C3D.md` §STILL OPEN (the part
map), and `MENU-CAR-EVIDENCE.md` (the car's other defect).

---

## 0. THE THREE LINES

1. **The frame is not on this machine. I could not measure it, and neither could
   `WHITE-BOX-UNDER-CAR`, which went looking for it at 08:22. Every number the phone sent is
   the only measurement of that file that exists.** §1.
2. **The 0.63 aspect she measured cannot be read as "the game is rendering a portrait
   viewport" — the number is degenerate.** This panel is natively **800x1280 portrait** and
   the desktop rotates it to 1280x800; a 1280x800 frame that is presented or photographed
   rotated 90° has aspect **0.625**, which is what she measured. The game's own frames are
   1280x800 in **377 of 377** captures on disk and the projection aspect is **1.600 exactly**.
   §2 — and §2 ends with the one test that discriminates.
3. **Her parts lead is right in kind and wrong in three details, and the census she asks for
   is not yet able to answer.** The car is 14 parts and **the four wheels are parts 0-3 of the
   body file**, all four stacked at the local origin — so "one wheel, face-on, nothing else"
   is exactly what that structure looks like when placement is missing. But in our own runs
   the body **and** the wheels both reach draws, and the instrument that would settle it has
   a sampling hole. §3, §4.

---

## 1. THE FILE IS NOT HERE — and that is the whole caveat, stated as a measurement

She said her vision pass and pixel measurement are all she has. They are all anyone has.

* **Method.** Every file on the Deck with an image signature was parsed for its own header
  dimensions — JPEG SOF, PNG IHDR, BMP, GIF, TIFF, PNM — by `/tmp/imgsweep.py`, over the
  candidate file list `/tmp/cl2.txt` (every file >15 kB and <40 MB under `/home/deck`, `/tmp`,
  `/var/tmp`, `/run/user/1000`, excluding `.cache`, object files, `zigcache`, `__pycache__`,
  `.git/objects`, `htmlcache`, `baloo`, `.so`). **9,184 image files** had their dimensions
  read. The only 1800s are two 2880x1800 Minecraft modpack thumbnails. **No 1355x1800
  file exists.**
* **Not in the relay either.** `lena-relay.py` carries JSON, not attachments
  (`get_file`/`put_file` — a repo file, inline base64 ≤1 MB). Nothing image-shaped has ever
  arrived through it. The two phone frames this project *did* receive, `f_3890.jpg` and
  `f_t84.jpg`, are **1280x800** and arrived in `work/RACE/fromlenaphone/` at 06:59 by a route
  that wrote files (scp over the home Wi-Fi, or the lab tree) — not by the relay.
* **Consequence: I am not reporting anything about his photo.** I have no picture of the
  defect, no way to confirm the wheel, the white line, the glare, or the crop. Where §2 and §3
  disagree with her message they do it against things that *are* on this disk.
* **The ask is one line and it is not a criticism:** put the file where it can be measured —
  `work/RACE/fromlenaphone/` by scp on the home Wi-Fi, or a commit in the lab tree
  (`work/cmr2lab-publish/`), which is how the last two frames arrived. Until then every
  question about that frame is answered by inference from other frames.

---

## 2. THE ASPECT PROVES NOTHING ABOUT THE VIEWPORT — the panel is portrait-native

Her sentence: *"ASPECT ~0.63 — that is PORTRAIT, and 800x1280 (a rotated Deck screen) is
0.625. Worth asking him whether the Deck was rotated for this run, because if the game is
genuinely rendering an 800x1280 viewport that changes what the viewport maths is being
handed."* The aspect is real. The inference is not safe, because 0.625 here is a property of
the hardware, measured:

| what | value | how |
|---|---|---|
| panel native/preferred mode | **800x1280** | `/sys/class/drm/card0-eDP-1/modes` (first entry) |
| X screen / current output | **1280x800, rotation `right`** | `xrandr` (eDP-1 primary, `800x1280 59.93*+`) |
| panel physical size | **100 mm x 150 mm** — portrait | `xrandr` output geometry |
| every swapchain ever created by the port | **1280x800**, 118 lines / 59 runs | `[A7VK] RESOLUTION` in `out/*.log` |
| every frame capture on disk | **1280x800**, 377 of 377 | PPM headers, `out/**/*.ppm*` |
| projection aspect the port hands the shader | **1.600 exactly** | `FRAMING.md` §0.2 |

So the Deck's glass is a **portrait rectangle rotated by software into landscape**, and
**0.625 is the shape of an 800x1280 image — which is what a 1280x800 framed picture is after a
90° rotation.** Her 0.63 is therefore satisfied by at least three different worlds:

1. the game rendering a genuine portrait viewport (her reading — would change the viewport maths);
2. a correct 1280x800 frame photographed with the phone held sideways, or stored rotated with
   EXIF Orientation 6/8 and read by a pipeline that ignores EXIF (no game defect at all);
3. something in the present path applying or dropping the panel rotation (a real defect, but
   **not** a viewport-maths defect).

**The test that separates them costs nothing and needs no GPU: read the EXIF Orientation tag
of the original JPEG.** If it is 6 or 8, the stored pixels are rotated and her whole portrait
reading is a photo-storage artifact — the frame is 1280x800 landscape like every other frame
this project has ever seen. If it is 1, we have a genuine portrait presentation and it is a
new class of defect worth a run.

**Second discriminator, free, on the picture itself:** if the frame is a rotated landscape
image, then her *"THIN VERTICAL WHITE LINE running roughly full height"* is a **horizontal**
feature spanning the full **width** in the game's own frame — and her *"four or five small
white blobs spaced along it just above/left of the wheel"* are objects strung along a
horizontal line. That is a much more ordinary thing to find in a rally stage than a vertical
one, and it is consistent with the sky/horizon band she is looking for. If instead the white
line really is vertical in game space, rotations are out and her reading stands.

**What I am not doing:** I am not asserting the frame is sideways. I am asserting that
aspect 0.625 cannot tell us, and that the project has no business handing a 800x1280 viewport
to the maths ladders on the strength of it.

---

## 3. THE PARTS — right in kind, and three details corrected

Verified as real, from this project's own format work (`../.lena_cmr2/port/C3D.md`,
`docs/GLOSSARY.md`): the CMR2 car is **parts**, `N` = body, `L` = left wheel, `S` = right
wheel. Her framing survives. The details do not:

**(a) The wheels are inside the body file, and they are its first four parts.** `C3D.md:1348`,
the 14-record part map of `206a1N.c3d`:

```
part 0-3  '01WhlLOD00'  verts 0+86  faces 0+72   <- the four wheels
part 4    '05BonCam'    …  part 7 '08BodySim' (the body) …  part 13 '15undsim'
```

This sharpens her lead instead of weakening it. There is no separate "wheel model" being
loaded instead of the body: a car whose part list is walked and cut short at the wheel parts
puts **four wheels and no body** on screen.

**(b) All four wheel parts sit at the LOCAL ORIGIN — identical extent, identical centroid,
stacked.** `C3D.md` §STILL OPEN 2: *"identical extent 0.654 x 0.654 x 0.276, identical centroid
(0.00, 0.00, 0.03), stacked. They are placed at runtime by code not yet in the decomp …
NEXT LEAD: the 22 `.cin` files in Game/Cars/"*. **Therefore "exactly one wheel, isolated and
face-on" is the expected picture of all four wheel parts drawn with no placement transform** —
four coincident wheels look exactly like one wheel. Her two named forks (per-part transform vs
per-part bind) are the right forks; this tells you **how to tell them apart without a picture
of the car**: if placement is missing, the four are coincident and their draw count in the
frame is 4 (or a subset if LODs drop); if only one part is bound, the count is 1. That is a
countable difference, in the instrument she already asked for.

**(c) "the two wheels byte-identical because one is a mirror" — false on the bytes.** Measured
in `cmr2cd/fscommand/Game/Cars/`:

```
206a1L.c3d   2687 B   md5 d43b77dc7081bcdcc87b72cefa10c27a
206a1S.c3d   2685 B   md5 cd29ad137bc1520ed2e58c46e28a7930
cmp: differ at byte 12; 2655 of 2685 bytes differ (the whole deflate stream)
```

What *is* true is what `C3D.md:158` actually says — **identical size**, not identical bytes:
the two files unpack to the same 52,132 B of geometry, consistent with a mirror. The
distinction matters, because "byte-identical" would make a left/right mix-up undetectable and
would point the hunt at the loader; as it is, L and S are distinct assets (both `.c3d` files
are gzip: `1f 8b 08`).

---

## 4. THE CENSUS SHE ASKED FOR, RUN ON WHAT IS ON DISK

Her test: *"count which `PP_F` blobs reach a draw in this frame and compare against the parts
of that car."* There are three instruments for that already, and I ran all three over the
race traces in `out/` (`texreq_race.log`, `texreq2/3/4_race.log`, `idxtrace_race.log` —
Kenya stage, **Ford Focus `CARS2/FOC2000`**, which is the combo Miami actually drove).

**What they show — the body and the wheels both reach draws.**

*Car mesh → part → texture, from `[TEXREQ] MESH` lines (the Focus arrives as 7 meshes of 1-3
parts each, grouped by texture):*
`slot 196 CFFDBODF.tga` (body) · `208 CFFGLIDF.tga` / `212 CFFGLODF.tga` (glass) ·
`211 CFFINTDF.tga` (interior) · `218 CFFUNDDF.tga` (under).

*Per-part window table (`[TEXREQ] part slot=… draws=… bind=… skip=…`), body slot 196:*
present in **11 of 16** windows at **923-1045 draws / 1386-1568 binds** per window. The body
draws, thousands of times.

*Wheel textures:* `CFFLWBDF.tga` and `CFFLWHB4.tga` appear as `[TEXREQ] BINDFIRST` binds and
as `[TEXREQ] batch slot=… runs=…` with **1232** and **424** batch runs. The wheels draw too.

**So her specific hypothesis — "exactly one wheel part draws and body + other wheel do not" —
is not what the traces show in our runs.** I am not reporting that her frame is impossible; I
am reporting that for Focus/Kenya on this machine, both families draw, so a frame that shows
one wheel and no body is not explained by part starvation *at the draw level* — it points at
placement/transform or at what happens to those draws downstream (the near-plane blow-up,
§5), which is the other half of her own fork.

**And the instrument is not yet good enough to settle it — this is the part worth acting on.**
Two measured limits in the existing instrumentation:

* **`trq_mesh` is a sample, not an enumeration.** `patch_texreq.py:173-183`: a mesh is logged
  only if an open-addressed probe of a 1024-entry pointer table finds a free slot **within 24
  probes**, and the log stops after 600 meshes. We logged 329 meshes; **no wheel texture
  appears in any logged mesh's part list** — and I am explicitly *not* claiming wheels are
  absent from part lists, because the 24-probe dedupe can silently drop a mesh. Absence here
  is not evidence, and must not be reported as one.
* **The per-part table is capped at the top 12 slots by draws per window** (`trq_window`,
  `for (shown = 0; shown < 12; shown++)`), and its counters are zeroed each window. A quiet
  part cannot appear in it at all, so it cannot answer "which parts did *not* draw".

**The change that makes her test real, in one round, no new instrument:** key the dedupe by
mesh pointer in an actual set (or, simpler, print the part list for **every** draw inside a
bounded frame window) and print **all** parts with their draws/bind/skip instead of the top
12. Then "which of the 14 parts of the car reached a draw in frame N" is a `grep`, and her
fork — placement vs bind — is decided by a count. `TEXUSE` is already uncapped
(`n=65 (ALL, not top-10)`, per texture id, per frame, with screen coverage and NDC extents),
so the frame-level half of the answer already exists; it is the mesh→part→name half that is
sampled.

---

## 5. NO ROAD — already measured, and it is not a new bug

Her honest half: *"no road either … if you are still waiting on the road surface, this frame
says it has not arrived yet."* `FRAMING.md` §0.1 settled the class of this before tonight:
with the 3D batches off the frame is **exactly one colour**, and with 3D on and no texture
bound the frame is **exactly one colour, `(255,255,255)` — the 3D geometry alone covers
100.000 % of the pixels**. There is no uncovered region anywhere in a race frame for a
horizon, a sky or a road verge to live in; the "flat pale stretch with no horizon" is the
near-plane blow-up (clip `w` ∈ [-89.3, +121.5] against near plane 5.86, NDC `x` out to
-2.8×10⁷). So the missing road in her frame is consistent with the known blow-up signature,
not with a road surface that failed to arrive separately. Supporting, from my own re-measure
of the newest race captures on disk: `out/owner1.04_t98.ppm` is **93.46 %** one colour,
`out/clean.03_t86.ppm` **62.61 %** backdrop, `out/mc/mp_sub.ppm.4300` **64.38 %** backdrop,
`out/death/control4.ppm.3000` **99.62 %** backdrop + 0.38 % white in a single 108x68 px box at
`x[522..630] y[382..450]` (that last one is a frontend frame, not a race frame — flagging it
so nobody reads it as the race).

---

## 6. FOLD-IN: KEEP THEM SEPARATE, AND SAY WHY

Her caution was that this and `MENU-CAR-FLATTENED` may be one bug. On what is measured they
are different failure modes that share call sites:

* **MENU-CAR-FLATTENED:** the parts are all there and painted with the car's own livery, and
  the **connectivity** is wrong — a compact patch of shards, vertex colours and UVs correct.
* **This one:** the question is **which parts are drawn and where they are placed** — a
  selection/transform question, not a connectivity question.

Different observable, different candidate fix. They do share the draw sites the last round
enumerated (`Graphics_DrawMeshPartsByTexture` / `Graphics_MarkTexturesAndDrawMeshParts`,
`Graphics_DrawMeshTextureBatches`), so a fix in the part-walk would have to be checked against
both — keep the tickets separate, cross-reference the call sites. If a frame ever arrives for
this one, the discriminating measurement is in §4, not in the menu A/B.

---

## 7. WHAT I DID NOT CLAIM — AND WHAT I DID NOT DO

**Not claimed**
* Nothing about his photo. I have not seen it; no measurement of it exists on this machine.
* Not that the frame is sideways. Only that 0.625 cannot discriminate (§2).
* Not that the wheels are absent from mesh part lists — the mesh log is sampled and I said so (§4).
* Not that the car is fine. Both families *reach draws* in our runs; whether those draws put a
  car on the screen is a different question, and the answer in our frames is that they mostly
  do not (§5).
* No new bug invented for the missing road (§5).

**Did not do**
* No game run, no GPU touch, no window on his desktop, no build, no source edit.
* Nothing of worker 1's files was modified. `CHECKPOINT.md` got one pointer block at the top;
  `MENU-CAR*.md`, `DEATH-AND-LIGHT-ROUND.md` and every `out/` artefact are untouched.
* No `state/`, wallet, worklog, memories or Signal data touched.
* Kernel ledger held: `journalctl -k | grep -c "ring gfx_0.0.0 timeout"` = **12** and `MODE2 reset` = **14**, both unmoved (nothing ran this round).

**New in this directory:** `ONE-WHEEL-FRAME.md` (this), `onewheel_census.py` (the TEXREQ/TEXUSE
join, kept because it documents the id-space question even though the capped instrument
limited what it could print).
