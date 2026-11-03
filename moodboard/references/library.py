#!/usr/bin/env python3
"""Read the moodboard library: list it, find trends, build a project board.

  library.py list [--tag halftone] [--job palette] [--since 2026-10-01]
  library.py trends [--days 45] [--min 3]          techniques shared by several authors recently
  library.py board <project> <ref-id>=<job> ...    boards/<project>/board.md and board.png
  library.py palette <image> [<image> ...]         dominant colours with their share

The library is $MOODBOARD_DIR (default ~/moodboard): one folder per reference with card.json.
Needs Pillow and numpy for palette and board.png.
"""
import argparse
import datetime as dt
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

LIB = Path(os.environ.get("MOODBOARD_DIR", Path.home() / "moodboard")).expanduser()
JOBS = {"technique", "palette", "type", "layout", "shape", "pose", "composition", "motion", "copy"}


def cards():
    for f in sorted(LIB.glob("*/card.json")):
        c = json.loads(f.read_text())
        c["_dir"] = f.parent
        yield c


def extract_palette(paths, k=6, size=96):
    """k-means over the pixels of every image: [{"hex", "share"}], largest first."""
    import numpy as np
    from PIL import Image
    px = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        im.thumbnail((size, size))
        px.append(np.asarray(im, float).reshape(-1, 3))
    x = np.concatenate(px)
    rng = np.random.default_rng(0)
    c = x[rng.choice(len(x), k, replace=False)]
    for _ in range(20):
        lab = ((x[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
        c = np.array([x[lab == i].mean(0) if (lab == i).any() else c[i] for i in range(k)])
    share = np.bincount(lab, minlength=k) / len(x)
    order = share.argsort()[::-1]
    return [{"hex": "#%02x%02x%02x" % tuple(int(v) for v in c[i]), "share": round(float(share[i]), 3)}
            for i in order if share[i] > 0.01]


def cmd_list(a):
    rows = []
    for c in cards():
        if a.tag and a.tag not in c["techniques"]:
            continue
        if a.job and a.job not in c["jobs"]:
            continue
        if a.since and (c.get("saved") or "") < a.since:
            continue
        rows.append(c)
    print("| id | author | posted | techniques | jobs | subject |")
    print("|---|---|---|---|---|---|")
    for c in rows:
        todo = "" if c["techniques"] else " (not broken down)"
        print(f"| {c['id']} | {c.get('author') or ''} | {c.get('posted') or ''} | "
              f"{', '.join(c['techniques'])}{todo} | {', '.join(c['jobs'])} | {c.get('subject', '')} |")
    print(f"\n{len(rows)} references in {LIB}")


def cmd_trends(a):
    since = (dt.date.today() - dt.timedelta(days=a.days)).isoformat()
    by_tag = defaultdict(list)
    for c in cards():
        when = c.get("posted") or c.get("saved") or ""
        if when >= since:
            for t in c["techniques"]:
                by_tag[t].append(c)
    rows = []
    for tag, cs in by_tag.items():
        authors = {c.get("author") for c in cs}
        rows.append((len(authors), tag, cs))
    rows.sort(key=lambda r: (-r[0], r[1]))
    print(f"| technique | authors | references | status |")
    print(f"|---|---|---|---|")
    for n, tag, cs in rows:
        status = "trend" if n >= a.min else ""
        print(f"| {tag} | {n} | {', '.join(c['id'] for c in cs)} | {status} |")
    trends = [r for r in rows if r[0] >= a.min]
    print(f"\n{len(trends)} trends: techniques used by {a.min}+ different authors since {since}. "
          "A trend enters a project as one ingredient, never as the whole style.")


def cmd_board(a):
    index = {c["id"]: c for c in cards()}
    picks, seen_jobs, problems = [], {}, []
    for arg in a.refs:
        rid, _, job = arg.partition("=")
        if rid not in index:
            sys.exit(f"{rid}: not in the library (library.py list)")
        if job not in JOBS:
            sys.exit(f"{rid}: job {job!r} is not one of {sorted(JOBS)}")
        if job in seen_jobs:
            problems.append(f"{job} has two references ({seen_jobs[job]}, {rid}): keep one")
        seen_jobs[job] = rid
        picks.append((index[rid], job))
    out = LIB / "boards" / a.project
    out.mkdir(parents=True, exist_ok=True)
    lines = [f"# {a.project} board", "", f"Made {dt.date.today().isoformat()} from {LIB}.", "",
             "| Reference | Job | What is taken | Everything else |", "|---|---|---|---|"]
    for c, job in picks:
        lines.append(f"| [{c['id']}]({c['url']}) {c.get('author') or ''} | {job} | <fill: the values or technique taken> | ignored |")
    lines += ["", "Identity of each reference, kept out of this project:", ""]
    lines += [f"- {c['id']}: {c.get('identity') or '<fill>'}" for c, _ in picks]
    (out / "board.md").write_text("\n".join(lines) + "\n")
    try:
        from PIL import Image, ImageDraw
        tile = 320
        sheet = Image.new("RGB", (tile * min(4, len(picks)), tile * (-(-len(picks) // 4)) + 0), "white")
        draw = ImageDraw.Draw(sheet)
        for i, (c, job) in enumerate(picks):
            media = [m for m in c["media"] if m.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
            x, y = (i % 4) * tile, (i // 4) * tile
            if media:
                im = Image.open(c["_dir"] / media[0]).convert("RGB")
                im.thumbnail((tile - 10, tile - 34))
                sheet.paste(im, (x + (tile - im.width) // 2, y + 5))
            draw.rectangle([x, y + tile - 26, x + tile, y + tile], fill="white")
            draw.text((x + 6, y + tile - 20), f"{job}: {c['id']}"[:48], fill="black")
        sheet.save(out / "board.png")
    except ImportError:
        problems.append("Pillow missing: board.png not written")
    print(f"board: {out / 'board.md'}, {out / 'board.png'}")
    for p in problems:
        print(f"- {p}")
    sys.exit(1 if problems else 0)


def cmd_palette(a):
    for h in extract_palette([Path(p) for p in a.images]):
        print(f"{h['hex']}  {h['share']:.0%}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list")
    p.add_argument("--tag")
    p.add_argument("--job")
    p.add_argument("--since")
    p.set_defaults(fn=cmd_list)
    p = sub.add_parser("trends")
    p.add_argument("--days", type=int, default=45)
    p.add_argument("--min", type=int, default=3)
    p.set_defaults(fn=cmd_trends)
    p = sub.add_parser("board")
    p.add_argument("project")
    p.add_argument("refs", nargs="+", metavar="ref-id=job")
    p.set_defaults(fn=cmd_board)
    p = sub.add_parser("palette")
    p.add_argument("images", nargs="+")
    p.set_defaults(fn=cmd_palette)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
