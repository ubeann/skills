# skills

Personal Claude Code skills. One skill per top-level folder: `<name>/SKILL.md` plus `<name>/references/`.

- Writing or editing a skill: follow the `writing-for-agents` skill. Steps end on a completion criterion; reference the agent needs only sometimes goes in `references/` behind a pointer in `SKILL.md`.
- The frontmatter `name` equals the folder name. The `description` is the trigger: lead with what the skill builds, then when to use it, then which bundled skill handles the neighbouring cases.
- `python3 scripts/check_skills.py` validates every skill. CI runs it on every push.
- `python3 scripts/sync_profiles.py` symlinks each skill into every Claude profile (`~/.claude`, `~/.claude-*`), or into the checkout named by `project:` in its frontmatter via `projects.txt`, and syncs `profile/` (settings, plugins, MCP servers, rules). Run it from the main checkout after merging; `sh scripts/link.sh` does the skills step only.
- Shared Claude config belongs in `profile/`, never edited inside one profile. Secrets in `profile/mcp.json` are `${VAR}` references; the repo is public.
- A skill that depends on one repository's files (its templates, scripts, directories) gets `project: <name>` so it never triggers elsewhere.
- Prose and deck copy use no em dashes.
