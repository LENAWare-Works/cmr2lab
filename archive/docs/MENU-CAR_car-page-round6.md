# the option-preview car page, round 6 — the alpha end of the fork, measured

`work/MENU-CAR-FLATTENED/`, 2026-10-11 12:19–12:40 EEST. Binary `out-md2/cmr2`
md5 `cfd9cb7980dff26a5e56649467845432` unless noted; `out-md3/cmr2` md5
`1e5a22a2a48857cd95886d0d2341cab0` for the alpha-off arm. Four guarded runs.

## the frames

| PNG | run / frame | arm | car cells (x160–1080, y280–560): pixels that are NOT the dominant colour |
|---|---|---|---|
| `opt-preview-car_20261011-1235_CAR-PAGE_default-arm.png` | `md_texcar2` f4100 | default | **11.01 %** (all of it 2D chrome: the shaded band the earlier rounds named) |
| `opt-preview-car_20261011-1237_CAR-PAGE_alpha-off-arm.png` | `md_opq3` f3657 | `LENA_MENUOPAQUE=1` | **1.60 %** |

Both are the option screen with the car camera up (`eye=(0.14 -0.09 -5.00)`), with the car's
draws in flight (1,015 and 174 `MENUDRAW` lines at those frames) and the owner map putting
2,747 triangles on 587 of 2,560 cells. `ppm2png.py` round-trips all 1,024,000 pixels identical,
so what is in the PNG is what the RHI presented.

**Neither frame has a car in it, and the arm that removes alpha test and blending from the 3D
draws does not put one there.** That is the round's second negative and the reason the alpha end
of the fork is closed.

## the alpha inputs, as the shader sees them (`LENA_MENUDRAW_ALPHA=1`)

```
[ALPHADRAW] #1 fvf=0x2d2 stride=48 atest=1 aref=1 afunc=7 blend=1 src=5 dst=6
            aop=4 aa1=2 aa2=0 v0_off24=ffffffff (a=255) v0_off28=ff000000
```

atext on, ref = 1/255, func GREATEREQUAL; blend on, SRCALPHA/INVSRCALPHA; stage-0 alpha op
MODULATE of (DIFFUSE × TEXTURE); the first vertex's own diffuse dword is opaque white.
With the body texture's alpha at 254 that computes c.a ≈ 0.996 — a draw that should paint.
It does not. So the car is not being eaten by alpha test or by blending.
