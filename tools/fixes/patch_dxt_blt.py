#!/usr/bin/env python3
"""patch_dxt_blt.py -- THE ROAD. Decode DXT1/DXT5 in DeckSurface7::Blt.

THE FAULT, MEASURED (work/RACE/tx1.log, and `bfl.py`/`cmp_model.py` on disk):

    [TEX] DDS .\\Game\\Tracks\\KENYA\\KENlo.DDS 64x64 fcc=DXT5 bits=0
          hdrflags=0xa1007 linearSize=4096 dds=0xee362c10 data=0xee362c90
    [SURF] CREATE 64x64 caps=0x401808 asked: bitcount=0 flags=0x4
           FOURCC=0x35545844 (DXT5) linearSize=4096
    [SURF] LOCK 0x2cd18f0 ... pitch=256
    [SURF] BLT dst=0x2ae9010(64x64 fcc=00000000 tex=1)
           <- src=0x2cd18f0(64x64 fcc=35545844) srcbytes=6465000000...
    [SURF]  ST_UPLOAD 0x2ae9010 64x64 pitch=256 id=-1 wroteByGame=0

Every one of the 181 stage textures is **DXT5** (0 stages textures are RGB). The
game never decodes DXT in software: `CGraphics::LoadDDSTexture` copies the block
bytes into a *system surface marked DXT5* and then calls
`pTexture->pSurface->Blt(...)`, i.e. **it asks the driver to convert the format
during the blit.** That is what a real DirectDraw driver does and this port's Blt
does not: it is a 4-byte-per-pixel row copy, so 4096 bytes of compressed blocks
land in a 16384-byte ARGB texture and are uploaded as pixels.

Verified on disk, not inferred: the dumped upload tex085 is reproduced exactly
(100.00% of 4096 texels) by copying `kenlo.dds`'s 4096 block bytes with the
game's own row loop, and 0% by treating them as pixels
(`cmp_model.py /tmp/texd2/tex085.ppm .../KenLot.bfl`).

WHY THE FRONTEND IS FINE AND THE STAGE IS NOT, in one line: the frontend and the
cars load **TGA** (`LoadTGATexture` decodes those in software, correctly), the
stages load **DDS/DXT5** and rely on the driver's blit. The port implemented the
first and not the second.

THE FIX, three parts, all in deck_dd7.cpp:

  1. `surface_fill_desc` reports a compressed surface as compressed -- FourCC
     pixel format and DDSD_LINEARSIZE -- instead of claiming every surface is
     32-bit A8R8G8B8. This is what a driver returns from Lock, and it is the
     branch the game already has (`Graphics.cpp:3060`): `memcpy(lpSurface, pSrc,
     dwLinearSize)`. Without it the game takes its else-branch, whose source
     pointer advances by dwHeight per row -- 64 bytes for a 64-wide texture --
     and smears the blocks as well.
  2. `Blt` decodes DXT1/DXT5 when the SOURCE surface was created with a DXT
     FourCC. That is the format conversion the blit is being asked for.
  3. `Blt` marks its destination dirty, so a surface that is blitted into
     after it has already been uploaded is re-uploaded. (This one is latent
     today: the DXT surfaces happen to get a fresh texId.)

Idempotent. Backs up before writing.
"""
import os
import shutil
import sys
import time

SRC = "/home/deck/lena/.lena_cmr2/port/rhi/deck_dd7.cpp"
MARK = "LENA-DXTBLT"
TS = time.strftime("%Y%m%d-%H%M%S")

# ---------------------------------------------------------------- 1. the format
FILL_ANCHOR = """static void surface_fill_desc(DeckSurface7 *s, DDSURFACEDESC2 *d)
{
    if (!d) return;
    memset(d, 0, sizeof *d);
    d->dwSize = sizeof(DDSURFACEDESC2);
    d->dwFlags = DDSD_CAPS|DDSD_HEIGHT|DDSD_WIDTH|DDSD_PITCH|DDSD_PIXELFORMAT;
    d->dwHeight = s->h; d->dwWidth = s->w; d->lPitch = (LONG)s->pitch;
    d->lpSurface = s->pixels;
    d->ddsCaps.dwCaps = s->caps;
    d->ddpfPixelFormat.dwSize = sizeof(DDPIXELFORMAT);
    d->ddpfPixelFormat.dwFlags = DDPF_RGB|DDPF_ALPHAPIXELS;
    d->ddpfPixelFormat.dwRGBBitCount = 32;
    d->ddpfPixelFormat.dwRBitMask = 0x00FF0000;
    d->ddpfPixelFormat.dwGBitMask = 0x0000FF00;
    d->ddpfPixelFormat.dwBBitMask = 0x000000FF;
    d->ddpfPixelFormat.dwRGBAlphaBitMask = 0xFF000000;
}
"""

