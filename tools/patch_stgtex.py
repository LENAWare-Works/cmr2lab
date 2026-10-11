#!/usr/bin/env python3
"""patch_stgtex.py -- round r6 (ROAD, the road is indistinguishable): LENA-STGTEX.

The r5 report's single next item, in the report's own words: "Instrument the race's
3D draws the way LENA_MENUTEX instrumented the menu car ... per-indexed-3D-draw
reporting of the bound texture ids, the stage ops and args, the vertex diffuse, and
the port's own combiner's predicted fragment colour (a7_eval_texop) against the
framebuffer."

WHY A NEW GATE AND NOT MENUTEX ITSELF
  MENUTEX rides LENA_MENUDRAW, and MENUDRAW prints four lines per draw through the
  same md_draw(). The menu car is 29 draws inside one burst. The race is 4.2 MILLION
  indexed 3D draws of FVF 0x2d2, so "one line per draw" is 800 MB of log and a
  stall, and the burst trigger (a file, consumed once) aims at the wrong thing.
  So STGTEX is the same QUESTION at stage scale, with a census instead of a dump:
  per-window and whole-run DISTRIBUTIONS of exactly MENUTEX's fields, plus a bounded
  number of full per-draw lines (first 10 draws of every window, then a stride).

WHAT IT PRINTS, all of it from the draw's own state and the draw's own bytes:
  * tex0/tex1 -- the RHI's bound handles per draw, counted, with each texture's
    own w x h, mean colour and distinct-colour count (a CPU snapshot at upload:
    the exact bytes a7_upload_texture handed the GPU);
  * stage-0/1 ops and args, alpha op and args, and the render states that decide
    whether ANY of it reaches the fragment: LIGHTING, FOGENABLE, ALPHABLENDENABLE,
    ZENABLE, ALPHATESTENABLE;
  * the vertex DIFFUSE, counted as values, with same-across-triangle flags;
  * the material diffuse, counted as values;
  * TWO predictions per vertex, both through the port's own a7_eval_texop, which
    is the same combiner as a7vk3d.frag:
        predV = texel (x) vertex diffuse    -- what a D3DMCS_COLOR1 vertex-coloured
                                               pipeline would put on screen
        predM = texel (x) material diffuse  -- what THIS port puts on screen today,
                                               because a7vk3d.vert's flags.w is
                                               hardcoded 0 and D3DRS_COLORVERTEX /
                                               DIFFUSEMATERIALSOURCE are dropped
    Both are printed because the framebuffer comparison is two-sided: whichever one
    the picture matches is the one the pipeline is actually using.
  * uv0/uv1 ranges, NaN counts and out-of-[0,1] counts -- the texture is bound and
    the texel is fetched AT THE VERTEX'S OWN UV, so a wrong UV is a wrong texel and
    shows up as "the UVs are outside the unit square" before it shows up as a
    smeared road.

WINDOWS: one summary every LENA_STGTEX_WINF frames (default 500) and one at exit.
The A7VK_AB arms land inside the windows, and the windows SHOW the arms (an arm with
textures unbound reads hasTex0=0; AB_SKIP3D reads draws=0), so a captured frame's
arm is legible from the instrument's own output. LENA_STGTEX_DETAIL bounds the
full per-draw lines (default 200 total).

Inert unless LENA_STGTEX is set. Every read is clamped by the draw's own buffer
length and by the snapshot's own length.
"""
import shutil
import sys
import time

SRC = "/home/deck/lena/.lena_cmr2/port/rhi/deck_dd7.cpp"

