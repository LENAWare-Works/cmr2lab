#!/usr/bin/env python3
"""patch_menudraw.py -- LENA-MENUDRAW: the instrument the menu-car ticket asked for.

WHY THIS EXISTS
    `work/RACE/MENU-CAR-EVIDENCE.md` §4 specced this line and left it unwritten
    ("SPECCED IN §4 OF MENU-CAR-EVIDENCE.md AND WRITTEN NOWHERE IN THE TREE").
    It is the one instrument that separates the four mechanisms that survive
    Miami's description of the setup-screen car ("flattens into one place on the
    menu, all mangled and jungled up into one flat piece of paper"):

      B  the preview's own per-frame deform collapsing vertices;
      C  a stride/FVF mismatch on the preview's own converted vertices
         (32-byte 16.16 fixed read as 48-byte IEEE float -> every coordinate is
         a denormal, i.e. every vertex collapses toward the origin);
      A/D a degenerate or wrong world/view, or the 2D transform used for a 3D draw.

    B and C are separated in ONE line by decoding the same bytes the draw read
    twice: as 48-byte float, and as 32-byte 16.16 fixed. If the float decode is
    degenerate (all ~0, or NaN) and the fixed decode is car-shaped, it is C. If
    both are car-shaped and the picture is still flat, it is A/B/D -- geometry or
    transform, not format.

    It also prints, on every line, whether startVert is zero, because the
    index-base fix only touches draws with startVert != 0: a line with
    zeroBase=yes is a draw the A7VK_IDXBASE switch CANNOT have changed. That is
    the cheapest possible test of the ticket's own hypothesis, per draw.

WHAT IT COSTS
    Nothing when the env var is unset (one getenv per indexed 3D draw). Bounded
    when set: LENA_MENUDRAW_MAX lines (default 60), LENA_MENUDRAW_EVERY draws
    apart after that (default 2000). Every read is clamped to the vertex
    buffer's own byte length, so it cannot walk off the allocation.

USE
    LENA_MENUDRAW=1 LENA_MENUDRAW_MAX=200 A7VK_IDXBASE=sub ./cmr2   > md_sub.log 2>&1
    LENA_MENUDRAW=1 LENA_MENUDRAW_MAX=200 ./cmr2                    > md_raw.log 2>&1
    grep '\[MENUDRAW\]' md_raw.log | head -40

Idempotent. Backs the file up once, prints a diff-sized summary, and does not
rebuild anything -- rebuild with the lane's own script when the GPU is free.
"""
import os
import shutil
import sys
import time

SRC = "/home/deck/lena/.lena_cmr2/port/rhi/deck_dd7.cpp"
TS = time.strftime("%Y%m%d-%H%M%S")

MARK = "LENA-MENUDRAW"

DECL_ANCHOR = """/* --- LENA-IDXTRACE (work/RACE/patch_idxtrace.py): off unless DECK_IDXTRACE --- */"""

