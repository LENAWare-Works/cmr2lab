#!/usr/bin/env python3
"""CMR2LRE public-face art -- corrected final palette, reproducible from this file.

PALE SAGE FIELD, because that is what the real game actually does: the main menu
is #9bb5aa with white type, flat, quiet, almost soft. The banner should look like
the game at a glance, so it takes the game's own field.

THREE THINGS FIXED FROM EARLIER BUILDS:
 1. PALETTE. v1 sourced red+gold from bgre.tga -- the Greece menu texture, the
    ONLY warm one of nine. Every other country menu is cool. Identity now comes
    from the corrected set (teal/sage/sand) already used by the installer.
 2. GHOST TEXT. The source texture carries its own words ("RALLY OF ITALY",
    "EMTEC official sponsors"). Shipped sharp it competed with the wordmark.
    The field is now FLAT and the texture is gone from the type zone entirely.
 3. CONTRAST. White type on pale sage is 2.15:1 -- the real menu gets away with
    it because it is seven huge words on a sparse screen. A wordmark is not.
    Type here is deep teal #033d52 = 5.33:1 on this field. AA, holds at thumbnail.

Source: FrontEnd/res1024.bfl (cmr2.tga wordmark, bita.tga texture), extracted
with cmr2lab from Miami's own retail install. No assets ship -- this is art for
the repo, built from his copy.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys

FE = os.environ.get('FE_DIR', '/tmp/fe')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'art')
os.makedirs(OUT, exist_ok=True)

SAGE_PALE  = (170, 194, 183)   # #aac2b7  the field
SAGE       = (155, 181, 170)   # #9bb5aa  the game's own menu field
TEAL_DEEP  = (3, 61, 82)       # #033d52  5.33:1 on SAGE_PALE  <- type
TEAL       = (0, 123, 155)     # #007b9b  the loud CMR2 teal   <- slab
TEAL_BRIGHT= (3, 160, 149)     # #03a095

F = {'bd':'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
     'rg':'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
     'mk':'/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'}
def font(k,n): return ImageFont.truetype(F[k], n)

def logo_rgba():
    return Image.open(os.path.join(FE,'cmr2.tga')).convert('RGBA')

def tint(lg, rgb):
    """keep the wordmark's alpha, replace its colour"""
    a = lg.split()[3]
    return Image.merge('RGBA', (Image.new('L', lg.size, rgb[0]),
                                Image.new('L', lg.size, rgb[1]),
                                Image.new('L', lg.size, rgb[2]), a))

def flat_field(size, base, tex_op=0.0, blur=18):
    im = Image.new('RGB', size, base)
    if tex_op > 0:
        t = Image.open(os.path.join(FE,'bita.tga')).convert('RGB')
        t = t.resize((256*2,128*2), Image.LANCZOS).filter(ImageFilter.GaussianBlur(blur))
        s = Image.new('RGB', size, base)
        for y in range(0, size[1], t.height):
            for x in range(0, size[0], t.width):
                s.paste(t,(x,y))
        im = Image.blend(im, s, tex_op)
    return im

def build_banner(w=1600, h=400):
    im = flat_field((w,h), SAGE_PALE)
    d = ImageDraw.Draw(im)
    d.polygon([(int(w*0.60),0), (w,0), (w,h), (int(w*0.52),h)], fill=TEAL)
    # striped divider, parallel to the slab edge. the stray sage separator v1
    # drew here got read as a clipped wedge -- gone.
    for off,cd in [(0,(3,160,149)),(40,(3,160,149)),(80,(3,160,149))]:
        d.polygon([(int(w*0.60)-off,0),(int(w*0.60)-off+10,0),
                   (int(w*0.52)-off+10,h),(int(w*0.52)-off,h)], fill=cd)
    d.rectangle((0,0,w,5), fill=TEAL_DEEP)
    d.rectangle((0,h-5,w,h), fill=TEAL_DEEP)

    # ONE SHARED BASELINE. v1 centred each block independently and the two halves
    # read as two layouts. Everything now sits on y = BASE.
    BASE = int(h*0.625)
    lg = tint(logo_rgba(), TEAL_DEEP)
    tw = int(w*0.40); th = int(lg.height*tw/lg.width)
    lg = lg.resize((tw,th), Image.LANCZOS)
    x = int(w*0.045)
    im.paste(lg,(x, BASE - th - 22), lg)                    # wordmark bottom -> baseline-gap
    d = ImageDraw.Draw(im)
    d.text((x+3, BASE), "Linux Rally Edition", font=font('rg',34), fill=TEAL_DEEP, anchor="ls")

    rx = w - int(w*0.045)
    d.text((rx, BASE), "native  ·  no wine  ·  no proton",
           font=font('rg',22), fill=(226,240,236), anchor="rs")
    d.text((rx, BASE-52), "CMR2LRE", font=font('bd',60), fill=(255,255,255), anchor="rs")
    im.save(os.path.join(OUT,'banner-1600x400.png'), optimize=True)