FILL_NEW = """/* ==================== @@MARK@@: DXT1/DXT5 ====================
 * A DXT surface is not a 32-bit surface and must not be described as one. The
 * game branches on this desc (`Graphics.cpp:3060`, `if (desc.dwFlags &
 * DDSD_LINEARSIZE) memcpy(lpSurface, pSrc, dwLinearSize)`), so getting it right
 * is the difference between a contiguous block stream and a smeared one.
 * The storage this port allocates stays 4-bytes-per-pixel-sized (a superset);
 * only the first bw*bh*blk bytes are the block stream. Documented, not implied.
 */
#define DL_DXT1 0x31545844u    /* 'DXT1' */
#define DL_DXT5 0x35545844u    /* 'DXT5' */
static int dl_is_dxt(DWORD fcc) { return fcc == DL_DXT1 || fcc == DL_DXT5; }
static DWORD dl_block_bytes(DWORD fcc) { return (fcc == DL_DXT1) ? 8u : 16u; }
static DWORD dl_block_pitch(DWORD fcc, DWORD w) { return ((w + 3) / 4) * dl_block_bytes(fcc); }
static DWORD dl_linear_size(DWORD fcc, DWORD w, DWORD h)
{
    return ((w + 3) / 4) * ((h + 3) / 4) * dl_block_bytes(fcc);
}
/* DXT1's colour is either 4 colours or 3 + transparent black */
static void dl_colours(unsigned short c0, unsigned short c1, int dxt5, BYTE out[4][4])
{
    unsigned short v[2]; int i;
    v[0] = c0; v[1] = c1;
    for (i = 0; i < 2; i++) {
        out[i][0] = (BYTE)((v[i] & 31) * 255 / 31);            /* b */
        out[i][1] = (BYTE)(((v[i] >> 5) & 63) * 255 / 63);     /* g */
        out[i][2] = (BYTE)(((v[i] >> 11) & 31) * 255 / 31);    /* r */
        out[i][3] = 255;
    }
    if (c0 > c1 || dxt5) {
        for (i = 0; i < 3; i++) {
            out[2][i] = (BYTE)((2 * out[0][i] + out[1][i]) / 3);
            out[3][i] = (BYTE)((out[0][i] + 2 * out[1][i]) / 3);
        }
        out[2][3] = 255; out[3][3] = 255;
    } else {
        for (i = 0; i < 3; i++) { out[2][i] = (BYTE)((out[0][i] + out[1][i]) / 2); out[3][i] = 0; }
        out[2][3] = 255; out[3][3] = 0;   /* DXT1 3-colour mode: index 3 is transparent */
    }
    if (dxt5) out[3][3] = 255;            /* in DXT5 alpha comes from its own block */
}

static void dl_put(BYTE *dst, DWORD dpitch, DWORD dw, DWORD dh, int x, int y, const BYTE *c)
{
    BYTE *p;
    if (x < 0 || y < 0 || (DWORD)x >= dw || (DWORD)y >= dh) return;
    p = dst + (size_t)y * dpitch + (size_t)x * 4;
    p[0] = c[0]; p[1] = c[1]; p[2] = c[2]; p[3] = c[3];
}

/* one 4x4 block: 8 or 16 bytes in, 16 texels out, in B8G8R8A8 */
static void dl_block(const BYTE *blk, DWORD fcc, BYTE *dst, DWORD dpitch, DWORD dw, DWORD dh,
                     int x0, int y0)
{
    int dxt5 = (fcc == DL_DXT5);
    int i, x, y;
    unsigned short c0, c1;
    unsigned long cbits;
    BYTE col[4][4];
    BYTE alpha[16];

    if (dxt5) {
        BYTE a0 = blk[0], a1 = blk[1];
        unsigned long long ab = 0;
        BYTE at[8];
        for (i = 0; i < 6; i++) ab |= (unsigned long long)blk[2 + i] << (8 * i);
        at[0] = a0; at[1] = a1;
        if (a0 > a1) { for (i = 2; i < 8; i++) at[i] = (BYTE)(((8 - i) * a0 + (i - 1) * a1) / 7); }
        else { for (i = 2; i < 6; i++) at[i] = (BYTE)(((6 - i) * a0 + (i - 1) * a1) / 5); at[6] = 0; at[7] = 255; }
        for (i = 0; i < 16; i++) alpha[i] = at[(int)((ab >> (3 * i)) & 7)];
    } else {
        for (i = 0; i < 16; i++) alpha[i] = 255;
    }

    c0 = (unsigned short)(blk[dxt5 ? 8 : 0] | (blk[dxt5 ? 9 : 1] << 8));
    c1 = (unsigned short)(blk[dxt5 ? 10 : 2] | (blk[dxt5 ? 11 : 3] << 8));
    cbits = (unsigned long)blk[dxt5 ? 12 : 4] | ((unsigned long)blk[dxt5 ? 13 : 5] << 8) |
            ((unsigned long)blk[dxt5 ? 14 : 6] << 16) | ((unsigned long)blk[dxt5 ? 15 : 7] << 24);
    dl_colours(c0, c1, dxt5, col);

    for (y = 0; y < 4; y++) {
        for (x = 0; x < 4; x++) {
            int i4 = y * 4 + x;
            BYTE c[4];
            int k = (int)((cbits >> (2 * i4)) & 3);
            c[0] = col[k][0]; c[1] = col[k][1]; c[2] = col[k][2];
            c[3] = dxt5 ? alpha[i4] : col[k][3];
            /* DXT1's transparent index carries the source alpha of 0 */
            if (!dxt5 && c0 <= c1 && k == 3) c[3] = 0;
            dl_put(dst, dpitch, dw, dh, x0 + x, y0 + y, c);
        }
    }
}

/* Decode a contiguous block stream (bw*bh blocks, row-major) into a 32-bit
 * destination. This is what Blt was being asked to do and did not. */
static void dl_decode(const BYTE *src, DWORD fcc, DWORD sw, DWORD sh,
                      BYTE *dst, DWORD dpitch, DWORD dw, DWORD dh)
{
    DWORD bw = (sw + 3) / 4, bh = (sh + 3) / 4, bs = dl_block_bytes(fcc), bx, by;
    for (by = 0; by < bh; by++)
        for (bx = 0; bx < bw; bx++)
            dl_block(src + ((size_t)by * bw + bx) * bs, fcc, dst, dpitch, dw, dh,
                     (int)(bx * 4), (int)(by * 4));
}
/* ============================ @@MARK@@ end ============================ */

static void surface_fill_desc(DeckSurface7 *s, DDSURFACEDESC2 *d)
{
    if (!d) return;
    memset(d, 0, sizeof *d);
    d->dwSize = sizeof(DDSURFACEDESC2);
    d->dwFlags = DDSD_CAPS|DDSD_HEIGHT|DDSD_WIDTH|DDSD_PITCH|DDSD_PIXELFORMAT;
    d->dwHeight = s->h; d->dwWidth = s->w; d->lPitch = (LONG)s->pitch;
    d->lpSurface = s->pixels;
    d->ddsCaps.dwCaps = s->caps;
    d->ddpfPixelFormat.dwSize = sizeof(DDPIXELFORMAT);
    if (dl_is_dxt(s->pxfmtFourCC)) {
        /* @@MARK@@: a compressed surface, reported as one. DDSD_LINEARSIZE +
         * dwLinearSize is the branch the game wants (it writes the block bytes
         * contiguously); lPitch is the real block-row pitch, not 4*w. */
        DWORD lin = s->pxfmtLinearSize ? s->pxfmtLinearSize : dl_linear_size(s->pxfmtFourCC, s->w, s->h);
        d->dwFlags = (d->dwFlags & ~DDSD_PITCH) | DDSD_LINEARSIZE;
        d->lPitch = (LONG)dl_block_pitch(s->pxfmtFourCC, s->w);
        d->dwLinearSize = lin;
        d->ddpfPixelFormat.dwFlags = DDPF_FOURCC;
        d->ddpfPixelFormat.dwFourCC = s->pxfmtFourCC;
        d->ddpfPixelFormat.dwRGBBitCount = 0;
        return;
    }
    d->ddpfPixelFormat.dwFlags = DDPF_RGB|DDPF_ALPHAPIXELS;
    d->ddpfPixelFormat.dwRGBBitCount = 32;
    d->ddpfPixelFormat.dwRBitMask = 0x00FF0000;
    d->ddpfPixelFormat.dwGBitMask = 0x0000FF00;
    d->ddpfPixelFormat.dwBBitMask = 0x000000FF;
    d->ddpfPixelFormat.dwRGBAlphaBitMask = 0xFF000000;
}
""".replace("@@MARK@@", MARK)

