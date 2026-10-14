#!/usr/bin/env python3
"""c3dlib.py -- CMR2 PP_F geometry reader.

Field map measured from the retail files (2026-10-12), not guessed:

  vertex pool : starts at the c14 array offset, stride 48, count = c14
      +0  vec3 POSITION   (x = length, +x = front | y = up | z = width)
      +12 vec3 NORMAL
      +24 2 floats        (junk on the 205 -- skipped)
      +32 vec2 TEXCOORD0  (the one to use; 100% inside [0,1])
      +40 vec2 TEXCOORD1  (secondary / lightmap -- not a substitute)
  face records: c20 array offset +12, stride 76, 3x u16 indices at +52
  part records: c1a array offset, stride 288
      name[12] | d3 = vblk (byte offset into pool) | d4 = V
      d8 = face base idx | d10 = F

A car is NOT one mesh: a .c3d holds several parts (four separate wheel parts,
an interior layer, glass, lights) and the retail disc ships ten .c3d variants
per car. This reader exposes parts individually; the caller decides what to draw.
"""
import struct, gzip, os

ST_V, OFF_POS, OFF_NRM, OFF_UV0, OFF_UV1 = 48, 0, 12, 32, 40
ST_F, OFF_IDX = 76, 52

# Directory holding the retail .c3d / .bfl files. Override with CMR2_CARS.
CARS = os.environ.get('CMR2_CARS', './Game/Cars')


def load(p):
    r = open(p, 'rb').read()
    b = gzip.decompress(r) if r[:2] == b'\x1f\x8b' else r
    return b[8:] if b[:4] == b'CMPR' else b


class C3D:
    def __init__(self, path):
        self.path = path
        p = self.p = load(path)
        if p[:4] != b'PP_F':
            raise ValueError('not PP_F: ' + path)
        H = lambda o, f: struct.unpack_from(f, p, o)[0]
        self.texcount = H(0x24, '<H')
        c18, c1a, c1c, c1e = H(0x18, '<H'), H(0x1a, '<H'), H(0x1c, '<H'), H(0x1e, '<H')
        c20, c14, c10, c28, c26 = H(0x20, '<I'), H(0x14, '<I'), H(0x10, '<I'), H(0x28, '<H'), H(0x26, '<H')
        o18 = 0x30
        o1a = o18 + c18 * 396
        o1c = o1a + c1a * 288
        o1e = o1c + c1c * 288
        o28 = o1e + c1e * 136
        o20 = o28 + c28 * 28
        o14 = o20 + c20 * 76
        o10 = o14 + c14 * 52
        o26 = o10 + c10 * 20
        self.nparts, self.nvpool, self.nfaces = c1a, c14, c20
        self.VB = o14          # vertex pool base (position at +0)
        self.FB = o20 + 12     # face base (measured: +12)
        self.o1a = o1a
        # identity: header + every array + the texture trailer == file size
        self.identity = (o26 + c26 * 92 == len(p) - self.texcount * 24 - self.texcount * 260)
        te = len(p) - self.texcount * 24 - self.texcount * 260
        self.tex_names = [p[te + i * 24: te + i * 24 + 12].split(b'\0')[0].decode('latin1', 'ignore')
                          for i in range(self.texcount)]
        pe = te + self.texcount * 24
        self.tex_paths = [p[pe + i * 260: pe + i * 260 + 120].split(b'\0')[0].decode('latin1', 'ignore')
                          for i in range(self.texcount)]
        self.tex_base = [os.path.basename(x).lower() for x in self.tex_paths]

    def parts(self):
        out = []
        for i in range(self.nparts):
            r = self.o1a + i * 288
            d = struct.unpack_from('<20I', self.p, r)
            name = self.p[r:r + 12].split(b'\0')[0].decode('latin1', 'ignore')
            out.append(dict(idx=i, name=name, vblk=d[3], V=d[4],
                            fbase=d[9], F=d[10], mat=d[12], mat2=d[13]))
        return out

    def geometry(self):
        """-> (verts, norms, uvs, tris, part_of_tri)"""
        p, VB, FB = self.p, self.VB, self.FB
        verts = []; norms = []; uvs = []; tris = []; tpart = []
        for pt in self.parts():
            base = len(verts); V = pt['V']; vb = VB + pt['vblk']
            for q in range(V):
                o = vb + q * ST_V
                verts.append(struct.unpack_from('<3f', p, o + OFF_POS))
                norms.append(struct.unpack_from('<3f', p, o + OFF_NRM))
                uvs.append(struct.unpack_from('<2f', p, o + OFF_UV0))
            fb = FB + pt['fbase']
            for k in range(pt['F']):
                a, b, c = struct.unpack_from('<3H', p, fb + k * ST_F + OFF_IDX)
                if a < V and b < V and c < V and a != b and b != c and a != c:
                    tris.append((base + a, base + b, base + c)); tpart.append(pt['idx'])
        return verts, norms, uvs, tris, tpart

    def bbox(self):
        v = self.geometry()[0]
        return ([min(x[i] for x in v) for i in range(3)],
                [max(x[i] for x in v) for i in range(3)])


def car_file(cid):
    for suf in ('a1N', 'a1L', 'a1S', 'a1'):
        f = os.path.join(CARS, cid + suf + '.c3d')
        if os.path.exists(f):
            return f
    raise FileNotFoundError(cid)


if __name__ == '__main__':
    import sys
    for cid in (sys.argv[1:] or ['205']):
        m = C3D(car_file(cid)); v, n, u, t, tp = m.geometry()
        lo, hi = m.bbox()
        print(f"{cid}: parts={m.nparts} V={len(v)} tris={len(t)}  "
              f"dims {hi[0]-lo[0]:.2f} x {hi[1]-lo[1]:.2f} x {hi[2]-lo[2]:.2f}  "
              f"identity_ok={m.identity}")
