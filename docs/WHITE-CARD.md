# WHITE-CARD — the white box under the car, measured

Round: `WHITE-BOX-UNDER-CAR`, worker 1, 2026-10-11 08:22–08:5x EEST.
Input: the phone's 07:45 handover (her sentence, treated as a lead) + Miami's verbatim
report: *"the demo also worked here with Ford Focus and Kenya rally untill it didn't and
froze which was coool / again super janky and white box under the car, textures were
overall better tho"*.

**One line: the port has a measured reason to draw a white card where a colour belongs —
on the 3D path the colour comes from the MATERIAL, not from the vertex, because
`D3DRS_COLORVERTEX` and `D3DRS_DIFFUSEMATERIALSOURCE` are both dropped states; the car's
shadow is a draw whose only colour is in its vertices; and the specimen white card in our
own captures is pure `#ffffff`, hard-edged, opaque. The one test that closes the loop
(`A7VK_AB=vcol`, no rebuild) is written and has NOT been run — the GPU was held by an
orphaned `cmr2` that is not mine (see §6).**

---

## 1. The specimen, measured offline (no GPU, no run)

`out/death/control4.ppm.3000` — capture of the current binary
(`97a9eb3b08595858a563282596680401`, the same md5 as `work/PLAY/out-plain/cmr2`):

* **exactly 2 distinct colours in the whole frame** (counted per pixel, all 1,024,000):
  `#9cb4ac` 99.62 % — the 2D backdrop/clear colour — and `#ffffff` **0.38 %** (3,885 px).
* the white is **one hard-edged quad**, not a blob and not a gradient. Per-row extents of
  *exact* `#ffffff`, y = 382…450:

  | row | x span | width |
  |---|---|---|
  | 382 | 581–585 | 5 |
  | 388 | 572–630 | 59 |
  | 405 | 555–616 | 62 |
  | 427 | 532–599 | 68 |
  | 441 | 523–587 | 65 |
  | 450 | 574–577 | 4 |

  corners ≈ **(583,382) (630,388) (576,450) (523,441)** — a rotated convex quad,
  interior uniformly 255/255/255. Centre (576,416) = **45 % across, 52 % down**.

The same region in `out/death/death2.ppm.3000` — **a race frame** from the same binary,
same frame number, 0.0 % backdrop — holds only **729 px of exact white** in
x[526..634] y[379..436] over a field of dirt (`#a47529` `#9c6d20` `#ac7c30` …). Same
screen position, an *eighth* of the white.

Two things follow, and I keep them separate:

1. There is a thing in this port that draws a **hard-edged, fully opaque, pure white
   quad**. That is the visible shape the phone described. Whether it is *the* quad Miami
   saw is NOT established by this measurement (§5, §7).
2. Whether a card that big survives into a live race frame depends on what is in front of
   it: in `control4` almost nothing is drawn (99.6 % backdrop — a frontend screen), so the
   card is whole; in `death2.3000` (the race) the ground is in front of most of it.

---

## 2. Why the port has white to give: the notex A/B, already on disk

`out/ab/abfix.ppm.3590`, a frame taken while `A7VK_AB` was in **notex** mode (proved by the
run's own log, `out/framing1.log:964` — `[AB] frame 3300 -> mode 1`; 3590 is inside that
window; the schedule line at `:60` is `0:normal,3300:notex,3600:normal,…`):

* **near-white pixels: 1,024,000 = 100.00 %**, single 4-connected component, 100 % fill.
  The **entire frame** is `#ffffff` when no texture is sampled.

So on this port, with the texture out of the equation, *every* 3D draw outputs white.
That is not "the geometry is white" — it is the port's colour source: with
`flags.w = 0` the shader takes `base = b.matDiffuse` (`a7vk3d.vert`), and the material is
whatever the game's single `SetMaterial` call left there (the census counts
`SetMaterial=1` in a whole 6 M-draw run, `out/death2.log`).

Two of the phone's candidate mechanisms are therefore **not** the mechanism:

* *(b) "a draw that never got a texture bound"* — an unbound texture would still be
  modulated against the diffuse; the diffuse is what is white.
