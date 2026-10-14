#!/usr/bin/env python3
"""livery.py -- decide WHICH texture goes on WHICH part.

The part names in a .c3d are literal: "01WhlLOD00", "24semitran", "14LigEffect",
"21bonunder". So the assignment is by name, with one real subtlety -- there are
usually TWO body textures and only one is the livery. The other is a grey
ambient-occlusion pass. pick_livery() chooses by saturation, because the name
suffixes are not stable across the fleet.

Parts deliberately left untextured: the lights and the underbody. In the engine
these are unlit / additive, and giving them a body texture makes them look
painted on.

The four wheel parts are all stacked at the origin in the file, but build()
stamps them out to the corners and renumbers them 100..103, so the wheel texture
is mapped to those four ids as well as to the original part index.
"""
import c3dlib
import tex


def build_texmap(cid, d, verbose=True):
    """-> {part_index: float array HxWx4}"""
    body = tex.pick_livery(d)
    if verbose:
        print(f"  {cid}: livery = {body}")
    B = d[body]
    m = {}

    for p in c3dlib.C3D(c3dlib.car_file(cid)).parts():
        n = p['name'].lower()
        if 'whl' in n:
            t = tex.first([tex.pick(d, 'nwhdf'), tex.pick(d, 'nwh')])
        elif 'light' in n:
            t = None
        elif 'und' in n:
            t = None
        elif 'semi' in n or 'trans' in n:
            t = tex.first([tex.pick(d, 'glidf')])
        else:
            t = B
        if t is not None:
            m[p['idx']] = t

    # the stamped wheels
    wt = tex.first([tex.pick(d, 'nwhdf'), tex.pick(d, 'nwh')])
    if wt is not None:
        for i in (100, 101, 102, 103):
            m[i] = wt
    return m


# fallback colours for parts with no texture
FB = {6: (0.05, 0.09, 0.15)}
for _i in (100, 101, 102, 103):
    FB[_i] = (0.13, 0.13, 0.15)