def build_social(w=1280, h=640):
    im = flat_field((w,h), SAGE_PALE)
    d = ImageDraw.Draw(im)
    d.polygon([(int(w*0.60),0),(w,0),(w,h),(int(w*0.50),h)], fill=TEAL)
    d.polygon([(int(w*0.617),0),(int(w*0.637),0),(int(w*0.517),h),(int(w*0.497),h)],
              fill=TEAL_BRIGHT)
    d.rectangle((0,0,w,6), fill=TEAL_DEEP)

    lg = tint(logo_rgba(), TEAL_DEEP)
    tw = int(w*0.50); th = int(lg.height*tw/lg.width)
    lg = lg.resize((tw,th), Image.LANCZOS)
    x, y = int(w*0.055), int(h*0.30)
    im.paste(lg,(x,y),lg)
    d = ImageDraw.Draw(im)
    d.text((x+3, y+th+26), "Linux Rally Edition", font=font('bd',50), fill=TEAL_DEEP)
    d.text((x+3, y+th+100), "Colin McRae Rally 2.0, running natively on Linux.",
           font=font('rg',24), fill=TEAL_DEEP)
    d.text((x+3, y+th+136), "A reverse-engineered port of the 2000 original.",
           font=font('rg',24), fill=(31,83,64))
    d.text((x+3, h-72), "CMR2LRE", font=font('mk',19), fill=TEAL_DEEP)
    d.rectangle((0,h-26,int(w*0.40),h-20), fill=TEAL_DEEP)
    d.rectangle((int(w*0.40)+4,h-26,int(w*0.62),h-20), fill=TEAL)
    im.save(os.path.join(OUT,'social-1280x640.png'), optimize=True)
    # GitHub's social-preview slot is a separate upload; keep its local source
    # at the repo path documented in ART-PROVENANCE.md.
    im.save(os.path.join(ROOT,'docs','social-preview.png'), optimize=True)

def build_icon(s=512):
    im = flat_field((s,s), SAGE_PALE)
    d = ImageDraw.Draw(im)
    d.rectangle((0,s-int(s*0.20),s,s), fill=TEAL)
    d.rectangle((0,0,s,5), fill=TEAL_DEEP)
    lg = tint(logo_rgba(), TEAL_DEEP)
    tw = int(s*0.86); th = max(1,int(lg.height*tw/lg.width))
    lg = lg.resize((tw,th), Image.LANCZOS)
    x, y = (s-tw)//2, int(s*0.34)
    im.paste(lg,(x,y),lg)
    d = ImageDraw.Draw(im)
    f = font('bd', int(s*0.105)); sub="LRE"
    sw = d.textlength(sub, font=f)
    d.text(((s-sw)/2, y+th+int(s*0.045)), sub, font=f, fill=TEAL_DEEP)
    im.save(os.path.join(OUT,'icon-512.png'), optimize=True)
    im.resize((256,256),Image.LANCZOS).save(os.path.join(OUT,'icon-256.png'),optimize=True)
    im.resize((128,128),Image.LANCZOS).save(os.path.join(OUT,'icon-128.png'),optimize=True)

if __name__=='__main__':
    build_banner(); build_social(); build_icon()
    for f in sorted(os.listdir(OUT)):
        if f.endswith('.png'):
            print(f"  {f:28s} {os.path.getsize(os.path.join(OUT,f)):>9,} B")
