#!/usr/bin/env python3
"""scan.py -- CPU-only frame scanner + pair matcher (no numpy, no PIL).

Every frame is decoded once, then measured:
  mean, sd          -- the controls the phone used to argue the pair was comparable
  speckle  %        -- share of pixels differing from BOTH horizontal neighbours by
                       >=24 luma in OPPOSITE directions (the phone's definition)
  sig 64x40         -- coarse colour signature, used to find the SAME SCREEN in two
                       different runs so a noise delta is never quoted between two
                       different moments.

Usage:
  scan.py frames FILE...              one line per file
  scan.py pairs A1 B1 A2 B2 ...       per-pair table incl. content divergence
  scan.py match A1..An -- B1..Bm      every A x B pair by content match, then the
                                      speckle delta of the best-matched pairs
"""
import sys, zlib, struct

_cache = {}

def decode(p):
    if p in _cache: return _cache[p]
    d = open(p, 'rb').read()
    if d.startswith(b'\x89PNG'):
        i, idat, w, h, nch = 8, b'', 0, 0, 3
        while i < len(d):
            ln = struct.unpack('>I', d[i:i+4])[0]; typ = d[i+4:i+8]; dat = d[i+8:i+8+ln]
            if typ == b'IHDR':
                w, h = struct.unpack('>II', dat[:8]); bd, ct = dat[8], dat[9]
                assert bd == 8 and ct in (2, 6), f"{p}: need 8-bit RGB/RGBA, got {bd}/{ct}"
                nch = 3 if ct == 2 else 4
            if typ == b'IDAT': idat += dat
            i += 12 + ln
        raw = zlib.decompress(idat); stride = w*nch
        out = bytearray(w*h*3); prev = bytearray(stride); pos = 0
        for y in range(h):
            ft = raw[pos]; pos += 1; line = bytearray(raw[pos:pos+stride]); pos += stride
            if ft == 1:
                for x in range(nch, stride): line[x] = (line[x] + line[x-nch]) & 255
            elif ft == 2:
                for x in range(stride): line[x] = (line[x] + prev[x]) & 255
            elif ft == 3:
                for x in range(stride):
                    a = line[x-nch] if x >= nch else 0
                    line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
            elif ft == 4:
                for x in range(stride):
                    a = line[x-nch] if x >= nch else 0
                    b = prev[x]; c = prev[x-nch] if x >= nch else 0
                    pa = abs(b-c); pb = abs(a-c); pc = abs(a+b-2*c)
                    pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                    line[x] = (line[x] + pr) & 255
            elif ft != 0: raise ValueError(f"{p}: filter {ft}")
            prev = line
            if nch == 3: out[y*w*3:(y+1)*w*3] = line
            else:
                for x in range(w): out[(y*w+x)*3:(y*w+x)*3+3] = line[x*4:x*4+3]
        res = (w, h, bytes(out))
    else:
        f = []; i = 2
        while len(f) < 3:
            while d[i:i+1].isspace(): i += 1
            if d[i:i+1] == b'#':
                while d[i:i+1] != b'\n': i += 1
                continue
            j = i
            while not d[j:j+1].isspace(): j += 1
            f.append(int(d[i:j])); i = j
        i += 1; w, h, _ = f
        res = (w, h, d[i:i+w*h*3])
    _cache[p] = res
    return res

def luma(w, h, buf):
    return bytes((buf[k]*77 + buf[k+1]*150 + buf[k+2]*29) >> 8 for k in range(0, w*h*3, 3))

def sig(w, h, L, cw=64, ch=40):
    # coarse mean-luma signature: s=16 in x, s=20 in y -> 64x40
    sx, sy = w//cw, h//ch
    out = []
    for cy in range(ch):
        y0 = cy*sy
        for cx in range(cw):
            x0 = cx*sx; t = 0
            for y in range(y0, y0+sy):
                row = y*w
                t += sum(L[row+x0:row+x0+sx])
            out.append(t/(sx*sy))
    return out

def band_speck(L, W, H, y0, y1):
    sp = 0
    for y in range(y0, y1):
        row = y*W
        for x in range(1, W-1):
            c = L[row+x]; dl = c-L[row+x-1]; dr = c-L[row+x+1]
            if (dl >= 24 and dr >= 24) or (dl <= -24 and dr <= -24): sp += 1
    return 100.0*sp/(W*(y1-y0))

class F:
    __slots__ = ('p','w','h','L','mean','sd','speck','sig','th','bo','t3')

