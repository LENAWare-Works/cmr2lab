#!/usr/bin/env python3
"""render_tex.py -- assemble one car and rasterise it. No GPU, no engine.

Two stages:

  build(cid)   flattens a car into ONE vertex list. The subtlety worth knowing:
               a .c3d holds FOUR separate wheel parts, each modelled at the
               origin. Drawing the file as-is stacks all four wheels inside the
               body and the result reads as an exploded model. So the body is
               taken without the wheel parts, and ONE wheel part is then stamped
               at the four corners. WHEEL_X/Y/Z are the axle positions for the
               CMR2 fleet; a car with a different track or wheelbase needs these
               adjusted, which is the same constraint the engine has (see
               docs/CAR-FORMAT.md -- physics reads halfExtents + wheelPos[4]
               and never consults the mesh).

  render(...)  z-buffered scanline rasteriser with per-pixel interpolated
               normals, two directional lights, specular, and UV0 texturing.
               Returns uint8 RGB, or (RGB, mask) when want_mask=True -- the mask
               is what the grounding pass needs to find the contact line.
"""
import math
import numpy as np

import c3dlib

# axle positions for the CMR2 fleet (metres, car space)
WHEEL_X, WHEEL_Y, WHEEL_Z = 1.245, -0.227, 0.747

# A .c3d is a set of render passes, not one mesh, and only some of them are the
# car. The first two characters of a part name are its draw-order prefix, and
# those ARE stable across the fleet -- the rest of the name is not
# (06UnlitSim / 06IntSim / 06Unlit, 15undsim / 15UndSim, 09Bonnet / 09BonDay).
#   05  bonnet-camera interior        14  light-effect flares
#   06  unlit shadow / interior sim   15  underbody sim
# This viewer draws everything opaque and lit, so those four passes come out as
# a grey slab under the car and loose plates floating around it. They are not
# part of the body and must not be drawn.
NON_BODY_PREFIX = ('05', '06', '14', '15')


def non_body_ids(parts):
    """Part ids of the sim / camera / effect passes, ready for skip_parts."""
    return [q['idx'] for q in parts
            if 'Whl' not in q['name'] and q['name'][:2] in NON_BODY_PREFIX]


def build(cid, skip_parts=(), skip_non_body=True):
    """-> (hdr, parts, V, N, UV, T, TP)  with wheels stamped at the 4 corners."""
    m = c3dlib.C3D(c3dlib.car_file(cid))
    P = m.parts()
    verts, norms, uvs, tris, tpart = m.geometry()
    V = np.array(verts, np.float64); N = np.array(norms, np.float64)
    UV = np.array(uvs, np.float64); T = np.array(tris, np.int32); TP = np.array(tpart, np.int32)

    wids = [p['idx'] for p in P if 'Whl' in p['name']]

    # np.isin(TP, {5}) matches NOTHING: np.asarray({5}) is a 0-d OBJECT array,
    # not an array of elements. Every caller passed a set, so skip_parts was
    # silently ignored from the day this was written. Normalise to a list.
    skip = [int(x) for x in skip_parts]
    if skip_non_body:
        skip = skip + non_body_ids(P)
    isw = np.isin(TP, wids) | np.isin(TP, skip)
    body_t, body_tp = T[~isw], TP[~isw]
    keep_v = np.unique(body_t) if len(body_t) else np.array([], np.int32)
    remap = -np.ones(len(V), np.int32); remap[keep_v] = np.arange(len(keep_v))
    Vb, Nb, Ub = V[keep_v], N[keep_v], UV[keep_v]
    Tb = remap[body_t]

    if wids:
        wi = wids[0]
        pv = P[wi]['V']; start = sum(p['V'] for p in P[:wi])
        vs = np.arange(start, start + pv)
        wv, wn, wu = V[vs], N[vs], UV[vs]
        wsel = (TP == wi); wt = T[wsel] - start
        corners = [(-WHEEL_X, -WHEEL_Z), (-WHEEL_X, WHEEL_Z),
                   (WHEEL_X, -WHEEL_Z), (WHEEL_X, WHEEL_Z)]
        for n, (dx, dz) in enumerate(corners):
            base = len(Vb)
            Vb = np.vstack([Vb, wv + np.array([dx, WHEEL_Y, dz])])
            Nb = np.vstack([Nb, wn]); Ub = np.vstack([Ub, wu])
            Tb = np.vstack([Tb, wt + base])
            body_tp = np.concatenate([body_tp, np.full(len(wt), 100 + n)])
    return m, P, Vb, Nb, Ub, Tb, body_tp


def make_wheels(P, V, N, UV, T, TP):
    """the four wheel parts' triangles, placed at their axle positions too.
    Used for measuring the true contact line."""
    wids = [p['idx'] for p in P if 'Whl' in p['name']]
    if not wids:
        return None
    wi = wids[0]
    pv = P[wi]['V']; start = sum(p['V'] for p in P[:wi])
    vs = np.arange(start, start + pv)
    wv, wn, wu = V[vs], N[vs], UV[vs]
    wsel = (TP == wi); wt = T[wsel] - start
    Vb = Nb = Ub = None; Tb = []
    corners = [(-WHEEL_X, -WHEEL_Z), (-WHEEL_X, WHEEL_Z),
               (WHEEL_X, -WHEEL_Z), (WHEEL_X, WHEEL_Z)]
    for dx, dz in corners:
        base = 0 if Vb is None else len(Vb)
        add = wv + np.array([dx, WHEEL_Y, dz])
        Vb = add if Vb is None else np.vstack([Vb, add])
        Nb = wn if Nb is None else np.vstack([Nb, wn])
        Ub = wu if Ub is None else np.vstack([Ub, wu])
        Tb.append(wt + base)
    return Vb, Nb, Ub, np.vstack(Tb)


