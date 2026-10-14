# CMR2 FOG — VERIFIED SPEC

Read out of the decomp at `CMR2Decomp/` (branch `main`), **2026-10-14**, while the Deck was
down. Every line below is quoted from source. Nothing here is inferred from a render.

**This file was corrected within the hour of being written.** The first pass said "fog is a
dropped state, implement it." The runtime census in `docs/S2-CENSUS.md` says something
sharper, and §1 is the correction. Read §1 before anything else.

**Corrected AGAIN, 2026-10-14 evening — the first §1 overclaimed, and it was my error.** It
said the capability bit was *the* gate on fog, i.e. that fixing caps would make fog appear.
That is false. Caps gates fog's **range and mode**. It has never gated fog's **enable**. The
enable comes from the track's own lighting data, on a path with no caps call in it at all.
§1 is rewritten below.

The caps fix was still correct and worth doing — it is why states 35/140/36/37 now arrive,
which is measured. But it was never what was keeping fog off. Two different facts; the first
version of this file merged them, and merged them in the direction that would have sent the
next round looking at the device caps for a value that lives in the track file.

---

## 1. TWO PATHS. ONLY ONE OF THEM IS CAPS-GATED.

### Path A — the ENABLE (`D3DRENDERSTATETYPE` 28 / `0x1c`). NOT caps-gated.

    Race.cpp:760           StageObject_SetLighting(g_unk0x00538238, g_unk0x00538234)
    StageObjects.cpp:5097  g_stageLighting[0x25] = pPrimary->field_0x14
                           g_stageLighting[0x26] = pPrimary->field_0x18
                           g_stageLighting[0x52] = pSecondary->field_0x14
                           g_stageLighting[0x53] = pSecondary->field_0x18
    StageObjects.cpp:5293  if (all four == 0) StageObject_SetForwardedFlareState(0);   // OFF
                           else              StageObject_SetForwardedFlareState(1);   // ON
    StageObject_SetForwardedFlareState  (0x00492fd0)
        -> Graphics_SetFlareStateValue  -> g_unk0x00816704
    Game.cpp:2662          SetRenderState(0x1c, Graphics_GetFlareStateValue())

**There is no `GetDeviceCaps` call anywhere in that chain.** The enable is a *stage-data*
property — four slots taken from the track's lighting presets. The struct:

    struct StageLightPreset {
        FixVector dir;       // 0x00
        int field_0xc;
        int field_0x10;      // 0x10
        int field_0x14;      // 0x14  -> g_stageLighting[0x25] / [0x52]
        int field_0x18;      // 0x18  -> g_stageLighting[0x26] / [0x53]
        BYTE colour[11][4];  // 0x1c
    };

Both preset pointers are filled by `StageObject_BlendSettingPairRecords` (Race.cpp:4385) from
the stage's own setting records. Note the call at Race.cpp:760 passes them in the order
`(g_unk0x00538238, g_unk0x00538234)`, while Race.cpp:4389-4390 assigns
`pPrimary = g_unk0x00538234`. **The two pointers are swapped between those two sites** —
worth one line of checking before anyone reasons about "which preset is primary".

**What the Deck measured:** state 28 set **24,369 times, `uniq=1`, every value 0**, across a
full race stage. That is not the port blocking fog. That is the enable path running correctly
while the *stage data* says "no fog." A caps fix could not have changed that, and did not.

### Path B — the RANGE and MODE (35, 140, 36, 37). THIS is caps-gated.

    void Graphics_EnableFog(void)          // 0x004bcbb0 — sets 35, 140, 36, 37
    {
        if (Graphics_GetDeviceCaps90() != 0) {      // <- the gate, and it is real
            ...
        }
    }
    void Graphics_DisableFog(void)         // 0x004bcc20 — sets 35, 140
    {
        if (Graphics_GetDeviceCaps94() != 0 || Graphics_GetDeviceCaps90() != 0) { ... }
    }

`CGraphics::CacheRenderDeviceCapabilities` (0x004b7210) feeds both getters from the caps the
**port** supplies:

    m_pTextureManager->pD3D->GetCaps(&d3ddesc);          // <- PORT-SUPPLIED
    if ((d3ddesc.dpcTriCaps.dwMiscCaps  & 0x80) != 0)    // D3DPMISCCAPS_COLORWRITEENABLE
        m_d3dDeviceDesc7.field0x90 = 1;                  // <- GetDeviceCaps90()
    if ((d3ddesc.dpcTriCaps.dwRasterCaps & 0x100) != 0)  // D3DPRASTERCAPS_FOGTABLE
        m_d3dDeviceDesc7.field0x94 = 1;                  // <- GetDeviceCaps94()

With both bits zero, `EnableFog`/`DisableFog` are no-ops and 36/37 are never sent — so even a
stage that DID enable fog would have had no range for the port to apply. That is a real bug
and it is fixed.

### Which is which, stated plainly