def load(p):
    f = F(); f.p = p
    f.w, f.h, buf = decode(p); n = f.w*f.h
    L = luma(f.w, f.h, buf); f.L = L
    f.mean = sum(L)/n
    f.sd = (sum((v-f.mean)**2 for v in L)/n)**0.5
    W = f.w
    sp = 0
    for y in range(f.h):
        row = y*W
        for x in range(1, W-1):
            c = L[row+x]; dl = c-L[row+x-1]; dr = c-L[row+x+1]
            if (dl >= 24 and dr >= 24) or (dl <= -24 and dr <= -24): sp += 1
    f.speck = 100.0*sp/n
    f.sig = sig(f.w, f.h, L)
    f.th = band_speck(L, W, f.h, 0, f.h//2)
    f.bo = band_speck(L, W, f.h, f.h//2, f.h)
    f.t3 = tuple(band_speck(L, W, f.h, k*f.h//3, (k+1)*f.h//3) for k in range(3))
    return f

def div(fa, fb):
    return sum(abs(a-b) for a, b in zip(fa.sig, fb.sig))/len(fa.sig)

def pixdiff(a, b, out=None, amp=6):
    fa, fb = load(a), load(b)
    W, H = fa.w, fa.h
    A, B = fa.L, fb.L
    n = W*H
    d1 = d8 = d24 = 0
    mx = 0
    rows = []
    for y in range(H):
        row = y*W
        orow = bytearray()
        for x in range(W):
            d = abs(A[row+x]-B[row+x])
            if d: d1 += 1
            if d > 8: d8 += 1
            if d >= 24: d24 += 1
            if d > mx: mx = d
            if out: orow += bytes((min(255, d*amp),)*3)
        if out: rows.append(orow)
    print(f"{a.split('/')[-1][:26]:26s} vs {b.split('/')[-1][:26]:26s} "
          f"any={100.0*d1/n:6.3f}%  >8={100.0*d8/n:6.3f}%  >24={100.0*d24/n:6.3f}%  max={mx:3d}")
    if out:
        with open(out, 'wb') as f:
            f.write(b'P6\n%d %d\n255\n' % (W, H))
            f.write(b''.join(rows))

if __name__ == '__main__':
    mode = sys.argv[1]; args = sys.argv[2:]
    if mode == 'frames':
        print(f"{'file':44s} {'mean':>7s} {'sd':>7s} {'speck%':>7s} {'top1/3':>8s} {'mid1/3':>8s} {'bot1/3':>8s}")
        for a in args:
            f = load(a)
            print(f"{a.split('/')[-1][:44]:44s} {f.mean:7.2f} {f.sd:7.2f} {f.speck:9.3f} "
                  f"{f.t3[0]:8.3f} {f.t3[1]:8.3f} {f.t3[2]:8.3f}")
    elif mode == 'pairs':
        print(f"{'A':30s} {'B':30s} {'meanA':>6s} {'meanB':>6s} {'sdA':>6s} {'sdB':>6s} "
              f"{'spkA':>7s} {'spkB':>7s} {'ratio':>6s} {'div':>6s}")
        for k in range(0, len(args), 2):
            fa, fb = load(args[k]), load(args[k+1])
            r = fa.speck/fb.speck if fb.speck else float('inf')
            print(f"{args[k].split('/')[-1][:30]:30s} {args[k+1].split('/')[-1][:30]:30s} "
                  f"{fa.mean:6.1f} {fb.mean:6.1f} {fa.sd:6.2f} {fb.sd:6.2f} "
                  f"{fa.speck:7.3f} {fb.speck:7.3f} {r:6.2f} {div(fa,fb):6.2f}")
    elif mode == 'diff':
        for k in range(0, len(args), 2):
            pixdiff(args[k], args[k+1])
    elif mode == 'match':
        i = args.index('--'); A = args[:i]; B = args[i+1:]
        FA = [(a, load(a)) for a in A]; FB = [(b, load(b)) for b in B]
        rows = []
        for a, fa in FA:
            for b, fb in FB:
                rows.append((div(fa, fb), a, b, fa, fb))
        rows.sort()
        print("best CONTENT matches (a pair whose divergence is small is the same moment)\n")
        print(f"{'A':30s} {'B':30s} {'meanA':>6s} {'meanB':>6s} {'sdA':>6s} {'sdB':>6s} "
              f"{'spkA':>7s} {'spkB':>7s} {'ratio':>6s} {'div':>6s}")
        for d, a, b, fa, fb in rows[:10]:
            r = fa.speck/fb.speck if fb.speck else float('inf')
            print(f"{a.split('/')[-1][:30]:30s} {b.split('/')[-1][:30]:30s} "
                  f"{fa.mean:6.1f} {fb.mean:6.1f} {fa.sd:6.2f} {fb.sd:6.2f} "
                  f"{fa.speck:7.3f} {fb.speck:7.3f} {r:6.2f} {d:6.2f}")
        print("\nwithin-A spread (content only, same build):")
        ws = sorted((div(fa.sig and fa, fb) if False else div(fa, fb), a, b)
                    for i2, (a, fa) in enumerate(FA) for b, fb in FA[i2+1:])
        for d, a, b in ws[:3]:
            print(f"   {a.split('/')[-1][:28]:28s} {b.split('/')[-1][:28]:28s} div={d:6.2f}")
        print("\nwithin-B spread (content only, same built):")
        ws = sorted((div(fa, fb), a, b) for i2, (a, fa) in enumerate(FB) for b, fb in FB[i2+1:])
        for d, a, b in ws[:3]:
            print(f"   {a.split('/')[-1][:28]:28s} {b.split('/')[-1][:28]:28s} div={d:6.2f}")
