#!/usr/bin/env python3
"""Build every shipped asset of the cast from the approved images.

Sources: hero/hero-v1.webp (the hero), raw/<skill>.webp (one costume per skill on plain white),
scene/<skill>.webp (that costume in its own spot of the valley world, for the card) and
scene/banner.webp (the whole cast around the toolbox). Everything in out/ is a build cache.

    python3 art/cast/build.py            # stickers, tiles, brand icon, favicon, cards, banner
    python3 art/cast/build.py --check /tmp/check.png   # also a light/dark README check sheet

Writes:
  art/cast/out/<name>.png            transparent cutout (cutout.py)
  art/cast/out/sticker/<name>.png   cutout with a white sticker outline, 1024 tall
  assets/skills/<skill>.png          256 px peek-crop icon tile, for the README table
  assets/icon-512.png, favicon.ico   the brand icon (the hero, waving)
  assets/cards/<skill>.png           900 x 1200 card: the scene in a window, name, expression and line below
  assets/banner.png                  1280 x 640 banner: the cast scene with the title, by headless Chrome
Run from the repo root. Needs Pillow, numpy and Google Chrome.
"""
import argparse
import json
import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from cutout import cutout

R = Image.Resampling.LANCZOS
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CAST = json.loads((HERE / "cast.json").read_text())
INK = "#141414"
PAPER = "#f6f1e7"
COBALT = "#2a46ff"


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def tint(h, k):
    """Mix a colour with white; k is the share of the colour."""
    return tuple(round(c * k + 255 * (1 - k)) for c in hexrgb(h))


def sticker(name, stroke=26):
    """The cutout scaled to 1024 tall with a white outline and a thin ink rim around it."""
    im = Image.open(HERE / "out" / f"{name}.png").convert("RGBA")
    im = im.resize((round(im.width * 1024 / im.height), 1024), R)
    pad = stroke + 8
    cv = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    cv.alpha_composite(im, (pad, pad))
    a = cv.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    grow = a
    for _ in range(stroke // 4):  # grow in steps so the outline stays round
        grow = grow.filter(ImageFilter.MaxFilter(9))
    grow = grow.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 110 else 0)
    rim = grow.filter(ImageFilter.MaxFilter(5))
    out = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", cv.size, hexrgb(INK) + (255,)), mask=rim.filter(ImageFilter.GaussianBlur(0.8)))
    out.paste(Image.new("RGBA", cv.size, (255, 255, 255, 255)), mask=grow.filter(ImageFilter.GaussianBlur(0.8)))
    out.alpha_composite(cv)
    out = out.crop(out.getchannel("A").getbbox())
    path = HERE / "out" / "sticker" / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path, optimize=True)
    return out


def squircle(size, n=5.0):
    m = Image.new("L", (size * 4, size * 4), 0)
    pts = []
    for i in range(720):
        t = 2 * math.pi * i / 720
        c, s = math.cos(t), math.sin(t)
        x = abs(c) ** (2 / n) * (1 if c >= 0 else -1)
        y = abs(s) ** (2 / n) * (1 if s >= 0 else -1)
        pts.append(((x + 1) * size * 2, (y + 1) * size * 2))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.resize((size, size), R)


def tile(st, bg, peek, size=1024):
    """The peek crop: the character, tilted, enters from the lower left and fills the tile."""
    scale, cx, top, angle = peek
    s = st.resize((round(st.width * size * scale / st.height), round(size * scale)), R)
    s = s.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    cv = Image.new("RGBA", (size, size), bg + (255,))
    # a soft lighter disc behind the face gives the tile depth without a second colour
    glow = Image.new("L", (size, size), 0)
    ImageDraw.Draw(glow).ellipse([size * 0.18, size * 0.02, size * 1.02, size * 0.86], fill=70)
    cv.paste(Image.new("RGBA", (size, size), (255, 255, 255, 255)), mask=glow.filter(ImageFilter.GaussianBlur(60)))
    cv.alpha_composite(s, (round(size * cx - s.width / 2), round(size * top)))
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(cv, mask=squircle(size))
    return out


def chrome(html, out, w, h):
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=HERE, delete=False) as f:
        f.write(html)
        page = Path(f.name)
    try:
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--virtual-time-budget=4000", f"--window-size={w},{h}", f"--screenshot={out}",
                        page.as_uri()], check=True, capture_output=True)
    finally:
        page.unlink()


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,800'
         '&display=block" rel="stylesheet">')