def sample(texel, u, v, flip=False):
    TH, TW = texel.shape[:2]
    if flip:
        v = 1.0 - v
    u = np.clip(u, 0, 1 - 1e-6) * (TW - 1)
    v = np.clip(v, 0, 1 - 1e-6) * (TH - 1)
    return texel[v.astype(np.int32), u.astype(np.int32)]


def render(V, N, UV, T, TP, texmap, fallback, W=760, H=500, az=214, el=11,
           dist=9.6, fov=30, bg=(155, 181, 170), flip=False, want_mask=False):
    lo, hi = V.min(0), V.max(0); ctr = (lo + hi) / 2
    f = 1.0 / math.tan(math.radians(fov) / 2)
    a, e = math.radians(az), math.radians(el)
    fwd = np.array([math.cos(e) * math.sin(a), math.sin(e), math.cos(e) * math.cos(a)])
    eye = ctr + fwd * dist
    zax = (eye - ctr); zax /= np.linalg.norm(zax)
    xax = np.cross(np.array([0, 1, 0]), zax); xax /= np.linalg.norm(xax)
    yax = np.cross(zax, xax)
    R = np.stack([xax, yax, zax])
    cam = (V - eye) @ R.T
    z = cam[:, 2]; ok = z < -1e-4
    sx = (cam[:, 0] * f / (-z) * (H / 2)) + W / 2
    sy = (-cam[:, 1] * f / (-z) * (H / 2)) + H / 2

    bg = tuple(c / 255.0 for c in bg) if max(bg) > 1.0 else bg
    img = np.zeros((H, W, 3), np.float64); img[:, :] = bg
    zb = np.full((H, W), 1e9)

    L1 = np.array([0.55, 0.72, 0.42]); L1 /= np.linalg.norm(L1)
    L2 = np.array([-0.62, 0.35, -0.70]); L2 /= np.linalg.norm(L2)
    view = zax

    for i in range(len(T)):
        a_, b_, c_ = T[i]
        if not (ok[a_] and ok[b_] and ok[c_]):
            continue
        x0, y0, x1, y1, x2, y2 = sx[a_], sy[a_], sx[b_], sy[b_], sx[c_], sy[c_]
        minx = max(int(min(x0, x1, x2)), 0); maxx = min(int(max(x0, x1, x2)) + 1, W)
        miny = max(int(min(y0, y1, y2)), 0); maxy = min(int(max(y0, y1, y2)) + 1, H)
        if minx >= maxx or miny >= maxy:
            continue
        d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(d) < 1e-9:
            continue
        xs = np.arange(minx, maxx) + 0.5; ys = np.arange(miny, maxy) + 0.5
        gx, gy = np.meshgrid(xs, ys)
        w0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / d
        w1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / d
        w2 = 1 - w0 - w1
        mm = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not mm.any():
            continue
        zz = w0 * z[a_] + w1 * z[b_] + w2 * z[c_]
        sub = zb[miny:maxy, minx:maxx]
        hit = mm & (zz < sub)
        if not hit.any():
            continue
        nn = (w0[..., None] * N[a_] + w1[..., None] * N[b_] + w2[..., None] * N[c_])
        nn /= (np.linalg.norm(nn, axis=2, keepdims=True) + 1e-9)
        pid = int(TP[i]); t = texmap.get(pid)
        if t is None:
            col = np.array(fallback.get(pid, (0.7, 0.7, 0.72)), np.float64)
            rgb = col[None, None, :]
        else:
            u = w0 * UV[a_, 0] + w1 * UV[b_, 0] + w2 * UV[c_, 0]
            v = w0 * UV[a_, 1] + w1 * UV[b_, 1] + w2 * UV[c_, 1]
            rgb = sample(t, u, v, flip)[..., :3]
        l1 = np.clip(nn @ L1, 0, 1); l2 = np.clip(nn @ L2, 0, 1)
        diff = 0.42 + 0.58 * l1 + 0.22 * l2 + 0.10
        hh = nn + view; hh /= (np.linalg.norm(hh, axis=2, keepdims=True) + 1e-9)
        spec = np.clip(np.sum(nn * hh, axis=2), 0, 1) ** 30 * 0.5 * np.clip(nn @ L1, 0, 1)
        rim = (1 - np.clip(nn @ view, 0, 1)) ** 3 * 0.08
        rgb = np.clip(rgb * diff[..., None] + spec[..., None] + rim[..., None], 0, 1)
        pix = img[miny:maxy, minx:maxx]
        np.copyto(pix, rgb, where=hit[..., None])
        img[miny:maxy, minx:maxx] = pix
        np.copyto(sub, zz, where=hit)

    out = (img * 255).astype(np.uint8)
    if want_mask:
        return out, (zb < 1e8)
    return out
