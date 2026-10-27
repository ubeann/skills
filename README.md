<!-- mascot goes here once the reference is chosen: assets/icon-512.png, width 160 -->

# skills

My personal Claude Code skills: workflows distilled from real projects, written for the agent rather than for me. Each skill is one folder with a `SKILL.md` and the reference files it points at.

Skills are symlinked into `~/.claude/skills/` so Claude Code picks them up in every project. Written with Claude in [T3 Code](https://t3.gg).

## Skills

| Skill | Use it for |
|---|---|
| [html-pdf-report](html-pdf-report/SKILL.md) | Data-driven PDF reports and decks: JSON from a slow pass, fixed-size HTML pages, headless Chrome, an overflow gate, read-only review, commit per page. |

## Layout

```
<name>/SKILL.md           the skill: frontmatter, steps with completion criteria
<name>/references/        files the skill points at, loaded only when needed
scripts/check_skills.py   validates frontmatter and reference links
scripts/link.sh           symlinks every skill into ~/.claude/skills
assets/                   mascot, when it exists
AGENTS.md                 pointers for any coding agent working here
```

## Workflow

1. Finish a piece of work somewhere, run a retro, and keep what was portable.
2. Open the **skills** project in T3 Code and ask for a skill from the retro. The `writing-for-agents` skill sets the house style: steps end on a checkable criterion, reference lives behind pointers.
3. Run the checker, run `scripts/link.sh`, commit.

## Commands

```sh
python3 scripts/check_skills.py   # validate every skill
sh scripts/link.sh                # symlink skills into ~/.claude/skills
```
