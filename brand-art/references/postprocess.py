#!/usr/bin/env python3
"""Clean vendor downloads into files a product can ship.

  postprocess.py normalize raw/* --out out/              real extensions, SVG without background, metadata, fixed size
  postprocess.py snap out/a.svg --pack pack.json          every SVG fill and stroke to its nearest palette colour
  postprocess.py snap out/a.png --pack pack.json --flat   flat raster art quantised to the palette, alpha kept
  postprocess.py texture out/a.png --texture scan.jpg --blend multiply --opacity 0.35
  postprocess.py edge out/a.png --out out/a-edge.png --seed 3          torn-paper (deckled) edge with alpha
  postprocess.py export out/a.png --size 1280x720 --fit cover --format jpg --bg "#ffffff"
  postprocess.py export out/mascot.png --icon out/icon/               app icon and favicon set

Commands that take one input write next to it with a suffix unless --out is given.
Needs Pillow and numpy.
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageFilter, ImageOps
    LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
except ImportError:
    sys.exit("needs Pillow and numpy: python3 -m pip install pillow numpy")

MAGIC = [(b"\x89PNG", "png"), (b"\xff\xd8\xff", "jpg"), (b"GIF8", "gif")]
ICON_SIZES = [16, 32, 48, 64, 128, 180, 192, 256, 512, 1024]


def sniff(path):
    head = Path(path).read_bytes()[:64]
    for sig, ext in MAGIC:
        if head.startswith(sig):
            return ext
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    if b"<svg" in Path(path).read_bytes()[:2048] or head.lstrip().startswith(b"<?xml"):
        return "svg"
    return None


def out_path(src, out, suffix, ext=None):
    src = Path(src)
    if out:
        o = Path(out)
        return o / f"{src.stem}.{ext or src.suffix[1:]}" if o.is_dir() or str(out).endswith("/") else o
    return src.with_name(f"{src.stem}{suffix}.{ext or src.suffix[1:]}")


def save_raster(im, dst, bg="#ffffff", quality=88):
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    fmt = dst.suffix.lower()[1:]
    if fmt in ("jpg", "jpeg"):
        flat = Image.new("RGB", im.size, bg)
        rgba = im.convert("RGBA")
        flat.paste(rgba, mask=rgba.getchannel("A"))
        flat.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
    elif fmt == "webp":
        im.save(dst, "WEBP", quality=quality, method=6)
    else:
        im.save(dst, "PNG", optimize=True)


# ---------- colour

def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def to_lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def pack_palette(pack_path):
    pack = json.loads(Path(pack_path).read_text())
    cols = [h for role in ("dominant", "secondary", "accent", "neutral") for h in pack["palette"].get(role, [])]
    return cols, pack


# ---------- normalize

SVG_COLOUR = re.compile(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b')


def parse_colour(s):
    if s.startswith("rgb"):
        return tuple(int(x) for x in re.findall(r"\d+", s)[:3])
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def clean_svg(text, keep_bg=False):
    notes = []
    n = len(text)
    text = re.sub(r"<metadata>.*?</metadata>", "", text, flags=re.S)
    text = re.sub(r'\s+xmlns:c2pa="[^"]*"', "", text)
    if len(text) < n:
        notes.append(f"metadata -{(n - len(text)) // 1024} KB")
    vb = re.search(r'viewBox="([\d.\s-]+)"', text)
    if vb and not keep_bg:
        x, y, w, h = (float(v) for v in vb.group(1).split())
        def full_canvas(m):
            nums = [float(v) for v in re.findall(r"-?[\d.]+", m.group("d"))]
            xs, ys = nums[0::2], nums[1::2]
            letters = set(re.findall(r"[A-Za-z]", m.group("d")))
            return letters <= set("MLZmlz") and min(xs) <= x and min(ys) <= y and max(xs) >= x + w and max(ys) >= y + h
        pat = re.compile(r'<path\b[^>]*?\bd="(?P<d>[^"]*)"[^>]*/>')
        for m in pat.finditer(text):
            if full_canvas(m):
                fill = re.search(r'fill="([^"]*)"', m.group(0))
                text = text[:m.start()] + text[m.end():]
                notes.append(f"full-canvas background {fill.group(1) if fill else ''} removed")
                break
        rect = re.search(r'<rect\b[^>]*\bwidth="(100%%|%g)"[^>]*\bheight="(100%%|%g)"[^>]*/>' % (w, h), text)
        if rect:
            text = text[:rect.start()] + text[rect.end():]
            notes.append("full-canvas background rect removed")
    head = re.match(r"(.*?<svg\b[^>]*>)", text, re.S).group(1)
    new_head = re.sub(r'\s(width|height|preserveAspectRatio)="[^"]*"', "", head)
    if new_head != head:
        notes.append("fixed width/height dropped, viewBox kept")
    return text.replace(head, new_head, 1), notes


def cmd_normalize(a):
    for src in a.inputs:
        kind = sniff(src)
        if kind is None:
            print(f"{src}: unknown format, skipped")
            continue
        if kind == "svg":
            text, notes = clean_svg(Path(src).read_text(), a.keep_bg)
            dst = out_path(src, a.out, "", "svg")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(text)
            print(f"{src} -> {dst}: svg; {'; '.join(notes) or 'already clean'}")
            continue
        im = Image.open(src)
        im = ImageOps.exif_transpose(im)
        ext = a.to or ("png" if kind == "webp" else kind)
        dst = out_path(src, a.out, "", ext)
        save_raster(im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im, dst, a.bg)
        claimed = Path(src).suffix.lower().lstrip(".")
        lie = f" (was {kind} named .{claimed})" if claimed and claimed != kind and not (claimed == "jpeg" and kind == "jpg") else ""
        print(f"{src} -> {dst}: {im.size[0]}x{im.size[1]} {ext}{lie}")


# ---------- snap

def cmd_snap(a):
    cols, _ = pack_palette(a.pack)
    pal_rgb = np.array([hex_rgb(h) for h in cols], float)
    pal_lab = to_lab(pal_rgb)
    for src in a.inputs:
        kind = sniff(src)
        if kind == "svg":
            text = Path(src).read_text()
            changes = {}
            def repl(m):
                rgb = parse_colour(m.group(0))
                de = np.linalg.norm(pal_lab - to_lab(np.array(rgb, float)), axis=1)
                i = int(de.argmin())
                if de[i] > a.max_de:
                    changes[m.group(0)] = f"kept (nearest {cols[i]} is dE {de[i]:.0f}, over {a.max_de:.0f})"
                    return m.group(0)
                if de[i] > 0.5:
                    changes[m.group(0)] = f"{cols[i]} (dE {de[i]:.0f})"
                return cols[i]
            body_start = text.index(">", text.index("<svg")) + 1
            text = text[:body_start] + SVG_COLOUR.sub(repl, text[body_start:])
            dst = out_path(src, a.out, "-snap", "svg")
            dst.write_text(text)
            print(f"{src} -> {dst}")
            for k, v in changes.items():
                print(f"  {k} -> {v}")
            continue
        if not a.flat:
            print(f"{src}: raster snapping posterises gradients and grain. Pass --flat for flat art; "
                  "regenerate painterly art that fails the palette check instead.")
            continue
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGBA")
        arr = np.asarray(im, float)
        lab = to_lab(arr[..., :3])
        idx = np.linalg.norm(lab[..., None, :] - pal_lab[None, None, :, :], axis=-1).argmin(-1)
        out = np.concatenate([pal_rgb[idx], arr[..., 3:]], -1).astype(np.uint8)
        dst = out_path(src, a.out, "-snap", "png")
        save_raster(Image.fromarray(out, "RGBA"), dst)
        used = np.bincount(idx[arr[..., 3] > 127].ravel(), minlength=len(cols))
        share = ", ".join(f"{c} {u / max(1, used.sum()):.0%}" for c, u in zip(cols, used) if u)
        print(f"{src} -> {dst}: {share}")


# ---------- texture

def cmd_texture(a):
    im = ImageOps.exif_transpose(Image.open(a.input)).convert("RGBA")
    tex = ImageOps.fit(Image.open(a.texture).convert("RGB"), im.size, LANCZOS)
    base = np.asarray(im, float)[..., :3] / 255
    t = np.asarray(tex, float) / 255
    if a.desaturate:
        t = np.repeat((t @ np.array([0.299, 0.587, 0.114]))[..., None], 3, -1)
    if a.blend == "multiply":
        mixed = base * t
    elif a.blend == "screen":
        mixed = 1 - (1 - base) * (1 - t)
    elif a.blend == "overlay":
        mixed = np.where(base < 0.5, 2 * base * t, 1 - 2 * (1 - base) * (1 - t))
    else:  # soft-light
        mixed = (1 - 2 * t) * base ** 2 + 2 * t * base
    rgb = base * (1 - a.opacity) + mixed * a.opacity
    out = np.concatenate([rgb * 255, np.asarray(im, float)[..., 3:]], -1).clip(0, 255).astype(np.uint8)
    dst = out_path(a.input, a.out, "-tex", "png")
    save_raster(Image.fromarray(out, "RGBA"), dst)
    print(f"{a.input} -> {dst}: {a.blend} at {a.opacity:.0%}")


# ---------- edge

def cmd_edge(a):
    rng = np.random.default_rng(a.seed)
    img = ImageOps.exif_transpose(Image.open(a.input)).convert("RGB")
    W, H = img.size
    m = round(min(W, H) * a.inset)
    k = min(W, H) / 1024

    def side(n):
        t = np.linspace(0, 1, n)
        d = sum(amp * np.sin(2 * np.pi * (f * t + rng.random())) for f, amp in ((3, 4.0), (7, 3.0), (17, 2.0), (41, 1.2)))
        fib = np.convolve(rng.normal(0, 1.6, n), np.ones(3) / 3, mode="same")
        return (d + fib) * k * a.roughness

    yy, xx = np.mgrid[0:H, 0:W]
    L, R, T, B = side(H), side(H), side(W), side(W)
    mask = (xx > m + L[yy]) & (xx < W - 1 - m - R[yy]) & (yy > m + T[xx]) & (yy < H - 1 - m - B[xx])
    alpha = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9))
    inner = alpha.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(2))
    rim = (np.asarray(alpha, float) - np.asarray(inner, float)).clip(0, 255) / 255 * a.rim
    rgb = np.asarray(img, float)
    paper = np.array(hex_rgb(a.paper), float)
    rgb = rgb * (1 - rim[..., None]) + paper * rim[..., None]
    out = Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).convert("RGBA")
    out.putalpha(alpha)
    dst = out_path(a.input, a.out, "-edge", "png")
    save_raster(out, dst, a.bg)
    print(f"{a.input} -> {dst}: {W}x{H}, seed {a.seed}")


# ---------- export

def cmd_export(a):
    im = ImageOps.exif_transpose(Image.open(a.input)).convert("RGBA")
    if a.icon:
        d = Path(a.icon)
        d.mkdir(parents=True, exist_ok=True)
        sq = ImageOps.pad(im, (1024, 1024), LANCZOS, color=(0, 0, 0, 0))
        for s in ICON_SIZES:
            sq.resize((s, s), LANCZOS).save(d / f"icon-{s}.png", optimize=True)
        sq.save(d / "favicon.ico", sizes=[(s, s) for s in (16, 32, 48, 64, 128, 256)])
        print(f"{a.input} -> {d}/: icon-{{{','.join(map(str, ICON_SIZES))}}}.png, favicon.ico")
        if min(im.size) < 1024:
            print(f"  source is {im.size[0]}x{im.size[1]}: upscale first (crisp, never creative) for a sharp 1024")
        return
    w, h = (int(v) for v in a.size.lower().split("x"))
    if a.fit == "cover":
        out = ImageOps.fit(im, (w, h), LANCZOS, centering=(0.5, a.anchor))
    else:
        out = ImageOps.pad(im, (w, h), LANCZOS, color=(0, 0, 0, 0))
    dst = out_path(a.input, a.out, f"-{w}x{h}", a.format)
    save_raster(out, dst, a.bg, a.quality)
    scale = min(im.size[0] / w, im.size[1] / h)
    warn = f"  (upscaled x{1 / scale:.2f}: soft; upscale at the vendor first)" if scale < 1 else ""
    print(f"{a.input} -> {dst}: {w}x{h} {a.format}, {dst.stat().st_size // 1024} KB{warn}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("normalize", help="real extensions, clean SVG")
    p.add_argument("inputs", nargs="+")
    p.add_argument("--out", help="output folder (end with /) or file")
    p.add_argument("--to", choices=["png", "jpg", "webp"], help="raster format to write; default keeps it, WebP becomes PNG")
    p.add_argument("--bg", default="#ffffff", help="flatten colour when writing jpg")
    p.add_argument("--keep-bg", action="store_true", help="keep a full-canvas SVG background")
    p.set_defaults(fn=cmd_normalize)

    p = sub.add_parser("snap", help="colours to the pack palette")
    p.add_argument("inputs", nargs="+")
    p.add_argument("--pack", required=True)
    p.add_argument("--out")
    p.add_argument("--flat", action="store_true", help="allow raster quantising (flat art only)")
    p.add_argument("--max-de", type=float, default=30, help="leave colours further than this from every palette colour")
    p.set_defaults(fn=cmd_snap)

    p = sub.add_parser("texture", help="blend an owned texture over the art")
    p.add_argument("input")
    p.add_argument("--texture", required=True)
    p.add_argument("--blend", choices=["multiply", "screen", "overlay", "soft-light"], default="multiply")
    p.add_argument("--opacity", type=float, default=0.35)
    p.add_argument("--desaturate", action="store_true", help="use the texture's values only")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_texture)

    p = sub.add_parser("edge", help="torn-paper edge with alpha")
    p.add_argument("input")
    p.add_argument("--out")
    p.add_argument("--seed", type=int, default=7, help="one seed per image keeps edges different but alike")
    p.add_argument("--inset", type=float, default=0.03)
    p.add_argument("--roughness", type=float, default=1.0)
    p.add_argument("--rim", type=float, default=0.35, help="strength of the light paper rim")
    p.add_argument("--paper", default="#f6efe2")
    p.add_argument("--bg", default="#ffffff", help="flatten colour when --out is a jpg")
    p.set_defaults(fn=cmd_edge)

    p = sub.add_parser("export", help="target sizes, formats, icon sets")
    p.add_argument("input")
    p.add_argument("--size", help="WxH")
    p.add_argument("--fit", choices=["cover", "contain"], default="contain")
    p.add_argument("--anchor", type=float, default=0.5, help="vertical crop anchor for cover, 0 top to 1 bottom")
    p.add_argument("--format", choices=["png", "jpg", "webp"], default="png")
    p.add_argument("--quality", type=int, default=88)
    p.add_argument("--bg", default="#ffffff")
    p.add_argument("--icon", help="write the app icon and favicon set into this folder")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_export)

    a = ap.parse_args()
    if a.cmd == "export" and not (a.icon or a.size):
        ap.error("export needs --size or --icon")
    a.fn(a)


if __name__ == "__main__":
    main()
