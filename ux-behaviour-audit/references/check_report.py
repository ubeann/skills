#!/usr/bin/env python3
"""Check a filled report.html before it is previewed.

    python3 check_report.py report.html

Errors (exit 1): placeholders left, a template section missing, a screen with no image or file,
counts that disagree (screens, matrix rows, next-level rows, the findings tile, the severity key),
a finding missing a field, a precedent id that is not in case-studies.md, findings out of severity
order, an image path that does not exist, a case row with no pass or fail, and no word on persuasion.
Warnings: the matrix total differs from the findings count, or most precedents are "none".
Standard library only.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SEVERITIES = ["blocker", "friction", "doubt", "polish"]
FILE_LINE = re.compile(r"[\w./-]+\.\w+:\d+")
VOID = {"img", "br", "hr", "meta", "link", "input", "source", "wbr"}


class Node:
    def __init__(self, tag, attrs, parent=None):
        self.tag, self.attrs, self.parent, self.children, self.text = tag, dict(attrs), parent, [], ""

    @property
    def classes(self):
        return set((self.attrs.get("class") or "").split())

    def walk(self):
        for c in self.children:
            yield c
            yield from c.walk()

    def find(self, tag=None, cls=None):
        return [n for n in self.walk() if (tag is None or n.tag == tag) and (cls is None or cls in n.classes)]

    def all_text(self):
        return (self.text + " ".join(c.all_text() for c in self.children)).strip()


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = self.cur = Node("root", {})

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.text += data


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    html = path.read_text()
    body = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    body = re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S)
    tree = Tree()
    tree.feed(body)
    root = tree.root
    errors, warnings = [], []
    cases_file = Path(__file__).with_name("case-studies.md")
    known_ids = set(re.findall(r"^### (CS\d+)", cases_file.read_text(), re.M)) if cases_file.exists() else set()

    left = sorted(set(re.findall(r"\{\{[^}]*\}\}", body)))
    if left:
        errors.append(f"{len(left)} placeholders left, e.g. {', '.join(left[:3])}")

    h2s = {n.all_text() for n in root.find("h2")}
    for label, ok in [
        ("title (h1)", root.find("h1")),
        ("frame line (.frame)", root.find(cls="frame")),
        ("screen strip (.strip)", root.find(cls="strip")),
        ("findings section", any(t.startswith("Findings") for t in h2s)),
        ("lens matrix (table.mx)", root.find("table", "mx")),
        ("next-level list (ul.next)", root.find("ul", "next")),
        ("not-checked note (p.note)", root.find("p", "note")),
    ]:
        if not ok:
            errors.append(f"missing {label}")

    shots = root.find(cls="shot")
    for i, s in enumerate(shots, 1):
        imgs = s.find("img")
        if not imgs and not s.find("code") and not s.find(cls="code") and not FILE_LINE.search(s.all_text()):
            errors.append(f"screen {i} has no image and no file:line")
        for img in imgs:
            src = img.attrs.get("src", "")
            if src.startswith("/") and not Path(src).exists():
                errors.append(f"screen {i}: image {src} does not exist")

    rows = [r for r in root.find("tr") if r.find("td", "t")]
    nexts = [li for ul in root.find("ul", "next") for li in ul.find("li")]
    if shots and len(rows) != len(shots):
        errors.append(f"{len(shots)} screens but {len(rows)} matrix rows")
    if shots and len(nexts) != len(shots):
        errors.append(f"{len(shots)} screens but {len(nexts)} next-level rows")

    findings = root.find("article", "f")
    sevs, nones = [], 0
    for i, f in enumerate(findings, 1):
        sev = next((s for s in SEVERITIES if f"sev-{s}" in f.classes), None)
        if not sev:
            errors.append(f"finding {i} has no sev-blocker/friction/doubt/polish class")
        sevs.append(sev)
        if not any(re.fullmatch(r"lens-[DSATCO]", c) for c in f.classes):
            errors.append(f"finding {i} has no lens class")
        fields = {}
        dts = f.find("dt")
        dds = f.find("dd")
        for dt, dd in zip(dts, dds):
            fields[dt.all_text().lower()] = dd
        for name in ("evidence", "fix", "precedent", "watch"):
            if name not in fields or not fields[name].all_text():
                errors.append(f"finding {i} has no {name}")
        prec = fields.get("precedent")
        if prec is not None:
            text = prec.all_text()
            ids = re.findall(r"\bCS\d+\b", text)
            for cid in ids:
                if known_ids and cid not in known_ids:
                    errors.append(f"finding {i}: precedent {cid} is not in case-studies.md")
            links = [a.attrs.get("href", "") for a in prec.find("a")]
            if text.strip().lower().strip('"').startswith("none"):
                nones += 1
            elif not any(h.startswith("http") for h in links):
                errors.append(f"finding {i}: precedent needs a link (the case's video or PR, or the peer product's page) or \"none\"")
    order = [SEVERITIES.index(s) for s in sevs if s]
    if order != sorted(order):
        errors.append("findings are not ordered blocker, friction, doubt, polish")
    if findings and nones * 2 > len(findings):
        warnings.append(f"{nones} of {len(findings)} precedents are \"none\": look again for a case or a peer product")

    for tile in root.find(cls="tile"):
        if "findings" in tile.all_text().lower():
            m = re.search(r"\d+", tile.all_text())
            if m and int(m.group()) != len(findings):
                errors.append(f"the findings tile says {m.group()} but there are {len(findings)} findings")
    for key in root.find(cls="sevkey"):
        for span in key.find("span"):
            m = re.match(r"\s*(\d+)\s+(\w+)", span.all_text())
            if m and m.group(2) in SEVERITIES and int(m.group(1)) != sevs.count(m.group(2)):
                errors.append(f"the severity key says {m.group(1)} {m.group(2)} but there are {sevs.count(m.group(2))}")

    total = 0
    for r in rows:
        for td in r.find("td"):
            if "t" not in td.classes and td.all_text().isdigit():
                total += int(td.all_text())
    if findings and total != len(findings):
        warnings.append(f"the matrix counts {total} failures but there are {len(findings)} findings")

    for table in root.find("table", "cases"):
        for i, tr in enumerate(table.find("tr"), 1):
            tds = tr.find("td")
            if tds and tds[-1].all_text().lower() not in ("pass", "fail"):
                errors.append(f"case row {i} has no pass or fail")

    note = " ".join(n.all_text() for n in root.find("p", "note")).lower()
    if not root.find("section", "flags") and "persuasion" not in note:
        errors.append("no flags section and the note says nothing about persuasion")

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"{len(shots)} screens, {len(findings)} findings, {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
