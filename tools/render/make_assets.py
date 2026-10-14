#!/usr/bin/env python3
"""make_assets.py -- regenerate every car image the README uses.

    CMR2_CARS=/path/to/Game/Cars python3 tools/render/make_assets.py

Writes into assets/:
    car-<cid>.png    one car per file, pale sage field, grounded
    cars-grid.png    the four-car strip used in the README table
    hero.png         the 1280x430 banner

The grounding pass is deliberately NOT inside the rasteriser. render_tex.render()
is the thing that produces the verified silhouette, so it is left alone; the floor
and the contact shadow are drawn afterwards into the background and the car is
composited on top with a real alpha channel. That keeps the renderer honest and
makes the presentation changeable without touching geometry code.

Everything here is a single baked still. No animation, no live wallpaper.
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_tex as R
import tex
import livery

SAGE = np.array([155, 181, 170], float) / 255.0     # CMR2's own menu field #9bb5aa
TEAL = np.array([0, 123, 155], float)               # #007b9b

# (c3d id, output filename, label)  -- filenames MUST match the README refs
CARDS = [('205', 'car-205.png',    'Peugeot 205 T16'),
         ('6r4', 'car-6r4.png',    'MG Metro 6R4'),
         ('sub', 'car-subaru.png', 'Subaru Impreza WRC'),
         ('foc', 'car-focus.png',  'Ford Focus WRC'),
         ('min', 'car-mini.png',   'Mini Cooper'),
         ('str', 'car-strada.png', 'Fiat Strada')]

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'assets')

FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def ground(im, mask):
    """Draw a graded floor + contact shadow behind a rendered car."""
    H, W = mask.shape
    ys = np.where(mask.any(1))[0]; xs = np.where(mask.any(0))[0]
    if not len(ys):
        return im
    base = int(ys.max())
    cx = int((xs.min() + xs.max()) / 2)
    hw = int((xs.max() - xs.min()) / 2)
    rows = np.arange(H, dtype=float)[:, None]

    sky = SAGE[None, None, :] * (1.0 - 0.07 * (rows / H))[..., None]
    frac = np.clip((rows - base) / max(1.0, (H - base)), 0, 1)
    flo = SAGE[None, None, :] * (0.60 - 0.17 * frac)[..., None] + 0.022
    out = np.where((rows < base)[..., None], sky, flo)
    out = np.broadcast_to(out, (H, W, 3)).copy()

    seam = np.exp(-((rows - base) ** 2) / (2 * (H * 0.010) ** 2))
    out += (SAGE * 0.09)[None, None, :] * seam[..., None]

    yy, xx = np.mgrid[0:H, 0:W]
    rx = max(1.0, hw * 1.18); ry = max(3.0, H * 0.050)
    ell = ((xx - cx) / rx) ** 2 + ((yy - base) / ry) ** 2
    hard = np.clip(1.0 - ell, 0, 1) ** 0.55
    p = Image.fromarray((hard * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(max(2, int(H * 0.020))))
    hard = np.asarray(p, np.float32) / 255.0
    amt = hard * (0.62 * (yy >= base - ry * 0.8))
    out = out * (1.0 - amt[..., None]) + (SAGE * 0.07)[None, None, :] * amt[..., None]

    out = np.where(mask[..., None], im.astype(float) / 255.0, out)
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


def car(cid, W=980, H=640, az=214.0, el=12.0, cars=None):
    """Render one car and ground it. Returns (grounded_rgb, raw_rgb, mask)."""
    d = tex.textures_for(cid, cars)
    m, P, V, N, UV, T, TP = R.build(cid, skip_parts={12})
    tmap = livery.build_texmap(cid, d)
    im, mk = R.render(V, N, UV, T, TP, tmap, livery.FB,
                      W=W, H=H, az=az, el=el, dist=10.6, fov=28,
                      bg=(155, 181, 170), want_mask=True)
    return ground(im, mk), im, mk


def hero(cid, path, W=1280, H=430, cars=None):
    """The banner. The car is composited with its true alpha mask -- take the
    alpha from an RGB file and the car's own background comes with it, which
    shows up as a pale rectangle pasted over the gradient."""
    d = tex.textures_for(cid, cars)
    m, P, V, N, UV, T, TP = R.build(cid, skip_parts={12})
    tmap = livery.build_texmap(cid, d, verbose=False)
    raw, mask = R.render(V, N, UV, T, TP, tmap, livery.FB,
                         W=900, H=620, az=214.0, el=12.0, dist=10.6, fov=28,
                         bg=(155, 181, 170), want_mask=True)

    rgba = np.dstack([raw, (mask * 255).astype(np.uint8)])
    c = Image.fromarray(rgba, 'RGBA')

    # crop to the car's own alpha bbox, so placement is predictable and the
    # shadow can be anchored to the real contact line rather than the frame.
    bb = c.split()[3].getbbox()
    if bb:
        c = c.crop(bb)
    cw, ch = c.size

    # leave a strip of ground under the car, otherwise the contact shadow has
    # nowhere to land and the car reads as glued to the bottom edge.
    GROUND = 0.16
    sc = min(1.0, (W * 0.56) / cw, (H * (1.0 - GROUND)) / ch)
    c = c.resize((max(1, int(cw * sc)), max(1, int(ch * sc))), Image.LANCZOS)
    cw, ch = c.size
    cx = max(0, min(W - cw - 24, W - cw))
    cy = max(0, min(H - ch - int(H * GROUND * 0.55), H - ch))

    xx, yy = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H))
    t = np.clip((xx * 0.75 + yy * 0.45), 0, 1)[..., None]
    hero_arr = np.clip((SAGE[None, None, :] * (1 - t) + TEAL[None, None, :] * t) * 0.96, 0, 255)

    # contact shadow: the car now fills its own box, so the bottom edge of the
    # box IS the wheel contact line.
    sh = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(sh)
    gx = int(cx + cw * 0.52); gy = int(cy + ch * 0.99)
    ry = max(6, int(H * 0.055)); rx = int(cw * 0.40)
    sd.ellipse([gx - rx, gy - ry, gx + rx, gy + ry], fill=185)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    hero_arr = hero_arr * (1 - np.asarray(sh, float)[..., None] / 255.0 * 0.60)

    canvas = Image.fromarray(np.clip(hero_arr, 0, 255).astype(np.uint8)).convert('RGBA')
    canvas.alpha_composite(c, (cx, cy))
    img = canvas.convert('RGB')

    dr = ImageDraw.Draw(img)
    dr.text((54, 52), "CMR2LRE", font=ImageFont.truetype(FONT_BOLD, 64), fill=(255, 255, 255))
    dr.text((56, 134), "Colin McRae Rally 2.0  /  Linux Rally Edition",
            font=ImageFont.truetype(FONT_REG, 23), fill=(255, 255, 255))
    dr.text((56, 172), "The 2000 PC original, rebuilt on Linux.  Real D3D7 engine.  No emulator.",
            font=ImageFont.truetype(FONT_REG, 23), fill=(233, 242, 238))
    dr.line([(56, 216), (292, 216)], fill=(255, 255, 255), width=3)
    f3 = ImageFont.truetype(FONT_REG, 19)
    for i, s2 in enumerate(["The car in this banner is not a screenshot.",
                            "It is the game's own .c3d mesh and .bfl livery,",
                            "decoded and rasterised by our renderer. No GPU."]):
        dr.text((56, 236 + i * 25), s2, font=f3, fill=(226, 238, 233))
    img.save(path)
    return img


def main():
    cars = os.environ.get('CMR2_CARS')
    os.makedirs(OUT, exist_ok=True)
    for cid, fname, label in CARDS:
        img, _raw, _mk = car(cid, cars=cars)
        Image.fromarray(img).save(os.path.join(OUT, fname))
        print("  %-22s -> %s" % (label, fname))

    picks = ['car-subaru.png', 'car-focus.png', 'car-205.png', 'car-6r4.png']
    ims = [Image.open(os.path.join(OUT, f)).convert('RGB') for f in picks]
    CW = 760; CH = int(ims[0].height * CW / ims[0].width)
    g = Image.new('RGB', (4 * CW + 50, CH + 12), (12, 16, 18))
    for i, im in enumerate(ims):
        g.paste(im.resize((CW, CH), Image.LANCZOS), (10 + i * (CW + 10), 6))
    g.save(os.path.join(OUT, 'cars-grid.png'))
    print("  grid -> cars-grid.png")

    hero('205', os.path.join(OUT, 'hero.png'), cars=cars)
    print("  banner -> hero.png")


if __name__ == '__main__':
    main()
