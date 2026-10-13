# CMR2LRE public-face art: palette and reproducibility

The repo's banner, icons and social preview use the game's measured public-facing UI
palette: pale sage `#9bb5aa`, teal `#007b9b` / `#03a095`, and deep teal `#033d52`.
This is not the Greece menu's red/gold. `bgre.tga` is one country texture, not the
identity of the whole game; it was the wrong source for the earlier art.

The palette correction and its measurements are recorded in commit `12097c1a`
("art: fix the palette -- the banner was built on the wrong country"). The checked-in
generator now matches that corrected art rather than silently rebuilding the old
red/gold version. Its design and measured palette live in `tools/build_art.py`.

## Regenerate

The generator uses the game's own `cmr2.tga` wordmark and `bita.tga` texture, extracted
from a user-owned copy of CMR2's `FrontEnd/res1024.bfl`. No game assets are included in
this repository. With Pillow and NumPy available:

```sh
cmr2lab unpack /path/to/FrontEnd/res1024.bfl ./fe
FE_DIR=./fe python3 tools/build_art.py
python3 tools/test_art.py
```

It writes the banner and three icon sizes into `docs/art/`, and writes the 1280×640
card to both `docs/art/social-1280x640.png` and `docs/social-preview.png`. GitHub's
repository social-preview setting is separate from the tracked file; if the preview
shown on GitHub needs changing, upload `docs/social-preview.png` in the repository's
Settings → General → Social preview.

## Verification

`tools/test_art.py` checks the expected dimensions and hashes of the generated assets,
asserts that the old red/gold warmth has not returned, and guards the generator against
the old palette values/claim. If the art is deliberately redesigned, inspect it at
phone scale first, then update the expected hashes and this record together.