BLOCK = r'''
/* ================= LENA-STGTEX (work/ROAD-r6/patch_stgtex.py) =================
 * The r5 report's single next item: MENUTEX's instrument, aimed at the RACE's
 * indexed 3D draws instead of the menu car's 29.
 *
 * MENUTEX rides MENUDRAW and prints four lines per draw -- correct for 29 draws,
 * impossible for 4.2 million. STGTEX asks the same question and answers it with
 * a census: per-window and whole-run distributions of the bound texture ids, the
 * stage ops and args, the vertex diffuse, the material diffuse, and BOTH combiner
 * predictions (vertex-coloured and material-coloured), plus a bounded number of
 * full per-draw lines.
 *
 * It also prints the uv0/uv1 range and the count of UVs outside [0,1], because
 * the texel is fetched at the vertex's OWN uv: a projective transform that the
 * port does not implement (a7vk3d.frag's b.flags[1] is "measured but NOT
 * implemented") would land here as uv values far outside the unit square, and
 * that is a DIFFERENT answer from "no texture is bound".
 *
 * Inert unless LENA_STGTEX is set. */
#define ST_TEXN 4096
#define ST_NK   16

typedef struct { uint32_t k; unsigned long n; } StKey;

typedef struct {
    unsigned long draws, tris, verts, oor;
    unsigned long has0, has1, no0, s1on;
    unsigned long light, fog, blend, ztest, atest, zwrite, cull;
    unsigned long vd_same, vd_uniq, vd_nonequal;
    unsigned long uv_nan, uv_out, uv1_nan, uv1_out, uv_samp;
    float u0min, u0max, v0min, v0max, u1min, u1max, v1min, v1max;
    unsigned long idxmin, idxmax;
    StKey op[ST_NK];  int nop, opovf;
    StKey vd[ST_NK];  int nvd, vdovf;
    StKey md[ST_NK];  int nmd, mdovf;
    StKey pv[ST_NK];  int npv, pvovf;
    StKey pm[ST_NK];  int npm, pmovf;
    unsigned long tex0[ST_TEXN];
    unsigned long tex1[ST_TEXN];
} StWin;

typedef struct { int done, w, h, distinct, zero_alpha; uint32_t mean; } StTex;

static int sg_on = -1;
static long sg_win_frames = 500, sg_detail = 200;
static unsigned long sg_win_id, sg_win_firsg_frame, sg_windows;
static unsigned long sg_detail_left, sg_win_draws, sg_tot_draws;
static StWin *sg_w, *sg_g;
static StTex *sg_tx;
static int sg_snap_missing;

static void sg_keyn(StKey *tab, int *n, int *ovf, uint32_t k, unsigned long add)
{
    int i;
    for (i = 0; i < *n; i++) if (tab[i].k == k) { tab[i].n += add; return; }
    if (*n < ST_NK) { tab[*n].k = k; tab[*n].n = add; (*n)++; } else (*ovf)++;
}
static void sg_key(StKey *tab, int *n, int *ovf, uint32_t k) { sg_keyn(tab, n, ovf, k, 1); }
static void sg_merge(StKey *dst, int *dn, int *dovf, const StKey *src, int sn)
{
    int i;
    for (i = 0; i < sn; i++) sg_keyn(dst, dn, dovf, src[i].k, src[i].n);
}
static void sg_tex(int id)
{
    StTex *t;
    MtTex *s;
    if (id < 0 || id >= ST_TEXN) return;
    t = &sg_tx[id];
    if (t->done) return;
    t->done = 1;
    s = mt_get(id);
    if (!s) { t->distinct = -1; sg_snap_missing++; return; }
    mt_texstat(s, &t->distinct, &t->mean, &t->zero_alpha);
    t->w = s->w; t->h = s->h;
}
static void sg_texline(const char *tag, const unsigned long *arr, int nshow)
{
    unsigned long best[8];
    int besti[8], i, k, j;
    for (i = 0; i < 8; i++) { best[i] = 0; besti[i] = -1; }
    for (i = 0; i < ST_TEXN; i++) {
        unsigned long v = arr[i];
        if (!v) continue;
        sg_tex(i);
        for (k = 0; k < 8; k++) if (v > best[k]) {
            for (j = 7; j > k; j--) { best[j] = best[j-1]; besti[j] = besti[j-1]; }
            best[k] = v; besti[k] = i; break;
        }
    }
    fprintf(stderr, "[STGTEX]     %s top:", tag);
    if (!besti[0]) fprintf(stderr, " (none)");
    for (k = 0; k < nshow; k++) if (besti[k] >= 0) {
        const StTex *t = &sg_tx[besti[k]];
        fprintf(stderr, " %d:%lu(%dx%d mean=%02x%02x%02x dist<=%d)  ", besti[k], best[k],
                t->w, t->h, (unsigned)((t->mean >> 16) & 0xFF), (unsigned)((t->mean >> 8) & 0xFF),
                (unsigned)(t->mean & 0xFF), t->distinct);
    }
    fprintf(stderr, "\n");
}
static void sg_keys(const char *tag, const StKey *tab, int n, int ovf)
{
    int i;
    fprintf(stderr, "[STGTEX]     %s:", tag);
    for (i = 0; i < n; i++) fprintf(stderr, " %08x:%lu", tab[i].k, tab[i].n);
    if (ovf) fprintf(stderr, " (+%d more kinds)", ovf);
    fprintf(stderr, "\n");
}
static void sg_dump(const char *why, const StWin *w, unsigned long f0, unsigned long f1)
{
    fprintf(stderr, "[STGTEX] === %s  frames %lu..%lu ===\n", why, f0, f1);
    fprintf(stderr, "[STGTEX]   draws=%lu tris=%lu verts=%lu oor=%lu tex0bound=%lu tex1bound=%lu "
                    "noTex0=%lu stage1on=%lu\n",
            w->draws, w->tris, w->verts, w->oor, w->has0, w->has1, w->no0, w->s1on);
    fprintf(stderr, "[STGTEX]   rs: light=%lu fog=%lu blend=%lu ztest=%lu zwrite=%lu "
                    "atest=%lu cull=%lu\n",
            w->light, w->fog, w->blend, w->ztest, w->zwrite, w->atest, w->cull);
    fprintf(stderr, "[STGTEX]   idx numIdx min=%lu max=%lu\n", w->idxmin, w->idxmax);
    sg_keys("ops  s0(op,a1,a2)+s1(op)+a0(op,a1,a2)", w->op, w->nop, w->opovf);
    sg_keys("vdiff values", w->vd, w->nvd, w->vdovf);
    sg_keys("matdiff values", w->md, w->nmd, w->mdovf);
    sg_keys("predV texel*vdiff", w->pv, w->npv, w->pvovf);
    sg_keys("predM texel*matdiff", w->pm, w->npm, w->pmovf);
    fprintf(stderr, "[STGTEX]   vdiffSame=%lu unequal=%lu nonequal=%lu\n",
            w->vd_same, w->vd_uniq, w->vd_nonequal);
    fprintf(stderr, "[STGTEX]   uv0 samples=%lu nan=%lu out[0,1]=%lu u[%.4g,%.4g] v[%.4g,%.4g]\n",
            w->uv_samp, w->uv_nan, w->uv_out, w->u0min, w->u0max, w->v0min, w->v0max);
    fprintf(stderr, "[STGTEX]   uv1 nan=%lu out[0,1]=%lu u1[%.4g,%.4g] v1[%.4g,%.4g]\n",
            w->uv1_nan, w->uv1_out, w->u1min, w->u1max, w->v1min, w->v1max);
    sg_texline("tex0 by draw count", w->tex0, 8);
    sg_texline("tex1 by draw count", w->tex1, 4);
    fflush(stderr);
}
static void sg_win_reset(void)
{
    memset(sg_w, 0, sizeof *sg_w);
    sg_w->u0min = sg_w->v0min = sg_w->u1min = sg_w->v1min = 1e30f;
    sg_w->u0max = sg_w->v0max = sg_w->u1max = sg_w->v1max = -1e30f;
    sg_win_draws = 0;
}
static void sg_init(void)
{
    const char *e;
    if (sg_on >= 0) return;
    e = getenv("LENA_STGTEX");
    sg_on = (e && e[0] && e[0] != '0') ? 1 : 0;
    if ((e = getenv("LENA_STGTEX_WINF")))    { sg_win_frames = atol(e); if (sg_win_frames < 1) sg_win_frames = 500; }
    if ((e = getenv("LENA_STGTEX_DETAIL")))  sg_detail = atol(e);
    sg_w = (StWin*)calloc(1, sizeof *sg_w);
    sg_g = (StWin*)calloc(1, sizeof *sg_g);
    sg_tx = (StTex*)calloc(ST_TEXN, sizeof *sg_tx);
    if (!sg_w || !sg_g || !sg_tx) { sg_on = 0; return; }
    sg_win_reset();
    sg_g->u0min = sg_g->v0min = sg_g->u1min = sg_g->v1min = 1e30f;
    sg_g->u0max = sg_g->v0max = sg_g->u1max = sg_g->v1max = -1e30f;
    sg_detail_left = (unsigned long)(sg_detail > 0 ? sg_detail : 0);
    if (sg_on) fprintf(stderr, "[STGTEX] on: window=%ld frames, %ld full per-draw lines, "
                               "texture snapshots are taken at upload\n",
                       sg_win_frames, sg_detail);
}
static uint32_t sg_f2u(float f) { uint32_t u; memcpy(&u, &f, 4); return u; }
static void sg_range(float v, float *mn, float *mx) { if (v < *mn) *mn = v; if (v > *mx) *mx = v; }

static void sg_accum(StWin *w, A7Device *d, DeckVB7 *v, DWORD stride, DWORD startVert,
                     const uint16_t *use, DWORD numIdx, int detail)
{
    const BYTE *base;
    DWORD avail, n;
    int samps[3], k, t0i, t1i;
    MtTex *t0, *t1;
    uint32_t matd_seen = mt_pack(&d->material.diffuse);
    uint32_t vds[3]; int vds_n = 0;
    uint32_t opsig;
    unsigned long idxmin = 0xFFFFFFFFu, idxmax = 0;

    avail = (stride && v->bytes) ? (v->bytes / stride) : 0;
    if (startVert >= avail || numIdx < 3) { w->oor++; return; }
    base = v->data + (size_t)startVert * stride;
    n = avail - startVert;
    t0i = d->boundTexture[0] ? (int)(intptr_t)d->boundTexture[0] - 1 : -1;
    t1i = d->boundTexture[1] ? (int)(intptr_t)d->boundTexture[1] - 1 : -1;

    w->draws++; w->tris += numIdx / 3; w->verts += numIdx;
    if (t0i >= 0) { w->has0++; if (t0i < ST_TEXN) w->tex0[t0i]++; } else w->no0++;
    if (t1i >= 0) { w->has1++; if (t1i < ST_TEXN) w->tex1[t1i]++; }
    if (d->stages[1].colorop > A7TOP_DISABLE && t1i >= 0) w->s1on++;
    if (d->rs[A7RS_LIGHTING]) w->light++;
    if (d->rs[A7RS_FOGENABLE]) w->fog++;
    if (d->rs[A7RS_ALPHABLENDENABLE]) w->blend++;
    if (d->rs[A7RS_ZENABLE]) w->ztest++;
    if (d->rs[A7RS_ZWRITEENABLE]) w->zwrite++;
    if (d->rs[A7RS_ALPHATESTENABLE]) w->atest++;
    w->cull += d->rs[A7RS_CULLMODE];
    if (numIdx < idxmin) idxmin = numIdx;
    if (numIdx > idxmax) idxmax = numIdx;
    if (!w->idxmin || idxmin < w->idxmin) w->idxmin = idxmin;
    if (idxmax > w->idxmax) w->idxmax = idxmax;
    sg_key(w->md, &w->nmd, &w->mdovf, matd_seen);
    opsig = ((uint32_t)(d->stages[0].colorop & 0xF) << 28) |
            ((uint32_t)(d->stages[0].colorarg1 & 0xF) << 24) |
            ((uint32_t)(d->stages[0].colorarg2 & 0xF) << 20) |
            ((uint32_t)(d->stages[1].colorop & 0xF) << 16) |
            ((uint32_t)(d->stages[0].alphaop & 0xF) << 12) |
            ((uint32_t)(d->stages[0].alphaarg1 & 0xF) << 8) |
            ((uint32_t)(d->stages[0].alphaarg2 & 0xF) << 4) |
            (uint32_t)(d->rs[A7RS_LIGHTING] ? 1 : 0);
    sg_key(w->op, &w->nop, &w->opovf, opsig);

    t0 = mt_get(t0i); t1 = mt_get(t1i);
    samps[0] = (int)use[0]; samps[1] = (int)use[numIdx / 2]; samps[2] = (int)use[numIdx - 1];
    for (k = 0; k < 3; k++) {
        DWORD vi = (DWORD)samps[k];
        const BYTE *q;
        float u, vv, u1, v1;
        int ok;
        uint32_t vd, tex, t1tex, pv, pm, c1;
        if (vi >= n) continue;
        q = base + (size_t)vi * stride;
        memcpy(&vd, q + 24, 4);
        memcpy(&u,  q + 32, 4); memcpy(&vv, q + 36, 4);
        memcpy(&u1, q + 40, 4); memcpy(&v1, q + 44, 4);
        w->uv_samp++;
        if (!(u == u) || !(vv == vv)) w->uv_nan++;
        else { sg_range(u, &w->u0min, &w->u0max); sg_range(vv, &w->v0min, &w->v0max);
               if (u < 0.0f || u > 1.0f || vv < 0.0f || vv > 1.0f) w->uv_out++; }
        if (!(u1 == u1) || !(v1 == v1)) w->uv1_nan++;
        else { sg_range(u1, &w->u1min, &w->u1max); sg_range(v1, &w->v1min, &w->v1max);
               if (u1 < 0.0f || u1 > 1.0f || v1 < 0.0f || v1 > 1.0f) w->uv1_out++; }
        sg_key(w->vd, &w->nvd, &w->vdovf, vd);
        if (vds_n < 3) vds[vds_n++] = vd;
        tex = mt_texel(t0, u, vv, &ok);
        a7_eval_texop(d->stages[0].colorop, d->stages[0].colorarg1, d->stages[0].colorarg2,
                      &tex, &vd, &pv);
        a7_eval_texop(d->stages[0].colorop, d->stages[0].colorarg1, d->stages[0].colorarg2,
                      &tex, &matd_seen, &pm);
        if (w->s1on) {
            t1tex = mt_texel(t1, u1, v1, &ok);
            a7_eval_texop(d->stages[1].colorop, d->stages[1].colorarg1, d->stages[1].colorarg2,
                          &t1tex, &pv, &c1);
            pv = c1;
            a7_eval_texop(d->stages[1].colorop, d->stages[1].colorarg1, d->stages[1].colorarg2,
                          &t1tex, &pm, &c1);
            pm = c1;
        }
        sg_key(w->pv, &w->npv, &w->pvovf, pv);
        sg_key(w->pm, &w->npm, &w->pmovf, pm);
        if (detail) {
            fprintf(stderr, "[STGTEX]   v%d vi=%lu vdiff=%08x uv0=(%g,%g) uv1=(%g,%g) "
                            "texel=%08x predV=%08x predM=%08x\n",
                    k, (unsigned long)vi, vd, u, vv, u1, v1, tex, pv, pm);
        }
    }
    if (vds_n == 3) {
        if (vds[0] == vds[1] && vds[1] == vds[2]) w->vd_same++;
        else w->vd_nonequal++;
        if (vds[0] != vds[1] && vds[1] != vds[2] && vds[0] != vds[2]) w->vd_uniq++;
    }
    if (detail) {
        fprintf(stderr, "[STGTEX] #%lu f=%lu fvf=%lx tex0=%d tex1=%d s0(op=%d a1=%d a2=%d) "
                        "s1(op=%d) a0(op=%d a1=%d a2=%d) light=%lu matd=%08x numIdx=%lu\n",
                sg_tot_draws, dd7_frames, (unsigned long)v->desc.dwFVF, t0i, t1i,
                d->stages[0].colorop, d->stages[0].colorarg1, d->stages[0].colorarg2,
                d->stages[1].colorop, d->stages[0].alphaop, d->stages[0].alphaarg1,
                d->stages[0].alphaarg2, (unsigned long)d->rs[A7RS_LIGHTING], matd_seen,
                (unsigned long)numIdx);
    }
}
static void sg_add2(StWin *g, const StWin *w)
{
    int i;
    g->draws += w->draws; g->tris += w->tris; g->verts += w->verts; g->oor += w->oor;
    g->has0 += w->has0; g->has1 += w->has1; g->no0 += w->no0; g->s1on += w->s1on;
    g->light += w->light; g->fog += w->fog; g->blend += w->blend;
    g->ztest += w->ztest; g->zwrite += w->zwrite; g->atest += w->atest; g->cull += w->cull;
    g->vd_same += w->vd_same; g->vd_uniq += w->vd_uniq; g->vd_nonequal += w->vd_nonequal;
    g->uv_nan += w->uv_nan; g->uv_out += w->uv_out; g->uv1_nan += w->uv1_nan;
    g->uv1_out += w->uv1_out; g->uv_samp += w->uv_samp;
    if (w->u0min < g->u0min) g->u0min = w->u0min;
    if (w->u0max > g->u0max) g->u0max = w->u0max;
    if (w->v0min < g->v0min) g->v0min = w->v0min;
    if (w->v0max > g->v0max) g->v0max = w->v0max;
    if (w->u1min < g->u1min) g->u1min = w->u1min;
    if (w->u1max > g->u1max) g->u1max = w->u1max;
    if (w->v1min < g->v1min) g->v1min = w->v1min;
    if (w->v1max > g->v1max) g->v1max = w->v1max;
    if (w->idxmin && (!g->idxmin || w->idxmin < g->idxmin)) g->idxmin = w->idxmin;
    if (w->idxmax > g->idxmax) g->idxmax = w->idxmax;
    for (i = 0; i < ST_TEXN; i++) { g->tex0[i] += w->tex0[i]; g->tex1[i] += w->tex1[i]; }
    sg_merge(g->op, &g->nop, &g->opovf, w->op, w->nop);
    sg_merge(g->vd, &g->nvd, &g->vdovf, w->vd, w->nvd);
    sg_merge(g->md, &g->nmd, &g->mdovf, w->md, w->nmd);
    sg_merge(g->pv, &g->npv, &g->pvovf, w->pv, w->npv);
    sg_merge(g->pm, &g->npm, &g->pmovf, w->pm, w->npm);
}
static void sg_atexit(void)
{
    if (sg_on <= 0 || !sg_w) return;
    if (sg_w->draws) { sg_dump("WINDOW (partial, at exit)", sg_w, sg_win_firsg_frame, dd7_frames); sg_add2(sg_g, sg_w); }
    sg_dump("TOTAL (whole run)", sg_g, 0, dd7_frames);
    if (sg_snap_missing) fprintf(stderr, "[STGTEX] NOTE: %d textures were bound but never seen at upload "
                                         "(snapshot cap or non-Deck upload path)\n", sg_snap_missing);
}
static void sg_draw(A7Device *d, DeckVB7 *v, DWORD stride, DWORD startVert,
                    const uint16_t *use, DWORD numIdx)
{
    unsigned long wid;
    int detail;
    if (sg_on < 0) {
        sg_init();
        atexit(sg_atexit);
    }
    if (sg_on <= 0 || !d || !v) return;
    wid = dd7_frames / (unsigned long)sg_win_frames;
    if (wid != sg_win_id) {
        if (sg_win_draws) { sg_dump("WINDOW", sg_w, sg_win_firsg_frame, dd7_frames); sg_add2(sg_g, sg_w); }
        sg_win_id = wid;
        sg_win_firsg_frame = dd7_frames;
        sg_win_reset();
        sg_windows++;
    }
    sg_tot_draws++;
    sg_win_draws++;
    detail = 0;
    if (sg_win_draws <= 10 || (sg_detail_left && (sg_tot_draws % 100000) == 0)) {
        if (sg_detail_left) sg_detail_left--;
        detail = 1;
    }
    sg_accum(sg_w, d, v, stride, startVert, use, numIdx, detail);
}
/* =========================== LENA-STGTEX end ================================== */
'''

