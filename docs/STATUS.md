# Status — can I use this yet?

**Short answer: it runs, and a full stage can be driven start to finish. It does not look
right yet.**

CMR2LRE (Colin McRae Rally 2.0: Linux Rally Edition) is a from-scratch native port of the
2000 PC rally game to modern Linux, aimed at the Steam Deck. It is **in progress** — a
working game with one big known visual defect.

## What works today

- Launch it. A window opens, the frontend loads, the menu car renders.
- A full stage loads and runs — car physics, terrain, a real race, **start to finish**.
- **The recipe:** launch, then **do not touch anything for ~30 seconds.** The attract
  demo walks itself into a race. *Pressing a key parks it on the frontend — that is not a
  crash, it is the wrong door.*

![The game's frontend running natively](media/frontend.jpg)

*The game's own frontend, running natively on a Steam Deck.*

## Fixed and measured — 12 October 2026

Six defects that were killing run after run are now closed, each with a written report in
`docs/`:

| | symptom it killed |
|---|---|
| stage textures never decoded | the world was chromatic noise (DXT5 never decompressed) |
| GPU reset every ~30 s | the game dying at random, ~30 seconds in, every time |
| wrong vertex base | the road drawn from the neighbouring record's vertices |
| our own tooling deleted two lines | **no binary for 2.5 hours could move a car** |
| no mipmaps ever built | **flickering textures** — every minified sample read level 0 |
| no near clip | **stretched triangles** smeared across the frame |

**Measured, not claimed.** The mip fix roughly halves the frame's local contrast
(14.10 → 8.14) and the near clip's arithmetic is verified by invariant — new vertices come
out at exactly 2× the straddling triangles, every time. How much the clip helps *on
screen* is **not yet proven**, and we say so.

## What is still broken

**The road does not separate from the terrain.** Every stage renders as one continuous
warm field — road, verge, sunlit and shadowed ground all merge. On snow stages (Sweden)
this becomes white-on-white and is effectively undrivable.

**We do not yet know why** — and the honest record of that search is the most useful
thing in this repo:

- The obvious cause was tested. The port drops the game's per-vertex colours, so we
  forced them through. Result: it multiplies the terrain by ~0.55 and stays **nearly
  flat** — not enough to separate road from verge. **That is not the fix, and we measured
  it rather than assuming it.** *(Measured in round r7. That report is written on the
  Deck but is not yet published to this repository — see the note below.)*
- The lighting term was tested next and came back a **1.0000 no-op**. *(Round r8. That
  report is likewise not yet published here. The 1.0000 is now understood to be the
  symptom rather than the verdict — see below.)*

### Both candidates, now characterised — 14 October 2026

Neither is an open mystery any more. Both were read out of the game's own decompiled source
rather than guessed at, and both are written up in `docs/`:

- **The scene ambient.** `docs/AMBIENT-CONTRADICTION-RESOLVED.md`. The 1.0000 above is not
  evidence that the lighting term does nothing — it *is* the bug.
  `Scene_RestoreLights` sets a **material** ambient of (1,1,1) and a **scene** ambient
  taken from track data, and D3D7's ambient term is their product. The port keeps the first
  and discards the second, so every lit pixel starts at 1.0 and can only clamp at 255.
  That is precisely the flat white snow.
- **The fog term.** `docs/FOG-VERIFIED-SPEC.md`. **Corrected 14 Oct — two separate paths,
  and only one is caps-gated.** The **range and mode** (35/140/36/37) sit behind
  `Graphics_EnableFog()`'s capability check; the port reported the bit as zero, so they were
  never sent. That is fixed and measured — 35/140 now arrive. The **enable** (state 28) is a
  different path with no caps call in it at all: it is driven by the track's own lighting
  slots `0x25/0x26/0x52/0x53`, and the game measures **0 in 24,369 calls, `uniq=1`**. Fog is
  off because the stage data does not ask for it, not because the port blocked it.

Separately and smaller: the setup-screen car renders collapsed.

## Under the hood

- **x86_64 build: 54 of 66 translation units compile** — up from 37, same harness.
- 32-bit oracle: **66 of 66**, unchanged.
- The play build is functionally the same game: **3,633 of 3,635 functions
  instruction-identical**.
- We refused to write `(intptr_t)` on casts whose value narrows straight back into an
  `int`. That would have raised the number to 66 tonight and made no pointer whole.

## Where this is going

`docs/WHERE-THIS-IS-GOING.md` is the roadmap. The immediate next item is the ambient
test, whose prediction is on record so it can be wrong.
See `docs/AMBIENT-CONTRADICTION-RESOLVED.md` for the prediction and
`docs/FOG-VERIFIED-SPEC.md` for the two fog paths — the capability-bit fix has landed and is
measured; what is open now is whether any stage enables fog at all.

## If you just want to play the original

Use Proton on Steam. This port is a reverse-engineering project, not yet a finished
replacement.
