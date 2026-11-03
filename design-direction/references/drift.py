#!/usr/bin/env python3
"""Compare a DESIGN.md token system with what screens actually use.

  drift.py DESIGN.md --platform web                      check the tokens against the budgets
  drift.py DESIGN.md screen-*.json --platform app        check each inventory.js result too

Prints one markdown table per screen and a list of findings. Exits 1 when anything is over budget.
Standard library only.
"""
import argparse
import colorsys
import json
import math
import re
import sys
from pathlib import Path

BUDGETS = {
    #            sizes/screen, sizes/system, weights, families, radii, shadows
    "app":     dict(sizes=4, system_sizes=6, weights=2, families=2, radii=3, shadows=3),
    "web":     dict(sizes=6, system_sizes=8, weights=3, families=2, radii=4, shadows=3),
    "desktop": dict(sizes=5, system_sizes=7, weights=2, families=2, radii=3, shadows=3),
}
ROOT_PX = 16
COLOUR_TOLERANCE = 6  # max RGB distance still counted as the same colour


# ---------- DESIGN.md frontmatter: the YAML subset the format uses (nested maps of scalars)

def strip_comment(line):
    out, quote = [], None
    for ch in line:
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (not out or out[-1].isspace()):
            break
        out.append(ch)
    return "".join(out).rstrip()


def scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    try:
        return float(v) if "." in v else int(v)
    except ValueError:
        return v


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        sys.exit("DESIGN.md has no YAML frontmatter")
    root = {}
    stack = [(-1, root)]
    for raw in m.group(1).splitlines():
        line = strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, _, value = line.strip().partition(":")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if value.strip():
            parent[key.strip()] = scalar(value)
        else:
            parent[key.strip()] = {}
            stack.append((indent, parent[key.strip()]))
    return root


# ---------- values

def to_px(v):
    """'16px' | '1rem' | 16 -> 16.0; anything else -> None."""
    if isinstance(v, (int, float)):
        return float(v)
    m = re.fullmatch(r"\s*(-?[\d.]+)\s*(px|rem|em|pt|dp)?\s*", str(v))
    if not m:
        return None
    n = float(m.group(1))
    return n * ROOT_PX if m.group(2) in ("rem", "em") else n


def size_range(v):
    """A token font size as (min, max) px; clamp() gives its bounds."""
    s = str(v)
    if s.startswith("clamp("):
        parts = [to_px(p) for p in s[6:-1].split(",")]
        ends = [p for p in (parts[0], parts[-1]) if p is not None]
        return (min(ends), max(ends)) if ends else None
    px = to_px(s)
    return (px, px) if px is not None else None


def rgb(c):
    """CSS colour -> (r, g, b) or None when the format is not comparable numerically."""
    c = str(c).strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3,8})", c)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h[:3])
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"rgba?\(([^)]+)\)", c)
    if m:
        p = [x for x in re.split(r"[\s,/]+", m.group(1)) if x]
        return tuple(round(float(x.rstrip("%")) * (2.55 if x.endswith("%") else 1)) for x in p[:3])
    m = re.fullmatch(r"hsla?\(([^)]+)\)", c)
    if m:
        p = [x for x in re.split(r"[\s,/]+", m.group(1)) if x]
        h, s, light = float(p[0].rstrip("deg")) / 360, float(p[1].rstrip("%")) / 100, float(p[2].rstrip("%")) / 100
        return tuple(round(x * 255) for x in colorsys.hls_to_rgb(h, light, s))
    return None


def alpha(c):
    m = re.fullmatch(r"rgba?\(([^)]+)\)", str(c).strip().lower())
    if m:
        p = [x for x in re.split(r"[\s,/]+", m.group(1)) if x]
        if len(p) > 3:
            return float(p[3].rstrip("%")) / (100 if p[3].endswith("%") else 1)
    return 1.0


def first_family(f):
    return str(f).split(",")[0].strip().strip("\"'").lower()


# ---------- the token system

class Tokens:
    def __init__(self, fm):
        self.colours = {k: v for k, v in (fm.get("colors") or {}).items() if isinstance(v, (str, int, float))}
        typo = fm.get("typography") or {}
        self.sizes = {k: size_range(r.get("fontSize")) for k, r in typo.items() if isinstance(r, dict) and r.get("fontSize")}
        self.weights = {str(r.get("fontWeight")) for r in typo.values() if isinstance(r, dict) and r.get("fontWeight")}
        self.families = {first_family(r.get("fontFamily")) for r in typo.values() if isinstance(r, dict) and r.get("fontFamily")}
        self.radii = {k: v for k, v in (fm.get("rounded") or {}).items()}
        self.spacing = {k: to_px(v) for k, v in (fm.get("spacing") or {}).items()}

    def colour_match(self, css):
        """Token name a computed colour belongs to (tints at reduced alpha count), else None."""
        c = rgb(css)
        for name, value in self.colours.items():
            t = rgb(value)
            if t is None:
                if str(value).strip().lower() == str(css).strip().lower():
                    return name
            elif c is not None and math.dist(c, t) <= COLOUR_TOLERANCE:
                return name if alpha(css) >= 0.99 else f"{name} at {round(alpha(css) * 100)}%"
        return None

    def nearest_colour(self, css):
        c = rgb(css)
        best = min(((math.dist(c, rgb(v)), k) for k, v in self.colours.items() if c and rgb(v)), default=None)
        return best[1] if best else "?"

    def size_ok(self, px):
        return any(lo - 0.5 <= px <= hi + 0.5 for lo, hi in filter(None, self.sizes.values()))

    def nearest_size(self, px):
        named = [(min(abs(px - lo), abs(px - hi)), k) for k, r in self.sizes.items() if r for lo, hi in [r]]
        return min(named)[1] if named else "?"

    def radius_ok(self, px):
        vals = [to_px(v) for v in self.radii.values()]
        return px >= 999 or any(v is not None and abs(px - v) <= 0.5 for v in vals)


