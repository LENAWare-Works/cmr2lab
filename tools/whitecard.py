#!/usr/bin/env python3
"""whitecard.py -- find a compact bright card in a CMR2 capture, offline.

  python3 whitecard.py <file.ppm> [--thr 240] [--map] [--quiet]

Measures, from the bytes only:
  * the exact count and fraction of near-white pixels (min(r,g,b) >= thr)
  * their bounding box, their row histogram (where they are vertically)
  * the largest 4-connected near-white component: bbox, area, and how
    "card-like" it is (fill = area / bbox area)
Nothing is guessed. No GPU, no window.
"""
import sys

W = 1280
H = 800


def load(path):
    d = open(path, 'rb').read()
    parts = d.split(b'\n', 3)
    assert parts[0] == b'P6', parts[0]
    w, h = (int(x) for x in parts[1].split())
    px = parts[3]
    return w, h, px


def main():
    path = sys.argv[1]
    args = sys.argv[2:]
    thr = 240
    if '--thr' in args:
        thr = int(args[args.index('--thr') + 1])
    do_map = '--map' in args
    quiet = '--quiet' in args
    w, h, px = load(path)

    mask = bytearray(w * h)
    n = 0
    x0, y0, x1, y1 = w, h, -1, -1
    rows = [0] * h
    for y in range(h):
        base = y * w * 3
        for x in range(w):
            o = base + x * 3
            if px[o] >= thr and px[o + 1] >= thr and px[o + 2] >= thr:
                mask[y * w + x] = 1
                n += 1
                rows[y] += 1
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y

    if not quiet:
        print(f"{path} {w}x{h} thr={thr}")
        print(f"  near-white pixels: {n} = {100.0*n/(w*h):.2f}%  "
              f"bbox x[{x0}..{x1}] y[{y0}..{y1}]")
        # row bands where the white lives
        band = 20
        for b in range(0, h, band):
            c = sum(rows[b:b + band])
            if c:
                print(f"    y {b:4d}-{b+band-1:4d}: {c:7d} {100.0*c/n:5.1f}%  "
                      f"{'#'*min(60, c*60//max(1,n))}")

    # largest 4-connected component (iterative, no recursion)
    best = None
    seen = bytearray(w * h)
    for sy in range(h):
        for sx in range(w):
            if not mask[sy * w + sx] or seen[sy * w + sx]:
                continue
            stack = [sy * w + sx]
            seen[sy * w + sx] = 1
            area = 0
            cx0, cy0, cx1, cy1 = sx, sy, sx, sy
            while stack:
                p = stack.pop()
                py, pxx = divmod(p, w)
                area += 1
                if pxx < cx0: cx0 = pxx
                if pxx > cx1: cx1 = pxx
                if py < cy0: cy0 = py
                if py > cy1: cy1 = py
                if pxx > 0 and mask[p - 1] and not seen[p - 1]:
                    seen[p - 1] = 1; stack.append(p - 1)
                if pxx < w - 1 and mask[p + 1] and not seen[p + 1]:
                    seen[p + 1] = 1; stack.append(p + 1)
                if py > 0 and mask[p - w] and not seen[p - w]:
                    seen[p - w] = 1; stack.append(p - w)
                if py < h - 1 and mask[p + w] and not seen[p + w]:
                    seen[p + w] = 1; stack.append(p + w)
            if best is None or area > best[0]:
                best = (area, cx0, cy0, cx1, cy1)

    if best:
        area, cx0, cy0, cx1, cy1 = best
        bw, bh = cx1 - cx0 + 1, cy1 - cy0 + 1
        print(f"  largest white component: area {area} px  "
              f"bbox x[{cx0}..{cx1}] y[{cy0}..{cy1}]  {bw}x{bh}  "
              f"fill {100.0*area/(bw*bh):.1f}%")
        cx = (cx0 + cx1) // 2; cy = (cy0 + cy1) // 2
        print(f"  centre ({cx},{cy})  = {100.0*cx/w:.0f}% across, "
              f"{100.0*cy/h:.0f}% down")

    if do_map:
        cols, rws = 64, 20
        sx_ = max(1, w // cols); sy_ = max(1, h // rws)
        print("  white map (each cell 20x40 px):")
        for cy in range(rws):
            line = []
            for cx in range(cols):
                c = 0
                for y in range(cy * sy_, min((cy + 1) * sy_, h)):
                    b = y * w
                    for x in range(cx * sx_, min((cx + 1) * sx_, w)):
                        c += mask[b + x]
                line.append('#' if c > 40 else ('+' if c > 8 else ('.' if c else ' ')))
            print("   |" + "".join(line) + "|")


main()