DECL = r"""/* --- LENA-MENUDRAW (work/MENU-CAR-FLATTENED/patch_menudraw.py): off unless
 * LENA_MENUDRAW is set. On an indexed 3D draw it prints the draw's own numbers
 * and decodes the same bytes the draw read TWICE -- as 48-byte IEEE float and as
 * 32-byte 16.16 fixed -- so "the object is degenerate" and "the object is read
 * with the wrong stride" are two different lines instead of a guess. --- */
static int md_on = -1;
static long md_every = 2000, md_max = 60;
static unsigned long md_n, md_shown;

static int md_finite(float f) { return (f == f) && f < 1e30f && f > -1e30f; }

/* min/max of the first 3 floats of each of n vertices at `stride`; copies of the
 * same bytes read as int32/65536 for the fixed decode. out = min[3], max[3],
 * bad-count, decoded-count. Every read is clamped by the caller's `n`. */
static void md_scan(float *out, const BYTE *p, DWORD n, DWORD stride, int as_fixed)
{
    DWORD i;
    int k, bad = 0, any = 0;
    float mx[3], mn[3];
    for (k = 0; k < 3; k++) { mx[k] = -1e30f; mn[k] = 1e30f; }
    for (i = 0; i < n; i++) {
        const BYTE *q = p + (size_t)i * stride;
        for (k = 0; k < 3; k++) {
            float val;
            if (as_fixed) {
                int raw;
                memcpy(&raw, q + k * 4, 4);
                val = (float)raw * (1.0f / 65536.0f);
            } else {
                memcpy(&val, q + k * 4, 4);
                if (!md_finite(val)) { bad++; continue; }
            }
            if (val > mx[k]) mx[k] = val;
            if (val < mn[k]) mn[k] = val;
            any = 1;
        }
    }
    for (k = 0; k < 3; k++) { out[k] = mn[k] > 1e29f ? 0.0f : mn[k]; out[3 + k] = mx[k] < -1e29f ? 0.0f : mx[k]; }
    out[6] = (float)bad;
    out[7] = (float)any;
}

/* One line per indexed 3D draw: the numbers the game handed us, then the same
 * bytes decoded three ways. `use` is the array the backend was actually given. */
static void md_draw(DeckVB7 *v, DWORD stride, DWORD startVert, DWORD numVerts,
                    const uint16_t *use, DWORD numIdx)
{
    const BYTE *base;
    DWORD avail, n, i;
    int inrange = 1;
    float f48[8], x48[8], x32[8];
    if (md_on <= 0) return;
    md_n++;
    if (md_shown >= (unsigned long)md_max && (md_n % (unsigned long)md_every) != 0) return;
    md_shown++;

    avail = (stride && v->bytes) ? (v->bytes / stride) : 0;
    if (startVert >= avail) {
        fprintf(stderr, "[MENUDRAW] #%lu fvf=0x%lx stride=%lu vb=%p startVert=%lu -- OUT OF RANGE "
                        "(buffer holds %lu vertices): the draw reads past its own vertex buffer\n",
                md_n, (unsigned long)v->desc.dwFVF, (unsigned long)stride, (void *)v->data,
                (unsigned long)startVert, (unsigned long)avail);
        return;
    }
    base = v->data + (size_t)startVert * stride;
    n = numVerts;
    if (startVert + n > avail) n = avail - startVert;

    for (i = 0; i < numIdx; i++)
        if ((DWORD)use[i] >= numVerts) { inrange = 0; break; }

    md_scan(f48, base, n, stride, 0);
    md_scan(x48, base, n, stride, 1);
    md_scan(x32, base, n, 32, 1);

    fprintf(stderr, "[MENUDRAW] #%lu fvf=0x%lx stride=%lu vb=%p bytes=%lu startVert=%lu numVerts=%lu "
                    "numIdx=%lu zeroBase=%s idxInRange=%s idx[0..5]=%u,%u,%u,%u,%u,%u\n",
            md_n, (unsigned long)v->desc.dwFVF, (unsigned long)stride, (void *)v->data,
            (unsigned long)v->bytes, (unsigned long)startVert, (unsigned long)numVerts,
            (unsigned long)numIdx, startVert ? "no" : "yes", inrange ? "yes" : "NO",
            numIdx > 0 ? use[0] : 0, numIdx > 1 ? use[1] : 0, numIdx > 2 ? use[2] : 0,
            numIdx > 3 ? use[3] : 0, numIdx > 4 ? use[4] : 0, numIdx > 5 ? use[5] : 0);
    fprintf(stderr, "[MENUDRAW]    float48 x[%.4g..%.4g] y[%.4g..%.4g] z[%.4g..%.4g] nonfinite=%g\n",
            f48[0], f48[3], f48[1], f48[4], f48[2], f48[5], f48[6]);
    fprintf(stderr, "[MENUDRAW]    fixed48 x[%.4g..%.4g] y[%.4g..%.4g] z[%.4g..%.4g]  (same bytes, 16.16)\n",
            x48[0], x48[3], x48[1], x48[4], x48[2], x48[5]);
    fprintf(stderr, "[MENUDRAW]    fixed32 x[%.4g..%.4g] y[%.4g..%.4g] z[%.4g..%.4g]  (32-byte packed?)\n",
            x32[0], x32[3], x32[1], x32[4], x32[2], x32[5]);
}

"""

CALL_ANCHOR = "    draws++;\n"

CALL = r"""    if (md_on < 0) {
        const char *e = getenv("LENA_MENUDRAW");
        md_on = (e && e[0] && e[0] != '0') ? 1 : 0;
        if ((e = getenv("LENA_MENUDRAW_MAX")))   md_max = atol(e);
        if ((e = getenv("LENA_MENUDRAW_EVERY"))) md_every = atol(e);
    }
    if (md_on > 0 && v->desc.dwFVF != A7FVF_TLVERTEX)
        md_draw(v, stride, startVert, numVerts, use, numIdx);
"""


def main():
    src = open(SRC).read()
    if MARK in src:
        print("skip (already applied):", SRC)
        return 0
    if DECL_ANCHOR not in src:
        print("ANCHOR MISSING (decl): the IDXTRACE comment is not in", SRC)
        return 2
    if src.count(CALL_ANCHOR) != 1:
        print("ANCHOR AMBIGUOUS: '    draws++;' appears %d times" % src.count(CALL_ANCHOR))
        return 2

    shutil.copy2(SRC, SRC + ".bak-pre-menudraw-" + TS)
    out = src.replace(DECL_ANCHOR, DECL + DECL_ANCHOR, 1)
    out = out.replace(CALL_ANCHOR, CALL + CALL_ANCHOR, 1)
    open(SRC, "w").write(out)

    print("applied to", SRC)
    print("backup:", SRC + ".bak-pre-menudraw-" + TS)
    print("added %d bytes; %d lines of source" % (len(out) - len(src), CALL.count(chr(10)) + DECL.count(chr(10))))
    print()
    print("next: rebuild when the GPU is free (do NOT relink the play binary while a")
    print("      peer's run or Miami's game is on the card):")
    print("        cd ~/.lena_cmr2/port/rhi && ./build32_dd7.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
