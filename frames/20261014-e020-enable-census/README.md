# ENABLE CENSUS — RESULT

Round: `FOG-IS-THE-FIRST-STATE-20261014`, continuation of the same day's fog lane.
Run tag `enablecensus`, 2026-10-14 20:34:37 → 20:41:44 EEST, 420 s.

---

## 1. THE ANSWER, IN ONE LINE

**State 28 (`D3DRS_FOGENABLE`, `0x1c`) is ZERO in every one of the three stages the
attract route walked — 25,626 calls across the three race stages, 28,370 calls in
the run, and not one of them non-zero.**

```
[ENABLE] frames=17422 stages=3 mesh_draws=6519149 gap=24
[ENABLE] epoch=0 frames=1..2752      calls=2744  nonzero=0  vals: 0:2744     <- frontend
[ENABLE] epoch=1 frames=2752..8068   calls=8775  nonzero=0  vals: 0:8775     <- stage 1
[ENABLE] epoch=2 frames=8068..14922  calls=11852 nonzero=0  vals: 0:11852    <- stage 2
[ENABLE] epoch=3 frames=14922..17421 calls=4999  nonzero=0  vals: 0:4999     <- stage 3
[ENABLE] TOTAL calls=28370 nonzero=0
[ENABLE] IN-STAGE (epoch>=1) stages=3 calls=25626 nonzero=0
```

**My prediction was that it would be 0 everywhere, and it holds.** The value
histogram is the strong form of that: not "0 on average" but **one single value
observed, `0`, in every stage**. There is no second value to find.

**What this settles.** Fog leaves the suspect list for retail CMR2 on these
tracks, with evidence. The caps fix stays and is not wasted — it is why states
35/140/36/37 arrive at all — but it could never have turned fog on, because the
enable is a different path and that path says no. The range work stays dormant
and correct, which is exactly the outcome the brief set up as the expected one.

---

## 2. THE EPOCH DETECTOR IS NOT TAKING MY WORD FOR IT

The result is only worth anything if the three "stages" are three stages. The
epochs come from the RHI's own view — a stage is a run of frames drawing meshes
(FVF `0x2d2`), separated by ≥24 frames with none. That is a heuristic, so it was
checked against a signal it does not use: **the game's own `[RT F]` per-frame
race log**, which carries `RallyDataState()` independently.

| my epoch | opens at frame | game's own race transition | delta |
|---|---|---|---|
| 1 | 2752 | `state 8` at frame 2757 | 5 frames |
| 2 | 8068 | `state 8` at frame 8070 | 2 frames |
| 3 | 14922 | `state 8` at frame 14923 | 1 frame |

The transitions in the game log are exactly three, and nothing else in 10,977
`[RT F]` lines looks like one:

```
frame 2757  state 8      frame 8067  state 5   (transition)
frame 6031  state 9      frame 8070  state 8   <- stage 2
frame 12969 state 9      frame 14920 state 13  (transition)
frame 14921 state 5      frame 14923 state 8   <- stage 3
```

Three stages, three matches, and the attract route is documented as
Kenya → Sweden → Greece. The epochs are stages.

---

## 3. THE TWO CORRECTIONS IN THE BRIEF, CONFIRMED INDEPENDENTLY IN SOURCE

Both were checked against the decomp in-tree, not accepted on the message.

**3a. The enable is not caps-gated — `Graphics_EnableFog` contains no state 28.**

```
void Graphics_EnableFog(void)
{
    if (Graphics_GetDeviceCaps90() != 0) {
        SetRenderState(D3DRENDERSTATE_FOGTABLEMODE,  D3DFOG_NONE);
        SetRenderState(D3DRENDERSTATE_FOGVERTEXMODE, D3DFOG_LINEAR);
        SetRenderState(D3DRENDERSTATE_FOGSTART, *(DWORD *)&g_fogStart);
        SetRenderState(D3DRENDERSTATE_FOGEND,   *(DWORD *)&g_fogEnd);
    }
}
```

The caps gate is on the **mode and range** and on nothing else. There is no
`D3DRENDERSTATE_FOGENABLE` (nor `0x1c`) anywhere in that body. So the corrected
spec's §1 is right: PATH B is the caps gate, PATH A is not.

