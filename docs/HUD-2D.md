# HUD-2D — is the in-race HUD on the transformed-lit 2D path, and is 336→5 the same bug?

`work/HUD-2D`, 2026-10-11 11:0x EEST. Worker (this round): the phone's 10:05 question
about Miami's race screenshot — sky + one dark mottled mass, **no car, no road, NO UI
at all**, and the number I measured earlier: 2D transformed-lit draws (FVF `0x1c4`)
collapse **336/frame (frontend) → 5/frame (race)**.

**ANSWER, in one line, for each of the three things asked:**

1. **Is the in-race HUD on that same path?  YES — all of it.** Text is
   `Font_DrawText` → `Font_DrawChar` → `Sprite_Queue` → `Sprite_DrawLayer` →
   `DrawPrimitive(TRIANGLESTRIP, D3DFVF_TLVERTEX /* 0x1c4 */, 4 verts)` — one draw per
   glyph/sprite. The panels/rects are `Quad2D_QueueFixedTriangle` → `Quad2D_DrawLayer`
   → `DrawPrimitiveVB` on the same TL vertex buffer (a7 stride 32). Dash, stage clock,
   car HUD, co-driver call slots: all of it.
2. **Is "336 → 5" the same bug as "no UI"?  Same transition, NOT the same cause.** In
   the race where the 5 happens, the game itself never asks for the HUD. Measured, not
   inferred: `Sprite_Queue` == `Sprite_DrawLayer` exactly (100 per 20-frame interval,
   both), so **nothing is dropped**. The 5 surviving draws are enumerated in §3.
3. **(a) or (b)?  (a) the game never asks** — in that state. And in a player race the
   same binary and the same 2D path carry the whole HUD (§5) — 66–70 sprite draws per
   frame, of which ~63 are glyphs, with `Sprite_Queue` == `Sprite_DrawLayer` to within
   176 draws out of 1,452,997 over the run. The port is not refusing 2D draws; it is
   not being asked.

**Correction to my own earlier number, stated first because it changes the reading:**
the census line `draws by FVF` counts `DrawPrimitive`/`DrawIndexedPrimitive` only —
`DrawPrimitiveVB` bumps `cm_draw_prims[]` but **not** `cm_draw_fvf[]`
(`deck_dd7.cpp:1394-1396`). Every `Quad2D_DrawLayer` flush is a `DrawPrimitiveVB`, so
the race's "5" is *sprites only*. The same races carry **2.0 `DrawPrimitiveVB`/frame**
(median, 27 runs, §6.3) — 2D quads the FVF line never counted.

---

## 1. THE PATH, IN THE GAME'S OWN CODE (static)

| what the HUD draws | call chain | primitive | FVF |
|---|---|---|---|
| every glyph (timer, splits, gear, position, names) | `Font_DrawText` → `Font_DrawChar` → `Sprite_Queue` → `Sprite_DrawLayer` | `DrawPrimitive(TRIANGLESTRIP, …, 4)` | **0x1c4** |
| dash panels, dial face, mph plate, gear marker, route boxes | `Sprite_FillRect` / `Quad2D_QueueFixedTriangle` → `Quad2D_DrawLayer` | `DrawPrimitiveVB(TRIANGLELIST, …, n)` | TL VB (32-byte stride) |
| needles, split bars, call-slot triangles | `Tri2D_Queue` → `Tri2D_DrawLayer` | `DrawPrimitive(TRIANGLELIST, 3·count)` | **0x1c4** |
| projected car marker / co-driver text | `Font_DrawText` (same as row 1) | `DrawPrimitive(TRIANGLESTRIP, …, 4)` | **0x1c4** |

* `D3DFVF_TLVERTEX` = `XYZRHW|DIFFUSE|SPECULAR|TEX1` = **0x1c4** (`Sprite.cpp:177`).
* The two halves sit in one frame at the end of `Game_DrawSceneViewport`
  (`Game.cpp:2665-2778`): `Sprite_DrawLayer(4)`/`Tri2D_DrawLayer(4)`/`ScreenLine2D_Draw(4)`
  before the 3D, `Sprite_DrawLayer(1,2,3)` + `Tri2D_DrawLayer(1,2,3)` after it, and
  `Quad2D_DrawLayer(8/0x10/0x20/0x40)` inside it.
* The whole in-race HUD block is one function:
  `RallyData_UpdateViewFrameAndDebugOverlay()` (`RallyData.cpp:6207`), called from the
  in-race state table's *render* callbacks (`Game.cpp:1385-1400`). The dash, the car
  HUD and the call slots live behind **`if (RallyDataState() == 1 && param3 != 0)`**.
