#!/usr/bin/env python3
"""tex.py -- read the .bfl container and hand back the car's textures.

A .bfl is a CMPR archive of .dds files (see docs/CONTAINER.md). This reads the
TOC, slices each entry, and decodes it with Pillow. The stage textures in the
retail game are DXT5 and need a real block decoder; the CAR textures are plain
uncompressed DDS, so Pillow handles them directly.

Naming, from the decomp's own string globals: a car's livery lives in a texture
whose name contains "bod" -- and there are usually two of them. The colourful
one is the livery; the grey one is an ambient-occlusion pass. pick_livery()
picks by saturation rather than by name, because the suffixes are not stable
across the fleet.
"""
import struct, gzip, io, os
import numpy as np
from PIL import Image

CARS = os.environ.get('CMR2_CARS', './Game/Cars')


def load(p):
    r = open(p, 'rb').read()
    return gzip.decompress(r) if r[:2] == b'\x1f\x8b' else r


def bfl_entries(blob):
    """-> [(size, offset, name)] for every entry in the archive."""
    csize = struct.unpack('<I', blob[4:8])[0]
    toc = struct.unpack('<I', blob[csize + 4:csize + 8])[0]
    pos = toc + 8
    out = []
    while pos < len(blob) - 4:
        size, off, slen = struct.unpack('<III', blob[pos:pos + 12]); pos += 12
        slen_p = slen + ((4 - slen % 4) % 4)
        name = blob[pos:pos + slen].rstrip(b'\0').decode('ascii', 'replace'); pos += slen_p
        out.append((size, off, name))
    return out


def textures_for(cid, cars=None):
    """-> {lowercase_dds_name: float array HxWx4 in 0..1}"""
    bfl = os.path.join(cars or CARS, cid + 'a1.bfl')
    blob = load(bfl)
    d = {}
    for size, off, name in bfl_entries(blob):
        if not name.lower().endswith('.dds'):
            continue
        data = blob[off + 8:off + 8 + size]
        im = Image.open(io.BytesIO(data)).convert('RGBA')
        d[name.lower()] = np.asarray(im, np.float32) / 255.0
    return d


def pick(d, *keys):
    for k in keys:
        for n in d:
            if k in n:
                return d[n]
    return None


def first(seq):
    for x in seq:
        if x is not None:
            return x
    return None


def pick_livery(d):
    """the colourful 'bod' texture is the livery; the grey one is an AO pass."""
    cands = [k for k in d if 'bod' in k and 'df' in k] or [k for k in d if 'bod' in k]
    best, bs = None, -1.0
    for k in cands:
        a = d[k][..., :3]
        sat = float(a.max(2).mean() - a.min(2).mean())
        if sat > bs:
            bs, best = sat, k
    return best


if __name__ == '__main__':
    import sys
    cid = sys.argv[1] if len(sys.argv) > 1 else '205'
    d = textures_for(cid)
    print(f"{cid}: {len(d)} textures")
    print(f"  livery -> {pick_livery(d)}")
    print(f"  names  -> {sorted(d.keys())[:8]}{' ...' if len(d) > 8 else ''}")
