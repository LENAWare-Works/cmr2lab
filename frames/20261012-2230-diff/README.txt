frames/20261012-2230-diff — the two published "regression" pairs as 4x amplified diffs
task MOVING-TARGET-NOISE-FOUND-20261012-2230, 2026-10-12 23:2x. No GPU run.

WHAT THESE IMAGES ARE
  Each is |luma(frame A) - luma(frame B)| x 4, white = large difference, black = none.
  They are the content control behind docs/NOISE-20261012.md: if a pair is the SAME moment,
  a diff like this is nearly black with thin edges; if it is two different moments, it is
  full of structure.

  diff-demo3000-amp4.png   B-0927-demo-f3000.png vs A-tonight-demo-f3000.png
                           (both frame index 3000; 98.60% of pixels differ, 78.84% by >8)
                           -> two cars in different positions, displaced road edge, lane
                              markings as strokes. NOT the same moment.
  diff-race-amp4.png       B-0927-race-f5500.png vs A-tonight-race-f6000.png
                           (different indices AND different moments; 98.87% differ)
                           -> the race pair the 2.7x speckle number came from.

  For contrast, the one pair that IS the same moment: the main menu at frame 2600 has
  0.046% of pixels differing, and those are the "Time 00:00.28" clock. Its diff would be
  a black frame with a few white digits. There, speckle is 0.091% on BOTH builds
  (ratio 1.000) -- i.e. no measurable noise delta between them.

scan-frames.py
  The whole instrument: PPM/PNG decode, luma, mean, sd, the speckle definition (a pixel
  differing from BOTH horizontal neighbours by >=24 luma in OPPOSITE directions), a 64x40
  content-signature divergence, and a per-pixel difference census. Standard library only
  (the Deck has no numpy and no PIL). Reproduce any number in docs/NOISE-20261012.md with:

    python3 scan-frames.py frames FILE...
    python3 scan-frames.py pairs A B [A B ...]
    python3 scan-frames.py diff  A B [A B ...]

  sha256 (2026-10-12):
83aa6c11ece084b510704af98f18e15d01dc339bbb5fa41732d99c242dc0e9e7  diff-demo3000-amp4.png
2473409079629696f1d3e8189d933ba1b8f8ebb103f50644afb89ab688699a5a  diff-race-amp4.png
a873b62f00ebca2bfd383488a4669c1e877c626d3382bdb2d8764d5c9438d11e  scan-frames.py
