<p align="center"><img src="assets/icon-512.png" alt="skills mascot: toolbox" width="160"></p>

# skills

My personal Claude Code skills: workflows distilled from real projects, written for the agent rather than for me. Each skill is one folder with a `SKILL.md` and the reference files it points at.

Global skills are symlinked into every Claude profile (`~/.claude` and each `~/.claude-*` dir that T3 Code launches through `CLAUDE_CONFIG_DIR`) so Claude Code picks them up in every project. A skill with `project: <name>` in its frontmatter is symlinked into that repository's `.claude/skills/` instead, so it only triggers there; `projects.txt` maps the name to the checkout.

The rest of the shared setup lives in `profile/` and is synced the same way: plugins and their marketplaces, user MCP servers, hooks and permissions, and files like rules. Change it here, not in a profile, or the next sync puts it back. Written with Claude in [T3 Code](https://t3.gg).

## Skills

| Skill | Use it for |
|---|---|
| [html-pdf-report](html-pdf-report/SKILL.md) | Data-driven PDF reports and decks: JSON from a slow pass, fixed-size HTML pages, headless Chrome, an overflow gate, read-only review, commit per page. |
| [learn](learn/SKILL.md) | Answer a learning question from verified sources and file it as a note. Scoped to the [study](https://github.com/ubeann/study) repo. |
| [video-context](video-context/SKILL.md) | Turn a video URL or file into a bundle an agent can read: post text, captions or whisper transcript, deduplicated frames, and a timestamped summary. |
| [ux-behaviour-audit](ux-behaviour-audit/SKILL.md) | Audit a UI by how users behave on it: walk one task, six behaviour lenses, a junior-to-staff ladder, persuasion flags, case studies with video timestamps, a report rendered in chat. |

## Layout

```
<name>/SKILL.md           the skill: frontmatter, steps with completion criteria
<name>/references/        files the skill points at, loaded only when needed
scripts/check_skills.py   validates frontmatter and reference links
scripts/sync_profiles.py  syncs skills and profile/ into every Claude profile
scripts/link.sh           the skills step only
projects.txt              project name -> checkout path for project-scoped skills
profile/settings.json     keys merged into each profile's settings.json: plugins, marketplaces, hooks, permissions
profile/mcp.json          user-scope MCP servers; write secrets as ${VAR}, read from the env at sync time
profile/home/             files symlinked into each profile at the same path (rules/, CLAUDE.md, agents/)
assets/                   mascot, when it exists
AGENTS.md                 pointers for any coding agent working here
```

## Workflow

1. Finish a piece of work somewhere, run a retro, and keep what was portable.
2. Open the **skills** project in T3 Code and ask for a skill from the retro. The `writing-for-agents` skill sets the house style: steps end on a checkable criterion, reference lives behind pointers.
3. Run the checker, commit, merge, then run `scripts/sync_profiles.py` (it always links from the main checkout, so a worktree being deleted never leaves dangling links).

## Commands

```sh
python3 scripts/check_skills.py   # validate every skill
python3 scripts/sync_profiles.py  # sync every profile: plugins, mcp, settings, skills, files
python3 scripts/sync_profiles.py --dry-run --only settings   # preview one step
sh scripts/link.sh                # skills only
```

## Profile sync

- Profiles are `~/.claude` plus every `~/.claude-*` dir; set `CLAUDE_PROFILES=dir:dir` to choose others.
- Settings are merged, not replaced: shared keys win, list entries (hooks, permission rules) are added to the profile's own, and keys only the profile has (its `theme`, a plugin installed with `/plugin`) stay.
- What a sync adds is recorded in `<profile>/.skills-sync.json`; drop an entry from `profile/` and the next sync removes it everywhere. Dropping a plugin only removes it from `enabledPlugins`; it stays installed until `claude plugin uninstall` in that profile.
- MCP servers and plugins go through the `claude` CLI, never by editing `.claude.json`, which also holds the profile's login. OAuth MCP servers still need signing in once per profile.
- The shared `SessionStart` hook runs `sync-claude-profiles --current` in whichever profile starts, so a profile picks up changes on its next session. The first run installs `~/.local/bin/sync-claude-profiles` and should be done by hand, since adding marketplaces clones them.
- This repo is public: keep tokens out of `profile/`.
