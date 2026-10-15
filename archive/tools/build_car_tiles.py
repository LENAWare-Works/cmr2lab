#!/usr/bin/env python3
"""Rebuild the four README car tiles from CMR2's coherent part heuristic.

The C3D material dwords are not texture-table indices.  Texture choice therefore
follows the verified part-name/number heuristic in rnd/carlib.py, while the
renderer uses the corrected vertical UV orientation (flipv=True).
"""
import os, sys
from pathlib import Path
sys.path.insert(0, '/root/.lena_cmr2/rnd')
import final_icons

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
CARS = {
    'sub': 'car-subaru.png',
    'foc': 'car-focus.png',
    '205': 'car-205.png',
    '6r4': 'car-6r4.png',
}
# The public tiles use the same selected mesh parts as the previous good render.
for cid, filename in CARS.items():
    image = final_icons.car_rgba(cid, 720, 480, az=216, el=8, ss=3)
    # Keep the existing transparent-free tile presentation: sage field behind the car.
    from PIL import Image
    bg = Image.new('RGB', image.size, (155, 181, 170))
    bg.paste(image.convert('RGB'), mask=image.getchannel('A'))
    bg.save(OUT / filename, optimize=True)
    print(f'WROTE {OUT / filename} {bg.size}')