def card_html(i, skill, c, scene):
    """The art in a square window, the name, expression and line on their own plate below it."""
    name = skill.replace("-", "&#8209;")
    size = 84 if len(skill) <= 11 else 72 if len(skill) <= 16 else 64
    return f"""<!doctype html><meta charset="utf-8">{FONTS}<style>
*{{margin:0;box-sizing:border-box}}
html,body{{width:900px;height:1200px;background:#fff}}
.face{{position:absolute;inset:16px;border-radius:30px;overflow:hidden;background:{PAPER};border:6px solid {c["colour"]}}}
.win{{position:absolute;left:18px;right:18px;top:18px;aspect-ratio:1;border-radius:20px;overflow:hidden;border:4px solid {INK}}}
.win img{{width:100%;height:100%;display:block}}
.idx{{position:absolute;left:34px;top:34px;width:66px;height:66px;border-radius:50%;background:{c["colour"]};
border:4px solid {INK};display:grid;place-items:center;font:800 28px/1 'Bricolage Grotesque';color:{INK}}}
.plate{{position:absolute;left:18px;right:18px;bottom:18px;top:812px;display:flex;flex-direction:column;align-items:center;
justify-content:center;gap:14px;padding:0 24px 22px;text-align:center;color:{INK}}}
h1{{font:800 {size}px/0.95 'Bricolage Grotesque';letter-spacing:-.035em}}
.chip{{padding:7px 16px;border-radius:99px;background:{c["colour"]};border:3px solid {INK};font:800 19px/1.1 'Bricolage Grotesque';
letter-spacing:.1em;text-transform:uppercase}}
.line{{font:600 28px/1.2 'Bricolage Grotesque';text-wrap:balance}}
</style>
<div class="face"><div class="win"><img src="{scene.as_uri()}"></div><div class="idx">{i:02d}</div>
<div class="plate"><h1>{name}</h1><span class="chip">{c["expression"]}</span><span class="line">&ldquo;{c["line"]}&rdquo;</span></div></div>"""


def banner_html(b, scene):
    """The generated cast scene with the title in its calm upper-left sky."""
    return f"""<!doctype html><meta charset="utf-8">{FONTS}<style>
*{{margin:0}}
body{{width:1280px;height:640px;position:relative;overflow:hidden;background:url('{scene.as_uri()}') center/cover;color:{INK};
font-family:'Bricolage Grotesque',system-ui,sans-serif}}
h1{{position:absolute;left:64px;top:92px;font-weight:800;font-size:150px;line-height:.9;letter-spacing:-.045em}}
p{{position:absolute;left:70px;top:242px;font-weight:600;font-size:30px;line-height:1.25;max-width:420px;text-wrap:balance}}
.u{{position:absolute;left:70px;top:372px;padding:8px 16px;border-radius:99px;background:{INK};color:#fff;font-weight:600;font-size:20px}}
</style><h1>skills</h1><p>{b["tagline"]}</p><div class="u">{b["url"]}</div>"""


def round_card(path, radius=44):
    """Cut the card's corners transparent so it sits on GitHub's light and dark themes."""
    im = Image.open(path).convert("RGBA")
    m = Image.new("L", (im.width * 4, im.height * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width * 4 - 1, im.height * 4 - 1], radius=radius * 4, fill=255)
    im.putalpha(m.resize(im.size, R))
    im.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(path, optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", help="write a light and dark README check sheet here")
    args = ap.parse_args()
    skills = CAST["skills"]
    (HERE / "out").mkdir(exist_ok=True)
    cutout(HERE / "hero" / "hero-v1.webp", HERE / "out" / "hero.png")
    for skill in skills:
        cutout(HERE / "raw" / f"{skill}.webp", HERE / "out" / f"{skill}.png")
    st = {n: sticker(n) for n in ["hero", *skills]}

    (ROOT / "assets" / "skills").mkdir(parents=True, exist_ok=True)
    tiles = {}
    for skill, c in skills.items():
        t = tile(st[skill], tint(c["colour"], 0.55), c["peek"])
        small = t.resize((256, 256), R).quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        small.save(ROOT / "assets" / "skills" / f"{skill}.png", optimize=True)
        tiles[skill] = t
    brand = tile(st["hero"], hexrgb(COBALT), CAST["hero"]["peek"])
    brand.resize((512, 512), R).save(ROOT / "assets" / "icon-512.png", optimize=True)
    brand.save(ROOT / "assets" / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

    (ROOT / "assets" / "cards").mkdir(parents=True, exist_ok=True)
    for i, (skill, c) in enumerate(skills.items(), 1):
        card = ROOT / "assets" / "cards" / f"{skill}.png"
        chrome(card_html(i, skill, c, HERE / "scene" / f"{skill}.webp"), card, 900, 1200)
        round_card(card)
    banner = ROOT / "assets" / "banner.png"
    chrome(banner_html(CAST["banner"], HERE / CAST["banner"]["scene"]), banner, 1280, 640)
    Image.open(banner).convert("RGB").quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(banner, optimize=True)

    if args.check:
        W = 140
        sheet = Image.new("RGB", (W * (len(tiles) + 1), 2 * W), "white")
        for k, bg in enumerate([(255, 255, 255), (13, 17, 23)]):
            layer = Image.new("RGBA", sheet.size, bg + (255,))
            for i, t in enumerate([brand, *tiles.values()]):
                layer.alpha_composite(t.resize((80, 80), R), (i * W + 4, k * W + 30))
                layer.alpha_composite(t.resize((48, 48), R), (i * W + 88, k * W + 46))
            sheet.paste(layer.convert("RGB").crop((0, k * W, sheet.width, (k + 1) * W)), (0, k * W))
        sheet.save(args.check)
    print(f"{len(skills)} skills, brand icon, cards, banner")


if __name__ == "__main__":
    main()