# ------------------------------------------------------- 2. the linear size
CREATE_ANCHOR = """    if (s) {   /* LENA-TEXTRACE: recorded always, not only when tracing */
        s->pxfmtFourCC = d->ddpfPixelFormat.dwFourCC;
        s->pxfmtLinearSize = d->dwLinearSize;
        s->pxfmtFlags = d->ddpfPixelFormat.dwFlags;
        s->pxfmtBits = d->ddpfPixelFormat.dwRGBBitCount;
    }
"""
CREATE_NEW = """    if (s) {   /* LENA-TEXTRACE: recorded always, not only when tracing */
        s->pxfmtFourCC = d->ddpfPixelFormat.dwFourCC;
        s->pxfmtLinearSize = d->dwLinearSize;
        s->pxfmtFlags = d->ddpfPixelFormat.dwFlags;
        s->pxfmtBits = d->ddpfPixelFormat.dwRGBBitCount;
        /* @@MARK@@: a compressed surface's real size, computed from the FourCC
         * rather than trusted from the request (the game leaves dwLinearSize
         * unset for some of them). The allocation stays 32-bit-pitch-sized:
         * a superset, so nothing that addresses it by pitch can overrun. */
        if (dl_is_dxt(s->pxfmtFourCC))
            s->pxfmtLinearSize = dl_linear_size(s->pxfmtFourCC, w, h);
    }
""".replace("@@MARK@@", MARK)

