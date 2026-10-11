#!/usr/bin/env python3
"""ppmcrop.py <in.ppm> <out.ppm> <x0> <y0> <x1> <y1> -- crop a P6 PPM.

Written for the WHITE-BOX round: the specimen has to be shown to a human eye as
an image, not only as numbers, and the Deck has no ImageMagick.
"""
import sys


def main():
    src, dst, x0, y0, x1, y1 = sys.argv[1], sys.argv[2], *(int(v) for v in sys.argv[3:7])
    d = open(src, 'rb').read()
    parts = d.split(b'\n', 3)
    assert parts[0] == b'P6'
    w, h = (int(x) for x in parts[1].split())
    px = parts[3]
    x0 = max(0, x0); y0 = max(0, y0); x1 = min(w, x1); y1 = min(h, y1)
    cw, ch = x1 - x0, y1 - y0
    out = bytearray()
    for y in range(y0, y1):
        o = (y * w + x0) * 3
        out += px[o:o + cw * 3]
    with open(dst, 'wb') as f:
        f.write(b'P6\n%d %d\n255\n' % (cw, ch))
        f.write(bytes(out))
    print(f"{dst} {cw}x{ch} from {src} x[{x0}..{x1}] y[{y0}..{y1}]")


main()
