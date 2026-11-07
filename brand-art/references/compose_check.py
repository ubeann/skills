#!/usr/bin/env python3
"""Check a composed layout (banner, card, scene) for figure-ground separation.

  compose_check.py out/banner.png out/card-*.png --plates out/plates/ --sheet compose.png

Each layout needs a plate: the same layout rendered without its figures (same size, same
file name in --plates, or <name>.plate.png beside it). The figures are the pixels that differ.

Per layout it measures:
  figure    share of the canvas the figures cover
  camo      share of coloured figure pixels that share a hue (within camo_hue degrees) and a value
            (within camo_l L*) with a coloured ground colour around them: the costume that melts into
            its own card, the navy body on a blue banner. An outline between them does not count.

Writes, with --sheet, one row per layout: colour, greyscale, greyscale blurred, and the camouflaged
pixels in magenta. Look at the blurred column for hierarchy: one shape should lead.
Exits 1 when any layout fails. Needs Pillow and numpy.
"""
import argparse
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageFilter, ImageOps
    LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
except ImportError:
    sys.exit("needs Pillow and numpy: python3 -m pip install pillow numpy")

CHECKS = {
    "diff_de": 8.0,       # layout vs plate distance that marks a figure pixel
    "chroma_min": 20.0,   # figure pixels below this are neutrals (ink, white, outline) and skip camo
    "ground_chroma": 10.0, # ground colours below this are neutral and cannot camouflage a figure
    "camo_hue": 30.0,     # hue angle difference, in degrees, that counts as the same hue
    "camo_l": 30.0,       # L* difference within which a same-hue pixel counts as camouflaged
    "camo_max": 0.15,     # share of coloured figure pixels allowed to camouflage
    "ring": (0.01, 0.04), # ground ring around the figures, as a share of the long side
}
WORK = 480


def lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def load(path):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    scale = WORK / max(im.size)
    im = im.resize((round(im.width * scale), round(im.height * scale)), LANCZOS)
    return im, np.asarray(im, float)


def grow(mask, px):
    im = Image.fromarray((mask * 255).astype(np.uint8))
    for _ in range(max(1, px // 4)):
        im = im.filter(ImageFilter.MaxFilter(9))
    return np.asarray(im) > 127


def ground_colours(ring_lab, step=6.0, share=0.05):
    """The distinct colours the figures sit on: Lab quantised, kept when they cover 5% of the ring."""
    q = np.round(ring_lab / step).astype(int)
    keys, counts = np.unique(q, axis=0, return_counts=True)
    keep = counts / counts.sum() >= share
    return (keys[keep] * step).astype(float)


def measure(path, plate_path):
    im, rgb = load(path)
    _, plate = load(plate_path)
    if plate.shape != rgb.shape:
        sys.exit(f"{plate_path}: size differs from {path}")
    L, P = lab(rgb), lab(plate)
    fig = np.linalg.norm(L - P, axis=-1) > CHECKS["diff_de"]
    fig = np.asarray(Image.fromarray((fig * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3))) > 127
    long = max(fig.shape)
    inner, outer = (round(long * k) for k in CHECKS["ring"])
    ring = grow(fig, outer) & ~grow(fig, inner)
    r = {"image": Path(path).name, "figure": fig.mean(), "camo": 0.0, "map": None}
    if fig.sum() < 50 or ring.sum() < 50:
        r["error"] = "no figures found: is the plate the same layout without them?"
        return r, im
    grounds = ground_colours(P[ring])
    grounds = grounds[np.hypot(grounds[:, 1], grounds[:, 2]) >= CHECKS["ground_chroma"]]
    chroma = np.hypot(L[..., 1], L[..., 2])
    coloured = fig & (chroma >= CHECKS["chroma_min"])
    camo = np.zeros_like(fig)
    hue = np.degrees(np.arctan2(L[..., 2], L[..., 1]))
    for g in grounds:
        dh = np.abs((hue - np.degrees(np.arctan2(g[2], g[1])) + 180) % 360 - 180)
        camo |= coloured & (dh < CHECKS["camo_hue"]) & (np.abs(L[..., 0] - g[0]) < CHECKS["camo_l"])
    r["camo"] = camo.sum() / max(1, coloured.sum())
    r["map"] = camo
    return r, im


def verdict(r):
    if "error" in r:
        return [r["error"]]
    out = []
    if r["camo"] > CHECKS["camo_max"]:
        out.append(f"camo {r['camo']:.0%} of the coloured figure pixels match the ground around them "
                   f"(max {CHECKS['camo_max']:.0%}): move the ground to the costume's complement, "
                   f"a neutral, or a value at least {CHECKS['camo_l']:.0f} L* away")
    return out


def sheet(rows, out):
    tiles = []
    for r, im in rows:
        g = ImageOps.grayscale(im)
        blur = g.filter(ImageFilter.GaussianBlur(max(im.size) * 0.012))
        camo = g.convert("RGB")
        if r["map"] is not None:
            a = np.asarray(camo).copy()
            a[r["map"]] = (255, 0, 200)
            camo = Image.fromarray(a)
        tiles.append([im, g.convert("RGB"), blur.convert("RGB"), camo])
    w = max(t[0].width for t in tiles)
    h = sum(t[0].height for t in tiles) + 8 * len(tiles)
    s = Image.new("RGB", (w * 4 + 24, h), "white")
    y = 0
    for t in tiles:
        for i, part in enumerate(t):
            s.paste(part, (i * (w + 8), y))
        y += t[0].height + 8
    s.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layouts", nargs="+")
    ap.add_argument("--plates", help="folder holding each layout's plate under the same file name")
    ap.add_argument("--sheet", help="write the review sheet here")
    args = ap.parse_args()
    rows, failed = [], 0
    print("| layout | figure | camo | status |")
    print("|---|---|---|---|")
    for p in args.layouts:
        p = Path(p)
        plate = Path(args.plates) / p.name if args.plates else p.with_suffix(".plate.png")
        if not plate.exists():
            sys.exit(f"{p}: no plate at {plate}; render the layout once more without its figures")
        r, im = measure(p, plate)
        r["found"] = verdict(r)
        failed += bool(r["found"])
        rows.append((r, im))
        print(f"| {r['image']} | {r['figure']:.0%} | {r['camo']:.0%} | {'fail' if r['found'] else 'pass'} |")
    print()
    for r, _ in rows:
        for f in r["found"]:
            print(f"- {r['image']}: {f}")
    print(f"\n{len(rows)} layouts, {failed} with findings")
    if args.sheet:
        sheet(rows, args.sheet)
        print(f"sheet: {args.sheet}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
