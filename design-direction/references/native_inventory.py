#!/usr/bin/env python3
"""Count the literal type, spacing, colour, radius and shadow values in SwiftUI, AppKit and UIKit code.

    python3 native_inventory.py <file-or-dir> [...] --out screen-<name>.json

Writes the same JSON shape as inventory.js, so drift.py compares it with DESIGN.md (or with the
budgets alone: `drift.py none screen-*.json --platform desktop`). Pass the files that draw one
screen to measure that screen, or a whole source folder to measure the system. Each value lists
up to three `file:line` samples.

Only literals count: `.font(.system(size: 13))` is a size, `.font(Metrics.body)` is a token and is
skipped. A literal inside the token file itself is the token's definition, so leave that file out
or pass it with --tokens to skip it. Standard library only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

NUM = r"(\d+(?:\.\d+)?)"
SIZE = [
    re.compile(r"\.system\(\s*size:\s*" + NUM),
    re.compile(r"[sS]ystemFont\(\s*ofSize:\s*" + NUM),
    re.compile(r"monospaced(?:Digit)?SystemFont\(\s*ofSize:\s*" + NUM),
    re.compile(r"(?:\.custom\(\s*\"[^\"]+\"|Font\(\s*name:\s*\"[^\"]+\")\s*,\s*(?:fixedSize|size):\s*" + NUM),
]
FAMILY = [
    re.compile(r"\.custom\(\s*\"([^\"]+)\""),
    re.compile(r"(?:NS|UI)Font\(\s*name:\s*\"([^\"]+)\""),
]
DESIGN = re.compile(r"design:\s*\.(monospaced|rounded|serif)")
SYSTEM = re.compile(r"\.system\(|[sS]ystemFont\(")
WEIGHTS = {"ultraLight": 100, "thin": 200, "light": 300, "regular": 400, "medium": 500,
           "semibold": 600, "bold": 700, "heavy": 800, "black": 900}
WEIGHT = re.compile(r"(?:weight:\s*|\.fontWeight\(\s*)(?:\.|NSFont\.Weight\.|UIFont\.Weight\.)(\w+)")
BOLD = re.compile(r"\.bold\(\)")
SPACING = [
    re.compile(r"\.padding\(\s*" + NUM + r"\s*\)"),
    re.compile(r"\.padding\(\s*\.\w+\s*,\s*" + NUM + r"\s*\)"),
    re.compile(r"\bspacing:\s*" + NUM),
    re.compile(r"\b(?:top|leading|bottom|trailing|left|right):\s*" + NUM),
]
INSETS = re.compile(r"EdgeInsets\(")
RADIUS = [
    re.compile(r"cornerRadius(?::|\s*=|\()\s*" + NUM),
    re.compile(r"(?:topLeading|topTrailing|bottomLeading|bottomTrailing)Radius:\s*" + NUM),
]
RGB = re.compile(r"(?:Color|NSColor|UIColor|CGColor)\(\s*(?:\.sRGB,\s*)?(?:srgbRed|calibratedRed|deviceRed|red):\s*"
                 + NUM + r"\s*,\s*green:\s*" + NUM + r"\s*,\s*blue:\s*" + NUM + r"(?:\s*,\s*(?:alpha|opacity):\s*" + NUM + r")?")
WHITE = re.compile(r"(?:Color|NSColor|UIColor)\(\s*(?:calibrated|device|generic)?[wW]hite:\s*" + NUM + r"(?:\s*,\s*(?:alpha|opacity):\s*" + NUM + r")?")
HEX = re.compile(r"(?:Color|NSColor|UIColor)\(\s*hex:\s*\"?#?([0-9a-fA-F]{6})")
TEXT_HINT = re.compile(r"foreground|textColor|tint", re.I)
BORDER_HINT = re.compile(r"stroke|border", re.I)
SHADOW = re.compile(r"\.shadow\(([^)]*\b(?:radius|x|y):\s*\d[^)]*)\)|shadowRadius\s*=\s*" + NUM)
SKIP_DIRS = {".build", "build", "DerivedData", "Pods", "Carthage", ".git", "Tests"}


def walk(roots, skip):
    for root in map(Path, roots):
        files = [root] if root.is_file() else sorted(root.rglob("*.swift"))
        for f in files:
            if f.suffix == ".swift" and f.resolve() not in skip and not (set(f.parts) & SKIP_DIRS):
                yield f


def colour(m, kind):
    if kind == "rgb":
        r, g, b, a = m.groups()
        r, g, b = (round(float(x) * 255) if float(x) <= 1 else round(float(x)) for x in (r, g, b))
    elif kind == "white":
        w, a = m.groups()
        r = g = b = round(float(w) * 255)
    else:
        h, a = m.group(1), None
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {float(a):g})" if a and float(a) < 1 else f"rgb({r}, {g}, {b})"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roots", nargs="+")
    ap.add_argument("--tokens", action="append", default=[], help="token file to leave out (repeatable)")
    ap.add_argument("--out", help="write the JSON here (default: stdout)")
    a = ap.parse_args()
    skip = {Path(t).resolve() for t in a.tokens}

    maps = {k: {} for k in ("sizes", "weights", "families", "spacing", "radius", "shadow", "text", "background", "border")}

    def add(group, value, where):
        e = maps[group].setdefault(value, {"count": 0, "samples": []})
        e["count"] += 1
        if len(e["samples"]) < 3:
            e["samples"].append(where)

    files = list(walk(a.roots, skip))
    if not files:
        sys.exit("no .swift files found")
    for f in files:
        for n, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
            code = line.split("//")[0]
            if not code.strip():
                continue
            where = f"{f}:{n}"
            for rx in SIZE:
                for v in rx.findall(code):
                    add("sizes", f"{float(v):g}px", where)
            for rx in FAMILY:
                for v in rx.findall(code):
                    add("families", v, where)
            if SYSTEM.search(code):
                d = DESIGN.search(code)
                add("families", f"system-{d.group(1)}" if d else "system-ui", where)
            for w in WEIGHT.findall(code):
                if w in WEIGHTS:
                    add("weights", str(WEIGHTS[w]), where)
            if BOLD.search(code):
                add("weights", "700", where)
            insets = INSETS.search(code)
            for rx in SPACING:
                if rx is SPACING[-1] and not insets:  # top:/leading: count only inside EdgeInsets(...)
                    continue
                for v in rx.findall(code):
                    add("spacing", f"{float(v):g}px", where)
            for rx in RADIUS:
                for v in rx.findall(code):
                    add("radius", f"{float(v):g}px", where)
            group = "text" if TEXT_HINT.search(code) else "border" if BORDER_HINT.search(code) else "background"
            for m in RGB.finditer(code):
                add(group, colour(m, "rgb"), where)
            for m in WHITE.finditer(code):
                add(group, colour(m, "white"), where)
            for m in HEX.finditer(code):
                add(group, colour(m, "hex"), where)
            for m in SHADOW.finditer(code):
                add("shadow", re.sub(r"\s+", " ", (m.group(1) or f"radius: {m.group(2)}").strip()), where)

    def sorted_(group):
        return sorted(({"value": v, **e} for v, e in maps[group].items()), key=lambda e: -e["count"])

    out = {
        "url": "code: " + ", ".join(a.roots),
        "source": "code",
        "viewport": {"w": 0, "h": 0},
        "files": len(files),
        "counts": {k: len(v) for k, v in maps.items()},
        "type": {"sizes": sorted_("sizes"), "weights": sorted_("weights"), "families": sorted_("families"), "lineHeights": []},
        "colour": {"text": sorted_("text"), "background": sorted_("background"), "border": sorted_("border"), "areaShare": []},
        "spacing": sorted_("spacing"),
        "radius": sorted_("radius"),
        "shadow": sorted_("shadow"),
        "roles": {},
    }
    text = json.dumps(out, indent=2)
    if a.out:
        Path(a.out).write_text(text)
        c = out["counts"]
        print(f"{len(files)} files: {c['sizes']} font sizes, {c['weights']} weights, {c['families']} families, "
              f"{c['spacing']} spacing values, {c['radius']} radii, {c['text'] + c['background'] + c['border']} literal colours, "
              f"{c['shadow']} shadows -> {a.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
