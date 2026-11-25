#!/usr/bin/env python3
"""Build the in-chat photo cards for a deal-check run: one HTML file per price
range, each small enough for one html_render.

    python3 cards.py run.json --ranges 600000,1000000,1500000,2000000 --out cards/

run.json is the run's single source of truth (prices.py reads it too):

    {
      "date": "2026-11-25",              # the day the prices were read
      "slug": "footlocker-b2g1-shoes",   # names the snapshot folder
      "noun": "shoes",                   # used in each file's heading
      "terms": ["Cheapest of three is free", "!No returns or exchanges", "Ends 30 Nov 2026"],
                                         # promo terms as chips; a leading ! marks a cost to the buyer
      "sets": [{"name": "Black, brown, grey", "urls": ["...", "...", "..."], "note": "..."}],
                                         # optional bundles for a cheapest-item-free promo
      "items": [{
        "store": "Foot Locker", "brand": "Lacoste", "model": "Baseshot Pro",
        "colour": "Black",               # named from the photo, not the listing
        "url": "https://...",            # the product page
        "price": 1259300,                # payable for this item alone, before any voucher
        "list_price": 1799000,           # null when none is shown
        "image": "/abs/path/photo.jpg",  # local file; null drops the photo
        "fit": "UK 8 in stock",          # the buyer's size or the spec that matters
        "tags": ["Leather", "Black sole"],
        "promo": "Buy 2 Get 1",          # null when the item is in no promo
        "verdict": "buy",                # buy | consider | wait | skip
        "pick": "Most formal",           # optional label on the photo
        "note": "One sentence: the reason for the verdict.",
        "evidence": {                    # every key present; "not found" when no source
          "year": "2024 model, this colour 2025",
          "stars": "4.6 (212) Foot Locker, 4.8 (95) Zalora",
          "review": "Runs true to size (Zappos, 3 reviews)",
          "trend": "Lowest of 3 snapshots; Zalora 1,675,000 today",
          "popularity": "Rank 12 of 250 by popularity"
        }
      }]
    }

Photos are resized to 360 px with sips and embedded, so each file is
self-contained. A range with more than --per-file cards is split into parts.
`skip` items get no card: they are listed with their note under the last file.
The script prints one JSON line per file (path, title, cards, chars) and exits
1 on a missing field, an unknown verdict, or a file over the render limit.
"""
import argparse
import base64
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

LIMIT = 500_000  # html_render takes 512,000 characters
EVIDENCE = [("year", "Year"), ("stars", "Stars"), ("review", "Review"),
            ("trend", "Price trend"), ("popularity", "Popularity")]
VERDICT = {"buy": ("Buy", "--success"), "consider": ("Consider", "--info"),
           "wait": ("Wait", "--warning")}
REQUIRED = ["store", "brand", "model", "colour", "url", "price", "verdict", "note", "evidence"]

CSS = """
*{box-sizing:border-box}
.h{margin:4px 0 2px;font-size:18px;font-weight:650;color:var(--foreground)}
.s{margin:0 0 12px;font-size:13px;color:var(--muted-foreground)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px}
.chip{border:1px solid var(--border);border-radius:999px;padding:3px 10px;font-size:12.5px;color:var(--foreground)}
.chip.warn{border-color:var(--warning);color:var(--warning)}
.sets{display:grid;gap:8px;margin:0 0 14px}
.set{border:1px solid var(--border);border-radius:var(--radius);background:var(--card);padding:10px 12px;display:grid;grid-template-columns:1fr auto;gap:4px 16px;font-size:13px}
.set b{font-weight:650}
.set ul{margin:2px 0 0;padding:0;list-style:none;color:var(--muted-foreground);font-size:12.5px}
.set .free{color:var(--success)}
.set .pay{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.set .pay b{display:block;font-size:16px}
.set .pay s,.set .pay span{font-size:12px;color:var(--muted-foreground)}
.set p{grid-column:1/-1;margin:2px 0 0;font-size:12px;color:var(--muted-foreground)}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
a.c{display:flex;flex-direction:column;text-decoration:none;color:inherit;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;min-width:0}
a.c:hover{border-color:var(--ring)}
.im{position:relative;background:#fff;height:0;padding-top:80%}
.im img{position:absolute;inset:6px;width:calc(100% - 12px);height:calc(100% - 12px);object-fit:contain}
.off{position:absolute;top:8px;left:8px;background:var(--destructive);color:#fff;font-size:12px;font-weight:700;padding:2px 7px;border-radius:999px}
.pk{position:absolute;bottom:8px;left:8px;right:8px;background:var(--primary);color:var(--primary-foreground);font-size:11px;font-weight:650;padding:3px 7px;border-radius:6px;text-align:center}
.b{padding:10px 11px 12px;display:flex;flex-direction:column;gap:5px;flex:1}
.br{font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted-foreground)}
.n{font-size:13.5px;font-weight:600;line-height:1.3;color:var(--card-foreground,var(--foreground))}
.n span{font-weight:400;color:var(--muted-foreground)}
.p{font-size:16px;font-weight:700;color:var(--foreground);font-variant-numeric:tabular-nums}
.w{font-size:12px;color:var(--muted-foreground);text-decoration:line-through;display:block;margin-top:-4px}
.fit{font-size:12.5px;color:var(--foreground)}
.m{display:flex;flex-wrap:wrap;gap:4px}
.t{font-size:11px;padding:1px 6px;border-radius:4px;background:var(--secondary);color:var(--secondary-foreground)}
.ev{display:grid;grid-template-columns:auto 1fr;gap:1px 8px;margin:2px 0 0;padding-top:6px;border-top:1px solid var(--border);font-size:11.5px;line-height:1.35}
.ev dt{color:var(--muted-foreground);white-space:nowrap}
.ev dd{margin:0;color:var(--foreground)}
.ev dd.nf{color:var(--muted-foreground);font-style:italic}
.no{font-size:11.5px;line-height:1.35;color:var(--muted-foreground)}
.f{display:flex;justify-content:space-between;align-items:center;gap:6px;white-space:nowrap;font-size:12px;margin-top:auto;padding-top:4px;color:var(--muted-foreground)}
.v{display:inline-flex;align-items:center;gap:5px;font-weight:600}
.v i{width:8px;height:8px;border-radius:50%;display:inline-block}
.out{margin:14px 0 0;font-size:12.5px;color:var(--muted-foreground)}
.out b{color:var(--foreground);font-weight:600}
"""

