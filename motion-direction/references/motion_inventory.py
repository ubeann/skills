#!/usr/bin/env python3
"""List every piece of motion in a codebase and check it against the motion tokens.

    python3 motion_inventory.py <src-dir> [<src-dir> ...] [--tokens app.css] [--json out.json] [--strict]
    python3 motion_inventory.py Sources --tokens Sources/App/Design.swift [--guard 'Motion\.reduced']

Scans .css .scss .svelte .vue .astro .html .js .jsx .ts .tsx and .swift (skipping node_modules,
build output and test files) for:

  durations   CSS times on transition/animation/duration/delay lines, JS `duration:`/`delay:`,
              Tailwind `duration-*`/`delay-*` classes
  easings     cubic-bezier(), linear(), steps(), keyword easings, Tailwind `ease-*` classes
  token refs  var(--duration-*), var(--delay-*), var(--easing-*), var(--ease-*), var(--motion-*)
  libraries   imports of motion runtimes (gsap, motion, rive, lottie, svelte/motion, ...)
  flags       `transition: all`, ease-in on an entrance, layout properties in a transition,
              scale(0), files with JS-driven motion and no reduced-motion reference

Swift (SwiftUI, AppKit, UIKit, Core Animation): durations from `duration:`, `response:`,
`.duration =`, `withDuration:`, `setAnimationDuration(` and `.delay(` (seconds, every branch of a
ternary), easings from `.easeOut(`, `.spring(...)`, `.smooth`, `CAMediaTimingFunction`, and so on.
A Swift --tokens file makes each `static var/let/func` of its types a token: `Motion.glide`
counts as a token reference, and a literal equal to a value defined under a token is unnamed.
Swift flags: `unguarded-literal` (a literal animation with no reduced-motion check on that line or
the 12 above; add the project's own check with --guard) and `forever-loop` (`repeatForever`, an
infinite `repeatCount`), which must stop under reduced motion and off screen.

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

EXTS = {".css", ".scss", ".svelte", ".vue", ".astro", ".html", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".swift"}
SKIP_DIRS = {"node_modules", ".svelte-kit", "dist", "build", ".next", ".output", "coverage", ".git", ".turbo", ".build", "DerivedData", "Pods", "Tests"}
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
REDUCED = re.compile(r"prefers-reduced-motion|prefersReducedMotion|useReducedMotion|reducedMotion|reduceMotion", re.I)

# Swift
SW_TIME = re.compile(r"(?:\bduration|\bresponse|withDuration|\.delay)\s*[:=(]\s*([^,)\n{]+)|setAnimationDuration\(([^)]*)\)")
SW_NUM = re.compile(r"(?<![\w.])(\d*\.?\d+)(?![\w.])")
SW_CURVE = re.compile(r"\.(easeInOut|easeIn|easeOut|linear)\b(\([^)]*\))?(?=\s*(?:$|[,)\s.{]))")
SW_SPRING = re.compile(r"\.(spring|interactiveSpring|interpolatingSpring|smooth|snappy|bouncy)\b(\([^)]*\))?")
SW_CA = re.compile(r"CAMediaTimingFunction\(\s*(?:name:\s*\.(\w+)|controlPoints:[^)]*)\)")
SW_ANIM = re.compile(r"withAnimation|\.animation\(|Animation\b|animator\(\)|timingFunction|NSAnimationContext|CATransaction|transaction|\.duration\s*=|withDuration")
SW_GUARD = re.compile(r"reduce[d]?\s*motion|accessibilityDisplayShouldReduceMotion|isReduceMotionEnabled|\breduced\b", re.I)
SW_FOREVER = re.compile(r"repeatForever|repeatCount\s*=\s*(?:\.infinity|Float\.infinity|\.greatestFiniteMagnitude)")
SW_TYPE = re.compile(r"\b(?:enum|struct|class|extension)\s+(\w+)")
SW_STATIC = re.compile(r"\bstatic\s+(?:let|var|func)\s+(\w+)")
LIBS_SWIFT = {
    "lottie-ios": re.compile(r"^\s*import\s+Lottie\b", re.M),
    "rive-ios": re.compile(r"^\s*import\s+RiveRuntime\b", re.M),
}
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


def swift_time_values(line):
    out = []
    for m in SW_TIME.finditer(line):
        expr = m.group(1) or m.group(2) or ""
        out += [round(float(v) * 1000) for v in SW_NUM.findall(expr)]
    return [ms for ms in out if ms > 1]


def swift_easings(line):
    out = ["." + m.group(1) + re.sub(r"\s+", "", m.group(2) or "") for m in SW_CURVE.finditer(line)]
    for m in SW_SPRING.finditer(line):
        args = re.sub(r"\s+", "", m.group(2) or "")
        out.append("." + m.group(1) + args)
    out += ["CA:" + (m.group(1) or "controlPoints") for m in SW_CA.finditer(line)]
    return out


def load_swift_tokens(text, durations, easings, refs):
    """Each static member of a type in the token file is a token; literals under it are its values."""
    current_type, current, members, timed = None, None, set(), set()
    for line in text.splitlines():
        t = SW_TYPE.search(line)
        if t and not line.lstrip().startswith("//"):
            current_type = t.group(1)
        s = SW_STATIC.search(line)
        if s and current_type:
            current = f"{current_type}.{s.group(1)}"
            members.add(current)
        if current and not line.lstrip().startswith("//"):
            values = swift_time_values(line) + swift_easings(line)
            if values:
                timed.add(current.split(".")[0])
            for ms in swift_time_values(line):
                durations.setdefault(ms, current)
            for e in swift_easings(line):
                easings.setdefault(norm(e), current)
    # Only the types that define timing (Motion, not Palette) count as motion tokens.
    refs.update(m for m in members if m.split(".")[0] in timed)


def load_tokens(paths, swift_refs=None):
    durations, easings = {}, {}
    for p in paths:
        text = Path(p).read_text(errors="ignore")
        if Path(p).suffix == ".swift":
            load_swift_tokens(text, durations, easings, swift_refs if swift_refs is not None else set())
            continue
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


def scan_swift(f, text, rows, tok_dur, tok_ease, swift_refs, guard, files_with_motion):
    lines = text.splitlines()
    for lib, rx in LIBS_SWIFT.items():
        if rx.search(text):
            rows["libraries"][lib].append(str(f))
            files_with_motion.add(str(f))
    for n, raw in enumerate(lines, 1):
        line = raw.split("//")[0]
        if not line.strip():
            continue
        where = f"{f}:{n}"
        for ref in re.findall(r"\b([A-Z]\w*\.\w+)", line):
            if ref in swift_refs:
                rows["token_refs"][ref] += 1
                files_with_motion.add(str(f))
        anim = bool(SW_ANIM.search(line)) or bool(SW_CURVE.search(line) or SW_SPRING.search(line))
        durs = swift_time_values(line) if anim or SW_TIME.search(line) and re.search(r"\.duration\s*=|withDuration|setAnimationDuration|duration:", line) else []
        eases = swift_easings(line) if anim else []
        for ms in durs:
            rows["durations"].append({"ms": ms, "at": where, "token": tok_dur.get(ms)})
        for e in eases:
            rows["easings"].append({"value": e, "at": where, "token": tok_ease.get(norm(e))})
        if durs or eases:
            files_with_motion.add(str(f))
            window = "\n".join(lines[max(0, n - 13):n])
            if not (SW_GUARD.search(window) or (guard and guard.search(window))):
                rows["flags"].append({"flag": "unguarded-literal", "at": where, "line": raw.strip()[:120] + "  (fine if the value it drives checks reduced motion where it is read)"})
        if SW_FOREVER.search(line):
            rows["flags"].append({"flag": "forever-loop", "at": where, "line": raw.strip()[:120]})


def scan(roots, token_files, guard=None):
    swift_refs = set()
    tok_dur, tok_ease = load_tokens(token_files, swift_refs)
    token_paths = {Path(t).resolve() for t in token_files}
    rows = {"durations": [], "easings": [], "token_refs": Counter(), "keyframes": [], "libraries": defaultdict(list), "flags": []}
    files_with_motion = set()
    js_motion_files, reduced_files = set(), set()

    for f in walk(roots):
        is_token_file = f.resolve() in token_paths
        is_css = f.suffix in {".css", ".scss"}
        text = f.read_text(errors="ignore")
        if f.suffix == ".swift":
            if not is_token_file:
                scan_swift(f, text, rows, tok_dur, tok_ease, swift_refs, guard, files_with_motion)
            continue
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


def ref(token):
    return token if "." in token else f"var(--{token})"


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
            print(f"- {d['at']}  {d['ms']}ms -> {ref(d['token'])}")
        for e in named_e:
            print(f"- {e['at']}  {e['value']} -> {ref(e['token'])}")
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
    ap.add_argument("--guard", help="regex for the project's own reduced-motion check, e.g. 'Motion\\.reduced'")
    a = ap.parse_args()
    rows = scan(a.roots, a.tokens, re.compile(a.guard) if a.guard else None)
    report(rows, bool(a.tokens))
    if a.json:
        out = dict(rows, libraries=dict(rows["libraries"]), token_refs=dict(rows["token_refs"]))
        Path(a.json).write_text(json.dumps(out, indent=2))
    off = [d for d in rows["durations"] if not d["token"]] + [e for e in rows["easings"] if not e["token"]]
    sys.exit(1 if a.strict and a.tokens and off else 0)


if __name__ == "__main__":
    main()