* The stage clock is a separate gate: `if (CGameInfo::GetGameModeOptionBit19() != 0)
  { … StageTiming_DrawClockAndCountdown(); }` (`RallyData.cpp:6392-6399`).

## 2. WHAT WAS BUILT TO SEE IT (all env-gated, inert when unset)

`patch_hudtrace.py` (this round, 17 insertion sites, 8 files, `--revert` provided,
`.bak-pre-hudtrace` backups). Both ENDS of the 2D path are counted, so "the game never
asked" and "the port did not deliver" cannot be confused:

* **producers** `Sprite_Queue` (per layer), `Font_DrawText`, `Font_DrawChar`,
  `Quad2D_DrawLayer` (quads queued)
* **consumers** `Sprite_DrawLayer` (sprites handed to `DrawPrimitive`, per layer, with
  dst rect + texture name), `Quad2D_DrawLayer` flushes, `Tri2D`, `Line2D`, `ScreenLine2D`
* **gates** every entry of `RallyData_UpdateViewFrameAndDebugOverlay` split by
  `param3`, both of its early returns, its two HUD blocks, `Dash_Draw` (+ the driver
  record bit that decides whether a player has a dash), `RallyData_DrawAndHandleCarHUD`,
  `Race_DrawPlayerCallSlots`, and `StageTiming_DrawClockAndCountdown` (+ the
  result-table byte and `optBit19` it is gated on)
* **`LenaHudFrame()`** prints one `[HUD2D]` line per 20 frames from
  `CGame::DispatchFrontendResourceState` (`main.cpp:86` calls it every frame in **every**
  resource mode), so the census lands **on the same timeline as `[MODE]`** — the exact
  thing the phone asked for in question 2.
* `DECK_HUD_TRACE=1` counters, `=2` also dumps individual sprites (`[HUDSPR]`),
  texts (`[HUDTXT]`) and quad layers (`[HUDQ2]`) inside the in-race modes, plus an
  on-screen/off-screen split for every sprite.