e = html.escape


def rp(n):
    return "Rp " + f"{n:,}".replace(",", ".")


def short(n):
    return f"{n / 1e6:g}M" if n >= 1_000_000 else f"{n // 1000}K"


def range_titles(bounds):
    titles = [f"Under Rp {short(bounds[0])}"]
    titles += [f"Rp {short(a)} to {short(b)}" for a, b in zip(bounds, bounds[1:])]
    return titles + [f"Rp {short(bounds[-1])} and up"]


def photo(src, dest):
    """Resize to 360 px JPEG with sips; without sips, embed the file as it is."""
    if shutil.which("sips"):
        done = subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72",
                               "-Z", "360", str(src), "--out", str(dest)], capture_output=True)
        if done.returncode == 0 and dest.exists():
            src = dest
    return "data:image/jpeg;base64," + base64.b64encode(Path(src).read_bytes()).decode()


def card(x, img):
    off = pk = was = fit = tags = ""
    if x.get("list_price") and x["list_price"] > x["price"]:
        off = f'<span class="off">-{round((1 - x["price"] / x["list_price"]) * 100)}%</span>'
        was = f'<span class="w">{rp(x["list_price"])}</span>'
    if x.get("pick"):
        pk = f'<span class="pk">{e(x["pick"])}</span>'
    if x.get("fit"):
        fit = f'<div class="fit">{e(x["fit"])}</div>'
    chips = list(x.get("tags") or []) + ([x["promo"]] if x.get("promo") else [])
    if chips:
        tags = '<div class="m">' + "".join(f'<span class="t">{e(t)}</span>' for t in chips) + "</div>"
    rows = ""
    for key, label in EVIDENCE:
        val = (x["evidence"].get(key) or "not found").strip()
        cls = ' class="nf"' if val == "not found" else ""
        rows += f"<dt>{label}</dt><dd{cls}>{e(val)}</dd>"
    label, var = VERDICT[x["verdict"]]
    pic = f'<img src="{img}" alt="{e(x["brand"] + " " + x["model"] + ", " + x["colour"])}">' if img else ""
    return (f'<a class="c" href="{e(x["url"])}" target="_blank" rel="noopener">'
            f'<div class="im">{pic}{off}{pk}</div><div class="b">'
            f'<div class="br">{e(x["brand"])}</div>'
            f'<div class="n">{e(x["model"])} <span>· {e(x["colour"])}</span></div>'
            f'<div class="p">{rp(x["price"])}</div>{was}{fit}{tags}'
            f'<dl class="ev">{rows}</dl><div class="no">{e(x["note"])}</div>'
            f'<div class="f"><span>{e(x["store"])}</span>'
            f'<span class="v" style="color:var({var})"><i style="background:var({var})"></i>{label}</span>'
            f"</div></div></a>")