ANCHOR_INSERT = "/* --- LENA-MENUDRAW (work/MENU-CAR-FLATTENED/patch_menudraw.py): off unless"

ANCHOR_CALL = """    if (md_on > 0 && v->desc.dwFVF != A7FVF_TLVERTEX)
        md_draw(v, stride, startVert, numVerts, use, numIdx);"""

CALL_NEW = """    if (md_on > 0 && v->desc.dwFVF != A7FVF_TLVERTEX)
        md_draw(v, stride, startVert, numVerts, use, numIdx);
    /* LENA-STGTEX: the stage-scale census. Its own env, its own gate -- MENUDRAW
     * must NOT have to be on, or the instrument would be measuring the menu car's
     * burst window again. */
    if (v->desc.dwFVF != A7FVF_TLVERTEX)
        sg_draw(rhi, v, stride, startVert, use, numIdx);"""


def main():
    src = open(SRC, encoding="utf-8", errors="surrogateescape").read()
    orig = src
    if "LENA-STGTEX" in src:
        print("already patched")
        return 0
    if ANCHOR_INSERT not in src:
        print("ANCHOR INSERT MISSING")
        return 1
    src = src.replace(ANCHOR_INSERT, BLOCK + "\n" + ANCHOR_INSERT, 1)
    if ANCHOR_CALL not in src:
        print("ANCHOR CALL MISSING")
        return 1
    src = src.replace(ANCHOR_CALL, CALL_NEW, 1)
    if src == orig:
        print("NOTHING CHANGED")
        return 1
    bak = SRC + ".bak-pre-stgtex-" + time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(SRC, bak)
    open(SRC, "w", encoding="utf-8", errors="surrogateescape").write(src)
    print("patched; backup", bak)
    print("inserted bytes:", len(src) - len(orig))
    return 0


if __name__ == "__main__":
    sys.exit(main())
