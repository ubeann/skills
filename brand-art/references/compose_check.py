#!/usr/bin/env python3
"""Check a composed layout (banner, card, scene) for figure-ground separation and for text that
sits on the art.

  compose_check.py out/banner.png out/card-*.png --plates out/plates/ --sheet compose.png
  compose_check.py assets/cards/*.png --bare out/bare/cards/ --record art/<name>/review.json

A plate is the same layout rendered without its figures (same size, same file name in --plates,
or <name>.plate.png beside it): the figures are the pixels that differ. A bare render is the same
layout with its letters hidden and everything else kept, chips and plates included (in CSS,
`*{color:transparent!important}`): the glyphs are the pixels that differ. Give either or both.

Per layout it measures:
  figure    share of the canvas the figures cover                                    (plates)
  camo      share of coloured figure pixels that share a hue (within camo_hue degrees) and a value
            (within camo_l L*) with a coloured ground colour around them: the costume that melts into
            its own card, the navy body on a blue banner. An outline between them does not count.
  busy      in the bare render, the share of pixels under a letter or word that are not the main
            colour beneath it, for the worst one: a cloud, a sun or a pair of shoes under the title.
            Text on a flat plate, sky or chip measures 0                                 (bare)
  contrast  WCAG contrast between glyph cores and the bare pixels under them, at the 10th
            percentile: the part of the title that sits on the wrong colour               (bare)

Writes, with --sheet, one row per layout: colour, greyscale, greyscale blurred, the camouflaged
pixels in magenta, and with --bare the glyphs in cyan over the art under them in magenta. Look at
the blurred column for hierarchy: one shape should lead. With --record, writes each layout's result
into a review.json for brand-art's handover gate, pinned to the file's hash.
Exits 1 when any layout fails. Needs Pillow and numpy.
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
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
    "ground_de": 12.0,    # distance from the main colour under a letter or word that counts as art
    "busy_max": 0.10,     # share of pixels under the worst letter or word that are not its ground
    "contrast_min": 3.0,  # WCAG contrast of glyph cores against the art under them (large text)
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


def luminance(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    return c @ np.array([0.2126, 0.7152, 0.0722])


def components(mask):
    """Connected regions of a mask, as index tuples, 8-connected."""
    seen = np.zeros_like(mask)
    h, w = mask.shape
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        stack, ys, xs = [(y0, x0)], [], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            ys.append(y)
            xs.append(x)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        yield np.array(ys), np.array(xs)


def measure_text(rgb, bare_path, r):
    """Glyphs are where the layout differs from its bare render; judge the art under them."""
    _, bare = load(bare_path)
    if bare.shape != rgb.shape:
        sys.exit(f"{bare_path}: size differs from {r['image']}")
    L, B = lab(rgb), lab(bare)
    diff = np.linalg.norm(L - B, axis=-1)
    glyph = diff > CHECKS["diff_de"]
    glyph = np.asarray(Image.fromarray((glyph * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3))) > 127
    r["text"] = glyph.mean()
    if glyph.sum() < 30:
        r["busy"] = r["contrast"] = None
        return None
    long = max(glyph.shape)
    zone = Image.fromarray((glyph * 255).astype(np.uint8))
    for _ in range(max(1, round(long * 0.002))):  # a pixel or two around each letter, not the chip it sits in
        zone = zone.filter(ImageFilter.MaxFilter(3))
    zone = np.asarray(zone) > 127
    art = np.zeros_like(zone)
    worst = 0.0
    for blob in components(zone):  # a letter or a word, each judged against its own ground
        if len(blob[0]) < 30:
            continue
        under = B[blob]
        off = np.linalg.norm(under - np.median(under, axis=0), axis=-1) > CHECKS["ground_de"]
        worst = max(worst, float(off.mean()))
        art[blob] = off
    r["busy"] = worst
    core = glyph & (diff >= np.percentile(diff[glyph], 50))
    lf, lb = luminance(rgb[core]), luminance(bare[core])
    ratio = (np.maximum(lf, lb) + 0.05) / (np.minimum(lf, lb) + 0.05)
    r["contrast"] = float(np.percentile(ratio, 10))
    return {"glyph": glyph, "edge": art & ~glyph}


def measure(path, plate_path, bare_path=None):
    im, rgb = load(path)
    r = {"image": Path(path).name, "path": str(path), "figure": None, "camo": None, "map": None, "text_map": None}
    if bare_path:
        r["text_map"] = measure_text(rgb, bare_path, r)
    if not plate_path:
        return r, im
    _, plate = load(plate_path)
    if plate.shape != rgb.shape:
        sys.exit(f"{plate_path}: size differs from {path}")
    L, P = lab(rgb), lab(plate)
    fig = np.linalg.norm(L - P, axis=-1) > CHECKS["diff_de"]
    fig = np.asarray(Image.fromarray((fig * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3))) > 127
    long = max(fig.shape)
    inner, outer = (round(long * k) for k in CHECKS["ring"])
    ring = grow(fig, outer) & ~grow(fig, inner)
    r["figure"], r["camo"] = fig.mean(), 0.0
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
    if r.get("busy") is not None and r["busy"] > CHECKS["busy_max"]:
        out.append(f"busy {r['busy']:.0%} of the pixels under the text are art, not its ground (max "
                   f"{CHECKS['busy_max']:.0%}): move the text onto its own plate, or regenerate with the calm zone kept empty")
    if r.get("contrast") is not None and r["contrast"] < CHECKS["contrast_min"]:
        out.append(f"contrast {r['contrast']:.1f}:1 between the text and the art under it (min "
                   f"{CHECKS['contrast_min']:.0f}:1): darken or lighten the zone behind it, or set the text on a plate")
    if r["camo"] is not None and r["camo"] > CHECKS["camo_max"]:
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
        row = [im, g.convert("RGB"), blur.convert("RGB"), camo]
        if r["text_map"] is not None:
            a = np.asarray(g.convert("RGB")).copy() // 2 + 127
            a[r["text_map"]["edge"]] = (255, 0, 200)
            a[r["text_map"]["glyph"]] = (0, 200, 255)
            row.append(Image.fromarray(a.astype(np.uint8)))
        tiles.append(row)
    w = max(t[0].width for t in tiles)
    n = max(len(t) for t in tiles)
    h = sum(t[0].height for t in tiles) + 8 * len(tiles)
    s = Image.new("RGB", (w * n + 8 * (n - 1), h), "white")
    y = 0
    for t in tiles:
        for i, part in enumerate(t):
            s.paste(part, (i * (w + 8), y))
        y += t[0].height + 8
    s.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layouts", nargs="+")
    ap.add_argument("--plates", help="folder holding each layout's plate (no figures) under the same file name")
    ap.add_argument("--bare", help="folder holding each layout's bare render (letters hidden) under the same file name")
    ap.add_argument("--sheet", help="write the review sheet here")
    ap.add_argument("--record", help="write each layout's result into this review.json")
    args = ap.parse_args()
    rows, failed = [], 0
    pct = lambda v: "-" if v is None else f"{v:.0%}"
    print("| layout | figure | camo | busy | contrast | status |")
    print("|---|---|---|---|---|---|")
    for p in args.layouts:
        p = Path(p)
        plate = Path(args.plates) / p.name if args.plates else p.with_suffix(".plate.png")
        if not plate.exists():
            if args.plates or not args.bare:
                sys.exit(f"{p}: no plate at {plate}; render the layout once more without its figures")
            plate = None
        bare = Path(args.bare) / p.name if args.bare else None
        if bare and not bare.exists():
            sys.exit(f"{p}: no bare render at {bare}; render the layout once more with its letters hidden")
        r, im = measure(p, plate, bare)
        r["found"] = verdict(r)
        failed += bool(r["found"])
        rows.append((r, im))
        con = "-" if r.get("contrast") is None else f"{r['contrast']:.1f}:1"
        print(f"| {r['image']} | {pct(r['figure'])} | {pct(r['camo'])} | {pct(r.get('busy'))} | {con} | "
              f"{'fail' if r['found'] else 'pass'} |")
    print()
    for r, _ in rows:
        for f in r["found"]:
            print(f"- {r['image']}: {f}")
    print(f"\n{len(rows)} layouts, {failed} with findings")
    if args.sheet:
        sheet(rows, args.sheet)
        print(f"sheet: {args.sheet}")
    if args.record:
        record(Path(args.record), rows)
        print(f"recorded: {args.record}")
    sys.exit(1 if failed else 0)


def record(review, rows):
    data = json.loads(review.read_text()) if review.exists() else {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for r, _ in rows:
        key = Path(os.path.relpath(Path(r["path"]).resolve(), review.parent.resolve())).as_posix()
        digest = hashlib.sha256(Path(r["path"]).read_bytes()).hexdigest()[:16]
        e = data.get(key, {})
        if e.get("sha") != digest:
            e = {"sha": digest}  # a changed file loses every earlier verdict
        nums = {k: (round(float(r[k]), 3) if r.get(k) is not None else None) for k in ("camo", "busy", "contrast")}
        e["compose"] = {"status": "fail" if r["found"] else "pass", "t": now, **nums, "findings": r["found"]}
        data[key] = e
    review.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
