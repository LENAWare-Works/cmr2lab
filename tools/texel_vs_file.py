#!/usr/bin/env python3
"""texel_vs_file.py -- is the texel the port samples the texel that is in the FILE?

WHY THIS EXISTS
  Every instrument in this tree (LENA-MENUTEX, LENA-STGTEX) prints, per draw, the texel the
  port's own CPU-side lookup returns at a vertex's UV, and predicts the fragment from it. The
  predictions matching the framebuffer only proves the port is SELF-CONSISTENT: if the upload
  were wrong, the prediction and the picture would be wrong together. This tool closes that
  loop from the other side, offline, with no GPU: it reads the same texel out of the game's own
  .bfl/.dds bytes, using the port's own rule (x = floor(u*w), y = floor(v*h)), and prints
  MATCH or DIFFER.

USAGE
  texel_vs_file.py <car-or-any.bfl> <texture-name.dds> "u,v,0xAARRGGBB" ["u,v,0xAARRGGBB" ...]

  The (u,v,texel) triples are transcribed from the port's own log lines, e.g.
    [MENUTEX]    v0 idx=2 uv0=(0.924088,0.255157) ... pred=ff080905
  Pair a draw's UVs with the texture that draw BOUND (tex0 in the same log line group) --
  attributing a UV to the wrong texture produces a false DIFFER. That mistake was made once
  this round before the tex0 column was read; do not repeat it.

MEASURED RESULT 2026-10-11 (foca1.bfl = the frontend preview car, the Ford Focus):
  affnwbdf.dds  (0.924088,  0.255157) file ff080905  port ff080905  MATCH
  affnwbdf.dds  (0.0102844, 0.5)      file ff080008  port ff080008  MATCH
  affnwbdf.dds  (0.744843,  0.0759125) file ff080808 port ff080808  MATCH
  -> file -> DDraw surface -> SetTexture -> texel lookup is faithful for the car's draws.
"""
import struct, sys, os

def dxt_block(blk, dxt5):
    out = []
    if dxt5:
        a0, a1 = blk[0], blk[1]
        abits = int.from_bytes(blk[2:8], 'little')
        c0, c1 = struct.unpack_from('<HH', blk, 8)
        cbits = struct.unpack_from('<I', blk, 12)[0]
    else:
        c0, c1 = struct.unpack_from('<HH', blk, 0)
        cbits = struct.unpack_from('<I', blk, 4)[0]
        a0 = a1 = abits = None
    col = lambda c: (((c >> 11) & 31) * 255 // 31, ((c >> 5) & 63) * 255 // 63, (c & 31) * 255 // 31)
    cols = [col(c0), col(c1)]
    if c0 > c1:
        cols += [tuple((2 * cols[0][k] + cols[1][k]) // 3 for k in range(3)),
                 tuple((cols[0][k] + 2 * cols[1][k]) // 3 for k in range(3))]
    else:
        cols += [tuple((cols[0][k] + cols[1][k]) // 2 for k in range(3)), (0, 0, 0)]
    for py in range(4):
        for px in range(4):
            idx = (cbits >> (2 * (4 * py + px))) & 3
            if dxt5:
                ai = (abits >> (3 * (4 * py + px))) & 7
                if ai == 0:      a = a0
                elif ai == 1:    a = a1
                elif a0 > a1:    a = ((8 - ai) * a0 + (ai - 1) * a1) // 7
                else:            a = ((6 - ai) * a0 + (ai - 1) * a1) // 5 if ai < 7 else 0
            else:
                a = 0 if (c0 <= c1 and idx == 3) else 255
            out.append((cols[idx][0], cols[idx][1], cols[idx][2], a))
    return out

def find_blob(bf, want):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'RACE'))
    import bfl
    buf = bfl.load(bf)
    for fid, off, nlen, name, p in bfl.entries(buf):
        if name == want:
            return bfl.blob(buf, off)
    return None

def texel(blob, u, v):
    (size, flags, h, w, pitch, depth, mips) = struct.unpack_from('<7I', blob, 4)
    fcc = blob[0x54:0x58]
    if fcc not in (b'DXT5', b'DXT1'):
        return None
    dxt5 = (fcc == b'DXT5')
    need = 16 if dxt5 else 8
    x = min(w - 1, int(u * w))          # the port's own rule: mt_floori(u*w)
    y = min(h - 1, int(v * h))
    bw = (w + 3) // 4
    bx, by = x // 4, y // 4
    o = (by * bw + bx) * need
    px = dxt_block(blob[128 + o:128 + o + need], dxt5)
    r, g, b, a = px[(y % 4) * 4 + (x % 4)]
    return w, h, (a << 24) | (r << 16) | (g << 8) | b

def main():
    bf, name = sys.argv[1], sys.argv[2]
    blob = find_blob(bf, name)
    if blob is None:
        raise SystemExit('no %s in %s' % (name, bf))
    print('%-20s  %s' % (name, os.path.basename(bf)))
    for spec in sys.argv[3:]:
        u, v, want = spec.split(',')
        r = texel(blob, float(u), float(v))
        if r is None:
            print('  uv=(%s,%s)  not DXT' % (u, v)); continue
        w, h, got = r
        want = want.lower().replace('0x', '')
        got_s = '%08x' % got
        d = sum(abs(int(got_s[i:i+2], 16) - int(want[i:i+2], 16)) for i in (0, 2, 4, 6))
        print('  uv=(%s,%s)  %dx%d  file=%s  port=%s  %s (sum|d|=%d)'
              % (u, v, w, h, got_s, want, 'MATCH' if got_s == want else 'DIFFER', d))

if __name__ == '__main__':
    main()
