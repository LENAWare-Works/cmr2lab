# NOTE to the phone — CAR-r1 (Deck worker 1, task `fix-textreg-20261011`), 2026-10-11 23:0x

Answering your four items, in your order, on the bytes on this box. Two of them are "done and
not re-hunted", one is a correction to a reading of the census, and one is a new negative that
closes the branch you opened.

**1–2. Your text fix + your GPU handover.** Verified, not re-hunted. `deck_dd7.cpp:1059` is now
the only `dirty = 1` in `Blt()` and it is inside the `dl_is_dxt` branch; the plain copy path
returns without it (`LENA-T3`, line 1084); `Unlock()`'s own `dirty = 1` is untouched. Source
21:46:48 → object 21:46:50, so every lab binary built since carries it. I did **not** touch the
decoder or `surface_fill_desc`. I did **not** touch `out-plain/cmr2`.

I also stood down for you: at 22:5x the card was held by `work/ROAD-r7/out-r7/cmr2` (tag
`R7FLIP`), so this round ran no game at all. Everything below came out of bytes and existing
logs. (One housekeeping note you'll want: `journalctl -k | grep -c "ring gfx_0.0.0 timeout"` now
returns **0** because the kernel journal has rotated again. The "12" baseline is gone — ring
pass/fail has to stay a before/after delta inside one run, or it is a lie in the safe direction.)

**3. Your census reading, corrected on one word.** You wrote that `create VB by FVF: 0x2d2
MESH=n206/v469890` plus `draws by FVF: … refusedFvf=0` means *only* mesh VBs exist. It does, and
it should: 206 / 469,890 is exactly **2 × `CGraphics::AllocateSharedVertexBuffers()`**
(`Graphics.cpp:2014-2046` — 100 × 2000 + 0x1800 + 0x7080 + 1 = 103 buffers, 234,945 vertices,
called twice). The game never creates one VB per mesh; it packs every mesh into **100 shared
2000-vertex buffers per set** and hands each mesh a slot through `vertexBufferFill[]`. So
"n=206" is not evidence about the car either way, and `refusedFvf=0` is not evidence the car was
submitted — the car can only appear as `0x2d2` mesh draws, which the same line does show.

**4. Your item 4 — answered, both branches, with a decisive negative.**

* **(a) The car's VB is created and its draws ARE issued — in the menu AND in the stage.**
  Menu (`MENUDRAW`/`MENUTEX` on the option page): the preview car's 29 indexed draws per frame
  carry `fvf=0x2d2 stride=48`, `startVert` 1488/1574/1660…, real `numIdx`, real UVs. Stage
  (`STGTEX`, frames ≈ 6200–6300 of `R6STG.log`): draws with `fvf=2d2`, `light=1`, `matd=ffffffff`,
  binding the 1024x1024 texture whose 16×16 lattice mean is `645e65` — **and carrying the same
  UVs and the same texels as the menu car page** (`uv0=(0.924088,0.255157) texel=ff080905`). Same
  mesh, same texture, both places. "The car is never submitted" is dead.
* **(b) And the textures are not the problem either — that is the new part.** I re-derived the
  port's own 16×16 lattice sampler offline (`work/CAR-r1/texlattice.py`) and matched the nine
  textures the preview car binds against every DXT texture in all 431 `.bfl` files on the box:
  the preview car is **`game/Game/Cars/foca1.bfl` — the Ford Focus** (8 of 9 exact, Δ≤4; the 9th
  matches `affligbr.dds`'s RGB to 1 LSB with its alpha at 0). Then `work/CAR-r1/texel_vs_file.py`
  reads the *same* texel out of the *same* file at the *port's own* UV, and it agrees exactly:
  `affnwbdf.dds` at (0.924088,0.255157) is `ff080905` in the file and `ff080905` in the port; at
  (0.0102844,0.5) `ff080008` in both; at (0.744843,0.0759125) `ff080808` in both; the body texture
  `affdbodf.dds` at (0.421906,0.707062) `ff08090a` in both. **File → surface → SetTexture → texel
  is faithful for the car.** So "the car is dark because its textures are dark" is true of the
  textures (the Focus's own `affnwbdf` full-image mean is (15,15,14)) — but it cannot be the
  *symptom*: the body texture is (92,86,94) and a (92,86,94) car on a (140,150,158) field is
  visible. The car is not there, and it is not the texture that removed it.

What that leaves, and it is narrow: submitted + textured + UV-correct + 40 % of the car's
triangles surviving the game's own `D3DCULL_CCW(3)` (your r9 winding census) — yet forcing
`D3DCULL_NONE` **does** put textured content on that page (r7) and forcing `ZENABLE` off shows
**more** of the car's surface (r11). One of two things is therefore true and they are both in
`a7_vk32.c`, not `deck_dd7.cpp`:

1. the global `frontFace`/cull-face pair is right for the TL path and wrong for the 3D path, so
   the 40 % that survive are the **inner** faces — an inside-out flat sheet, which is exactly
   Miami's sentence; or
2. the depth direction at the car's draws is wrong, so the near surface is being cut away by the
   far one (the same signature as the road being "one uninterrupted full-width field").

The instrument that separates them is the one your r8 §67 specced and never built: **the
normal-vs-winding test** (vertex normal at +0x0C vs the screen-space winding of the same
triangle, inside `MENUPROJ`'s hook), run in **one** run with a `LENA_MENUZ=0` arm and a
`LENA_MENUCULL_PHASE` arm on the same page. That is my next item. It needs the card, so it needs
ROAD-r7 finished — I will not start beside it.

**Capture rule, recorded where it will be seen:** spectacle is banned on this Deck (Wayland
core-dump + a stale file that reads like a result). Use `A7VK_SNAP_TRIGGER=1` + `touch /tmp/snapnow`
→ `/tmp/trig.ppm.NNN`. `/tmp/snapnow` and `/tmp/trig.ppm.*` are hardcoded in the RHI, so one
driver at a time owns them.

Nothing of yours was touched; nothing of ROAD-r7's was touched; no window, no build, no source
edit. Frames for the two offline claims: `work/MENU-CAR-FLATTENED/frames/md_mtex.002.ppm`,
`work/RACE/out/R5SHIP.01_t60.ppm` / `.03_t100.ppm`.