**3b. There are two paths, and only one is caps-gated.** Source of the four
state-28 sites and the enable's origin:

| site | what it writes |
|---|---|
| `Graphics.cpp:2056` `ConfigureDefaultRenderStates` | `0x1c, 0` — fog off at device init |
| `Game.cpp:2709` | `0x1c, Graphics_GetFlareStateValue()` — the live per-frame enable |
| `Game.cpp:2735` | `0x1c, 0` — off for the 2D/billboard pass |
| `Game.cpp:2755` | `0x1c, 0` — off for the 2D layer pass |

and the only feeder of `Graphics_GetFlareStateValue()`, at
`StageObjects.cpp:5301-5309`:

```c
if (g_stageLighting[0x25] == 0 && g_stageLighting[0x26] == 0 &&
    g_stageLighting[0x52] == 0 && g_stageLighting[0x53] == 0) {
    StageObject_SetForwardedFlareState(0);   /* fog OFF */
    ...
}
StageObject_SetForwardedFlareState(1);       /* fog ON */
```

`[0x25]/[0x26]` come from `pPrimary->field_0x14/0x18` (`StageObjects.cpp:5193-5194`)
and `[0x52]/[0x53]` from `pSecondary->field_0x14/0x18` (`:5198-5199`) — **track
lighting data**, exactly as the correction says. `"flare"` in those names is a
decomp misnomer; the path is the fog enable.

### ON THE LINE NUMBERS — one point worth recording, not a dispute

The brief gives the four sites as `Graphics.cpp:1895`, `Game.cpp:2662/2688/2708`.
**In the tree as it stands they are `Graphics.cpp:2056` and
`Game.cpp:2709/2735/2755`, and the code at each is exactly what the brief
describes.** `CMR2Decomp/Game.cpp` and `Graphics.cpp` have been edited since the
spec was written (the working tree is live — `git status` shows modifications
across the decomp), so the numbers moved under it. The brief's numbers were
correct when written; both sets name the same four statements. Anyone following
a citation should grep `0x1c` rather than trust either set, which is the spec's
own §2 advice.

---

## 4. THE FLAGGED POINTER SWAP — CHECKED, ONE LINE AS ASKED

**The swap is real, and it is between the two asymmetric consumers.**

```
Race.cpp:790    StageObject_SetLighting((const StageLightPreset *)g_unk0x00538238,
                                        (const StageLightPreset *)g_unk0x00538234);
                ^^ arg 1 (pPrimary)               ^^ arg 2 (pSecondary)

Race.cpp:4485   pPrimary   = g_unk0x00538234;
Race.cpp:4486   pSecondary = g_unk0x00538238;
```

Within one `StageObject_SetLighting` call the two pointers are opposite. So
`g_stageLighting[0x25]/[0x26]` and `[0x52]/[0x53]` — the pair that feeds the
**fog enable** and `Track_SetFogAndSkyAlpha` — are filled from the opposite
record to the one `Race.cpp`'s own `pPrimary`/`pSecondary` names.

**What this does and does not change:**

- It does **not** weaken §1 above. The four-zero test is a condition on all four
  slots *together*, so swapping which record feeds which pair cannot turn a
  four-way all-zero into a non-zero or back. The enable came out 0 in all three
  stages either way, and this census would have read the same with the pointers
  the other way round.
- It **does** matter for anyone reasoning about which preset is primary — e.g.
  which of the two records the fog range comes from on a stage that does have
  fog, or the sun-direction/asymmetry work (`pPrimary->dir` at `StageObjects.cpp:5113`).
- It is **not** symmetric everywhere: the colour average at `Race.cpp:4488` is
  `(pSecondary[0x48+i] + pPrimary[0x48+i]) / 2`, which is order-independent and
  so is unaffected. The asymmetry is in the lighting slots, not there.

Flagged as the brief asked — **as a thing to check before reasoning about which
preset is primary, not as a claimed bug.** I have not changed it.

---

## 5. WHAT WAS RUN, AND WHAT WAS NOT

