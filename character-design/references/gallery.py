#!/usr/bin/env python3
"""Lay sketches out as one numbered gallery, so the owner can answer with a number.

  gallery.py rounds/anatomy.png raw/sketch-*.webp
  gallery.py rounds/forms.png a.png b.png c.png --cols 3 --note "sketches, unreviewed"

Each image is fitted into a square tile on white, numbered from 1 in the order given.
Needs Pillow.
"""
import argparse
import sys

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    sys.exit("needs Pillow: python3 -m pip install pillow")


def font(size):
    for name in ("Helvetica.ttc", "Arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("images", nargs="+")
    ap.add_argument("--cols", type=int, help="tiles per row (default: up to 4)")
    ap.add_argument("--tile", type=int, default=480, help="tile size in px")
    ap.add_argument("--note", default="sketches, unreviewed", help="the label under the gallery")
    a = ap.parse_args()

    cols = a.cols or min(4, len(a.images))
    rows = -(-len(a.images) // cols)
    tile, gap, foot = a.tile, a.tile // 24, a.tile // 8
    sheet = Image.new("RGB", (cols * tile + (cols + 1) * gap, rows * tile + (rows + 1) * gap + foot), "white")
    draw = ImageDraw.Draw(sheet)
    badge, number = tile // 7, font(tile // 10)
    for i, path in enumerate(a.images):
        im = Image.open(path).convert("RGBA")
        im = Image.alpha_composite(Image.new("RGBA", im.size, "white"), im).convert("RGB")
        im = ImageOps.pad(im, (tile, tile), color="white")
        x, y = gap + (i % cols) * (tile + gap), gap + (i // cols) * (tile + gap)
        sheet.paste(im, (x, y))
        draw.rectangle((x, y, x + tile - 1, y + tile - 1), outline="#cccccc")
        draw.ellipse((x + 8, y + 8, x + 8 + badge, y + 8 + badge), fill="#141414")
        draw.text((x + 8 + badge / 2, y + 8 + badge / 2), str(i + 1), fill="white", font=number, anchor="mm")
    draw.text((gap, sheet.height - foot / 2), a.note, fill="#666666", font=font(tile // 16), anchor="lm")
    sheet.save(a.out)
    print(f"{a.out}: {len(a.images)} sketches, numbered 1 to {len(a.images)}")


if __name__ == "__main__":
    main()
