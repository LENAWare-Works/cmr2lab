# D3DRS_AMBIENT — THE r8 / SWEDEN CONTRADICTION IS RESOLVED

Both rounds were measuring correctly and neither was wrong. They were looking at the
same line from opposite ends, and r8 drew the wrong conclusion from a right measurement.

Resolved 2026-10-14 from source. Nothing here is a new hypothesis.

---

## THE SOURCE

`SceneNode.cpp:2449` `Scene_RestoreLights()`:

```c
memset(&g_sceneMaterial, 0, sizeof(g_sceneMaterial));
g_sceneMaterial.diffuse.r = 1.0f;
g_sceneMaterial.ambient.r = 1.0f;      // <-- MATERIAL ambient = (1,1,1) WHITE
g_sceneMaterial.diffuse.g = 1.0f;
g_sceneMaterial.ambient.g = 1.0f;
g_sceneMaterial.diffuse.b = 1.0f;
g_sceneMaterial.ambient.b = 1.0f;
...
g_sceneMaterial.emissive.r/g/b = 0.0f; // emissive is ZERO
g_sceneMaterial.specular.r/g/b = 0.0f;
SetMaterial(&g_sceneMaterial);

{
    BYTE *p = g_sceneAmbientColour;                       // <-- SCENE ambient, track data
    g_sceneAmbientD3D = (((p[3]<<8 | p[0])<<8 | p[1])<<8 | p[2]);   // ARGB
}
SetRenderState(D3DRENDERSTATE_AMBIENT, g_sceneAmbientD3D);         // state 139
```

`SceneNode.cpp:890-907` — the setter that fills it, called per stage:

```c
if (pColour[0] != g_sceneAmbientColour[0] || ...) {
    g_sceneAmbientColour[0..3] = pColour[0..3];
    g_sceneAmbient.x = g_sceneAmbientColour[0] << 16;   // 16.16 fixed copy too
    ...
    g_sceneAmbientD3D = ARGB(p);
    SetRenderState(D3DRENDERSTATE_AMBIENT, g_sceneAmbientD3D);
}
```

And it is re-applied at `Graphics.cpp:3542` and `:3551` around a state restore.

---

## THE DISTINCTION THAT WAS MISSED

D3D7 has **TWO** ambients and the ambient term is their **PRODUCT**:

```
ambient_contribution = M_ambient  ⊗  C_scene_ambient
                       (material)     (D3DRS_AMBIENT = 139)
```

- `M_ambient` = `g_sceneMaterial.ambient` = **(1,1,1)**, set once, never changes.
- `C_scene_ambient` = state **139**, = the **TRACK'S** ambient colour, changes per stage.

So the correct ambient floor is **sceneAmbient / 255**, not 1.0.

---

## WHAT THE PORT DOES

`a7vk3d.vert` computes `shade = matAmbient + key + fill` with `matAmbient` hardcoded to
**(1,1,1)** — this is the same hardcoded `flags.w = 0` at `a7_vk32.c:2752` that the
white-card ticket already names. `rs[A7RS_AMBIENT]` is stored and read by nothing.

The term therefore collapses to **(1,1,1) x 1.0 = 1.0**.

---

## HOW THIS RESOLVES r8 AND SWEDEN

| round | said | verdict |
|---|---|---|
| **r8** | measured `ambient + emissive + sum(diffuse*NdotL)` = **1.0000 for 99.82% of vertices, never below 1.0** | **MEASUREMENT CORRECT.** Interpretation wrong. |
| **r8** | concluded "the lit term is a no-op, Sweden's white-on-white is NOT this term" | **WRONG.** It measured the port's already-amputated term and read that as the term being irrelevant. |
| **SWEDEN** | the port drops the scene ambient, so every lit pixel starts at 1.0 and can only clamp | **CORRECT, and r8's own 1.0000 is its proof.** |

**r8's `1.0000` floor is not evidence the term does nothing. It IS the bug.**
An ambient floor of exactly 1.0 means the surface albedo alone decides the pixel, and any
albedo at or above 1.0 clamps to 255 — which is precisely the flat white field SWEDEN
measured on snow (albedo 0.85-1.0) and the washed, flat Kenya frame r5 measured
(albedo 0.2-0.5, brightens and flattens but keeps ratios).

One defect, two severities, and the stage order matches the complaint exactly.

---

## THE FIX

Feed the scene ambient into the ambient term instead of the hardcoded white:

```
ambient_rgb = (scene_ambient_rgb / 255.0) * (mat_ambient_rgb)     // mat_ambient = 1,1,1
shade = ambient_rgb + key + fill
```

Read it from `rs[A7RS_AMBIENT]`, which is already mapped and stored — this is the six-line
A/B that SWEDEN's section 4 already wrote and that has never been run.

## PREDICTION (SWEDEN's, now derived from source rather than assumed)

- Snow / Sweden: `road_edge` median **0.96 -> 3+**, road band median **206.5 -> toward 100**.
- The general floor drops from 1.0 to the track's ambient, so **every stage gets darker and
  gains contrast**, not just snow.
- If `road_edge` does NOT move, then the ambient is not where Sweden's contrast dies and the
  fog term (same colour source) is next — and this is now testable in the SAME run as the
  fog arm, since both are per-frame alternable state.

## CAVEAT

This is a reading of the GAME, not a claim about your mapping. If your census shows
state 139 being read somewhere, say so and overrule me. r8's number is already on record
and it is a real measurement — it just answers a different question than it was asked.
