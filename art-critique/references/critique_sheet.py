#!/usr/bin/env python3
"""Sheets a critic reads instead of a downscaled whole image, and the record it leaves.

  critique_sheet.py crops   <img> [<img> ...] --out DIR [--tile 768]
  critique_sheet.py pairs   <img> [<img> ...] --out DIR
  critique_sheet.py tally   VOTES.json --pairs DIR/pairs.json
  critique_sheet.py bench   <img> --refs <ref> [<ref> ...] --out sheet.png
  critique_sheet.py inplace <img> [<img> ...] --width 260 [--width 600] --out sheet.png
  critique_sheet.py record  art/<name>/review.json <file> [<file> ...] --verdict pass|fix|regenerate|waived --note "..."

crops    the whole image at 1024, a blurred greyscale copy (the value read), and crops at full
         resolution with overlap: a grip on the wrong handle or a smudge on a mouth is a few pixels
         in a whole image read at 1024 and plain in a crop.
pairs    every pair of candidates side by side, in both orders, labelled 1 and 2, with pairs.json.
tally    reads {"pair-01-ab": 1, "pair-01-ba": 2, ...} (1 = left won, 2 = right won, 0 = tie). A pair
         counts only when both orders agree; a pair that flips with the order is a tie, and a judge
         that prefers one side has position bias.
bench    the image beside each benchmark piece at one height, colour over greyscale.
inplace  the image at its real display widths on GitHub's light and dark grounds.
record   writes a critique verdict per file into review.json, keyed by path relative to the
         review file and pinned to the file's hash, so brand-art's handover gate knows it is current.
Needs Pillow.
"""
import argparse
import hashlib
import itertools
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
    LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
except ImportError:
    sys.exit("needs Pillow: python3 -m pip install pillow")

GROUNDS = {"light": (255, 255, 255), "dark": (13, 17, 23)}  # GitHub's page backgrounds


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow before 10.1
        return ImageFont.load_default()


def opened(path):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
    flat = Image.new("RGB", im.size, "white")
    flat.paste(im, mask=im.getchannel("A"))
    return im, flat


def fit(im, long):
    s = long / max(im.size)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), LANCZOS)


def label(im, text, size=28):
    out = Image.new("RGB", (im.width, im.height + size + 16), "white")
    out.paste(im, (0, size + 16))
    ImageDraw.Draw(out).text((8, 6), text, fill="black", font=font(size))
    return out


def row(images, gap=16, ground="white"):
    w = sum(i.width for i in images) + gap * (len(images) - 1)
    h = max(i.height for i in images)
    out = Image.new("RGB", (w, h), ground)
    x = 0
    for i in images:
        out.paste(i, (x, 0))
        x += i.width + gap
    return out


def stack(images, gap=16, ground="white"):
    w = max(i.width for i in images)
    h = sum(i.height for i in images) + gap * (len(images) - 1)
    out = Image.new("RGB", (w, h), ground)
    y = 0
    for i in images:
        out.paste(i, (0, y))
        y += i.height + gap
    return out