- **The caps fix was correct and productive.** It landed, and 35/140/36/37 now arrive —
  measured. Keep it.
- **It was never what kept fog off.** Fog is off because the stage data does not enable it.
  Two different facts. The first version of this file merged them.
- **"Implementing fog in the RHI first is dead code" was wrong.** It is the opposite kind of
  wrong from a harmless one: it framed a *range* bug as an *enable* bug.

### Order of work, corrected

1. **Done, keep it:** `GetCaps` reports both bits. Confirmed by census (35 and 140 arrive).
2. **NOW — and it is cheap:** does state 28 ever go non-zero, in *any* stage? Instrument the
   enable value per frame and run more than one stage (the attract route walks
   Kenya -> Sweden -> Greece by itself in ~5 minutes, no keys). If state 28 is 0 in every
   stage, fog is a dead feature in retail CMR2 and leaves the suspect list with evidence.
3. **Only if some stage enables it:** check whether `field_0x14`/`field_0x18` are non-zero in
   the port's own loaded setting record. Non-zero there while slot 0x25 stays 0 means the port
   is dropping them — *that* would be a port bug, and a different one from the caps.
4. **Then** the shader work. The term is already written and measured working when forced.

## 2. STATE 28 IS THE ENABLE — AND THE DECOMP WRITES IT AS RAW HEX

`D3DRENDERSTATE_FOGENABLE` is state **28**, and the decomp writes it as
`(D3DRENDERSTATETYPE)0x1c`, never by name.

That is why `grep -rn FOGENABLE` over the whole game returns **nothing**. It is set at four
sites. **Grep for `0x1c`.**

| where | value |
|---|---|
| `Graphics.cpp:1895` `ConfigureDefaultRenderStates` | `0x1c, 0` — fog OFF at device init |
| `Game.cpp:2662` | `0x1c, Graphics_GetFlareStateValue()` — the live per-frame enable |
| `Game.cpp:2688` | `0x1c, 0` — off for the 2D/billboard pass |
| `Game.cpp:2708` | `0x1c, 0` — off for the 2D layer pass |

Fog is toggled **several times per frame**. Per-draw state, not a global.

---

## 3. "FLARE" IS A MISNOMER IN THE DECOMP

```
Graphics_GetFlareStateValue(void)            0x004bcae0  -> returns g_unk0x00816704
StageObject_SetForwardedFlareState(int)      0x00492fd0  -> writes  g_unk0x00816704
```

Exactly one writer, `StageObjects.cpp:5293-5299`:

```c
if (g_stageLighting[0x25] == 0 && g_stageLighting[0x26] == 0 &&
    g_stageLighting[0x52] == 0 && g_stageLighting[0x53] == 0) {
    StageObject_SetForwardedFlareState(0);   // fog OFF
    g_stageLighting[0x5d] = 0;
    return;
}
StageObject_SetForwardedFlareState(1);       // fog ON
g_stageLighting[0x5d] = 1;
```

There is no lens flare anywhere in this path. **It is the fog enable, derived from the
track's own lighting table.** Four slots (`0x25, 0x26, 0x52, 0x53`) all zero => fog OFF for
that stage; any non-zero => ON. `g_stageLighting[0x5d]` is a shadow copy of the flag.

**Fog must be gated on stage data. There exist stages where the correct behaviour is no fog
at all — that is the control arm.**

---

## 4. THE MODE FUNCTIONS LIE ABOUT THEIR NAMES

| function | addr | what it actually does |
|---|---|---|
| `Graphics_SetFog(start,end,a,b,colour)` | 0x004bcaf0 | stores range, sets FOGCOLOR, sets fog **MODE** LINEAR |
| `Graphics_EnableFog()` | 0x004bcbb0 | re-applies **MODE** LINEAR + FOGSTART + FOGEND |
| `Graphics_DisableFog()` | 0x004bcc20 | sets fog **MODE** to NONE |

**None of the three touch the enable bit (28).** In this codebase "EnableFog/DisableFog"
mean *fog mode*. Mapping them onto state 28 is wrong.

```c
g_fogStart = (float)start * CGraphics::m_oneOver65536;   // 16.16 fixed -> float
g_fogEnd   = (float)end   * CGraphics::m_oneOver65536;
g_fogField1 = (float)a * m_oneOver65536;
g_fogField2 = (float)b * m_oneOver65536;
SetRenderState(D3DRENDERSTATE_FOGCOLOR,
    RGBA_MAKE(colour[0], colour[1], colour[2], 0xff));   // low 3 bytes, alpha forced 0xff
```

---

## 5. RANGE AND COLOUR ARE TRACK DATA

`Track_SetFogAndSkyAlpha(DWORD *pColour, int start, int end)` @ 0x00492fe0
(`TrackCollision.cpp:867`):

