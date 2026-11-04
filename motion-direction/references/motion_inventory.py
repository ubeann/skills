#!/usr/bin/env python3
"""List every piece of motion in a codebase and check it against the motion tokens.

    python3 motion_inventory.py <src-dir> [<src-dir> ...] [--tokens app.css] [--json out.json] [--strict]

Scans .css .scss .svelte .vue .astro .html .js .jsx .ts .tsx (skipping node_modules,
build output and test files) for:

  durations   CSS times on transition/animation/duration/delay lines, JS `duration:`/`delay:`,
              Tailwind `duration-*`/`delay-*` classes
  easings     cubic-bezier(), linear(), steps(), keyword easings, Tailwind `ease-*` classes
  token refs  var(--duration-*), var(--delay-*), var(--easing-*), var(--ease-*), var(--motion-*)
  libraries   imports of motion runtimes (gsap, motion, rive, lottie, svelte/motion, ...)
  flags       `transition: all`, ease-in on an entrance, layout properties in a transition,
              scale(0), files with JS-driven motion and no reduced-motion reference

With --tokens, every CSS custom property whose name contains duration, delay, stagger, easing, ease,
spring or motion becomes a token; a JS/TS token file (`{ panel: 220 }`) adds
millisecond durations. A literal equal to a token's value is an "unnamed token" (use the
token); any other literal is "off-scale". --strict exits 1 when an off-scale literal exists.
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXTS = {".css", ".scss", ".svelte", ".vue", ".astro", ".html", ".js", ".jsx", ".ts", ".tsx", ".mjs"}
SKIP_DIRS = {"node_modules", ".svelte-kit", "dist", "build", ".next", ".output", "coverage", ".git", ".turbo"}
TEST_RE = re.compile(r"\.(test|spec|stories)\.")

TOKEN_DEF = re.compile(r"--([\w-]*(?:duration|delay|stagger|easing|ease|spring|motion)[\w-]*)\s*:\s*([^;]+);")
TOKEN_REF = re.compile(r"var\(\s*--([\w-]*(?:duration|delay|stagger|easing|ease|spring|motion)[\w-]*)")
CSS_MOTION_LINE = re.compile(r"(transition|animation|duration|delay)", re.I)
CSS_TIME = re.compile(r"(?<![\w.-])(\d*\.?\d+)(ms|s)\b")
JS_TIME = re.compile(r"\b(duration|delay)\s*:\s*(\d*\.?\d+)\b")
TW_TIME = re.compile(r"(?<![\w-])(duration|delay)-(\d+)\b")
BEZIER = re.compile(r"cubic-bezier\([^)]*\)")
LINEAR_FN = re.compile(r"linear\([^)]{8,}\)")
STEPS = re.compile(r"steps\([^)]*\)")
KEYWORD_EASE = re.compile(r"(?<![\w-])(ease-in-out|ease-in|ease-out|ease)(?![\w-])")
TW_EASE = re.compile(r"(?<![\w-])ease-(linear|in|out|in-out)(?![\w-])")
SVELTE_EASE = re.compile(r"\b(linear|(?:back|bounce|circ|cubic|elastic|expo|quad|quart|quint|sine)(?:In|Out|InOut))\b")
KEYFRAMES = re.compile(r"@keyframes\s+([\w-]+)")
SVELTE_DIRECTIVE = re.compile(r"\b(transition|in|out|animate):[a-zA-Z]")
LIBS = {
    "gsap": re.compile(r"""from\s+['"]gsap"""),
    "motion": re.compile(r"""from\s+['"](motion|motion/[\w/-]+|framer-motion)['"]"""),
    "rive": re.compile(r"""from\s+['"]@rive-app/"""),
    "lottie": re.compile(r"""from\s+['"](lottie-web|lottie-react|@lottiefiles/[\w-]+)"""),
    "animejs": re.compile(r"""from\s+['"]animejs"""),
    "react-spring": re.compile(r"""from\s+['"]@react-spring/"""),
    "three": re.compile(r"""from\s+['"]three['"]"""),
    "svelte/transition": re.compile(r"""from\s+['"]svelte/transition"""),
    "svelte/animate": re.compile(r"""from\s+['"]svelte/animate"""),
    "svelte/motion": re.compile(r"""from\s+['"]svelte/motion"""),
    "view-transitions": re.compile(r"startViewTransition|onNavigate\("),
    "waapi": re.compile(r"\.animate\(\s*[\[{]"),
}
JS_MOTION_LIBS = {"gsap", "motion", "rive", "lottie", "animejs", "react-spring", "svelte/transition", "svelte/animate", "svelte/motion", "waapi"}
REDUCED = re.compile(r"prefers-reduced-motion|prefersReducedMotion|useReducedMotion|reducedMotion", re.I)
FLAG_RULES = [
    ("transition-all", re.compile(r"transition\s*:\s*all\b|(?<![\w-])transition-all(?![\w-])")),
    ("layout-property", re.compile(r"transition(-property)?\s*:[^;]*\b(width|height|top|left|right|bottom|margin|padding)\b")),
    ("scale-zero", re.compile(r"scale\(\s*0\s*\)")),
]


