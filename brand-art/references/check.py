#!/usr/bin/env python3
"""Check generated art against an identity pack.

  check.py --pack art/<name>/pack.json                 validate the pack itself
  check.py art/<name>/pack.json out/*.png              score each image against the pack
  check.py art/<name>/pack.json out/*.png --sheet s.png   also write a contact sheet

Per image it measures:
  palette   share of coloured pixels within reach of a palette colour
  off       share of loud pixels far from every palette colour (the stray orange)
  roles     dominant / secondary / accent split, against 60-30-10
  colour    share of coloured (not grey) pixels, against the hero's
  value     spread of lightness (p95 - p5 of L*): the greyscale test
  loud      share of highly saturated pixels: saturation belongs to the focal point
  texture   fine-detail energy as a ratio of the hero's: catches grain turning glossy
  shape     best silhouette overlap with the hero or a sheet panel (mascot and icon packs)

Prints one markdown table and a findings list. Exits 1 when anything fails.
Needs Pillow and numpy.
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageOps
    LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
    BILINEAR = getattr(Image, "Resampling", Image).BILINEAR
except ImportError:
    sys.exit("needs Pillow and numpy: python3 -m pip install pillow numpy")

DEFAULT_CHECKS = {
    "palette_min": 0.80,    # coloured pixels within palette_de of a palette colour
    "palette_de": 15.0,     # CIE76 distance from the palette ramps counted as "on palette"
    "off_max": 0.04,        # loud off-palette pixels
    "off_de": 25.0,         # distance from every ramp that counts as off-palette
    "value_min": 45.0,      # p95 - p5 of L*
    "loud_max": 0.35,       # pixels with chroma above 60
    "texture_ratio": [0.6, 1.5],  # creased image-to-image drift measured 1.5 to 1.95
    "shape_min": 0.75,      # silhouette IoU, mascot and icon packs only
    "accent_max": 0.20,     # accent role share
}
FAMILIES = {"mascot", "set", "scene", "icon"}
ROLES = ("dominant", "secondary", "accent", "neutral")
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
WORK = 160  # working size in px for the colour and shape metrics


# ---------- colour

def srgb_to_lab(rgb):
    """rgb: float array (..., 3) in 0..255 -> Lab (..., 3)."""
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], axis=-1)


def hex_rgb(h):
    return [int(h[i:i + 2], 16) for i in (1, 3, 5)]


def palette_lab(pack):
    names, cols = [], []
    for role in ROLES:
        for h in pack["palette"].get(role, []):
            names.append(role)
            cols.append(hex_rgb(h))
    return names, srgb_to_lab(np.array(cols, float))


def palette_ramps(pal_lab, steps=12):
    """Every mix of two palette colours, and every tint and shade of one: the colours a
    palette implies once it is painted with gradients, grain and light."""
    white, black = srgb_to_lab(np.array([[255.0, 255, 255], [0, 0, 0]]))
    ends = list(pal_lab) + [white, black]
    pts = []
    t = np.linspace(0, 1, steps)[:, None]
    for i, a in enumerate(pal_lab):
        for b in ends[i + 1:]:
            pts.append(a * (1 - t) + b * t)
    return np.concatenate(pts) if pts else pal_lab


# ---------- image loading

def load(path, size=WORK):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("RGBA")
    im.thumbnail((size, size), LANCZOS)
    a = np.asarray(im, float)
    return a[..., :3], a[..., 3] / 255.0


def subject_mask(rgb, alpha):
    """Alpha when the image has it, else pixels that differ from the corner background."""
    if alpha.min() < 0.9:
        return alpha > 0.5
    corners = np.concatenate([rgb[:4, :4].reshape(-1, 3), rgb[:4, -4:].reshape(-1, 3),
                              rgb[-4:, :4].reshape(-1, 3), rgb[-4:, -4:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    spread = np.abs(corners - bg).max()
    if spread > 30:  # full-bleed scene: no single background, the whole frame is the subject
        return None
    lab, bg_lab = srgb_to_lab(rgb), srgb_to_lab(bg[None, :])[0]
    return np.linalg.norm(lab - bg_lab, axis=-1) > 12


def normalise_mask(mask, n=96):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return np.zeros((n, n), bool)
    crop = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = crop.shape
    side = max(h, w)
    pad = np.zeros((side, side), bool)
    pad[(side - h) // 2:(side - h) // 2 + h, (side - w) // 2:(side - w) // 2 + w] = crop
    im = Image.fromarray((pad * 255).astype(np.uint8)).resize((n, n), BILINEAR)
    return np.asarray(im) > 127


def iou(a, b):
    union = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / union) if union else 0.0


def region(path, family, size):
    """Pixels that belong to the art: the subject for a mascot or icon, every opaque pixel otherwise."""
    rgb, alpha = load(path, size)
    mask = subject_mask(rgb, alpha) if family in ("mascot", "icon") else None
    if mask is None or mask.sum() < 50:
        mask = alpha > 0.5
    return rgb, alpha, mask


def texture_energy(path, family, side=384):
    """Mean fine-detail energy inside the art, away from its silhouette edge, with the art
    cropped and scaled to the same size so a smaller mascot does not read as busier."""
    rgb, _, mask = region(path, family, 1024)
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return 0.0
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    scale = side / max(box[2] - box[0], box[3] - box[1])
    size = (max(1, round((box[2] - box[0]) * scale)), max(1, round((box[3] - box[1]) * scale)))
    g = Image.fromarray(rgb.astype(np.uint8)).convert("L").crop(box).resize(size, LANCZOS)
    m = Image.fromarray((mask * 255).astype(np.uint8)).crop(box).resize(size, BILINEAR)
    g, inner = np.asarray(g, float), np.asarray(m) > 250
    lap = np.abs(4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:])
    inner = inner[1:-1, 1:-1]
    for _ in range(4):  # erode so the outline itself is not counted as texture
        inner[1:-1, 1:-1] &= inner[:-2, 1:-1] & inner[2:, 1:-1] & inner[1:-1, :-2] & inner[1:-1, 2:]
    return float(lap[inner].mean()) if inner.any() else 0.0


# ---------- metrics

def measure(path, family, checks, pal_names, pal_lab, ramps, shape_refs, hero=None):
    rgb, alpha, mask = region(path, family, WORK)
    lab = srgb_to_lab(rgb)[mask]
    chroma = np.hypot(lab[:, 1], lab[:, 2])
    nearest = np.linalg.norm(lab[:, None, :] - pal_lab[None, :, :], axis=-1).argmin(axis=1)
    near_de = np.linalg.norm(lab[:, None, :] - ramps[None, :, :], axis=-1).min(axis=1)
    coloured = chroma > 12  # greys, whites and near-blacks are judged by value, not palette

    r = {"image": Path(path).name}
    r["palette"] = float((near_de[coloured] <= checks["palette_de"]).mean()) if coloured.any() else 1.0
    r["colourful"] = float(coloured.mean())
    r["off"] = float(((near_de > checks["off_de"]) & (chroma > 25)).mean())
    roles = np.array(pal_names)[nearest]
    r["roles"] = {k: float((roles == k).mean()) for k in ROLES if k in pal_names}
    L = lab[:, 0]
    r["value"] = float(np.percentile(L, 95) - np.percentile(L, 5))
    r["loud"] = float((chroma > 60).mean())
    r["energy"] = texture_energy(path, family)
    r["texture"] = r["energy"] / hero["energy"] if hero and hero["energy"] else None
    r["shape"], r["shape_ref"] = None, None
    if shape_refs:
        m = subject_mask(*load(path))
        if m is not None:
            mine = normalise_mask(m)
            r["shape"], r["shape_ref"] = max(
                (max(iou(mine, ref), iou(mine[:, ::-1], ref)), name) for name, ref in shape_refs)
    return r


def verdict(r, checks, family, hero):
    found = []
    if r["palette"] < checks["palette_min"]:
        found.append(f"palette {r['palette']:.0%} < {checks['palette_min']:.0%}: colours drifted from the palette")
    if r["off"] > checks["off_max"]:
        found.append(f"off-palette {r['off']:.1%} > {checks['off_max']:.0%}: a loud colour outside the palette")
    if r["colourful"] < hero["colourful"] * 0.5:
        found.append(f"coloured pixels {r['colourful']:.0%} vs hero {hero['colourful']:.0%}: the colour drained out")
    if r["value"] < checks["value_min"]:
        found.append(f"value spread {r['value']:.0f} < {checks['value_min']:.0f}: greyscale reads muddy")
    loud_max = max(checks["loud_max"], hero["loud"] + 0.15)  # a candy-coloured hero sets its own bar
    if r["loud"] > loud_max:
        found.append(f"loud {r['loud']:.0%} > {loud_max:.0%}: saturation everywhere, no focal point")
    acc = r["roles"].get("accent")
    acc_max = max(checks["accent_max"], hero["roles"].get("accent", 0) + 0.10)
    if acc is not None and acc > acc_max:
        found.append(f"accent {acc:.0%} > {acc_max:.0%}: the 10% colour is spreading")
    lo, hi = checks["texture_ratio"]
    if r["texture"] is not None and not lo <= r["texture"] <= hi:
        found.append(f"texture x{r['texture']:.2f} of hero: rendering changed (grain vs smooth)")
    if family in ("mascot", "icon") and r["shape"] is not None and r["shape"] < checks["shape_min"]:
        found.append(f"shape {r['shape']:.2f} < {checks['shape_min']:.2f} vs {r['shape_ref']}: silhouette drifted")
    return found


# ---------- pack

def read_pack(path):
    pack_path = Path(path)
    pack = json.loads(pack_path.read_text())
    errors = []
    for key in ("name", "version", "family", "palette", "hero"):
        if key not in pack:
            errors.append(f"missing {key}")
    if pack.get("family") not in FAMILIES:
        errors.append(f"family must be one of {sorted(FAMILIES)}")
    pal = pack.get("palette", {})
    for role, cols in pal.items():
        if role not in ROLES:
            errors.append(f"palette role {role!r} is not one of {ROLES}")
        for h in cols:
            if not HEX.match(h):
                errors.append(f"palette {role}: {h!r} is not #RRGGBB")
    if not pal.get("dominant") or not pal.get("accent"):
        errors.append("palette needs at least one dominant and one accent colour")
    base = pack_path.parent
    for rel in [pack.get("hero", "")] + pack.get("sheet", []):
        if rel and not (base / rel).exists():
            errors.append(f"file {rel} does not exist")
    incomplete = []  # what a finished pack needs; scoring the sheet against the hero runs before it exists
    if pack.get("family") == "mascot":
        words = len(pack.get("identity_text", "").split())
        if not 30 <= words <= 90:
            errors.append(f"identity_text has {words} words; a mascot needs 30 to 90")
        if len(pack.get("sheet", [])) < 4:
            incomplete.append("a mascot pack needs a turnaround of at least 4 sheet panels")
    if pack.get("family") in ("set", "scene") and not pack.get("prompt_suffix"):
        incomplete.append("a set or scene pack needs prompt_suffix")
    checks = {**DEFAULT_CHECKS, **pack.get("checks", {})}
    return pack, base, checks, errors, incomplete


def contact_sheet(paths, labels, out, tile=220):
    cols = min(6, len(paths))
    rows = -(-len(paths) // cols)
    sheet = Image.new("RGB", (cols * tile, rows * (tile * 2 + 22)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, (p, label) in enumerate(zip(paths, labels)):
        im = ImageOps.exif_transpose(Image.open(p)).convert("RGBA")
        im.thumbnail((tile - 10, tile - 10), LANCZOS)
        flat = Image.new("RGB", im.size, "white")
        flat.paste(im, mask=im.getchannel("A"))
        x, y = (i % cols) * tile, (i // cols) * (tile * 2 + 22)
        ox, oy = x + (tile - im.width) // 2, y + (tile - im.height) // 2
        sheet.paste(flat, (ox, oy))
        sheet.paste(ImageOps.grayscale(flat).convert("RGB"), (ox, oy + tile))  # the value test
        draw.text((x + 6, y + tile * 2 + 4), label[:34], fill="black")
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack_or_flag", nargs="?")
    ap.add_argument("images", nargs="*")
    ap.add_argument("--pack", help="validate this pack and exit")
    ap.add_argument("--sheet", help="write a contact sheet: hero first, colour row over greyscale row")
    args = ap.parse_args()

    if args.pack:
        _, _, _, errors, incomplete = read_pack(args.pack)
        errors += incomplete
        for e in errors:
            print(f"- {e}")
        print(f"pack {args.pack}: {len(errors)} errors")
        sys.exit(1 if errors else 0)
    if not args.pack_or_flag or not args.images:
        ap.error("give a pack.json and at least one image, or --pack pack.json")

    pack, base, checks, errors, incomplete = read_pack(args.pack_or_flag)
    if errors:
        sys.exit("pack is invalid:\n" + "\n".join(f"- {e}" for e in errors))
    for e in incomplete:
        print(f"note: pack not finished: {e}")
    pal_names, pal_lab = palette_lab(pack)
    ramps = palette_ramps(pal_lab)
    hero = base / pack["hero"]
    shape_refs = []
    if pack["family"] in ("mascot", "icon"):
        for rel in [pack["hero"]] + pack.get("sheet", []):
            m = subject_mask(*load(base / rel))
            if m is not None:
                shape_refs.append((Path(rel).name, normalise_mask(m)))
    hero_r = measure(hero, pack["family"], checks, pal_names, pal_lab, ramps, [])

    rows, failed = [], 0
    print(f"| image | palette | off | dom/sec/acc | value | loud | texture | shape | status |")
    print(f"|---|---|---|---|---|---|---|---|---|")
    for p in args.images:
        r = measure(p, pack["family"], checks, pal_names, pal_lab, ramps, shape_refs, hero_r)
        found = verdict(r, checks, pack["family"], hero_r)
        failed += bool(found)
        rows.append((r, found))
        split = "/".join(f"{r['roles'].get(k, 0):.0%}" for k in ("dominant", "secondary", "accent"))
        tex = f"x{r['texture']:.2f}" if r["texture"] is not None else "-"
        shp = f"{r['shape']:.2f}" if r["shape"] is not None else "-"
        print(f"| {r['image']} | {r['palette']:.0%} | {r['off']:.1%} | {split} | {r['value']:.0f} | "
              f"{r['loud']:.0%} | {tex} | {shp} | {'fail' if found else 'pass'} |")
    print()
    for r, found in rows:
        for f in found:
            print(f"- {r['image']}: {f}")
    print(f"\n{len(rows)} images, {failed} with findings")
    if args.sheet:
        contact_sheet([hero] + list(args.images), ["HERO " + hero.name] + [Path(p).name for p in args.images], args.sheet)
        print(f"contact sheet: {args.sheet}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
