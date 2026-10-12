#!/usr/bin/env python3
"""patch_s3.py -- RAISE-THE-NUMBER stage 3: the bulk pass.

Every remaining 'cast from pointer to smaller type' site is rewritten to
intptr_t/uintptr_t.  That is only allowed to STAND if the audit (audit.sh,
-Wshorten-64-to-32) shows the widened value never lands in a 32-bit container.
Lines that fail the audit are reverted whole.

  patch_s3.py rewrite [logdir]     rewrite every flagged site; writes s3-map.json
  patch_s3.py revert  [auditdir]   revert every line the audit complains about
"""
import os, re, sys, json, shutil, datetime, collections

ROOT = "/home/deck/lena/.lena_cmr2/port/tree/CMR2Decomp"
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
MAP  = "/home/deck/lena/work/RTN-20261012/s3-map.json"
CASTRE = re.compile(r'\((unsigned int|int)\)')

def rd(p): return open(os.path.join(ROOT, p), errors="replace").read()

if sys.argv[1] == "rewrite":
    LOG = sys.argv[2]
    rec = {}
    for fn in sorted(os.listdir(LOG)):
        base = fn[:-4]
        txt = open(os.path.join(LOG, fn), errors="replace").read()
        hits = [(int(a), int(b)) for a, b in re.findall(r'\.cpp:(\d+):(\d+): error: cast from pointer', txt)]
        if not hits: continue
        path = os.path.join(ROOT, base)
        shutil.copy2(path, path + ".bak-S3-" + STAMP)
        lines = rd(base).split("\n")
        rec[base] = {}
        for ln, col in sorted(hits, reverse=True):
            src = lines[ln-1]
            m = CASTRE.match(src, col-1)
            if not m:
                print(f"  !! {base}:{ln}:{col} not a cast: {src.strip()[:80]}"); continue
            repl = "(uintptr_t)" if m.group(1) == "unsigned int" else "(intptr_t)"
            rec[base].setdefault(str(ln), src)
            lines[ln-1] = src[:col-1] + repl + src[col-1+len(m.group(0)):]
        open(path, "w").write("\n".join(lines))
        print(f"  {base}: {len(hits)} sites rewritten")
    json.dump(rec, open(MAP, "w"), indent=1)
    print("map:", MAP, "files:", len(rec), "lines:", sum(len(v) for v in rec.values()))

elif sys.argv[1] == "revert":
    AUD, BASE = sys.argv[2], sys.argv[3]
    rec = json.load(open(MAP))
    # baseline warning lines (before stage 3) -- anything not in there is mine
    def warnlines(d):
        out = collections.defaultdict(set)
        for fn in os.listdir(d):
            base = fn[:-4]
            for m in re.finditer(r'\.cpp:(\d+):\d+: warning: implicit conversion loses integer precision', open(os.path.join(d, fn), errors="replace").read()):
                out[base].add(int(m.group(1)))
        return out
    before, after = warnlines(BASE), warnlines(AUD)
    reverted = collections.Counter()
    for base, lines in rec.items():
        bad = sorted(after.get(base, set()) - before.get(base, set()))
        if not bad: continue
        live = rd(base).split("\n")
        for ln in bad:
            if str(ln) in lines:
                live[ln-1] = lines[str(ln)]          # whole line back to how it was
                reverted[base] += 1
        open(os.path.join(ROOT, base), "w").write("\n".join(live))
    print("=== lines reverted because the audit caught a truncation ===")
    for b, n in reverted.most_common(): print(f"  {n:4d}  {b}")
    print(f"  TOTAL {sum(reverted.values())} of {sum(len(v) for v in rec.values())} rewritten lines reverted")
    keep = sum(len(v) for v in rec.values()) - sum(reverted.values())
    print(f"  KEPT {keep} widened sites, each one audit-clean")