```c
Graphics_SetFog(start, end, start, end, *(DWORD *)rgb);
distance = (CGameInfo::GetGraphicsOptionBits21To24() + 2) * 0x320000;
// 0x320000 = 3276800 / 65536 = 50.0 world units
// => distance = (draw-distance option + 2) * 50.0 units
if      (distance <= start) a = -1;    // fully opaque sky
else if (distance >= end)   a = 0;     // sky gone
else                        a = lerp(t, range);
```

**Range and colour are per-track, not constants.** The sky alpha rides the same range so
the sky dissolves as the draw distance reaches into the fog — i.e. **fog is what hides the
draw-distance cut.** Do not invent FOGSTART/FOGEND.

---

## 6. PER-FRAME PASS STRUCTURE (`Game.cpp` ~2640-2690)

```c
SetRenderState(0x1c, Graphics_GetFlareStateValue());   // enable, from the stage flag
Graphics_DisableFog();                                 // MODE <- NONE
Graphics_SetLightingMode(5);
farPlane = CGraphics::m_farPlaneFixed;
CGraphics::SetProjection(0, 0, 0x960000, 0);           // near far plane, 146.5 units
Game_DrawUnsortedNodes(bit);                           // sky/unsorted: NO fog
CGraphics::SetProjection(0, 0, farPlane, 0);
Graphics_EnableFog();                                  // MODE <- LINEAR + START/END
Graphics_SetLightingMode(0);
Game_DrawCulledSectorMeshes();                         // terrain: FOGGED
...
SetRenderState(0x1c, 0);                               // fog OFF for the 2D pass
```

---

## 7. DEPTH AXIS — SETTLED

`D3DRENDERSTATE_RANGEFOGENABLE` (state 48 / `0x30`) is **never set anywhere in the game**
=> default FALSE => fog depth is **camera-space Z**, not radial distance.

For this projection `z_view == w_clip` (already established in `CAMERA-AND-NEAR-PLANE.md`):

```
f = clamp( (FOGEND - w_clip) / (FOGEND - FOGSTART), 0, 1 )
colour = mix(FOGCOLOR, lit_colour, f)
```

---

## 8. THE SIX IMPLEMENTATION CONSTRAINTS

1. **`GetCaps` must report the two cap bits, or the game never sends fog's RANGE and
   MODE (§1, Path B).** DONE — the census shows 35/140 arriving. Note the corrected limit:
   this fixes the range, *not* the enable. The enable is Path A and is stage-driven.
2. **State 28 is the enable. Grep `0x1c`, not `FOGENABLE`.**
3. **FOGSTART / FOGEND arrive as FLOAT BITS inside a DWORD.** The game does
   `SetRenderState(..., *(DWORD *)&g_fogStart)`. `memcpy` the bits back into a float.
   Reading them as integers silently produces a nonsense range that still renders.
4. **Vertex fog, LINEAR. Table fog explicitly NONE.** Not pixel fog.
5. **Fog affects RGB only — not alpha.** D3D7 vertex fog does not touch the alpha channel.
6. **Pipeline order: lighting -> FOG -> alpha test -> blend.** After the texture-stage
   cascade and the lit term, before the alpha test. (The old software rung did fog *before*
   lighting; that is not D3D7's order.) And honour it per draw — the game toggles it
   mid-frame.

---

## 9. PREDICTION (pre-registered, so it can be wrong)

- **Census first:** after the caps change, states 35 and 140 must appear with non-zero
  counts. **RESULT 2026-10-14: they do.** `FOGVERTEXMODE (140) = 3 (LINEAR)`, 17,952 calls;
  `FOGTABLEMODE (35) = 0 (NONE)`, 17,952 calls; 36/37 arrive where round 1 measured them
  absent. The caps fix landed and worked.
- **The real open question, and it is the one that decides whether fog matters at all:**
  does state 28 ever go non-zero, in any stage? Measured so far: **0 in 24,369 calls,
  `uniq=1`, one stage.** If it is 0 in every stage, fog is a dead feature in retail CMR2 and
  leaves the suspect list with evidence rather than with an assumption. If some stage enables
  it, that stage is the only one where the range work matters.
- **Kenya** — far terrain should stop matching near terrain; the one-warm-hue-family
  measurement should break up.
- **Sweden** — sharpest detector. Snow albedo 0.85-1.0 lands on 255 with no fog. Expect a
  depth gradient where there is currently a flat white field.
- **Control** — a stage whose lighting slots `0x25/0x26/0x52/0x53` are ALL ZERO must show
  **no change at all**. If it changes, the gating is wrong.

Method unchanged: arms alternating **per frame** (never by wall clock — the attract demo
does not run the same stage at the same time in two runs), prediction written down before
the run, `ring gfx_0.0.0 timeout` delta must be **0**. A negative is a real result.

This is the spec, not a verdict on the RHI. The RHI is the authority on what is actually
mapped. If the census says state 28 is already mapped and doing something, say so and
overrule me — I have been wrong on this project before and been corrected by measurement
twice.
