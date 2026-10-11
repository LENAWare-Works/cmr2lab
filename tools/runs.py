#!/usr/bin/env python3
"""runs.py -- print horizontal runs of constant colour in a band of a capture.

  python3 runs.py <file.ppm> <y0> <y1> [x0] [x1] [minlen]

For each row in [y0,y1) it prints the constant-colour runs of length >= minlen,
with their x span and colour. A debug artifact / opaque card shows up as a long
run of ONE colour with a hard left and right edge at the same x in every row.
"""
import sys


def load(path):
    d = open(path, 'rb').read()
    parts = d.split(b'\n', 3)
    w, h = (int(x) for x in parts[1].split())
    return w, h, parts[3]


def main():
    path = sys.argv[1]
    y0, y1 = int(sys.argv[2]), int(sys.argv[3])
    w, h, px = load(path)
    x0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    x1 = int(sys.argv[5]) if len(sys.argv) > 5 else w
    minlen = int(sys.argv[6]) if len(sys.argv) > 6 else 40
    for y in range(y0, min(y1, h)):
        base = y * w * 3
        run_start = x0
        prev = (px[base + x0 * 3], px[base + x0 * 3 + 1], px[base + x0 * 3 + 2])
        out = []
        for x in range(x0 + 1, x1):
            o = base + x * 3
            c = (px[o], px[o + 1], px[o + 2])
            if c != prev:
                if x - run_start >= minlen:
                    out.append((run_start, x - 1, prev))
                run_start = x
                prev = c
        if x1 - run_start >= minlen:
            out.append((run_start, x1 - 1, prev))
        if out:
            body = "  ".join(f"x[{a}..{b}] len{b-a+1} #{r:02x}{g:02x}{bl:02x}"
                             for a, b, (r, g, bl) in out)
            print(f"y={y:4d} {body}")


main()
