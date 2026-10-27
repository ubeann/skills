#!/bin/sh
# Symlink every skill folder into ~/.claude/skills so Claude Code loads it.
set -e
cd "$(dirname "$0")/.."
mkdir -p "$HOME/.claude/skills"
for skill in */SKILL.md; do
  name=$(dirname "$skill")
  ln -sfn "$PWD/$name" "$HOME/.claude/skills/$name"
  echo "linked $name"
done
