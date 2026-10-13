#!/usr/bin/env python3
"""Regression checks for the checked-in CMR2LRE public-face art."""
from pathlib import Path
from hashlib import md5
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/art/banner-1600x400.png": ((1600, 400), "c008645d9125e1440548a9408cdb015c"),
    "docs/art/icon-128.png": ((128, 128), "6cf7714dde43321b8efe1007bce0d19c"),
    "docs/art/icon-256.png": ((256, 256), "cee211bc02267a1b6992e3afe06ed021"),
    "docs/art/icon-512.png": ((512, 512), "15bad61427b818902f6e69b3c8ab5199"),
    "docs/art/social-1280x640.png": ((1280, 640), "970926bbd72e1ef40a859eb70d984c09"),
    "docs/social-preview.png": ((1280, 640), "970926bbd72e1ef40a859eb70d984c09"),
}
for rel, (size, digest) in EXPECTED.items():
    p = ROOT / rel
    assert p.is_file(), f"missing: {rel}"
    raw = p.read_bytes()
    im = Image.open(p).convert("RGB")
    assert im.size == size, f"{rel}: {im.size} != {size}"
    assert md5(raw).hexdigest() == digest, f"{rel}: hash differs; inspect before updating this test"
    a = np.asarray(im, dtype=np.int16)
    warm = float(((a[:, :, 0] - a[:, :, 2]) > 30).mean())
    assert warm < 0.001, f"{rel}: old red/gold warmth returned ({warm:.3%})"
    print(f"PASS {rel} {size[0]}x{size[1]} warm={warm:.3%}")

# Ensure the raster generator itself does not resurrect the old source palette.
src = (ROOT / "tools/build_art.py").read_text()
for token in ("#8b0000", "#fff300", "source of the red + gold"):
    assert token not in src.lower(), f"obsolete palette claim/value remains in generator: {token}"
print("PASS generator contains no obsolete red/gold palette")
