#!/usr/bin/env python3
"""Validate every <name>/SKILL.md: frontmatter name matches the folder,
description is present, and every references/ path mentioned exists."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []
skills = sorted(p for p in ROOT.glob("*/SKILL.md"))
if not skills:
    errors.append("no skills found")
for skill in skills:
    folder = skill.parent
    text = skill.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{folder.name}: missing frontmatter")
        continue
    front = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    front = {k.strip(): v.strip() for k, v in front.items()}
    if front.get("name") != folder.name:
        errors.append(f"{folder.name}: name is {front.get('name')!r}, want {folder.name!r}")
    if not front.get("description"):
        errors.append(f"{folder.name}: empty description")
    for ref in set(re.findall(r"references/[\w./-]+", text)):
        if not (folder / ref).exists():
            errors.append(f"{folder.name}: {ref} does not exist")
    for ref in (folder / "references").glob("*") if (folder / "references").is_dir() else []:
        if f"references/{ref.name}" not in text:
            errors.append(f"{folder.name}: references/{ref.name} is never pointed at")

for e in errors:
    print(e)
print(f"{len(skills)} skills, {len(errors)} errors")
sys.exit(1 if errors else 0)
