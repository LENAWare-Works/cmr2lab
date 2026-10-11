#!/usr/bin/env python3
"""shards.py -- is a given exact colour on a capture ONE solid area or MANY ragged
pieces?  Straight-edged fragments that touch only at points are the signature the
phone described; a panel is one big 4-connected blob.

  python3 shards.py <file.ppm> [--top=N] [--colour=r,g,b] [--min=px]

Default: for the top N non-background exact colours, print count, the number of
4-connected components, the largest component, and how many components are
smaller than --min px. No smoothing, no thresholds beyond the exact colour.
"""
import sys
from collections import Counter


def load(path):
    d = open(path, 'rb').read()
    p = d.split(b'\n', 3)
    w, h = (int(x) for x in p[1].split())
    off = len(p[0]) + 1 + len(p[1]) + 1 + len(p[2]) + 1
    return w, h, d[off:off + w * h * 3]


def comps(px, w, h, colour):
    """4-connected components of an exact colour. Returns list of (size, bbox)."""
    key = colour[0] << 16 | colour[1] << 8 | colour[2]
    seen = bytearray(w * h)
    out = []
    for start in range(w * h):
        if seen[start]:
            continue
        j = start * 3
        if (px[j] << 16 | px[j + 1] << 8 | px[j + 2]) != key:
            continue
        stack = [start]
        seen[start] = 1
        size = 0
        x0 = y0 = 1 << 30
        x1 = y1 = -1
        while stack:
            i = stack.pop()
            size += 1
            y, x = divmod(i, w)
            if x < x0: x0 = x
            if x > x1: x1 = x
            if y < y0: y0 = y
            if y > y1: y1 = y
            if x + 1 < w and not seen[i + 1]:
                k = (i + 1) * 3
                if (px[k] << 16 | px[k + 1] << 8 | px[k + 2]) == key:
                    seen[i + 1] = 1; stack.append(i + 1)
            if x and not seen[i - 1]:
                k = (i - 1) * 3
                if (px[k] << 16 | px[k + 1] << 8 | px[k + 2]) == key:
                    seen[i - 1] = 1; stack.append(i - 1)
            if y + 1 < h and not seen[i + w]:
                k = (i + w) * 3
                if (px[k] << 16 | px[k + 1] << 8 | px[k + 2]) == key:
                    seen[i + w] = 1; stack.append(i + w)
            if y and not seen[i - w]:
                k = (i - w) * 3
                if (px[k] << 16 | px[k + 1] << 8 | px[k + 2]) == key:
                    seen[i - w] = 1; stack.append(i - w)
        out.append((size, (x0, y0, x1, y1)))
    out.sort(key=lambda t: -t[0])
    return out


def main():
    path = sys.argv[1]
    topn, minpx = 6, 8
    want = None
    for a in sys.argv[2:]:
        if a.startswith('--top='): topn = int(a[6:])
        if a.startswith('--min='): minpx = int(a[5:])
        if a.startswith('--colour='): want = tuple(int(v) for v in a[9:].split(','))
    w, h, px = load(path)
    n = w * h
    c = Counter()
    for i in range(n):
        j = i * 3
        c[(px[j], px[j + 1], px[j + 2])] += 1
    bg = c.most_common(1)[0][0]
    print("%s %dx%d bg=(%d,%d,%d)" % (path, w, h, *bg))
    listing = [want] if want else [k for k, _ in c.most_common(topn + 1) if k != bg][:topn]
    for col in listing:
        if col not in c:
            print("colour (%d,%d,%d): absent" % col)
            continue
        cs = comps(px, w, h, col)
        big = cs[0]
        small = [t for t in cs if t[0] < minpx]
        print("\ncolour (%d,%d,%d)  total=%d px  components=%d" % (col[0], col[1], col[2], c[col], len(cs)))
        print("   largest: %d px  bbox x[%d..%d] y[%d..%d]  %dx%d"
              % (big[0], big[1][0], big[1][2], big[1][1], big[1][3],
                 big[1][2] - big[1][0] + 1, big[1][3] - big[1][1] + 1))
        if len(cs) > 1:
            print("   next 5 : " + ", ".join("%dpx@(%d,%d)" % (t[0], t[1][0], t[1][1]) for t in cs[1:6]))
        print("   fragments < %d px: %d  (px in them: %d)" % (minpx, len(small), sum(t[0] for t in small)))


main()
