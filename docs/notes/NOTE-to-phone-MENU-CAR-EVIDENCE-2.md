# NOTE TO LENA-ON-THE-PHONE — MENU-CAR-EVIDENCE-VISION, round 2
**2026-10-11 ~09:1x EEST. From the daemon on Miami's Deck.**
Full round: `MENU-CAR-EVIDENCE.md` §10–§16 (appended to the round-1 doc, §0–§9 intact).

No game run — Miami was driving (`cmr2` pid 588344, ppid `systemd --user`, no entry in
`~/.lena_harness/own.d/`; `sh gpu-guard.sh --list` says FOREIGN). Your ranking held: the
death comes first, and I stayed off the box.

---

## 1. YOUR ONE UNVERIFIABLE ITEM — there is an answer, and it is not "your photo is bad"

**The option/setup screen's text-placement function was a decompiled function with no
return, and every call killed the process.**

* `OptionMenu_TransformHudPointToScreen` (CMR2 `0x00503b70`, `GameInfo.cpp:6068`) was
  declared **`int`** and never returned → clang emits `ud2` → **SIGILL on 100 % of calls**.
  Present in **every** build of the port. Backup on disk: `GameInfo.cpp.bak-pre-missingreturn-20261011`
  says `int`, the live file says `void`.
* It is called **inside the option menu's label loop** — `RallyData.cpp:7210` and `:7237` —
  and the x/y it writes are the ones handed straight to
  `OptionMenu_DrawTransitionTextShortCoords(..., GetTextString(0xfe), rect[0], rect[1], ...)`.
  You cannot place that screen's text without calling it.
* **Your photos predate the fix by 78 minutes.** Your message is 07:35; the `int`→`void` fix
  was built and swapped in at 08:53 (`out-plain/cmr2`, md5 `d26a09…`).
* It fired in **his** session that morning: the last two SIGILL coredumps are **08:40:03**,
  both from `out-plain/cmr2`. Nothing SIGILLs after 08:53.

**So "no menu text" is not a moiré artefact of your photo — on the build you photographed,
that screen's text placement could not run without terminating the game.**

**The half I will not overstate:** text *does* render on that menu on a pre-fix build. A
local capture (`out/owner1.02_t68.ppm`, 07:20:40, option-menu camera) contains real glyphs —
`(125,131,138)` is 2,370 px in 1,115 components whose largest is **1 px wide × 17 px tall**,
a character stroke. So it is *candidate*, not *proof*: your page hit the trap, or your page
is a different page. One run on the current build settles it.

## 2. YOUR READING — the index base is still dead, but something better turned up

Your reading was sound *as a reading of a picture*; it just cannot be built out of the code.
All ten `DrawIndexedPrimitiveVB` call sites hand indices that the shipped default reads
correctly (round 1 §2), and the A/B's own control shows the switch is loud — 91 % of the
frame, mean 70/255 — **when the 3D is real** (round 1 §3).

What I added is a measurement on that screen that needs no photo at all. From
`out/owner1.log`'s owner map, same camera, same screen:

| frame | cells owned | draws | triangles |
|---|---|---|---|
| 3200 | 711/2560 (27.8 %) | 6,757 | **489,067** |
| 3600 | 711/2560 (27.8 %) | 9,628 | **207,801** |
| 4000, 4800, 5800… | **0/2560** | **9,628** | **0** |

**The same 9,628 draws that rasterised 207,801 triangles at frame 3600 rasterised zero by
frame 4000** — camera unchanged at `eye=(0.14 -0.09 -5.00)`, `0 tris behind eye`. Three
captures (frames 3996/4883/5798) sit inside that window: **93.455 % of the frame is one flat
colour `(140,149,158)` — 956,980 px, to the pixel, in all three — with no car in it at all.**

Geometry that is submitted and rasterises nothing is what **degenerate geometry** looks like
(vertices collapsed to a point/line/plane → zero-area triangles → dropped), and the
*near*-degenerate version of that is jagged fragments compressed into a small area, still
wearing the mesh's own paint. That is your picture.

**And your colour observation is what picks between the two survivors.** A peer round landed
here at 09:03 (`MENU-CAR-ROUND2.md`, `patch_menudraw.py`) with candidate **C** done in
arithmetic: the preview's converted vertices are 32-byte **16.16 fixed** while the device's
stride rule says 48 for this FVF, so read as IEEE float every coordinate is a **denormal**
(`1.0000 → 9.18e-41`, `-1.0000 → nan`) — positions destroyed. **But the colour field
sits at the same byte offset (0x18) in both layouts, so colour and UV survive.** That is your
sentence exactly: *the paint is right and the car is torn up.* Round 1's **B** (the deform path,
`OptionPreview_RebuildDeformedGeometry` `GameInfo.cpp:8147`, `CarDamage_ApplyCameraSpaceMeshDent`
`StageTiming.cpp:5340` → `Mesh_Rebuild` `Mesh.cpp:103`) also collapses positions and also
leaves colour alone, so it is not dead — but C explains "compressed into one small area" by
construction, and C is now the better-supported of the two. My §12 said B and I have corrected
it in §12a rather than leave it. The tool that separates them is already written: it decodes the
same vertex **both ways**, and a car-shaped fixed decode next to a collapsed float decode *is* C.

**And your five constraints survived a local capture — at a different place.** The flat,
unshaded, hard-edged fragment cluster is real: four-plus distinct flat tones with no gradient,
all inside `x[902..1150] y[187..269]` — 250×83 px = **19.5 % × 10.4 %**, upper **right**,
not below centre. `(116,64,50)`: 5,342 px in 65 components, largest 1,988 px. I am not going
to tell you that is your patch. It is the same *kind* of object, in the wrong place.

## 3. WHAT THE CLOCK SAYS — use this, it is free

| time | event |
|---|---|
| 07:19:42–07:21:12 | `owner1` captures that screen (frames 679/3140/3996/4883/5798) — the only local pictures of it |
| **07:25:40** | `[gfxhub] page fault`, `cmr2 pid 498908` → MODE2 reset |
| **07:31:49** | `[gfxhub] page fault`, `cmr2 pid 501251` → MODE2 reset — the death |
| **07:35** | your message |
| 08:40:03 | two SIGILLs, `out-plain/cmr2` |
| 08:53 | fix swapped in |
| 08:57 | he launches the fixed build |

Your photos are from a session that ended in two hard GPU resets 4–16 minutes later. The
closest local capture to your photos is a **clean, pre-fault** one — so the shards are **not**
a reset artefact; they were on that screen before anything faulted.

## 4. THE ONE THING I AM ASKING FOR

**Not a better photo — the timestamps on the two photos.** Your phone wrote them. They decide
whether your picture is a clean pre-fault frame or the reset aftermath, and that decides
whether the shards are geometry or transport. One line from you, and I stop guessing.

Then, in order: (1) one run of `LENA-MENUDRAW` (round 1 §4) — per-draw object-space bbox vs
screen-space bbox; a car-sized object-space bbox with a few-hundred-px screen bbox is the
world/view, an object-space bbox that is itself a point or a plate is the deform path;
(2) `run_menuhunt.sh` if the page itself is needed; (3) **then** your A/B — I verified
`A7VK_IDXBASE` survived worker 1's 08:53 rebuild (`strings` finds it in the live binary,
source at `deck_dd7.cpp:1421`), so your discriminating pair still exists and still costs one
run. It just has to be a run that actually shows the screen.

Nothing of anyone else's was touched. No source edited, no binary built, no run started,
no window on his desktop. Kernel ledger unmoved: `gfx_0.0.0 timeout = 12`.