def to_ms(value, unit):
    v = float(value)
    return round(v * 1000) if unit == "s" else round(v)


def norm(s):
    return re.sub(r"\s+", "", s.strip().lower())


def load_tokens(paths):
    durations, easings = {}, {}
    for p in paths:
        text = Path(p).read_text(errors="ignore")
        if Path(p).suffix not in {".css", ".scss"}:
            # A JS/TS mirror such as `export const duration = { panel: 220 }`: numbers are ms.
            for name, value in re.findall(r"\b(\w+)\s*:\s*(\d+)\b", text):
                durations.setdefault(int(value), name)
            continue
        for name, value in TOKEN_DEF.findall(text):
            value = value.strip()
            t = CSS_TIME.fullmatch(value)
            if t:
                durations[to_ms(*t.groups())] = name
            elif not value.startswith("var("):
                easings[norm(value)] = name
    return durations, easings


def walk(roots):
    for root in roots:
        root = Path(root)
        files = [root] if root.is_file() else root.rglob("*")
        for f in files:
            if f.is_file() and f.suffix in EXTS and not TEST_RE.search(f.name) and not (set(f.parts) & SKIP_DIRS):
                yield f


def scan(roots, token_files):
    tok_dur, tok_ease = load_tokens(token_files)
    token_paths = {Path(t).resolve() for t in token_files}
    rows = {"durations": [], "easings": [], "token_refs": Counter(), "keyframes": [], "libraries": defaultdict(list), "flags": []}
    files_with_motion = set()
    js_motion_files, reduced_files = set(), set()

    for f in walk(roots):
        is_token_file = f.resolve() in token_paths
        is_css = f.suffix in {".css", ".scss"}
        text = f.read_text(errors="ignore")
        if REDUCED.search(text):
            reduced_files.add(str(f))
        for lib, rx in LIBS.items():
            if rx.search(text):
                rows["libraries"][lib].append(str(f))
                files_with_motion.add(str(f))
                if lib in JS_MOTION_LIBS:
                    js_motion_files.add(str(f))
        if f.suffix == ".svelte" and SVELTE_DIRECTIVE.search(text):
            js_motion_files.add(str(f))
            files_with_motion.add(str(f))
        cont = False
        for n, raw in enumerate(text.splitlines(), 1):
            where = f"{f}:{n}"
            line = re.sub(r"/\*.*?\*/", "", raw)
            if re.match(r"\s*(\*|//|/\*)", line):
                continue
            in_decl = cont
            if re.search(r"(transition|animation)\s*:", line):
                in_decl = True
            cont = in_decl and ";" not in line and not line.rstrip().endswith(("{", "}"))
            for name in TOKEN_REF.findall(line):
                rows["token_refs"][name] += 1
                files_with_motion.add(str(f))
            for k in KEYFRAMES.findall(line):
                rows["keyframes"].append({"name": k, "at": where})
                files_with_motion.add(str(f))
            if is_token_file and TOKEN_DEF.search(line):
                continue
            stripped = re.sub(r"var\([^)]*\)", "", line)
            found = []
            if in_decl or (CSS_MOTION_LINE.search(stripped) and (is_css or "style" in stripped or ":" in stripped)):
                found += [to_ms(v, u) for v, u in CSS_TIME.findall(stripped)]
            if not is_css and not in_decl:
                found += [round(float(v)) for _, v in JS_TIME.findall(stripped)]
                found += [int(v) for _, v in TW_TIME.findall(stripped)]
            for ms in (m for m in found if m > 1):  # 0.01ms is the reduced-motion idiom
                rows["durations"].append({"ms": ms, "at": where, "token": tok_dur.get(ms)})
                files_with_motion.add(str(f))
            eases = BEZIER.findall(stripped) + LINEAR_FN.findall(stripped) + STEPS.findall(stripped)
            if in_decl or (is_css and CSS_MOTION_LINE.search(stripped)) or re.search(r"(easing|ease)\s*[:=]", stripped):
                eases += KEYWORD_EASE.findall(stripped)
            if not is_css and not in_decl:
                eases += ["tw:ease-" + e for e in TW_EASE.findall(stripped)]
                if "svelte/easing" in text:
                    eases += SVELTE_EASE.findall(stripped)
            for e in eases:
                rows["easings"].append({"value": e, "at": where, "token": tok_ease.get(norm(e))})
                files_with_motion.add(str(f))
            for flag, rx in FLAG_RULES:
                if rx.search(line):
                    rows["flags"].append({"flag": flag, "at": where, "line": line.strip()[:120]})
            if re.search(r"(animation|transition)[^;]*(?<![\w-])ease-in(?![\w-])", line):
                rows["flags"].append({"flag": "ease-in", "at": where, "line": line.strip()[:120]})

    for f in sorted(js_motion_files - reduced_files):
        rows["flags"].append({"flag": "no-reduced-motion-ref", "at": f, "line": "JS-driven motion with no reduced-motion reference in this file (fine if a shared helper gates it)"})
    rows["files_with_motion"] = sorted(files_with_motion)
    rows["tokens"] = {"durations": {str(k): v for k, v in sorted(tok_dur.items())}, "easings": tok_ease}
    return rows


