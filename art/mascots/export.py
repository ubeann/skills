#!/usr/bin/env python3
"""Export the skill characters for the README.

Reads art/mascots/hero/<skill>.png (transparent cutouts) and assets/icon-512.png (the toolbox),
writes assets/skills/<skill>.png at 256 px, and a light/dark check sheet
to the path given with --check. Run from the repo root.
"""
import argparse
import json
from pathlib import Path

from PIL import Image

R = Image.Resampling.LANCZOS
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def square(im, pad=0.06):
    """Crop to the opaque pixels and centre on a square canvas, standing on a shared baseline."""
    im = im.crop(im.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox())
    side = round(max(im.size) * (1 + 2 * pad))
    cv = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    cv.alpha_composite(im, ((side - im.width) // 2, side - im.height - round(side * pad)))
    return cv


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", help="write a light and dark theme check sheet here")
    args = ap.parse_args()
    order = list(json.loads((HERE / "characters.json").read_text()))
    cut = {n: square(Image.open(HERE / "hero" / f"{n}.png").convert("RGBA")) for n in order}
    (ROOT / "assets" / "skills").mkdir(parents=True, exist_ok=True)
    for n, im in cut.items():
        im.resize((256, 256), R).save(ROOT / "assets" / "skills" / f"{n}.png", optimize=True)

    if args.check:
        toolbox = square(Image.open(ROOT / "assets" / "icon-512.png").convert("RGBA"), pad=0.02).resize((160, 160), R)
        width = max(160, 20 + len(order) * 140)
        sheet = Image.new("RGB", (width, 2 * 420), "white")
        for k, bg in enumerate([(255, 255, 255), (13, 17, 23)]):  # GitHub light and dark
            layer = Image.new("RGBA", (width, 420), bg + (255,))
            layer.alpha_composite(toolbox, ((width - 160) // 2, 10))
            for i, n in enumerate(order):
                layer.alpha_composite(cut[n].resize((128, 128), R), (20 + i * 140, 190))
                layer.alpha_composite(cut[n].resize((40, 40), R), (64 + i * 140, 340))
            sheet.paste(layer.convert("RGB"), (0, k * 420))
        sheet.save(args.check)
    print(f"{len(order)} characters")


if __name__ == "__main__":
    main()
