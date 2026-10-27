#!/bin/sh
# Symlink every skill folder so Claude Code loads it.
# Skills without `project:` in their frontmatter go to ~/.claude/skills (global).
# Skills with `project: <name>` go to <checkout>/.claude/skills, where <checkout>
# comes from projects.txt, so they only trigger inside that repository.
set -e
cd "$(dirname "$0")/.."
mkdir -p "$HOME/.claude/skills"
for skill in */SKILL.md; do
  name=$(dirname "$skill")
  project=$(sed -n '2,/^---$/{s/^project:[[:space:]]*//p;}' "$skill")
  if [ -z "$project" ]; then
    ln -sfn "$PWD/$name" "$HOME/.claude/skills/$name"
    echo "linked $name -> ~/.claude/skills"
    continue
  fi
  checkout=$(awk -v p="$project" '$1==p {print $2}' projects.txt)
  if [ -z "$checkout" ] || [ ! -d "$checkout" ]; then
    echo "skip $name: project '$project' has no checkout in projects.txt" >&2
    continue
  fi
  mkdir -p "$checkout/.claude/skills"
  ln -sfn "$PWD/$name" "$checkout/.claude/skills/$name"
  echo "linked $name -> $checkout/.claude/skills"
done