Binaries (all from the same tree, `!` = this round's builds):
`out/cmr2` md5 `93c7ec27…` (run `hud1`), `out2/cmr2` md5 `a24ea91d…` (run `hud2`),
`out3/cmr2` md5 `80d927b5…` (run `hud3`). Kernel ledger unmoved: `ring gfx_0.0.0
timeout` 12, `MODE2 reset` 14 before and after every run.

## 3. THE 5 DRAWS, NAMED (hud3, mode 3, frame 2760, dumped)

```
[HUDSPR] layer=2 i=0 dst=1089,-216 278x232 tex=128x128  ".\Textures\NEWIMAGE\sunglow.DDS"
[HUDSPR] layer=2 i=1 dst=60,66  27x57 tex=512x512 ".\Fonts\general\hel_36pt.tga"
[HUDSPR] layer=2 i=2 dst=87,66  29x57 tex=512x512 ".\Fonts\general\hel_36pt.tga"
[HUDSPR] layer=2 i=3 dst=116,66 42x57 tex=512x512 ".\Fonts\general\hel_36pt.tga"
[HUDSPR] layer=2 i=4 dst=158,66 29x57 tex=512x512 ".\Fonts\general\hel_36pt.tga"
[HUDTXT] font=2 xy=60,111 "demo"          <- the four glyphs,  80x per race dump
```

So the five are: **one `sunglow.DDS` sprite drawn at dst y = −216 (off the top of the
screen — it can never be visible) and the four glyphs of the word `demo` in
`hel_36pt.tga` at the top-left**. Nothing else in the 2D path is submitted in that
frame. 100 queued → 100 drawn per interval; on-screen/off-screen = 80/20 per interval
(4 on + 1 off per frame). The picture Miami is looking at **is a demo session, and the
game is telling us so in 36-point text.**

## 4. WHY: WHICH GATE CLOSED — `param3`, and the state that decides it

`[HUD2D]` steady state in that race (`hud3`, f=2780 … 6600, 190 intervals in a row):

```
mode=3 | SQ 0 100 0 0 | SD 0 0 100 0 | DASH 0/0 | HUDVIEW 0/[20] r=0/0 s1=0 s2=0
       | carhud=0 calls=0 | CLK 0/0/0 | FT 20 (1 text/frame = "demo")
```

* `HUDVIEW 0/20` — `RallyData_UpdateViewFrameAndDebugOverlay` is entered **20/20 frames
  with `param3 == 0`**. Its HUD block needs `RallyDataState()==1 && param3 != 0`. `s1=0`
  for the whole race → `Dash_Draw`, `RallyData_DrawAndHandleCarHUD` and
  `Race_DrawPlayerCallSlots` are **never called**.
* `CLK 0/0/0` over >10,000 in-race frames: `StageTiming_DrawClockAndCountdown` is never
  entered at all, because `hud.optBit19 = 0` gates it out earlier in the same function.
  (Noted separately, and it is a *second*, independent reason the stage timer is absent
  — it is also absent in the player race of §5.)
* `r=0/0`: neither early return (in-race menu, championship final stage) fired. The
  function ran to its end, every frame, and drew nothing — because of `param3`.
* **`param3` is not a port flag.** It is the *variant of the render callback* the
  in-race state machine installs for the current state (`Game.cpp:1385-1400`):
  state 5/7/8 pass **1** (`GrowEntry…`), state 10/13 pass **0** (`ShrinkEntry…`).
  And `[RACE]` says which state the race is in:
  **`hud3`/`geo3`: `s0.state=13` (130/82 samples) → `ShrinkEntryAndDrawStageStarted` →
  param3=0 → no HUD.** `hud2`: `s0.state=8` (342 samples) → `Race_UpdateDriverCountdown`
  → `GrowEntryPanel` → param3=1 → HUD.

## 5. THE COUNTEREXAMPLE THAT SETTLES (a) vs (b): a player race, same binary family

Run `hud2` — one Early `Enter` at t=8 s, after which the attract drives the menus to
**Single Stage / Finland / `FINhit.bfl`** (`gmode=1`) instead of the attract's own demo.
Same instrument, same 2D path, steady state for thousands of frames:

```
mode=3 | SQ 0 1380 40 0 | SD 0 0 1380 40 | Q2 1760 0 … fl=20 | TRI 80 LN 200
       | FT 220 FC 1360 | DASH 20/20 | HUDVIEW 20/[0] s1=20 carhud=20 calls=20
       | CLK 0/0/0   (param3 = 1 on 20/20 frames, HUD block entered 20/20)
```

* **66–69 sprites/frame queued on layer 2 and 66–69 drawn; 2/frame on layer 3 queued
  and 2 drawn** — `SQ == SD` frame for frame.
* **~63 glyphs/frame** (`Font_DrawChar`) — that is the HUD text (dash gear letters,
  speed, car HUD), not menu text: the frontend's own `[HUD2D]` lines in the same run are
  200–314 sprites/frame = 300 glyphs/frame, an order of magnitude apart.
* `DASH 20/20` (dash drawn every frame, driver record bit 0x10 = 16 set),
  `carhud 20/20`, `calls 20/20`.
* Whole-run accounting against the RHI's own census in that run: game-side sprites
  **1,452,997**, RHI `0x1c4` `DrawPrimitive` **1,469,045** — agreement to 1.1 %;
  `Quad2D` flushes 23,043 (game) vs `DrawPrimitiveVB` 54,294 (RHI, and a flush can be
  several calls). `refusedFvf=0` in every census.

**So "the HUD has never drawn once in a race on this port" is false.** It draws, every
frame, in a player race. What has never drawn, in *any* state measured here, is the
stage clock — and that is the `optBit19` gate, not the draw path.

## 6. ANSWERS TO THE THREE MEASUREMENTS THE PHONE ASKED FOR

### 6.1 What are the 5? Where did the other ~331 go?
Answered in §3/§4. Not dropped: **not submitted.** `Sprite_Queue == Sprite_DrawLayer`
exactly; `refusedFvf=0`; the only 2D calls the port sees are the ones the game makes.
The ~331 are the frontend's menu sprites (200–314/frame at the main-menu screens,
`[HUDSPR]` names them: `cmr2.tga`, `Copyright1-4.tga`, then font glyphs) — the frontend
draws a full screen of text and panels; the demo race draws "demo".

### 6.2 Is the collapse tied to the RESOURCE MODE 0→3 switch?
It happens **at** the switch and is not **caused** by it. On one timeline (`[MODE]` and
`[HUD2D]` are printed from the same per-frame hook):
`[MODE] 0→3` at f≈2749 → one transition interval (f=2760: 5,949 sprites, the loading
text) → from f=2780 onward exactly 100/interval in every mode-3 line. What changes at
that instant is the *render callback variant* (`param3`), i.e. the game's own state, not
a surface. **There is no evidence of the port invalidating the frontend's 2D surfaces on
the transition**: the same surfaces are used afterwards (§3: `sunglow.DDS` and
`hel_36pt.tga` are bound and drawn), the same run's frontend sprites never stop being
queued, and `CreateSurface`/`Lock` counts are unchanged across the switch
(`[CENSUS] methods`). The one surface-lifecycle event in this area is
`StageTiming_RestoreDeviceStageResources()` (`StageTiming.cpp:9345`), which re-uploads
every live texture with a dummy `0x1c4` triangle — called once, from
`InRaceMenu_AdvanceCascade` on the way *out* of a race, not on the way in.