def on(e):
    return f"{e['count']} element{'s' if e['count'] != 1 else ''} (\"{e['samples'][0]}\")"


def on_grid(px):
    return px <= 2 or abs(px / 4 - round(px / 4)) < 0.01


# ---------- checks

def check_tokens(tokens, budget):
    rows, findings = [], []
    sizes = sorted({r for r in tokens.sizes.values() if r})
    rows.append(("Font sizes in the system", budget["system_sizes"], len(sizes)))
    rows.append(("Weights in the system", budget["weights"], len(tokens.weights)))
    rows.append(("Families", budget["families"], len(tokens.families)))
    off = [f"{k} {v:g}px" for k, v in tokens.spacing.items() if v is not None and not on_grid(v)]
    rows.append(("Spacing tokens off the 4 grid", 0, len(off)))
    findings += [f"spacing token {o} is off the 4 grid; use the nearest multiple of 4" for o in off]
    unreadable = [k for k, v in tokens.colours.items() if rgb(v) is None]
    findings += [f"colour token {k} is not hex, rgb() or hsl(); drift.py compares it as text only" for k in unreadable]
    if not tokens.colours:
        findings.append("no colour tokens: drift.py cannot check the palette")
    return rows, findings


def check_screen(inv, tokens, budget):
    rows, findings = [], []
    sizes = [(to_px(e["value"]), e) for e in inv["type"]["sizes"]]
    rows.append(("Font sizes", budget["sizes"], len(sizes)))
    for px, e in sizes:
        if px is not None and tokens.sizes and not tokens.size_ok(px):
            findings.append(f"font size {px:g}px on {on(e)}: nearest token {tokens.nearest_size(px)}")
    weights = inv["type"]["weights"]
    rows.append(("Weights", budget["weights"], len(weights)))
    for e in weights:
        if tokens.weights and e["value"] not in tokens.weights:
            findings.append(f"weight {e['value']} on {on(e)}: not a token weight")
    fams = inv["type"]["families"]
    rows.append(("Families", budget["families"], len(fams)))
    for e in fams:
        if tokens.families and first_family(e["value"]) not in tokens.families:
            findings.append(f"family {e['value']} on {on(e)}: not a token family")

    off_grid = [e for e in inv["spacing"] if not on_grid(to_px(e["value"]) or 0)]
    rows.append(("Spacing values off the 4 grid", 0, len(off_grid)))
    for e in off_grid[:15]:
        findings.append(f"spacing {e['value']} on {on(e)}: snap to a multiple of 4")

    off_palette = 0
    for group in ("text", "background", "border"):
        for e in inv["colour"][group]:
            if tokens.colours and tokens.colour_match(e["value"]) is None:
                off_palette += 1
                findings.append(f"{group} colour {e['value']} on {on(e)}: nearest token {tokens.nearest_colour(e['value'])}")
    rows.append(("Colours off the palette", 0, off_palette))

    radii = inv["radius"]
    rows.append(("Radius values", budget["radii"], len(radii)))
    for e in radii:
        px = to_px(e["value"].split()[0])
        if px is not None and tokens.radii and not tokens.radius_ok(px):
            findings.append(f"radius {e['value']} on {on(e)}: not a rounded token")
    rows.append(("Shadow recipes", budget["shadows"], len(inv["shadow"])))
    return rows, findings


def share_table(inv, tokens):
    lines = ["| Background colour | Token | Share of area |", "|---|---|---|"]
    for e in inv["colour"]["areaShare"][:8]:
        name = e["colour"] if e["colour"] in ("media", "gradient") else (tokens.colour_match(e["colour"]) or "off palette")
        lines.append(f"| `{e['colour']}` | {name} | {e['share'] * 100:.0f}% |")
    return "\n".join(lines)


def table(title, rows):
    out = [f"### {title}", "", "| Metric | Budget | Found | Status |", "|---|---|---|---|"]
    over = False
    for metric, budget, found in rows:
        ok = found <= budget
        over |= not ok
        out.append(f"| {metric} | {budget} | {found} | {'ok' if ok else 'over'} |")
    return "\n".join(out), over


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("design", type=Path)
    ap.add_argument("inventories", type=Path, nargs="*")
    ap.add_argument("--platform", choices=BUDGETS, required=True)
    a = ap.parse_args()
    budget = BUDGETS[a.platform]
    tokens = Tokens(frontmatter(a.design.read_text()))

    failed = False
    rows, findings = check_tokens(tokens, budget)
    text, over = table(f"Tokens in {a.design.name} ({a.platform})", rows)
    print(text)
    failed |= over
    for f in findings:
        print(f"- {f}")
    for path in a.inventories:
        inv = json.loads(path.read_text())
        rows, findings = check_screen(inv, tokens, budget)
        text, over = table(f"{path.name}: {inv.get('url', '')} at {inv['viewport']['w']}px", rows)
        print("\n" + text + "\n")
        print(share_table(inv, tokens))
        failed |= over or bool(findings)
        if findings:
            print("\nFindings:")
            for f in findings:
                print(f"- {f}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