def cmd_crops(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    written = 0
    paths = list(map(Path, a.images))
    stems = [p.stem for p in paths]
    for p in paths:
        # cards/learn.png and scene/learn.webp both have the stem learn: name by folder when stems repeat
        name = f"{p.parent.name}-{p.stem}" if stems.count(p.stem) > 1 else p.stem
        _, flat = opened(p)
        fit(flat, 1024).save(out / f"{name}-whole.png")
        g = ImageOps.grayscale(flat)
        fit(g.filter(ImageFilter.GaussianBlur(max(g.size) * 0.012)), 1024).save(out / f"{name}-value.png")
        written += 2
        t = a.tile
        if max(flat.size) > t:
            step = round(t * 0.85)
            xs = list(range(0, max(1, flat.width - t), step)) + [max(0, flat.width - t)]
            ys = list(range(0, max(1, flat.height - t), step)) + [max(0, flat.height - t)]
            for r, y in enumerate(sorted(set(ys)), 1):
                for c, x in enumerate(sorted(set(xs)), 1):
                    flat.crop((x, y, x + t, y + t)).save(out / f"{name}-r{r}c{c}.png")
                    written += 1
        print(f"{p.name}: {flat.width}x{flat.height}")
    print(f"{written} files in {out}: open every one")


def cmd_pairs(a):
    paths = [Path(p) for p in a.images]
    if not 2 <= len(paths) <= 6:
        sys.exit("pairs takes 2 to 6 candidates; screen the rest out on the rubric first")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tiles = {p: fit(opened(p)[1], 900) for p in paths}
    key = {}
    for n, (x, y) in enumerate(itertools.combinations(paths, 2), 1):
        for order, (left, right) in (("ab", (x, y)), ("ba", (y, x))):
            pid = f"pair-{n:02d}-{order}"
            row([label(tiles[left], "1"), label(tiles[right], "2")], gap=40).save(out / f"{pid}.png")
            key[pid] = [str(left), str(right)]
    (out / "pairs.json").write_text(json.dumps(key, indent=1))
    print(f"{len(key)} pair sheets in {out}, key in {out / 'pairs.json'}")
    print("judge each sheet on its own, in a shuffled order; write votes as {\"pair-01-ab\": 1, ...}")


def cmd_tally(a):
    key = json.loads(Path(a.pairs).read_text())
    votes = json.loads(Path(a.votes).read_text())
    missing = sorted(set(key) - set(votes))
    if missing:
        sys.exit(f"no vote for {', '.join(missing)}")
    wins, ties, bias = {}, [], {1: 0, 2: 0}
    for pid in sorted(key):
        for f in key[pid]:
            wins.setdefault(f, 0.0)
    for base in sorted({k[:-3] for k in key}):
        ab, ba = votes[f"{base}-ab"], votes[f"{base}-ba"]
        for v in (ab, ba):
            if v in bias:
                bias[v] += 1
        x, y = key[f"{base}-ab"]
        winner_ab = {1: x, 2: y}.get(ab)
        winner_ba = {1: y, 2: x}.get(ba)
        if winner_ab and winner_ab == winner_ba:
            wins[winner_ab] += 1
        else:
            wins[x] += 0.5
            wins[y] += 0.5
            ties.append(f"{Path(x).name} vs {Path(y).name}")
    print("| rank | candidate | wins |")
    print("|---|---|---|")
    for i, (f, w) in enumerate(sorted(wins.items(), key=lambda kv: -kv[1]), 1):
        print(f"| {i} | {Path(f).name} | {w:g} |")
    if ties:
        print("\nties (the verdict flipped with the order, or a 0 vote):")
        for t in ties:
            print(f"- {t}")
    total = bias[1] + bias[2]
    if total and max(bias.values()) / total > 0.7:
        side = "left" if bias[1] > bias[2] else "right"
        print(f"\nposition bias: {max(bias.values())} of {total} votes went to the {side} image; re-judge the ties")


def cmd_bench(a):
    h = 720
    cols = []
    for p, name in [(a.image, "OURS " + Path(a.image).name)] + [(r, Path(r).parent.name or Path(r).name) for r in a.refs]:
        _, flat = opened(p)
        s = h / flat.height
        c = flat.resize((max(1, round(flat.width * s)), h), LANCZOS)
        cols.append(stack([label(c, name[:40]), ImageOps.grayscale(c).convert("RGB")]))
    row(cols, gap=32).save(a.out)
    print(f"bench sheet: {a.out} (ours first, then {len(a.refs)} benchmark pieces)")


def cmd_inplace(a):
    blocks = []
    for gname, g in GROUNDS.items():
        tiles = []
        for p in a.images:
            im, _ = opened(p)
            for w in a.width:
                s = w / im.width
                t = im.resize((w, max(1, round(im.height * s))), LANCZOS)
                cell = Image.new("RGB", (t.width + 48, t.height + 72), g)
                cell.paste(t, (24, 48), t)
                ImageDraw.Draw(cell).text((24, 14), f"{Path(p).stem} at {w}px on {gname}",
                                          fill=(140, 140, 140), font=font(18))
                tiles.append(cell)
        blocks.append(row(tiles, gap=0, ground=g))
    stack(blocks, gap=0).save(a.out)
    print(f"in-place sheet: {a.out}")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def cmd_record(a):
    review = Path(a.review)
    data = json.loads(review.read_text()) if review.exists() else {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for f in a.files:
        key = Path(os.path.relpath(Path(f).resolve(), review.parent.resolve())).as_posix()
        e = data.get(key, {})
        if e.get("sha") != sha(f):
            e = {"sha": sha(f)}  # a changed file loses every earlier verdict
        e["critique"] = {"status": a.verdict, "t": now, "note": a.note}
        data[key] = e
    review.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    print(f"{len(a.files)} critique verdicts written to {review}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("crops")
    p.add_argument("images", nargs="+")
    p.add_argument("--out", required=True)
    p.add_argument("--tile", type=int, default=768)
    p = sub.add_parser("pairs")
    p.add_argument("images", nargs="+")
    p.add_argument("--out", required=True)
    p = sub.add_parser("tally")
    p.add_argument("votes")
    p.add_argument("--pairs", required=True)
    p = sub.add_parser("bench")
    p.add_argument("image")
    p.add_argument("--refs", nargs="+", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("inplace")
    p.add_argument("images", nargs="+")
    p.add_argument("--width", type=int, action="append", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("record")
    p.add_argument("review")
    p.add_argument("files", nargs="+")
    p.add_argument("--verdict", required=True, choices=["pass", "fix", "regenerate", "waived"])
    p.add_argument("--note", required=True)
    a = ap.parse_args()
    {"crops": cmd_crops, "pairs": cmd_pairs, "tally": cmd_tally, "bench": cmd_bench,
     "inplace": cmd_inplace, "record": cmd_record}[a.cmd](a)


if __name__ == "__main__":
    main()
