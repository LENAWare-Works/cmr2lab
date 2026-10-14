# CMR2 FOG — VERIFIED SPEC

Read out of the decomp at `CMR2Decomp/` (branch `main`), **2026-10-14**, while the Deck was
down. Every line below is quoted from source. Nothing here is inferred from a render.

**This file was corrected within the hour of being written.** The first pass said "fog is a
dropped state, implement it." The runtime census in `docs/S2-CENSUS.md` says something
sharper, and §1 is the correction. Read §1 before anything else.

---

## 1. THE REAL GATE — THE PORT ITSELF TURNS FOG OFF (READ THIS FIRST)

`S2-CENSUS.md` §4.1 lists what the port actually drops at runtime:

```
DROPPED render states (raw state: calls):
  136:9049   141:4525   145:4525   2:1  4:1  8:1  33:1  41:1  138:1  146:1  147:1  148:1
```

**No 28. No 34. No 35. No 36. No 37. Not one fog state.** Every fog state has a source
site in the game (`S2-CENSUS.md` §4 table) and **zero runtime calls**.

That is not the port dropping them. That is the game choosing not to send them — because
the port told it fog is unsupported.

`CGraphics::CacheRenderDeviceCapabilities` (0x004b7210) copies the device's real caps into
the game's own descriptor:

```c
m_pTextureManager->pD3D->GetCaps(&d3ddesc);          // <- PORT-SUPPLIED
...
if ((d3ddesc.dpcTriCaps.dwMiscCaps & 0x80) != 0)     // D3DPMISCCAPS_COLORWRITEENABLE
    m_d3dDeviceDesc7.field0x90 = 1;                  // <- GetDeviceCaps90()
if ((d3ddesc.dpcTriCaps.dwRasterCaps & 0x100) != 0)  // D3DPRASTERCAPS_FOGTABLE
    m_d3dDeviceDesc7.field0x94 = 1;                  // <- GetDeviceCaps94()
```

And the only gate that matters is on `field0x90`:

```c
void Graphics_EnableFog(void)                        // 0x004bcbb0
{
    if (Graphics_GetDeviceCaps90() != 0) {           // <-- ENTIRE BODY IS BEHIND THIS
        SetRenderState(D3DRENDERSTATE_FOGTABLEMODE,  D3DFOG_NONE);
        SetRenderState(D3DRENDERSTATE_FOGVERTEXMODE, D3DFOG_LINEAR);
        SetRenderState(D3DRENDERSTATE_FOGSTART, *(DWORD *)&g_fogStart);
        SetRenderState(D3DRENDERSTATE_FOGEND,   *(DWORD *)&g_fogEnd);
    }
}
```

`GetCaps` returns a zeroed `dwMiscCaps` => `field0x90` stays 0 => **`Graphics_EnableFog()`
is a no-op** => `FOGSTART`/`FOGEND`/`FOGVERTEXMODE` are never sent => the port has nothing
to drop, and a render is unchanged.

### THE CONSEQUENCE FOR THE ROUND

**Implementing fog in the RHI first is dead code and will measure as "no change."**

Order is:

1. **Port `IDirect3D7::GetCaps` and set `dpcTriCaps.dwMiscCaps |= 0x80`
   (`D3DPMISCCAPS_COLORWRITEENABLE`) and `dpcTriCaps.dwRasterCaps |= 0x100`
   (`D3DPRASTERCAPS_FOGTABLE`).**
2. *Then* the game starts sending fog states. Confirm it: state 35 and state 140 should
   appear in the census with non-zero counts, where today they are absent.
3. *Then* map and honour them, and have the shader read them.

Step 2 is a measurement that costs nothing and proves step 1 landed. **If the census still
shows no state 35/140 after the caps change, stop — the caps are not reaching the game and
nothing downstream is worth doing.**

The proxy is deliberate on the game's part: a 1999 title gating vertex fog on
`COLORWRITEENABLE` is a studio using "does this driver expose a modern misc cap" as a
stand-in for "is this a real driver." The port is being classified as an old driver and is
being served the old path. Whether the bit is *correct* is beside the point — the game reads
it, so the port has to answer it.

---

## 2. STATE 28 IS THE ENABLE — AND THE DECOMP WRITES IT AS RAW HEX

`D3DRENDERSTATE_FOGENABLE` is state **28**, and the decomp writes it as
`(D3DRENDERSTATETYPE)0x1c`, never by name.

That is why `grep -rn FOGENABLE` over the whole game returns **nothing**. It is set at four
sites. **Grep for `0x1c`.**

| where | value |
|---|---|
| `Graphics.cpp:1895` `ConfigureDefaultRenderStates` | `0x1c, 0` — fog OFF at device init |
| `Game.cpp:2643` | `0x1c, Graphics_GetFlareStateValue()` — the live per-frame enable |
| `Game.cpp:2669` | `0x1c, 0` — off for the 2D/billboard pass |
| `Game.cpp:2689` | `0x1c, 0` — off for the 2D layer pass |

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

1. **`GetCaps` must report the two cap bits, or the game never sends fog (§1).** Nothing
   downstream matters until this lands and the census shows states 35/140.
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
  counts. Today they are absent. If they are still absent, the caps are not reaching the
  game — stop and report that, do not proceed to shader work.
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
