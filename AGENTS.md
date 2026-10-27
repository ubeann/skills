# skills

Personal Claude Code skills. One skill per top-level folder: `<name>/SKILL.md` plus `<name>/references/`.

- Writing or editing a skill: follow the `writing-for-agents` skill. Steps end on a completion criterion; reference the agent needs only sometimes goes in `references/` behind a pointer in `SKILL.md`.
- The frontmatter `name` equals the folder name. The `description` is the trigger: lead with what the skill builds, then when to use it, then which bundled skill handles the neighbouring cases.
- `python3 scripts/check_skills.py` validates every skill. CI runs it on every push.
- `sh scripts/link.sh` symlinks each skill into `~/.claude/skills`. Run it after adding a skill.
- Prose and deck copy use no em dashes.
