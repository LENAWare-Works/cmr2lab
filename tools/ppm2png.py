#!/usr/bin/env python3
"""ppm2png.py <in.ppm> <out.png> -- binary PPM (P6) to PNG, standard library only.

The Deck has no ImageMagick and no PIL, and the RHI writes P6 PPMs. A PNG is
four chunks and a zlib stream, so this is the whole converter: IHDR (8-bit RGB,
no interlace), one IDAT of filter-0 scanlines, IEND.

It verifies itself: after writing, it decodes its own IDAT back and compares a
sample of pixels against the source, and refuses to leave a file behind if they
disagree. "It produced a file" is not the same as "the file is the picture".
"""
import struct
import sys
import zlib


def read_ppm(path):
    d = open(path, "rb").read()
    if not d.startswith(b"P6"):
        raise SystemExit("%s: not a P6 PPM" % path)
    # header: magic, width, height, maxval -- whitespace separated, '#' comments
    fields = []
    i = 2
    while len(fields) < 3:
        while i < len(d) and d[i:i + 1].isspace():
            i += 1
        if d[i:i + 1] == b"#":
            while i < len(d) and d[i:i + 1] != b"\n":
                i += 1
            continue
        j = i
        while j < len(d) and not d[j:j + 1].isspace():
            j += 1
        fields.append(int(d[i:j]))
        i = j
    i += 1
    w, h, maxv = fields
    if maxv != 255:
        raise SystemExit("%s: maxval %d, expected 255" % (path, maxv))
    px = d[i:i + w * h * 3]
    if len(px) != w * h * 3:
        raise SystemExit("%s: short pixel data (%d of %d)" % (path, len(px), w * h * 3))
    return w, h, px


def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def main():
    src, dst = sys.argv[1], sys.argv[2]
    w, h, px = read_ppm(src)

    raw = bytearray()
    for y in range(h):
        raw.append(0)                                  # filter type 0 (None)
        raw += px[y * w * 3:(y + 1) * w * 3]
    comp = zlib.compress(bytes(raw), 9)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", comp)
           + chunk(b"IEND", b""))

    # --- self-check: decode our own IDAT and compare pixels ------------------
    idat = png[png.index(b"IDAT") + 4:]
    got = zlib.decompress(idat[:struct.unpack(">I", idat[-8:-4])[0]])
    rows = []
    for y in range(h):
        off = y * (w * 3 + 1)
        if got[off] != 0:
            raise SystemExit("self-check: filter byte %d at row %d" % (got[off], y))
        rows.append(got[off + 1:off + 1 + w * 3])
    back = b"".join(rows)
    if back != px:
        bad = sum(1 for k in range(0, len(px), 3) if back[k:k + 3] != px[k:k + 3])
        raise SystemExit("self-check FAILED: %d differing pixels" % bad)

    open(dst, "wb").write(png)
    print("%s -> %s  %dx%d  %d bytes  (round-trip: all %d pixels identical)"
          % (src, dst, w, h, len(png), w * h))


main()
