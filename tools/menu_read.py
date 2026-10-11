#!/usr/bin/env python3
"""menu_read.py -- read a menu-screen capture offline, per pixel, no GUI.

Purpose: answer "is the 3D car in this frame a car, or a compressed patch of
shards, and where is it" from the BYTES, not from a guess.

  python3 menu_read.py <file.ppm> [--bbox] [--hist=N] [--map=COLS] [--crop=x0,y0,x1,y1]
                       [--families]

Everything printed is counted. Nothing is inferred.
"""
import sys
from collections import Counter


def load(path):
    d = open(path, 'rb').read()
    parts = d.split(b'\n', 3)
    assert parts[0] == b'P6', parts[0]
    w, h = (int(x) for x in parts[1].split())
    off = len(parts[0]) + 1 + len(parts[1]) + 1 + len(parts[2]) + 1
    return w, h, d[off:off + w * h * 3]


def fam(r, g, b):
    """crude colour family letter, for shape reading only"""
    mx, mn = max(r, g, b), min(r, g, b)
    if mx > 235 and mn > 235:
        return 'W'                      # white
    if mx < 22:
        return 'k'                      # black
    sat = mx - mn
    if sat < 14:
        return 'k' if mx < 90 else ('=' if mx < 180 else 'W')   # greys
    if r >= mx and g >= b:
        return 'O' if (r - b) > 90 and g > 0.55 * r else 'r'    # orange / red-brown
    if b >= mx:
        return 'b'
    if g >= mx:
        return 'g'
    return '?'


def main():
    path = sys.argv[1]
    args = sys.argv[2:]
    want_bbox = '--bbox' in args or not args
    want_fam = '--families' in args or not args
    hist_n = 12
    cols = 96
    crop = None
    for a in args:
        if a.startswith('--hist='):
            hist_n = int(a.split('=')[1])
        if a.startswith('--map='):
            cols = int(a.split('=')[1])
        if a.startswith('--crop='):
            crop = [int(v) for v in a.split('=')[1].split(',')]

    w, h, px = load(path)
    n = w * h
    hist = Counter()
    for i in range(n):
        o = i * 3
        hist[(px[o], px[o + 1], px[o + 2])] += 1

    print("== %s  %dx%d  (%d px)" % (path, w, h, n))
    dom, domn = hist.most_common(1)[0]
    print("dominant colour %s  %d px  %.2f%%  (everything else = %.2f%%)"
          % (dom, domn, 100.0 * domn / n, 100.0 * (n - domn) / n))
    print("distinct colours: %d" % len(hist))

    if want_bbox:
        # bbox of pixels that are NOT the dominant colour
        x0, y0, x1, y1 = w, h, -1, -1
        cnt = 0
        for y in range(h):
            base = y * w
            for x in range(w):
                o = (base + x) * 3
                if (px[o], px[o + 1], px[o + 2]) != dom:
                    cnt += 1
                    if x < x0: x0 = x
                    if x > x1: x1 = x
                    if y < y0: y0 = y
                    if y > y1: y1 = y
        if x1 < 0:
            print("non-dominant pixels: 0")
        else:
            print("non-dominant: %d px (%.2f%%)  bbox x[%d..%d] y[%d..%d] = %dx%d px"
                  % (cnt, 100.0 * cnt / n, x0, x1, y0, y1, x1 - x0 + 1, y1 - y0 + 1))
            print("  bbox as fraction: x %.1f%%..%.1f%%  y %.1f%%..%.1f%% of the frame"
                  % (100.0 * x0 / w, 100.0 * x1 / w, 100.0 * y0 / h, 100.0 * y1 / h))

    if want_fam:
        # colour families over the WHOLE frame and, if non-dominant exists, inside the bbox
        def family_counts(x0, y0, x1, y1):
            c = Counter()
            for y in range(y0, y1 + 1):
                base = y * w
                for x in range(x0, x1 + 1):
                    o = (base + x) * 3
                    c[fam(px[o], px[o + 1], px[o + 2])] += 1
            return c
        print("families whole frame:",
              dict(sorted(family_counts(0, 0, w - 1, h - 1).items(), key=lambda kv: -kv[1])))

    print("top %d colours:" % hist_n)
    for c, k in hist.most_common(hist_n):
        print("   %-16s %8d  %6.3f%%" % (str(c), k, 100.0 * k / n))

    # coarse family map of the whole frame
    rows = max(8, cols * h // (w * 2))
    sx, sy = max(1, w // cols), max(1, h // rows)
    print("map %dx%d (%dx%d px cells):" % (cols, rows, sx, sy))
    for cy in range(rows):
        line = []
        for cx in range(cols):
            r = g = b = c = 0
            for y in range(cy * sy, min((cy + 1) * sy, h), 2):
                base = y * w
                for x in range(cx * sx, min((cx + 1) * sx, w), 2):
                    o = (base + x) * 3
                    r += px[o]; g += px[o + 1]; b += px[o + 2]; c += 1
            line.append(fam(r // c, g // c, b // c) if c else ' ')
        print("  " + "".join(line))


if __name__ == '__main__':
    main()
