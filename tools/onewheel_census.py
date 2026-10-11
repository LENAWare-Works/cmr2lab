#!/usr/bin/env python3
"""onewheel_census.py -- does a CAR reach a draw as PARTS, and which parts?

Reads the traces the port already writes (no GPU, no new instrumentation):
  [TEXREQ] ... tris=N parts=P ... [pK slot=S name='....EXT' idx=I]   -> mesh -> part -> texture id -> NAME
  [TEXUSE] ... id=I cov=C screens draws=D ...                        -> which texture ids REACH A DRAW

Answers exactly the question the phone asked ("count which PP_F blobs reach a draw
and compare against the parts of that car"), at texture-name granularity instead of
blob granularity -- a car part in CMR2 is a named texture (BODY, WHEEL, GLASS,
LIGHT, INTERIOR...), so name families give the part, and TEXUSE says whether it drew.

Usage: python3 onewheel_census.py [log ...]
"""
import re, sys, glob, os
from collections import defaultdict, Counter

REQ = re.compile(r"\[TEXREQ\]\s+MESH\s+mesh=(\w+)\s+tris=(\d+)\s+parts=(\d+).*?"
                 r"\[p(\d+)\s+slot=(\d+)\s+name='([^']*)'\s+idx=(\d+)\]")
USE = re.compile(r"\[TEXUSE\]\s+id=(\d+)\s+cov=([\d.]+)\s+screens\s+draws=(\d+)")

# car part families in CMR2 car texture names (from the dumps in ~/.lena_cmr2/tex)
FAMILIES = [
    ("BODY",  ("bod",)),
    ("WHEEL", ("wh", "ligbr", "lwb", "lwh")),
    ("GLASS", ("gli", "glo", "glob", "glid", "glod")),
    ("LIGHT", ("lig", "lamp", "lgt")),
    ("INT",   ("int",)),
    ("UNDER", ("und", "under")),
]


def family(name):
    base = os.path.basename(name.replace("\\", "/")).lower()
    stem = base.rsplit(".", 1)[0]
    for fam, keys in FAMILIES:
        for k in keys:
            if k in stem:
                return fam
    return None


def carname(name):
    n = name.replace("\\", "/")
    m = re.search(r"Textures/CARS2/([^/]+)/", n, re.I)
    if m:
        return m.group(1).upper()
    if re.search(r"Textures/CARS", n, re.I):
        return "CARS?"
    return None


def parse(path):
    reqs, uses = {}, []
    for line in open(path, errors="replace"):
        if "[TEXREQ]" in line:
            m = REQ.search(line)
            if m:
                mesh, tris, parts, p, slot, name, idx = m.groups()
                reqs.setdefault(int(idx), []).append(
                    dict(mesh=mesh, tris=int(tris), parts=int(parts),
                         part=int(p), slot=int(slot), name=name))
        elif "[TEXUSE]" in line:
            m = USE.search(line)
            if m:
                uses.append((int(m.group(1)), float(m.group(2)), int(m.group(3))))
    return reqs, uses


def main(paths):
    allreq, alluse = {}, defaultdict(list)
    for p in paths:
        r, u = parse(p)
        for k, v in r.items():
            allreq.setdefault(k, []).extend(v)
        for i, cov, d in u:
            alluse[i].append((os.path.basename(p), cov, d))

    cars = defaultdict(lambda: defaultdict(list))
    for idx, entries in allreq.items():
        for e in entries:
            c = carname(e["name"])
            if not c:
                continue
            fam = family(e["name"])
            if fam:
                cars[c][fam].append((idx, e))

    print("=" * 78)
    print("CAR PARTS: requested (TEXREQ) vs reached a draw (TEXUSE), per car")
    print("=" * 78)
    if not cars:
        print("no car textures in these logs")
    for c in sorted(cars):
        print("\n%s -- %d part-texture ids" % (c, sum(len(v) for v in cars[c].values())))
        print("  %-7s %-5s %-6s %-9s %-8s %s" % ("part", "id", "draws", "coverscr", "tri", "name"))
        for fam in ("BODY", "WHEEL", "GLASS", "LIGHT", "INT", "UNDER"):
            seen = {}
            for idx, e in cars[c].get(fam, []):
                seen.setdefault(idx, e)
            for idx, e in sorted(seen.items()):
                u = alluse.get(idx, [])
                draws = max((d for _, _, d in u), default=0)
                cov = max((cv for _, cv, _ in u), default=0.0)
                mark = "DREW" if u else "NEVER"
                print("  %-7s %-5d %-6d %-9.2f %-8d %s  [%s]"
                      % (fam, idx, draws, cov, e["tris"],
                         os.path.basename(e["name"].replace("\\", "/")), mark))

    print("\n" + "=" * 78)
    print("ALL texture ids REQUESTED but NEVER reaching a TEXUSE draw (any texture)")
    print("=" * 78)
    never = [(i, v[0]["name"]) for i, v in allreq.items() if i not in alluse]
    print("requested ids=%d  used ids=%d  never-used ids=%d"
          % (len(allreq), len(alluse), len(never)))
    for i, n in sorted(never)[:40]:
        print("  id=%-5d %s" % (i, n))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        a = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "out", "*.log")))
    main(a)