def set_card(s, by_url):
    picked = [by_url[u] for u in s["urls"]]
    total = sum(x["price"] for x in picked)
    free = min(picked, key=lambda x: x["price"])
    pay = total - free["price"]
    lines = "".join(
        f'<li class="{"free" if x is free else ""}">{e(x["brand"])} {e(x["model"])}, {e(x["colour"])}: '
        f'{rp(x["price"])}{" (free)" if x is free else ""}</li>' for x in picked)
    note = f'<p>{e(s["note"])}</p>' if s.get("note") else ""
    return (f'<div class="set"><div><b>{e(s["name"])}</b><ul>{lines}</ul></div>'
            f'<div class="pay"><s>{rp(total)}</s><b>{rp(pay)}</b>'
            f'<span>about {rp(int(round(pay / len(picked), -2)))} each</span></div>{note}</div>')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run", type=Path)
    ap.add_argument("--ranges", default="500000,1000000,2000000",
                    help="price range boundaries in Rp, comma separated")
    ap.add_argument("--out", type=Path, default=Path("cards"))
    ap.add_argument("--per-file", type=int, default=9,
                    help="most cards in one file; 9 stays under the 2000 px frame at reply width")
    args = ap.parse_args()

    run = json.loads(args.run.read_text())
    items, errors = run["items"], []
    for i, x in enumerate(items):
        name = f'item {i} ({x.get("model", "?")})'
        errors += [f"{name}: missing {k}" for k in REQUIRED if x.get(k) in (None, "")]
        if x.get("verdict") not in (*VERDICT, "skip"):
            errors.append(f'{name}: verdict {x.get("verdict")!r} is not buy, consider, wait or skip')
        for key, label in EVIDENCE:
            if isinstance(x.get("evidence"), dict) and not (x["evidence"].get(key) or "").strip():
                errors.append(f'{name}: evidence.{key} is empty; write the value or "not found"')
        if x.get("image") and not Path(x["image"]).is_file():
            errors.append(f'{name}: image {x["image"]} does not exist')
    by_url = {x["url"]: x for x in items if x.get("url")}
    for s in run.get("sets") or []:
        errors += [f'set {s["name"]}: {u} is not an item url' for u in s["urls"] if u not in by_url]
    if errors:
        print("\n".join(errors))
        sys.exit(1)

    bounds = sorted(int(b) for b in args.ranges.split(","))
    titles = range_titles(bounds)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "img").mkdir(exist_ok=True)
    order = {"buy": 0, "consider": 1, "wait": 2}
    shown = [x for x in items if x["verdict"] != "skip"]
    skipped = [x for x in items if x["verdict"] == "skip"]
    groups = [[] for _ in titles]
    for x in shown:
        groups[sum(x["price"] >= b for b in bounds)].append(x)
    noun = run.get("noun", "items")
    used = []  # (title, cards in it), a range over --per-file split into parts
    for title, g in zip(titles, groups):
        g.sort(key=lambda x: (order[x["verdict"]], not x.get("pick"), x["price"]))
        parts = [g[i:i + args.per_file] for i in range(0, len(g), args.per_file)]
        used += [(title + (f" ({k + 1} of {len(parts)})" if len(parts) > 1 else ""), p)
                 for k, p in enumerate(parts)]
    over = False
    for n, (title, group) in enumerate(used):
        cards = "".join(
            card(x, photo(x["image"], args.out / "img" / f"{items.index(x):03d}.jpg") if x.get("image") else "")
            for x in group)
        head = f'<div class="h">{title} · {len(group)} {e(noun)}</div>'
        extra = tail = ""
        if n == 0:
            if run.get("terms"):
                extra += '<div class="chips">' + "".join(
                    f'<span class="chip{" warn" if t.startswith("!") else ""}">{e(t.lstrip("!"))}</span>'
                    for t in run["terms"]) + "</div>"
            if run.get("sets"):
                extra += '<div class="sets">' + "".join(set_card(s, by_url) for s in run["sets"]) + "</div>"
        if n == len(used) - 1 and skipped:
            tail = '<p class="out"><b>Left out.</b> ' + " ".join(
                f'{e(x["brand"])} {e(x["model"])}, {e(x["colour"])}: {e(x["note"])}' for x in skipped) + "</p>"
        doc = (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
               f'{head}{extra}<div class="g">{cards}</div>{tail}</body></html>')
        path = args.out / f"cards-{n + 1}.html"
        path.write_text(doc)
        over = over or len(doc) > LIMIT
        print(json.dumps({"path": str(path.resolve()), "title": f"{noun.capitalize()}: {title}",
                          "cards": len(group), "chars": len(doc)}))
    if over:
        print(f"a file is over {LIMIT} characters: add a boundary to --ranges so it splits")
        sys.exit(1)


if __name__ == "__main__":
    main()
