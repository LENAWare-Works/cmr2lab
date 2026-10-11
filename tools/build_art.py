#!/usr/bin/env python3
"""Build the CMR2LRE public-face art from the GAME'S OWN assets.

Nothing here is drawn by hand. Every colour and the wordmark itself come out of
the retail install's FrontEnd/res1024.bfl, extracted with cmr2lab:

    cmr2lab unpack <game>/FrontEnd/res1024.bfl ./fe
      cmr2.tga  -> the wordmark  (white + alpha, 512x64)
      bfin.tga  -> Finland menu texture (the tile)
      bgre.tga  -> Greece menu texture  (source of the red + gold)
    cmr2lab unpack <game>/Game/Tracks/Greece/*.bfl   -> rally stage photography

Palette, sampled from those files, not chosen:
    GOLD  #fff300   RED   #8b0000   BONE  #dcd3b1
    DIRT  #744032   SKY   #dae8ec   INK   #15100d
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys

HERE  = os.path.dirname(os.path.abspath(__file__))
FE    = os.environ.get('FE_DIR', '/tmp/fe')
OUT   = os.environ.get('OUT_DIR', os.path.join(os.path.dirname(HERE), 'docs', 'art'))
os.makedirs(OUT, exist_ok=True)

INK   = (21, 16, 13)
GOLD  = (255, 243, 0)
GOLD2 = (255, 219, 14)
RED   = (139, 0, 0)
RED2  = (160, 24, 24)
BONE  = (220, 211, 177)
DIM   = (157, 136, 116)

F = {
 'bd':  '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
 'rg':  '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
 'mk':  '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
}
def font(k, n): return ImageFont.truetype(F[k], n)

def logo():
    p = os.path.join(FE, 'cmr2.tga')
    return Image.open(p).convert('RGBA')

def tile():
    p = os.path.join(FE, 'bfin.tga')
    return Image.open(p).convert('RGB')

def textured_sheet(size, opacity=0.14, scale=2):
    """the game's own menu texture, tiled, screened back"""
    w, h = size
    t = tile().resize((256*scale, 128*scale), Image.LANCZOS)
    base = Image.new('RGB', size, INK)
    for y in range(0, h, t.height):
        for x in range(0, w, t.width):
            base.paste(t, (x, y))
    return Image.blend(Image.new('RGB', size, INK), base, opacity)

def vignette(im, strength=0.62):
    w, h = im.size
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((-w*0.35, -h*0.55, w*1.35, h*1.55), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(min(w, h)//5))
    dark = Image.new('RGB', (w, h), (0, 0, 0))
    return Image.composite(im, Image.blend(im, dark, strength), m)

def livery_bands(im, y, thickness=6, gap=3):
    """the CMR2 stripe: red block, gold block, in the way the frontend uses it"""
    d = ImageDraw.Draw(im)
    w = im.size[0]
    d.rectangle((0, y, int(w*0.40), y+thickness), fill=RED)
    d.rectangle((int(w*0.40)+gap, y, int(w*0.40)+gap+int(w*0.22), y+thickness), fill=GOLD)
    return im

# ---------------------------------------------------------------- the icon ----
def build_icon(size=512):
    """A square cannot hold an 8:1 wordmark gracefully, so: keep the field quiet,
    put the wordmark in the top two thirds where nothing competes, and let the
    livery sit at the foot like a number plate."""
    im = textured_sheet((size, size), 0.085)          # quiet, so white reads
    im = vignette(im, 0.42)
    d = ImageDraw.Draw(im)

    # a warm glow low in the frame — headlights through dust
    glow = Image.new('RGB', (size, size), INK)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-size*0.20, size*0.62, size*1.20, size*1.30), fill=(84, 54, 8))
    glow = glow.filter(ImageFilter.GaussianBlur(size//6))
    im = Image.blend(im, Image.blend(im, glow, 0.50), 0.40)
    d = ImageDraw.Draw(im)

    # the wordmark, straight out of the game, as large as the square allows
    lg = logo()
    tw = int(size*0.90)
    th = max(1, int(lg.height * tw / lg.width))
    lg = lg.resize((tw, th), Image.LANCZOS)
    x, y = (size-tw)//2, int(size*0.46)
    # a dark plate behind it so the tile can never eat the letters
    d.rounded_rectangle((x-14, y-12, x+tw+14, y+th+12), radius=8, fill=(11, 8, 6))
    im.paste(lg, (x, y), lg)

    d = ImageDraw.Draw(im)
    f = font('bd', int(size*0.105))
    sub = "LRE"
    sw = d.textlength(sub, font=f)
    d.text(((size-sw)/2, y+th+int(size*0.045)), sub, font=f, fill=GOLD)

    # livery foot: red block, gold block, exactly as the frontend stripes its screens
    fy = size - int(size*0.085)
    d.rectangle((0, fy, int(size*0.58), fy+int(size*0.050)), fill=RED)
    d.rectangle((int(size*0.58)+4, fy, size, fy+int(size*0.050)), fill=GOLD)

    im.save(os.path.join(OUT, 'icon-512.png'), optimize=True)
    im.resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, 'icon-256.png'), optimize=True)
    im.resize((128, 128), Image.LANCZOS).save(os.path.join(OUT, 'icon-128.png'), optimize=True)
    return im

