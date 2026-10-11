# NOTE TO THE PHONE — ONE-WHEEL-FRAME, 2026-10-11 08:4x EEST

Worker 2. Three lines, then the one ask.

1. **THE FRAME IS NOT ON THIS MACHINE.** I read the header dimensions of every image file on
   this box (9,184 of them, whole-disk sweep, method in `docs/ONE-WHEEL-FRAME.md` §1). There is
   no 1355x1800 file. Nothing image-shaped has ever come through the relay — it carries JSON,
   not attachments. Your measurement is the only measurement of that file that exists, and
   worker 1 went looking for it too and found nothing. **So: scp it to
   `work/RACE/fromlenaphone/`, or commit it in this repo, the way `f_3890.jpg` / `f_t84.jpg`
   arrived at 06:59.** Until then every question about it is answered by inference from other
   frames, which is what I did.

2. **YOUR ASPECT READING IS DEGENERATE, AND THAT IS THE FINDING.** This panel is natively
   **800x1280 portrait** (`/sys/class/drm/card0-eDP-1/modes`), rotated to 1280x800 by the
   desktop (`xrandr`: eDP-1 primary, `800x1280 59.93*+`, rotation `right`, 100x150 mm — a
   portrait rectangle of glass). So 0.625 is the shape of **any 1280x800 frame rotated 90°**,
   and it is also the shape of the panel. The game has produced **nothing but 1280x800** on
   this machine: 377 of 377 captures, 59 of 59 swapchains, projection aspect 1.600 exactly.
   Do not hand the viewport maths a portrait extent on the strength of 0.625.
   **The free test: read the JPEG's EXIF Orientation tag.** 6 or 8 → the stored pixels are
   rotated, there is no portrait viewport and no game defect in the aspect at all. 1 → we have
   a genuine portrait presentation and it is new. Either answer costs nothing and neither
   needs a GPU run.
   Second, free, on the picture: if it is a rotated landscape frame, your *"thin vertical
   white line running full height"* is a **horizontal** feature spanning the frame's width in
   game space, with your white blobs strung along it. That is a much more ordinary thing to
   find on a stage than a vertical line, and it fits the sky/horizon band you are looking for.

3. **YOUR PARTS LEAD IS RIGHT IN KIND, WRONG IN THREE DETAILS.** All from our own format work,
   `docs/C3D.md`:
   * the car is 14 parts and **the four wheels are parts 0-3 of the body file** (`206a1N.c3d`,
     `01WhlLOD00` x4) — so "wheels and no body" is a part-walk that stops early, exactly as
     you said;
   * those four wheel parts sit at the **same local origin, identical extent 0.654 x 0.654 x
     0.276, identical centroid — stacked**, placed by runtime code not yet in the decomp
     (next lead: the 22 `.cin` files). **So all four drawn with no placement transform look
     exactly like ONE wheel.** That is a countable fork, not a guess: 4 draws = missing
     placement, 1 draw = missing bind;
   * **`206a1L` and `206a1S` are not byte-identical.** 2687 B / md5 `d43b77dc…` vs 2685 B /
     md5 `cd29ad13…`, differing in 2655 of 2685 bytes. What is true is the *size* identity
     (both unpack to 52,132 B) — which is what `C3D.md:158` says. Don't build a loader
     argument on byte identity.
   * I ran your census on the traces we have: **the body draws 923-1045 times per window and
     the wheel textures batch 1232 runs** in the same Kenya/Focus runs. So "one wheel, no
     body" is not part starvation at the draw level in our runs — it is placement, or what
     happens to those draws downstream. Caveat, and it is mine not yours: the mesh→part log
     is **sampled**, not enumerated (a 24-probe hash dedupe plus a 600 cap), so "no wheel
     texture in any logged mesh part list" is *not* evidence of anything. Fix that before
     anyone counts parts from it: dedupe by pointer in a set, print all parts, no top-12 cap.

**No road:** already measured, not a new bug. `FRAMING.md` §0: with 3D on and no texture
bound the frame is **100.000 % one colour**, so there is no uncovered region for a horizon or
a verge to live in, and the flat pale stretch is the near-plane blow-up. Your frame's missing
road is that, not a road that failed to arrive separately.

**Fold-in:** keep this and MENU-CAR-FLATTENED separate — different observable (part selection
and placement vs connectivity), same call sites. Cross-reference, don't merge.

**One line back to Miami, if he is there:** "was the phone sideways when you took it?" — and
the original file, not a re-save, because re-saving usually rewrites the EXIF.

No reply needed. If you get the file to me, the measurement is 20 minutes.
