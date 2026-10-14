# PATCH AS APPLIED — ENABLE-CENSUS

Regenerating this from `patch_enable_census.py` alone is NOT enough, because the
patch was applied in three passes while the `re.sub` escape bug was being found.
The authoritative artefact is the patched source itself:

    src/a7_vk32.c    (census + 3 hooks)
    src/deck_dd7.cpp (UNCHANGED from .bak-pre-enablecensus -- the census was
                      moved out of it, see below)

## What the census does, in one place

All of it lives in `src/a7_vk32.c`, inserted directly after `#include <stdint.h>`
(lines 40-190), and hooked at three sites:

| site | line (approx) | hook |
|---|---|---|
| `a7_set_render_state` | 2934 | `ec_init_once(); if ((int)s == 28) ec_note(v);` |
| `a7vk_draw_core` (after `zl_draw`) | 4543 | `if (fvf == 0x2d2u) ec_mesh_draw();` |
| `a7_present` | 4923 | `ec_init_once(); ec_tick();` |

Plus `static void ec_init_once(void)` inserted immediately before `ec_dump`, and
`atexit(ec_dump_atexit)` inside it.

## Two things that were hit and are recorded because they will be hit again

1. **`re.sub` interprets `\n` in a STRING replacement.** The C block contains
   `\n` inside string literals; a string replacement turned each of those into a
   real newline and shattered the C source into "expected expression" errors at
   ~3,000 lines. `m.expand()` does the same thing -- a lambda is not a fix. The
   working form is a manual span splice. The patcher now does that.
2. **`[ x ] && continue` inside a `for` under `set -e` ABORTS THE LOOP** on the
   first non-matching iteration. Used to filter one object out of 67; left the
   list nearly empty and the link named every missing game object. Removed.

## Why nothing on the game side is instrumented

An earlier pass instrumented `StageObject_SetLighting` (the stage-load site) to
log the four fog coefficients per stage. That requires replacing
`obj-epoch/StageObjects.o`, and that is impossible on this base: the tree's
headers have drifted from the frozen epoch objects. Measured:

    tree  : Collision_ResolveStaticObstacleContact(int, SectorListEntry*, int, int)
    his   : Collision_ResolveStaticObstacleContact(int, int, int, int)

so a `StageObjects.o` compiled from today's tree leaves four undefined symbols
(`Collision_ResolveStaticObstacleContact`, `StageTiming_FindModelPartByNodeType`,
`StageTiming_SetPrimaryWheelTrailTexture`, `StageTiming_SetSecondaryWheelTrailTexture`)
and does not link. Dropped, not worked around. The census needs the ENABLE VALUE,
which the RHI sees directly; the coefficients stay readable in source at
`StageObjects.cpp:5193-5199` and `5301-5309`, and they are the STATIC half of the
answer, not the measurement.

## Provenance of the binary under measurement

    enable-census-cmr2  md5 df299ff0850a49b219db09b864552033  .text ae190a16cd3046b13cf90b47cfc920c2

    obj-epoch/*.o   (67)         his recovered game objects, EVERY one, unmodified
    plat-fix/*.o    (5)          his platform objects
    rhi-out/a7_vk32.o            THIS round (census added)
    rhi-out/deck_dd7.o           THIS round (fog work from the previous round)

His play binary is `PLAY/out-plain/cmr2`, md5 `8dbc7339c23a36b14cfef2571558c315`,
`.text 04d78c7f54b32f89820509bb06d48295`. NOT touched, not opened for write.