* *(c) "the blend is carried as opaque"* — relevant in general, but not needed here: the
  specimen card is fully opaque *white*, which is what you get when the **alpha** is taken
  from the material (1.0) instead of from the vertex (the shadow's is 0x32 = 20 %).

---

## 3. The mechanism, from the port's own source and its own census

* `rhi/a7_vk32.c:2620-2623`:
  `b->flags[3] = (g_ab_mode == AB_VCOL || …) ? 1.0f : 0.0f;` — i.e. **unless the A/B env var
  is set, the vertex diffuse is never used**; the comment beside it says so.
* `out/death2.log`, `[CENSUS] DROPPED render states`:
  `141:545898(last=1)` = `D3DRS_COLORVERTEX` **TRUE**, and `145:545898(last=0)`
  = `D3DRS_DIFFUSEMATERIALSOURCE`, both answered `D3D_OK` and dropped. `141`'s last value
  is 1 and `145`'s last value is 0.
* `CMR2Decomp/Graphics.cpp:3520-3566` `Graphics_SetLightingMode(mode)`: modes 0/1/2/4/5 all
  ask for `D3DMCS_MATERIAL`; **mode 3 is the only one that asks for `D3DMCS_COLOR1`** — the
  vertex colour — and mode 3 is "stage ambient + light 0".
* `CMR2Decomp/CarPhysics.cpp:451` `CarPhysics_DrawBodyWheelAndSkidShadows` — the car's body,
  wheel and skid shadow. Its queue call is
  `Quad2D_QueueFixedTriangle(0, &v0, &v1, &v2, NULL, (Quad2D *)10)` (`:418`):
  **`pTexture == NULL`**, vertex colour **black**, alpha 0x32…0xff, layer A, Z-write off.

So the phone's *shape* is right and her *premise* is wrong in a way that matters: the car's
shadow in CMR2 is **not** a soft dark blob drawn with a shadow texture. There is no texture
to bind, and nothing to fix by binding one. It is an untextured world-space triangle fan
whose entire appearance — colour **and** alpha — lives in its vertices. Every channel it
has is therefore discarded by §3's first bullet, and what is left is the material: white,
opaque.

Her test (c) said "a correctly-bound dark texture would STILL come out as a bright card.
Do not rule that out just because the fix is not 'bind the texture'". Measured: it comes
out bright *without* a texture, for the same underlying reason — the port is not reading
the vertex at all.

### Where it already shows in our own instrument

`out/owner6.log`, every frame dump, end of the legend:

```
[OWNER] texIds with draws but no cells: … -1(1 draws/253 tris) …
```

`texId -1` = a draw with **no texture bound on the 3D path** (`ow_note` is only called for
`path3d`, so this draw is `A7FVF_MESH`/0x2d2 — the 48-byte mesh path, `mvp` applied), once
per frame, 253 triangles. 253 triangles is the right order for one car's shadow: 24 body
(octagon ×3), 16 wheels (4 × 4), and the rest the skid trail (`3 × (count+4)`).

**And it owns zero cells.** That is in tension with §1 and I will not paper over it: either
the card is not this draw, or `ow_note`'s clip drops geometry the GPU still rasterises.
Which of the two it is is exactly what §4 decides.

---

## 4. The test that decides it — written, not run

`work/RACE/run_card.sh` — one run, **no rebuild, no source edit**, using the A/B switch that
is already inside the binary:

```sh
cd ~/lena/work/RACE && ./run_card.sh card1
```

* `A7VK_AB="0:normal,3020:vcol,3060:normal,3100:vcol,3140:normal"` — mode 4 (`vcol`) =
  `flags.w = 1` = use the vertex diffuse.
* `A7VK_SNAP="3010,3030,3050,3070,3090,3110,3130,3150:/tmp/card.ppm"` — eight captures,
  **four pairs 20 frames apart**, each pair straddling a switch, so the scene is the same
  and one variable changed.
* Prediction, stated before the fact: **the white card goes dark in the vcol frames and
  returns in the normal ones.** If it does not move, the mechanism in §3 is wrong for this
  card, and the round says so instead of building on it.

Second reading of the same eight frames, free: the car's shadow should become *visible* in
the vcol frames (a dark blob under the car) — that is the fix, before any code is written.

---

## 5. The other three things in the handover, folded in

* **Freeze reproduced (his point 1).** Second data point recorded. The kernel ledger now
  reads `ring gfx_0.0.0 timeout = 12, ring gfx_0.1.0 timeout = 3, MODE2 reset = 14, TCP page
  faults = 3`, i.e. the 12 the brief protects has not moved, and the two fault events of this
  morning are 07:25:40 / 07:31:49 (both `Process cmr2`, `Faulty UTCL2 client ID: TCP (0x8)`,
  `RW: 0x0`). Counted with `journalctl -k --no-pager`, **never `dmesg`** — her warning is
  correct: `dmesg` fails as `deck` and returns a clean zero that means nothing. Every script
  in this round counts with `journalctl`.
* **Car swap works (point 2).** Noted, nothing touched on the car path. Independent support
  in the same capture set: the attract-mode frames move through different cars without a
  load failure.
* **"Textures were overall better" (point 4).** In `progress.md` as his observation, in his
  words, beside the texel-level evidence — not as a number.
* **Debug-state correctness.** Both the shadow's `DrawIndexedPrimitiveVB`-family path and
  the `DrawPrimitiveVB` (0x2d2) layer path were checked in the census: `refusedFvf=0`,
  `unmappedTexOps=0`, `unmappedTexArgs=0` in `out/death2.log`.

---

## 6. Why there is no picture from a run this round

At 08:26:31 an **orphaned** `cmr2` appeared, not started by this round and not started by
any driver that is still alive:

```
530129  1374  08:26:31  3:32  11.4%  /home/deck/lena/work/PLAY/out-plain/cmr2.bak-pre-dxtblt-20261011
                ^ PPID 1374 = systemd --user, i.e. its parent is gone
```

This morning's display death happened with **two `cmr2` on one GPU**, and the phone's
08:10 ticket asked for exactly one guard: *kill by PID, and if a `cmr2` exists that you did
not start, abort*. So I aborted. `run_card.sh` carries the guard: it kills only its own
driver by PID (never `pkill -x cmr2`) and **refuses** on a foreign `cmr2`. That orphan
process is still on the box as I write; whoever owns it should reap it.

---

## 7. What I did NOT claim

* **Not claimed: that the §1 card IS Miami's white box.** It is a hard-edged pure-white quad
  on a screen that is otherwise the frontend backdrop, and a much smaller white patch at the
  same screen position in a race frame of the same binary. The A/B in §4 decides whether it
  is a vertex-coloured draw; nothing here decides whether it is the car's shadow rather than,
  say, the option-menu car preview (worker 2's `MENU-CAR` ticket) — the two runs are at the
  same frame number but in different game states (99.6 % backdrop vs 0.0 %).
* **Not claimed: that the shadow's draw is what lands on screen.** `ow_note` says it owns
  zero cells; §3's draw is one-per-frame with 253 triangles and no texture. Those two
  statements have not been reconciled — that is the open question, and it is the first thing
  to look at with `A7VK_OWNER=1` on the same frames as the A/B.
* **Not claimed: that `flags.w` is the only cause of "LIGHTING IS ALL FUCKED UP".** It is a
  measured cause of *this* class of defect (vertex colour and vertex alpha dropped).
* **Not claimed: the "20.5 % pure white" question is answered.** It is untouched here.
* No source file was edited this round and **this round did not relink or rebuild anything**.
  `work/PLAY/out-plain/cmr2` was `97a9eb3b08595858a563282596680401` when the round began
  (08:22) and is `46ef55760a556186fd75c799d6a9029f` as I write (08:40) — **not my change**: the
  other worker relinked it at 08:38 (`cmr2.bak-pre-txttest-20261011` appeared beside it) while
  my second run was starting, which is why §8's second row is a different program. Flagged
  rather than smoothed over: this is the second time tonight that line has been attributed
  wrongly in a report.

---

## 8. The A/B was then ATTEMPTED, twice, and is VOID twice — recorded so nobody re-learns it

The orphan in §6 exited on its own between 08:36 and 08:37 (`ps` at the end of the first
attempt: *no cmr2 left running*), so `gpu_guard` passed and `run_card.sh` ran.

| attempt | binary it actually ran | outcome |
|---|---|---|
| `card_probe` (08:37) | `97a9eb3b…` (his) | `[CENSUS] draws by FVF: 0x1c4 TL=924455` and **no `0x2d2 MESH` at all** — the stage was never reached. 8 frames, all the same static frontend page (white rule, y=269). |
| `card2` (08:38) | `46ef5576…` (**not** his — see below) | no census FVF line, no stage, 8 frames again identical (white rule, y=329). |

* **Void, both.** A frame that cannot contain a car cannot answer the question. The script now
  prints `NO STAGE -- … the run is void for this ticket` by itself (it greps for
  `0x2d2 MESH=[1-9]`); `out/card2.drive.out` carries that line.
* **The sequence is not what `run_framing.sh` uses.** That calibration is *one* Enter at
  t=12 s and then leave it alone, and its own captures (frames 3290-4510) are stage frames.
  `card2` did that and still sat in the frontend at frames 3010-3150. The `death`/`control`
  runs that DID reach the stage (`out/death2.log`: `0x1c4 TL=1699341 0x2d2 MESH=6344401`)
  pressed Enter **three** times, at t=14/24/34 s. So the reliable recipe for this ticket is
  `SEQ="w14,k=enter,w10,k=enter,w10,k=enter,w45"`, and the first-order fix is a
  **pre-flight stage check**, not more guessing.
* **The binary moved under the run.** `work/PLAY/out-plain/cmr2` was relinked at 08:38 by the
  other worker (`cmr2.bak-pre-txttest-20261011` appeared beside it): md5 `97a9eb3b…` →
  `46ef5576…`. So `card_probe` and `card2` measured two different programs. The second one's
  frames are NOT frames of the binary the ticket is about.
* Both runs are otherwise clean: no process left running, `/tmp/card.ppm.*` consumed, and the
  kernel ledger **12 / 3 / 14 / 3 before and after** (counted with `journalctl -k`).

**Next GPU window, in order:** (1) snapshot the md5 of `out-plain/cmr2` and run against
**that** — `BIN=` a private copy if the other worker is relinking; (2) `SEQ="w14,k=enter,w10,k=enter,w10,k=enter,w45"`;
(3) require `0x2d2 MESH` draws before reading any frame; (4) then `run_card.sh cardN` with the
A/B as specified; (5) then the same frames with `A7VK_OWNER=1` to settle the §3-vs-§7 tension
(does the untextured 3D draw really own no cells?).