**Run:** ONE binary, `enable-census-cmr2`, md5 `6f75655f0abcee94e8305183857bc393`,
`.text` from that link, on the attract route with **no keys injected, no synthetic
input, no `A7VK_FOGFORCE`, no `A7VK_SNAP`, no new recipe**. The only difference
from a plain play run is `DECK_ENABLE_CENSUS=1`. 420 s.

**Gate, all as required:**

| check | result |
|---|---|
| windows on his display | **0** |
| ring `gfx_0.0.0` timeout delta | **0** |
| panics / signal 11 | **0 / 0** |
| his binary `PLAY/out-plain/cmr2` md5 before/after | `8dbc7339c23a36b14cfef2571558c315` / **same, UNCHANGED** |
| `[RT F]` race frames | 10,977, of which 10,670 at `state=8` and 10,542 with the car moving |

**NOT done, on purpose:**

- **The forced-fog experiment was not re-run.** It already answered its question
  (fogC vs fogD: cross-arm signed mean delta **+11.74 luma forced vs −1.07
  unforced**, an 18× difference; ring delta 0). Re-running it would be motion.
- **No pixels were compared and no frames captured for this question.** The
  census leaves no `A7VK_SNAP` set; the 174 files in `frames/` are the previous
  round's, untouched. A visual result is a later round's job, and only if the
  enable had turned out non-zero.
- **Nothing was installed.** `PLAY/out-plain/cmr2` was read for its md5 twice and
  never opened for write.

---

## 6. HOW THE INSTRUMENT WORKS, AND THE TWO BUGS IT SHIPPED FIRST

The census hooks `a7_set_render_state` in `src/a7_vk32.c` — the single funnel every
render state passes through, which carries the game's own value for state 28.
Two triggers feed stage attribution: `a7vk_draw_core` (mesh draws, FVF `0x2d2`)
and `a7_present` (frames). Source and hooks are recorded in `PATCH-AS-APPLIED.md`.

**No game object was rebuilt, and that is a constraint, not a preference.** An
earlier pass also instrumented `StageObject_SetLighting` for the four fog
coefficients per stage. That requires replacing `obj-epoch/StageObjects.o`, which
**cannot be done on this base**: the tree's headers have drifted from his frozen
objects — measured, `Collision_ResolveStaticObstacleContact` is
`(int,int*,int,int)` in the tree and `(int,int,int,int)` in his object — so a
`StageObjects.o` compiled today leaves four undefined symbols and does not link.
Dropped, not worked around. The census needs the **enable value**, which the RHI
sees directly; the coefficients are the static half and stay readable in source.

**Two bugs in my own instrument, both caught before the run was believed:**

1. **The first version hooked `s == 28` and counted 0 calls.** The RHI sees the
   *remapped* enum, not the raw D3D state number — `A7RS_FOGENABLE` is `12`, and
   `deck_dd7.cpp` maps `D3DRENDERSTATE_FOGENABLE → A7RS_FOGENABLE` before calling
   through. The smoke run reported `TOTAL calls=0` and, worse, still printed a
   verdict. The verdict is now unreachable with `tot == 0`: a census that counted
   nothing is a **broken instrument, not a negative result**, and says so.
2. **The first version opened an epoch from the frame tick**, so it opened one
   every 24 quiet frames and left **255 empty epochs**, which the dump printed as
   "255 stages". Nothing opens an epoch now but the mesh draw, and an epoch
   cannot exist without mesh draws. The 255-stage line was visible in the smoke
   log before the real run and is why the smoke run was done.

Both are reported because the result is only as good as the instrument, and the
instrument was wrong twice on the way.

---

## 7. WHAT FOLLOWS

**Fog is settled as a suspect.** The one measurement that decided it has been
made, and it decided against. The range/mode work stays in the tree, correct and
dormant, for the day a stage that wants it turns up.

The next open item in this lane is unchanged and is **not** fog:
`D3DRS_AMBIENT` (state 139) — **534,078 calls, mapped, stored, read by nothing**
(`grep A7RS_AMBIENT a7_vk32.c` = 0 consumers). Measured in the race band with 12
distinct values, all discarded, in a lighting equation that is also missing the
scene-ambient term (`DEATH-AND-LIGHT.md` §2.2 B1/B2). That is a live defect with
a much larger blast radius than fog ever had, and it is where the next round
should go.
