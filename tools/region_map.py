#!/usr/bin/env python3
"""region_map.py -- print one crop of a capture as letters, one letter per exact
colour, background blanked.  For reading a shape without a GUI.

  python3 region_map.py <file.ppm> x0 y0 x1 y1 [cols] [rows] [--bg=r,g,b]
"""
import sys
from collections import Counter

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def load(path):
    d = open(path, 'rb').read()
    p = d.split(b'\n', 3)
    w, h = (int(x) for x in p[1].split())
    off = len(p[0]) + 1 + len(p[1]) + 1 + len(p[2]) + 1
    return w, h, d[off:off + w * h * 3]


def main():
    path = sys.argv[1]
    a = [v for v in sys.argv[2:] if not v.startswith('--')]
    x0, y0, x1, y1 = (int(v) for v in a[:4])
    cols = int(a[4]) if len(a) > 4 else 110
    rows = int(a[5]) if len(a) > 5 else 40
    bg = None
    for v in sys.argv[2:]:
        if v.startswith('--bg='):
            bg = v[5:]
    w, h, px = load(path)
    c = Counter()
    for y in range(y0, y1):
        for x in range(x0, x1):
            j = (y * w + x) * 3
            c[(px[j], px[j + 1], px[j + 2])] += 1
    bgk = bg if bg else ",".join(str(v) for v in c.most_common(1)[0][0])
    bgt = tuple(int(v) for v in bgk.split(','))
    table = {}
    for k, _ in c.most_common():
        if k != bgt and len(table) < len(LETTERS):
            table[k] = LETTERS[len(table)]
    print("crop x[%d..%d] y[%d..%d] -> %dx%d cells (%dx%d px each); bg=(%s) blank" %
          (x0, x1 - 1, y0, y1 - 1, cols, rows,
           (x1 - x0) // cols, (y1 - y0) // rows, bgk))
    print("legend: " + "  ".join("%s=(%d,%d,%d)" % (v, k[0], k[1], k[2]) for k, v in table.items()))
    sx = (x1 - x0) / cols
    sy = (y1 - y0) / rows
    for r in range(rows):
        line = []
        for cc in range(cols):
            # sample the exact colour at the cell centre
            x = int(x0 + (cc + 0.5) * sx)
            y = int(y0 + (r + 0.5) * sy)
            j = (y * w + x) * 3
            k = (px[j], px[j + 1], px[j + 2])
            line.append(' ' if k == bgt else table.get(k, '*'))
        print("|" + "".join(line) + "|")


main()
