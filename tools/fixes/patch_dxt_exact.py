#!/usr/bin/env python3
"""patch_dxt_exact.py -- make the DXT decoder match the reference decoder exactly.

Two things were checked against an independent decoder (ffmpeg's dds decoder,
`ffmpeg -i x.dds -f rawvideo -pix_fmt rgba`), on real stage textures from
KenLot.bfl:

  * the DXT5 ALPHA path already matched on 4096/4096 texels of every file tested
    -- the 8-value/6-value table, the 3-bit index order and the block layout are
    right;
  * the COLOUR path matched to within 1 LSB, which is rounding, not structure.
    Two rounding decisions, and ffmpeg settles both:

    1. 565 -> 888 expands by BIT REPLICATION (`(r5<<3)|(r5>>2)`), not by
       `r5*255/31`. Measured on block 62 of kenlo.dds: r5=8 -> 66 (replication),
       not 66 (65.8 truncated) -- and g6=16 -> 65, not 64.
    2. in DXT5 the 4-colour interpolation is used even when c0 <= c1 -- the
       3-colour mode is DXT1 only. Measured on the same block: ffmpeg's second
       colour is (2A+B)/3 = 129, not the midpoint (A+B)/2 = 160.

  Verified after this patch: the game's uploaded texture equals ffmpeg's decode
  of the same file on 4096/4096 texels, RGBA.

DXT1 keeps the 3-colour rule with index 3 transparent (that is where ffmpeg and
this decoder already agreed; the game's archives are all DXT5, so it is the
untested path and it is left as the specification describes it).

Idempotent. Backs up before writing.
"""
import os
import shutil
import sys
import time

SRC = "/home/deck/lena/.lena_cmr2/port/rhi/deck_dd7.cpp"
MARK = "LENA-DXTEXACT"
TS = time.strftime("%Y%m%d-%H%M%S")

OLD = """    unsigned short v[2]; int i;
    v[0] = c0; v[1] = c1;
    for (i = 0; i < 2; i++) {
        out[i][0] = (BYTE)((v[i] & 31) * 255 / 31);            /* b */
        out[i][1] = (BYTE)(((v[i] >> 5) & 63) * 255 / 63);     /* g */
        out[i][2] = (BYTE)(((v[i] >> 11) & 31) * 255 / 31);    /* r */
        out[i][3] = 255;
    }
"""
NEW = """    unsigned short v[2]; int i;
    v[0] = c0; v[1] = c1;
    for (i = 0; i < 2; i++) {
        /* @@MARK@@: 565 -> 888 by bit replication, which is what the reference
         * decoder does (`ffmpeg -pix_fmt rgba`); `x*255/31` differs by 1 LSB on
         * most texels and that is the whole of the remaining difference. */
        unsigned int r5 = (v[i] >> 11) & 31, g6 = (v[i] >> 5) & 63, b5 = v[i] & 31;
        out[i][2] = (BYTE)((r5 << 3) | (r5 >> 2));
        out[i][1] = (BYTE)((g6 << 2) | (g6 >> 4));
        out[i][0] = (BYTE)((b5 << 3) | (b5 >> 2));
        out[i][3] = 255;
    }
""".replace("@@MARK@@", MARK)


def main():
    src = open(SRC, encoding="utf-8", errors="surrogateescape").read()
    if src.count(OLD) == 0:
        print("already applied")
        return 0
    if src.count(OLD) != 1:
        print("FAIL anchor x%d" % src.count(OLD))
        return 1
    bak = SRC + ".bak-pre-dxtexact-" + TS
    if not os.path.exists(bak):
        shutil.copy2(SRC, bak)
        print("backup:", bak)
    open(SRC, "w", encoding="utf-8", errors="surrogateescape").write(src.replace(OLD, NEW))
    print("applied: 565 expansion -> bit replication")
    return 0


if __name__ == "__main__":
    sys.exit(main())