# -------------------------------------------------------- the social card ----
def build_social(w=1280, h=640):
    im = textured_sheet((w, h), 0.15, scale=2)
    im = vignette(im, 0.60)
    d = ImageDraw.Draw(im)

    # red wedge on the left, the way the frontend splits its own screens
    d.polygon([(0, 0), (int(w*0.34), 0), (int(w*0.22), h), (0, h)], fill=RED)
    d.polygon([(int(w*0.34)+6, 0), (int(w*0.355), 0),
               (int(w*0.235), h), (int(w*0.22)+6, h)], fill=GOLD)

    lg = logo()
    tw = int(w*0.56)
    th = int(lg.height * tw / lg.width)
    lg = lg.resize((tw, th), Image.LANCZOS)
    x, y = int(w*0.385), int(h*0.30)
    im.paste(lg, (x, y), lg)

    f = font('bd', 54)
    d.text((x+2, y+th+26), "Linux Rally Edition", font=f, fill=GOLD)

    f2 = font('rg', 25)
    d.text((x+3, y+th+96), "Colin McRae Rally 2.0, running natively on Linux.",
           font=f2, fill=BONE)
    d.text((x+3, y+th+132), "A reverse-engineered port of the 2000 original.",
           font=f2, fill=DIM)

    f3 = font('mk', 19)
    d.text((x+3, h-70), "CMR2LRE", font=f3, fill=DIM)

    livery_bands(im, h-30, thickness=5, gap=3)
    im.save(os.path.join(OUT, 'social-1280x640.png'), optimize=True)
    return im

# --------------------------------------------------------------- the banner --
def build_banner(w=1600, h=400):
    im = textured_sheet((w, h), 0.13, scale=2)
    im = vignette(im, 0.58)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 4), fill=RED)
    d.rectangle((0, h-4, w, h), fill=GOLD)

    lg = logo()
    tw = int(w*0.42)
    th = int(lg.height * tw / lg.width)
    lg = lg.resize((tw, th), Image.LANCZOS)
    im.paste(lg, (int(w*0.045), int(h*0.30)), lg)

    f = font('rg', 30)
    d.text((int(w*0.045), int(h*0.30)+th+22),
           "Linux Rally Edition", font=f, fill=GOLD)
    im.save(os.path.join(OUT, 'banner-1600x400.png'), optimize=True)
    return im

if __name__ == '__main__':
    missing = [p for p in ('cmr2.tga', 'bfin.tga') if not os.path.exists(os.path.join(FE, p))]
    if missing:
        sys.exit(f"missing game assets in {FE}: {missing}")
    build_icon(); build_social(); build_banner()
    for f in sorted(os.listdir(OUT)):
        print(f"  {f:28s} {os.path.getsize(os.path.join(OUT,f)):>9,} B")
