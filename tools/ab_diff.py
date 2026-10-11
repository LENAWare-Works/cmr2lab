#!/usr/bin/env python3
"""ab_diff.py -- per-pixel A/B of two captures of the SAME frame number.

  python3 ab_diff.py <dir> <tagA> <tagB> [frames...]

Prints, per frame: pixels differing by >8 (and >32), mean abs diff, the bbox of
the differing pixels, and a coarse map of where they are. Everything counted.
"""
import sys, os
from collections import Counter


def load(path):
    d = open(path, 'rb').read()
    parts = d.split(b'\n', 3)
    w, h = (int(x) for x in parts[1].split())
    off = len(parts[0]) + 1 + len(parts[1]) + 1 + len(parts[2]) + 1
    return w, h, d[off:off + w * h * 3]


def main():
    d = sys.argv[1]
    a, b = sys.argv[2], sys.argv[3]
    frames = sys.argv[4:]
    if not frames:
        frames = sorted({f.split('.')[-1] for f in os.listdir(d) if f.startswith(a + '.ppm.')}
                        & {f.split('.')[-1] for f in os.listdir(d) if f.startswith(b + '.ppm.')},
                        key=int)
    for fr in frames:
        pa = os.path.join(d, '%s.ppm.%s' % (a, fr))
        pb = os.path.join(d, '%s.ppm.%s' % (b, fr))
        if not (os.path.exists(pa) and os.path.exists(pb)):
            print("frame %s: missing" % fr); continue
        w, h, A = load(pa)
        _, _, B = load(pb)
        n = w * h
        gt8 = gt32 = 0
        tot = 0
        x0, y0, x1, y1 = w, h, -1, -1
        for y in range(h):
            base = y * w
            for x in range(w):
                o = (base + x) * 3
                dr = abs(A[o] - B[o]); dg = abs(A[o + 1] - B[o + 1]); db = abs(A[o + 2] - B[o + 2])
                m = max(dr, dg, db)
                tot += dr + dg + db
                if m > 8:
                    gt8 += 1
                    if x < x0: x0 = x
                    if x > x1: x1 = x
                    if y < y0: y0 = y
                    if y > y1: y1 = y
                if m > 32:
                    gt32 += 1
        mean = tot / (3.0 * n)
        line = ("frame %-5s d>8=%7d (%.3f%%)  d>32=%7d (%.3f%%)  mean=%.3f" %
                (fr, gt8, 100.0 * gt8 / n, gt32, 100.0 * gt32 / n, mean))
        if x1 >= 0:
            line += ("  bbox x[%d..%d] y[%d..%d] %dx%d = %.1f%%x%.1f%% of frame, centre (%d,%d)" %
                     (x0, x1, y0, y1, x1 - x0 + 1, y1 - y0 + 1,
                      100.0 * (x1 - x0 + 1) / w, 100.0 * (y1 - y0 + 1) / h,
                      (x0 + x1) // 2, (y0 + y1) // 2))
        else:
            line += "  identical"
        print(line)
        if x1 >= 0 and gt8 * 100.0 / n > 0.05:
            cols, rows = 64, 20
            sx, sy = max(1, w // cols), max(1, h // rows)
            for cy in range(rows):
                ln = []
                for cx in range(cols):
                    c = 0
                    for y in range(cy * sy, min((cy + 1) * sy, h), 3):
                        base = y * w
                        for x in range(cx * sx, min((cx + 1) * sx, w), 3):
                            o = (base + x) * 3
                            if max(abs(A[o] - B[o]), abs(A[o + 1] - B[o + 1]), abs(A[o + 2] - B[o + 2])) > 8:
                                c += 1
                    ln.append('#' if c > 40 else '+' if c > 12 else '.' if c > 2 else ' ')
                print("      |" + "".join(ln) + "|")


if __name__ == '__main__':
    main()