def report(rows, has_tokens):
    durs, eases = rows["durations"], rows["easings"]
    off_d = [d for d in durs if not d["token"]]
    named_d = [d for d in durs if d["token"]]
    off_e = [e for e in eases if not e["token"]]
    named_e = [e for e in eases if e["token"]]
    print("| Metric | Count |\n|---|---|")
    print(f"| Files with motion | {len(rows['files_with_motion'])} |")
    print(f"| Token references | {sum(rows['token_refs'].values())} ({len(rows['token_refs'])} distinct) |")
    print(f"| Literal durations | {len(durs)} ({len({d['ms'] for d in durs})} distinct) |")
    print(f"| Literal easings | {len(eases)} ({len({e['value'] for e in eases})} distinct) |")
    print(f"| @keyframes | {len(rows['keyframes'])} |")
    if has_tokens:
        print(f"| Literals equal to a token (unnamed) | {len(named_d) + len(named_e)} |")
        print(f"| Off-scale literals | {len(off_d) + len(off_e)} |")
    print(f"| Flags | {len(rows['flags'])} |")
    if rows["libraries"]:
        print("\nLibraries: " + ", ".join(f"{k} ({len(v)} files)" for k, v in sorted(rows["libraries"].items())))
    if durs:
        c = Counter(d["ms"] for d in durs)
        print("\nDurations (ms: uses): " + ", ".join(f"{k}: {v}" for k, v in sorted(c.items())))
    if eases:
        c = Counter(e["value"] for e in eases)
        print("Easings (value: uses): " + "; ".join(f"{k}: {v}" for k, v in c.most_common()))
    if has_tokens and (named_d or named_e):
        print("\nUnnamed tokens (swap the literal for the token):")
        for d in named_d:
            print(f"- {d['at']}  {d['ms']}ms -> var(--{d['token']})")
        for e in named_e:
            print(f"- {e['at']}  {e['value']} -> var(--{e['token']})")
    if has_tokens and (off_d or off_e):
        print("\nOff-scale literals (snap to the nearest token, or promote with a reason):")
        for d in off_d:
            print(f"- {d['at']}  {d['ms']}ms")
        for e in off_e:
            print(f"- {e['at']}  {e['value']}")
    if rows["flags"]:
        print("\nFlags:")
        for fl in rows["flags"]:
            print(f"- {fl['flag']}  {fl['at']}  {fl['line']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("roots", nargs="+")
    ap.add_argument("--tokens", action="append", default=[], help="CSS file defining the motion tokens (repeatable)")
    ap.add_argument("--json", help="write the full inventory as JSON")
    ap.add_argument("--strict", action="store_true", help="exit 1 when an off-scale literal exists")
    a = ap.parse_args()
    rows = scan(a.roots, a.tokens)
    report(rows, bool(a.tokens))
    if a.json:
        out = dict(rows, libraries=dict(rows["libraries"]), token_refs=dict(rows["token_refs"]))
        Path(a.json).write_text(json.dumps(out, indent=2))
    off = [d for d in rows["durations"] if not d["token"]] + [e for e in rows["easings"] if not e["token"]]
    sys.exit(1 if a.strict and a.tokens and off else 0)


if __name__ == "__main__":
    main()