# ---------------------------------------------------------------- 3. the blit
BLT_ANCHOR = """    if (!s || !s->pixels) return DDERR_NOTFOUND;
    RECT dr, sr;
"""
BLT_NEW = """    if (!s || !s->pixels) return DDERR_NOTFOUND;
    if (dl_is_dxt(s->pxfmtFourCC)) {
        /* @@MARK@@: THE FORMAT CONVERSION THE BLIT WAS BEING ASKED FOR.
         * The game copies DXT block bytes into a system surface and relies on
         * this blit to turn them into pixels; a real DDraw driver does exactly
         * that. Without it the stage's terrain textures reach the RHI as
         * compressed bytes read as ARGB -- measured 1.1% left-neighbour
         * agreement and mean alpha 16 of 255, against 90-100% for an image. */
        dl_decode(s->pixels, s->pxfmtFourCC, s->w, s->h, pixels, pitch, w, h);
        dirty = 1;
        blitsConverted++;
        if (st_on) st_log("[SURF] BLT-DXT dst=%p(%ux%u) <- src=%p(%ux%u fcc=%08x) decoded %ux%u blocks\\n",
                          (void*)this, (unsigned)w, (unsigned)h, (void*)s,
                          (unsigned)s->w, (unsigned)s->h, (unsigned)s->pxfmtFourCC,
                          (unsigned)((s->w + 3) / 4), (unsigned)((s->h + 3) / 4));
        return DD_OK;
    }
    RECT dr, sr;
""".replace("@@MARK@@", MARK)

# the normal path also changes the destination
BLT_END_ANCHOR = """        } else if (cw > 0) memcpy(drow, srow, (size_t)cw*4);
    }
    return DD_OK;
}
"""
BLT_END_NEW = """        } else if (cw > 0) memcpy(drow, srow, (size_t)cw*4);
    }
    dirty = 1;   /* @@MARK@@: the destination changed, so it must re-upload */
    return DD_OK;
}
""".replace("@@MARK@@", MARK)

COUNTER_ANCHOR = "static int st_on = 0; static int st_uid = 0;\n"
COUNTER_NEW = (COUNTER_ANCHOR +
               "static unsigned long blitsConverted = 0;   /* @@MARK@@ */\n".replace("@@MARK@@", MARK))

EDITS = [
    (FILL_ANCHOR, FILL_NEW, "surface_fill_desc + DXT decoder"),
    (COUNTER_ANCHOR, COUNTER_NEW, "converted-blit counter"),
    (CREATE_ANCHOR, CREATE_NEW, "linear size from the FourCC"),
    (BLT_ANCHOR, BLT_NEW, "Blt: decode DXT"),
    (BLT_END_ANCHOR, BLT_END_NEW, "Blt: mark dirty"),
]


def main():
    src = open(SRC, encoding="utf-8", errors="surrogateescape").read()
    for anchor, new, label in EDITS:
        if src.count(anchor) == 0:
            print("skip %-32s already applied" % label)
            continue
        if src.count(anchor) != 1:
            print("FAIL %-32s anchor x%d" % (label, src.count(anchor)))
            return 1
        src = src.replace(anchor, new)
        print("applied %-32s" % label)
    bak = SRC + ".bak-pre-dxtblt-" + TS
    if not os.path.exists(bak):
        shutil.copy2(SRC, bak)
        print("backup:", bak)
    open(SRC, "w", encoding="utf-8", errors="surrogateescape").write(src)
    return 0


if __name__ == "__main__":
    sys.exit(main())
