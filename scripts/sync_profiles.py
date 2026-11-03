#!/usr/bin/env python3
"""Sync the shared Claude Code setup in this repo into every Claude profile.

A profile is a Claude config dir: ~/.claude (the default) and every ~/.claude-*
dir, which T3 Code launches through CLAUDE_CONFIG_DIR. Each run does five steps:

  plugins   add the marketplaces in profile/settings.json, install its enabled plugins
  mcp       add the servers in profile/mcp.json at user scope (`${VAR}` reads the env)
  settings  merge profile/settings.json into <profile>/settings.json
  skills    symlink global skills into <profile>/skills, project skills into
            the checkout projects.txt names
  files     symlink everything under profile/home/ into the same path in <profile>

What a run adds is recorded in <profile>/.skills-sync.json, so removing an entry
from the repo removes it from every profile on the next run. Anything a profile
has that the repo does not (a plugin installed with /plugin, its theme) is left
alone. Sources come from the main checkout, never a linked worktree, so links
survive the worktree being deleted.

  python3 scripts/sync_profiles.py              # every profile
  python3 scripts/sync_profiles.py --current    # the profile running this (the SessionStart hook)
  python3 scripts/sync_profiles.py --only skills --dry-run
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
DEFAULT_PROFILE = HOME / ".claude"
STATE_FILE = ".skills-sync.json"
STEPS = ["plugins", "mcp", "settings", "skills", "files"]
BUILTIN_MARKETPLACES = {"claude-plugins-official"}
BIN_LINK = HOME / ".local/bin/sync-claude-profiles"

args = None
warnings = 0


def say(profile, msg):
    if not args.quiet:
        print(f"{profile.name}: {msg}")


def warn(profile, msg):
    global warnings
    warnings += 1
    print(f"{profile.name if profile else 'sync'}: warning: {msg}", file=sys.stderr)


def main_checkout():
    here = Path(os.path.realpath(__file__)).parent
    try:
        out = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out).parent
    except (subprocess.CalledProcessError, FileNotFoundError):
        return here.parent


def discover_profiles():
    if os.environ.get("CLAUDE_PROFILES"):
        return [Path(p).expanduser() for p in os.environ["CLAUDE_PROFILES"].split(":") if p]
    found = [DEFAULT_PROFILE] if DEFAULT_PROFILE.is_dir() else []
    found += sorted(p for p in HOME.glob(".claude-*") if p.is_dir())
    return found


def current_profile():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or DEFAULT_PROFILE).expanduser()


def is_default(profile):
    return profile.resolve() == DEFAULT_PROFILE.resolve()


def read_json(path, default):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return default


def write_json(path, data):
    tmp = path.with_name(f".{path.name}.sync-tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    os.replace(tmp, path)


def claude(profile, *cli):
    """Run the claude CLI against one profile. Returns True on success."""
    if args.dry_run:
        say(profile, "would run: claude " + " ".join(cli))
        return False
    env = dict(os.environ)
    if is_default(profile):
        env.pop("CLAUDE_CONFIG_DIR", None)
    else:
        env["CLAUDE_CONFIG_DIR"] = str(profile)
    binary = shutil.which("claude") or str(HOME / ".local/bin/claude")
    res = subprocess.run([binary, *cli], env=env, capture_output=True, text=True)
    if res.returncode != 0:
        warn(profile, f"claude {' '.join(cli)} failed: {(res.stderr or res.stdout).strip()[-300:]}")
        return False
    return True


# ---- plugins ---------------------------------------------------------------

def marketplace_arg(source):
    kind = source.get("source")
    return {"github": source.get("repo"), "git": source.get("url"),
            "url": source.get("url"), "directory": source.get("path")}.get(kind)


def sync_plugins(profile, repo, state):
    shared = read_json(repo / "profile/settings.json", {})
    known = read_json(profile / "plugins/known_marketplaces.json", {})
    for name, spec in shared.get("extraKnownMarketplaces", {}).items():
        if name in known or name in BUILTIN_MARKETPLACES:
            continue
        source = marketplace_arg(spec.get("source", {}))
        if not source:
            warn(profile, f"marketplace {name}: unsupported source {spec.get('source')}")
            continue
        if claude(profile, "plugin", "marketplace", "add", source):
            say(profile, f"added marketplace {name}")
    installed = read_json(profile / "plugins/installed_plugins.json", {}).get("plugins", {})
    for plugin, enabled in shared.get("enabledPlugins", {}).items():
        if not enabled or any(e.get("scope") == "user" for e in installed.get(plugin, [])):
            continue
        if claude(profile, "plugin", "install", plugin, "--scope", "user"):
            say(profile, f"installed plugin {plugin}")


# ---- mcp -------------------------------------------------------------------

def expand_env(value, missing):
    if isinstance(value, str):
        def sub(m):
            if m.group(1) not in os.environ:
                missing.append(m.group(1))
                return m.group(0)
            return os.environ[m.group(1)]
        return re.sub(r"\$\{(\w+)\}", sub, value)
    if isinstance(value, dict):
        return {k: expand_env(v, missing) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_env(v, missing) for v in value]
    return value


def sync_mcp(profile, repo, state):
    wanted = read_json(repo / "profile/mcp.json", {}).get("mcpServers", {})
    config = HOME / ".claude.json" if is_default(profile) else profile / ".claude.json"
    current = read_json(config, {}).get("mcpServers", {})
    for name in state.get("mcp", []):
        if name not in wanted and name in current:
            if claude(profile, "mcp", "remove", "--scope", "user", name):
                say(profile, f"removed MCP server {name}")
    applied = []
    for name, spec in wanted.items():
        missing = []
        spec = expand_env(spec, missing)
        if missing:
            warn(profile, f"MCP server {name}: skipped, env not set: {', '.join(missing)}")
            if name in state.get("mcp", []):
                applied.append(name)  # keep managing it; don't prune for a missing env var
            continue
        applied.append(name)
        if current.get(name) == spec:
            continue
        if name in current:
            claude(profile, "mcp", "remove", "--scope", "user", name)
        if claude(profile, "mcp", "add-json", "--scope", "user", name, json.dumps(spec)):
            say(profile, f"{'updated' if name in current else 'added'} MCP server {name}")
    state["mcp"] = applied


# ---- settings --------------------------------------------------------------
# The shared file is flattened into entries: ("set", path, value) for a scalar,
# ("item", path, item) for each element of a list (so hook groups and permission
# rules are unioned with the profile's own). Entries applied last time but gone
# from the repo now are removed.

def flatten(node, path=()):
    for key, value in node.items():
        p = path + (key,)
        if isinstance(value, dict) and value:
            yield from flatten(value, p)
        elif isinstance(value, list):
            for item in value:
                yield ["item", list(p), item]
        else:
            yield ["set", list(p), value]


def entry_id(entry):
    kind, path, value = entry
    return json.dumps([kind, path] + ([value] if kind == "item" else []), sort_keys=True)


def walk(root, path, create):
    node = root
    for key in path:
        if key not in node:
            if not create:
                return None
            node[key] = {}
        node = node[key]
    return node


def prune_empty(root, path):
    for depth in range(len(path), 0, -1):
        parent = walk(root, path[: depth - 1], False)
        key = path[depth - 1]
        if parent is not None and parent.get(key) in ({}, []):
            del parent[key]


def sync_settings(profile, repo, state):
    entries = list(flatten(read_json(repo / "profile/settings.json", {})))
    path = profile / "settings.json"
    settings = read_json(path, {})
    before = json.dumps(settings, sort_keys=True)
    wanted_ids = {entry_id(e) for e in entries}
    for old in state.get("settings", []):
        if entry_id(old) in wanted_ids:
            continue
        kind, keys, value = old
        parent = walk(settings, keys[:-1], False)
        if parent is None:
            continue
        if kind == "set" and parent.get(keys[-1]) == value:
            del parent[keys[-1]]
        elif kind == "item" and isinstance(parent.get(keys[-1]), list) and value in parent[keys[-1]]:
            parent[keys[-1]].remove(value)
        prune_empty(settings, keys)
    for kind, keys, value in entries:
        parent = walk(settings, keys[:-1], True)
        if kind == "set":
            parent[keys[-1]] = value
        else:
            items = parent.setdefault(keys[-1], [])
            if value not in items:
                items.append(value)
    state["settings"] = entries
    if json.dumps(settings, sort_keys=True) != before:
        if not args.dry_run:
            write_json(path, settings)
        say(profile, f"{'would merge' if args.dry_run else 'merged'} shared settings.json")


# ---- symlinks --------------------------------------------------------------

def link(profile, src, dst, label):
    """Point dst at src. Replaces an old link or an identical copy, never a different file."""
    if dst.is_symlink():
        if os.readlink(dst) == str(src):
            return True
    elif dst.exists():
        same = dst.is_file() and src.is_file() and dst.read_bytes() == src.read_bytes()
        if not same:
            warn(profile, f"{dst} exists and is not a link to this repo; left alone")
            return False
    if args.dry_run:
        say(profile, f"would link {label}")
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink() or dst.exists():
        dst.unlink()
    dst.symlink_to(src)
    say(profile, f"linked {label}")
    return True


def unlink_if_ours(profile, dst, repo, label):
    if dst.is_symlink() and os.readlink(dst).startswith(str(repo) + os.sep):
        if not args.dry_run:
            dst.unlink()
        say(profile, f"{'would remove' if args.dry_run else 'removed'} stale link {label}")


def skill_project(skill_md):
    m = re.match(r"---\n(.*?)\n---\n", skill_md.read_text(), re.S)
    found = re.search(r"^project:\s*(\S+)", m.group(1), re.M) if m else None
    return found.group(1) if found else None


def sync_skills(profile, repo, state):
    global_skills = {p.parent.name for p in repo.glob("*/SKILL.md") if not skill_project(p)}
    for name in sorted(global_skills):
        link(profile, repo / name, profile / "skills" / name, f"skill {name}")
    skills_dir = profile / "skills"
    if skills_dir.is_dir():
        for entry in skills_dir.iterdir():
            if entry.name not in global_skills:
                unlink_if_ours(profile, entry, repo, f"skill {entry.name}")


def sync_project_skills(repo):
    projects = {}
    for line in (repo / "projects.txt").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, checkout = line.split(None, 1)
            projects[name] = Path(checkout.strip()).expanduser()
    for skill_md in sorted(repo.glob("*/SKILL.md")):
        project = skill_project(skill_md)
        if not project:
            continue
        checkout = projects.get(project)
        if not checkout or not checkout.is_dir():
            warn(None, f"{skill_md.parent.name}: project {project!r} has no checkout in projects.txt")
            continue
        name = skill_md.parent.name
        link(checkout, repo / name, checkout / ".claude/skills" / name, f"project skill {name}")


def sync_files(profile, repo, state):
    home = repo / "profile/home"
    wanted = sorted(str(p.relative_to(home)) for p in home.rglob("*") if p.is_file() and p.name != ".DS_Store")
    for rel in state.get("files", []):
        if rel not in wanted:
            unlink_if_ours(profile, profile / rel, repo, rel)
    state["files"] = [rel for rel in wanted if link(profile, home / rel, profile / rel, rel)]


# ---- main ------------------------------------------------------------------

def main():
    global args
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--current", action="store_true", help="only the profile in CLAUDE_CONFIG_DIR (or ~/.claude)")
    parser.add_argument("--profile", action="append", type=Path, help="sync this profile dir (repeatable)")
    parser.add_argument("--only", action="append", choices=STEPS, help="run only this step (repeatable)")
    parser.add_argument("--repo", type=Path, help="source checkout (default: the main checkout)")
    parser.add_argument("--dry-run", action="store_true", help="print what would change")
    parser.add_argument("-q", "--quiet", action="store_true", help="print warnings only")
    args = parser.parse_args()

    main_repo = main_checkout()
    repo = (args.repo or main_repo).resolve()
    steps = args.only or STEPS
    profiles = args.profile or ([current_profile()] if args.current else discover_profiles())

    for profile in profiles:
        profile = profile.expanduser()
        if not profile.is_dir():
            warn(profile, "not a directory; skipped")
            continue
        state_path = profile / STATE_FILE
        state = read_json(state_path, {})
        for step in steps:
            globals()[f"sync_{step}"](profile, repo, state)
        if not args.dry_run:
            write_json(state_path, state)

    # Project checkouts and the PATH entry are machine-wide, so only the main
    # checkout may point them at itself.
    if repo == main_repo.resolve():
        if "skills" in steps:
            sync_project_skills(repo)
        if not args.dry_run:
            link(Path("bin"), repo / "scripts/sync_profiles.py", BIN_LINK, str(BIN_LINK))
    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
