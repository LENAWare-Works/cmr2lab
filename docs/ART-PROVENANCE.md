# The public face — measured, and the provenance audit of its palette

**Deck side, 2026-10-11 15:1x EEST.** Two questions: was the old art actually this
project, and does the new art's colour story hold up when the game files are asked
directly.

---

## 1. The old social preview was not this game (confirmed)

`docs/social-preview.png` as it stood (md5 `e692c6424fc4643232397946f09009f7`), 1280×640 =
819,200 px, census of exact pixel values:

| measure | rule | count |
|---|---|---|
| gold | exact `#fff300` | **0** |
| gold | any `r>200, g>170, b<100` | **0** |
| brand red | exact `#8b0000` | **9** |
| "red" as the phone measured it | `r≥95, g≤65, b≤65` | **5,666** |

The 5,666 reproduces exactly under that rule — and that is the point: those pixels are
not brand red, they are antialiased dark-tech maroon/grey edges. Its dominant colours are
`#0a0b0d`, `#0b0c0e`, `#1f2228`, `#1e2127`, `#24272e` — 50,520 distinct colours of generic
dark UI. It could be any project on GitHub.

## 2. The new art is made of the game's own files

Regenerated with `tools/build_art.py` from the retail FrontEnd container:

```
cmr2lab unpack <game>/FrontEnd/res1024.bfl ./fe      # 72 entries
  cmr2.tga  512×64 RGBA, white + alpha, 28,940 of 32,768 px fully transparent -> the wordmark
  bfin.tga  256×128   the Finland menu texture (the tile)
  bgre.tga  256×128   Greece: #8b0000 6,953 px and #fff100 2,641 px
  bken.tga            #dae8ec 6,020 px
```

Census of the regenerated `docs/social-preview.png` (1280×640), same rules as above:

| measure | rule | old | new |
|---|---|---|---|
| gold | `r>200, g>170, b<100` (the phone's rule — reproduces her 19,838 exactly) | 0 | **19,838** |
| gold | exact `#fff300` | 0 | 19,194 |
| red | `r≥95, g≤65, b≤65` | 5,666 | **231,183** |
| red | exact `#8b0000` | 9 | **231,183** |

**Contrast, measured three ways, because "18.6:1" depends on which pair you mean:**

| pair | ratio |
|---|---|
| white vs the icon's wordmark plate `#0b0806` (rendered) | 19.97 |
| white vs `#15100d`, the ink field | 18.89 |
| white vs the median background *inside the wordmark band* on the social card | 17.63 |
| band darkest → lightest pixel, measured on `icon-128.png` (the 128 px case) | 19.77 |

The claim that matters — legible at 128 px, not just at 512 — **holds**: at 128 px the
band still measures 19.77:1 (darkest `#000000`, lightest `#f8f8f8`), because the wordmark
is the game's own 512×64 alpha image, resampled, not redrawn.

## 3. Provenance audit — two of the six palette entries are NOT in the game files

`tools/build_art.py` claims: *"Every colour and the wordmark itself come out of the retail
install"*, and lists `GOLD #fff300 RED #8b0000 BONE #dcd3b1 DIRT #744032 SKY #dae8ec`.
Exact-pixel search over **all 72 textures** in `FrontEnd/res1024.bfl`:

| claimed | present in the game files? | what is actually there |
|---|---|---|
| `#8b0000` red | **yes** | 6,953 px, all in `bgre.tga` |
| `#744032` dirt | **yes** | 5,342 px, all in `bfin.tga` |
| `#dae8ec` sky | **yes** | 6,020 px, all in `bken.tga` (Kenya) |
| `#fff300` gold | **no — 0 px anywhere** | the game's golds are `#fff100` (2,641 px, `bgre.tga`) and `#ffff00` (856 px, `bgre.tga` + `tsweden.tga`) |
| `#dcd3b1` bone | **no — 0 px anywhere** | `bfin.tga`'s lightest colours are `#ffffff` (832 px), `#f9f4f3`, `#f6f3f2`, `#f2eae8`; nothing at `#dcd3b1` |
| `#15100d` ink | no (and not claimed to be) | — |

So: the identity — the red, the gold *family*, the tile, the wordmark — is genuinely the
game's. The **silver** is off by two in the red channel (`fff300` vs `fff100`), which is
invisible, and the **bone** (`#dcd3b1`, quoted as "the only thing readable as body text on
a dark field") is not from the game at all — it is a plausible cream that was chosen and
then attributed to Finland. Same class of error the installer had in a different shape:
right-looking output, wrong provenance.

Nothing was changed behind her back. Either:

* set `GOLD = (255, 241, 0)` and take bone from a measured value (`#f2eae8` from `bfin.tga`,
  or the cream in the Finland tile's text), **or**
* keep the colours and drop "sampled, not chosen" to "red, dirt and sky sampled from the
  game; the rest chosen to sit with them".

Recommended: the second, one line, honest, and the art does not change at all. If the
first is wanted it is a two-constant edit and a re-run; the pixel counts above are the
check that the change is real.

## 4. Where the files went

| file | size | md5 |
|---|---|---|
| `docs/social-preview.png` (1280×640, GitHub's social preview size) | 172,442 B | `3fa84b1d783063858372398e9767f1b2` |
| `docs/art/icon-512.png` | 68,996 B | `b7fa137d1f8606c373b51989f05fe677` |
| `docs/art/icon-256.png` | 29,521 B | `35f18b54963b8f3e05c7f0d83c018b9b` |
| `docs/art/icon-128.png` | 11,074 B | `5ca71a6f6b5f8aadff1eaae977e27f2c` |
| `docs/art/banner-1600x400.png` | 106,398 B | `49e7b5687d9a9c2bbfd5ecb259abd7c3` |
| `docs/art/old-social-preview-e692c642.png` (the generic one, kept for the diff) | 467,474 B | `e692c6424fc4643232397946f09009f7` |

`docs/social-preview.png` **has been replaced** in this commit — that file is the repo's
public face and it was measurably not this game. The old one is kept beside it under its
own md5 so the change can be undone by copying it back.

**GitHub's social preview upload is web-UI only — there is no REST endpoint for it.** So
this commit puts the right file in the right place and nothing more: **someone has to set
it by hand in Settings → General → Social preview**, which is a two-minute job for whoever
is at a browser.

Regenerate any of it with:

```
cmr2lab unpack <game>/FrontEnd/res1024.bfl ./fe
FE_DIR=./fe tools/build_art.py            # -> docs/art/{icon-128,icon-256,icon-512,banner-1600x400}.png
cp docs/art/social-1280x640.png docs/social-preview.png   # the 1280x640 card, under its GitHub name
```