### 6.3 (a) the game never asks, or (b) the port does not deliver?
**(a)**, in the state that produced the 5. And where the game does ask (§5), the port
delivers every draw — so (b) is not merely unproven here, it is contradicted for the
sprite half of the path, and the quadrant half is delivered too
(`DrawPrimitiveVB` median 2.0/frame in 27 race runs, 0/frame in the frontend,
`refused_by_backend=0` everywhere).

## 7. IS "336 → 5" A RED HERRING? — my own verdict, since I measured it

**Half a red herring, and the half that is real is not the half that was assumed.**

* **Wrong as a proxy for "HUD loss":** it counts one of the two 2D paths (sprites; not
  `DrawPrimitiveVB`), and in the runs it was measured on the game was asking for
  nothing, so it could not have measured a drop even in principle.
* **Right as a tripwire:** it changes on exactly the transition where the HUD
  disappears, and it goes back up (5 → 66–70) exactly when the HUD comes back. It is a
  usable *alarm*, with no explanatory power about *why*.
* **The number that would have settled it in the first place** is the pair
  (producer, consumer): `Sprite_Queue` vs `Sprite_DrawLayer`, per layer, per frame.
  Those two are available now and they agree in every state measured.

### 6.4 The route is not deterministic, and one more demo state exists (run `hud4`)

The same "one early Enter" shape that reached a **player race** in `hud2` produced a
**demo** in `hud4` (same md5 `80d927b5…` binary, `w8,k=enter,w45,…`): `[MODE] 0→3` →
`KENhit.bfl`, `s0.state=13` in **200 of 200** `[RACE]` heartbeats, `HUDVIEW 0/0` — i.e.
in that state `RallyData_UpdateViewFrameAndDebugOverlay` is **never called at all** (the
render callback of that state is the loading screen, not a view frame), and the frame is
nonetheless a rich picture (8,687 distinct colours sampled, 8–37 % pure white). Its
first in-race interval does dump a dash sprite on layer 3 (`REVDIGIT`, dst 974,594)
which then stops. **Consequence for the phone's question: "no UI" has at least three
looks on this port — (i) demo/fade-out state, 5 sprites and the word `demo` (§3);
(ii) loading-screen render of the same state, no 2D view frame at all; (iii) player
race, full HUD (§5) — and only a capture from his own session can say which one he is
looking at.**

## 8. STILL OPEN, AND THE NEXT CHEAPEST TEST (stated, not hidden)

* **The phone's frame has zero glyphs; the demo state draws four.** My capture of that
  state (hud3.02_t115.ppm, `[MODE] 0→3`, `s0.state=13`) is 95.9 % one colour with a pale
  diffuse blob, a slightly brighter lower band, and the word *demo* in white at
  (60…200, 66…123) — measured, `distinct=16-31, lum 171→255` in that box versus a
  *flat* 1-colour control box beside it. If Miami's frame genuinely has no glyph
  anywhere, then either (i) it is one of the sub-states where `RallyData_UpdateViewFrame-
  AndDebugOverlay`'s own early paths suppress even that text, or (ii) the font texture is
  arriving non-image-like *in his session*. **The separating test is one capture from his
  own session with `DECK_HUD_TRACE=2 DECK_FE_TRACE=1` on**: the `[HUD2D]`/`[HUDTXT]`
  lines then say which of the three states his race is in, and whether the glyphs were
  queued at all.
* **Not measured this round:** the on-screen/off-screen split *inside a player race*
  (the v3 counters exist, but the two player-race runs I have were made with v2). Until
  that is run, "the HUD is queued and drawn" is measured, and "the HUD lands on screen
  in a player race" is inferred from (i) the same path drawing on-screen in the demo
  state and (ii) dst rects computed from `resX/resY` — not yet counted.
* **Not this lane:** the car and the road are not in the 2D path at all (§1); "no car,
  no road" stays with `WHITE-BOX-UNDER-CAR` / `FINDING-TRACK-DETAIL-PRINT`.

## 9. HOW TO RE-RUN

```
python3 work/HUD-2D/patch_hudtrace.py            # idempotent; --revert to undo
OBJ=… OUT=… sh work/RACE/build-plain-race.sh     # builds only the game objects
BIN=work/HUD-2D/out3/cmr2 work/HUD-2D/run_hud.sh hud5 260 "<seq>"
python3 work/HUD-2D/analyze_hud.py out/hud5.log   # the [HUD2D] table + dumps
```
Sequences that matter: `w12,k=enter,w200` / no key → attract demo, `s0.state=13`,
no HUD. `w8,k=enter,w52,…` → attract drives the menus → Single Stage Finland,
`s0.state=8`, full HUD.
