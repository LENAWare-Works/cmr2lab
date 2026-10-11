#!/usr/bin/env python3
"""shard_bbox.py -- where is the content on a menu-screen capture, and what shape
is it?  Counted, not guessed.

  python3 shard_bbox.py <file.ppm> [--bg=r,g,b]

Prints: background + its share; bbox of everything that is not background; then
per colour-family count and bbox; then a row profile and a column profile so a
compact patch can be told from a full-width element.
"""
import sys
from collections import Counter


def load(path):
    d = open(path, 'rb').read()
    parts = d.split(b'\n', 3)
    w, h = (int(x) for x in parts[1].split())
    off = len(parts[0]) + 1 + len(parts[1]) + 1 + len(parts[2]) + 1
    return w, h, d[off:off + w * h * 3]


def fam(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    if mx > 235 and mn > 235:
        return 'W'
    if mx < 22:
        return 'k'
    sat = mx - mn
    if sat < 14:
        return 'k' if mx < 90 else ('=' if mx < 180 else 'W')
    if r >= mx and g >= b:
        return 'O' if (r - b) > 90 and g > 0.55 * r else 'r'
    if b >= mx:
        return 'b'
    if g >= mx:
        return 'g'
    return '?'


def main():
    path = sys.argv[1]
    px_w = 8
    hdr = load(path)
    w, h, px = hdr
    px_w = None
    bg = None
    for a in sys.argv[2:]:
        if a.startswith('--bg='):
            bg = tuple(int(v) for v in a[5:].split(','))
    n = w * h
    c = Counter()
    for i in range(n):
        j = i * 3
        c[(px[j], px[j + 1], px[j + 2])] += 1
    if bg is None:
        bg, bgc = c.most_common(1)[0]
    else:
        bgc = c.get(bg, 0)
    print("%s  %dx%d (%d px)  bg=(%d,%d,%d) %d px %.3f%%  distinct=%d"
          % (path, w, h, n, bg[0], bg[1], bg[2], bgc, 100.0 * bgc / n, len(c)))

    fams = {}
    nbx0, nby0, nbx1, nby1 = w, h, -1, -1
    rows = [0] * h
    cols = [0] * w
    for y in range(h):
        base = y * w * 3
        for x in range(w):
            j = base + x * 3
            r, g, b = px[j], px[j + 1], px[j + 2]
            if (r, g, b) == bg:
                continue
            nbx0 = min(nbx0, x); nbx1 = max(nbx1, x)
            nby0 = min(nby0, y); nby1 = max(nby1, y)
            rows[y] += 1
            cols[x] += 1
            f = fam(r, g, b)
            e = fams.setdefault(f, [0, w, h, -1, -1])
            e[0] += 1
            e[1] = min(e[1], x); e[2] = min(e[2], y)
            e[3] = max(e[3], x); e[4] = max(e[4], y)

    if nbx1 < 0:
        print("NOTHING differs from the background colour.")
        return
    tot = n - bgc
    print("NON-BG bbox x[%d..%d] y[%d..%d]  %d x %d px  = %.2f%% x %.2f%% of frame  centre=(%d,%d)"
          % (nbx0, nbx1, nby0, nby1, nbx1 - nbx0 + 1, nby1 - nby0 + 1,
             100.0 * (nbx1 - nbx0 + 1) / w, 100.0 * (nby1 - nby0 + 1) / h,
             (nbx0 + nbx1) // 2, (nby0 + nby1) // 2))
    print("frame centre = (%d,%d); frame v-centre at y=%d" % (w // 2, h // 2, h // 2))
    print("\nfamilies (count, %% of non-bg, bbox):")
    for f in sorted(fams, key=lambda k: -fams[k][0]):
        cnt, x0, y0, x1, y1 = fams[f]
        print("  %s  %8d  %6.2f%%  x[%d..%d] y[%d..%d]  %dx%d"
              % (f, cnt, 100.0 * cnt / tot, x0, x1, y0, y1, x1 - x0 + 1, y1 - y0 + 1))

    print("\nrow profile (non-bg px per row, rows with >0 only, grouped by 10s):")
    band = [(y, rows[y]) for y in range(h) if rows[y] > 0]
    if band:
        y0, y1 = band[0][0], band[-1][0]
        for s in range(y0, y1 + 1, 10):
            tot10 = sum(rows[s:s + 10])
            if tot10:
                print("  y %3d-%3d : %6d  %s" % (s, s + 9, tot10, '#' * min(60, tot10 // 200)))
    print("\ncolumn profile (non-bg px per column, grouped by 20s):")
    cs = [(x, cols[x]) for x in range(w) if cols[x] > 0]
    if cs:
        x0, x1 = cs[0][0], cs[-1][0]
        for s in range(x0, x1 + 1, 20):
            tot20 = sum(cols[s:s + 20])
            if tot20:
                print("  x %4d-%4d : %6d  %s" % (s, s + 19, tot20, '#' * min(60, tot20 // 200)))


main()
