#!/usr/bin/env python3
"""Sync the shared Claude Code setup in this repo into every Claude profile.

A profile is a Claude config dir: ~/.claude (the default) and every ~/.claude-*
dir, which T3 Code launches through CLAUDE_CONFIG_DIR. Each run does five steps:

  plugins   add the marketplaces in profile/settings.json, install its enabled plugins,
            uninstall plugins and remove marketplaces the repo dropped
  mcp       add the servers in profile/mcp.json at user scope (`${VAR}` reads the env)
  settings  merge profile/settings.json into <profile>/settings.json
  skills    symlink global skills and those in profile/skill-sources.txt into
            <profile>/skills, project skills into the checkout projects.txt names
  files     symlink everything under profile/home/ into the same path in <profile>

What a run adds is recorded in <profile>/.skills-sync.json, so removing an entry
from the repo removes it from every profile on the next run. Anything a profile
has that the repo does not (a plugin installed with /plugin, its theme) is left
alone. Sources come from the main checkout, never a linked worktree, so links
survive the worktree being deleted.

  python3 scripts/sync_profiles.py              # every profile
  python3 scripts/sync_profiles.py --current    # the profile running this (the SessionStart hook)
  python3 scripts/sync_profiles.py --only skills --dry-run
  python3 scripts/sync_profiles.py --drift      # what a profile has that the repo does not
"""
import argparse
import filecmp
import glob
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
    """The main checkout of the repo this script is in, or None outside git.

    None matters: a copy of the repo outside git must never be mistaken for the
    main checkout, or it would point the machine-wide links at itself.
    """
    here = Path(os.path.realpath(__file__)).parent
    try:
        out = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out).parent.resolve()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


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
    plugins = shared.get("enabledPlugins", {})
    marketplaces = shared.get("extraKnownMarketplaces", {})
    installed = read_json(profile / "plugins/installed_plugins.json", {}).get("plugins", {})
    known = read_json(profile / "plugins/known_marketplaces.json", {})

    # Dropped from the repo: uninstall (a plugin set to false stays, disabled).
    for plugin in state.get("plugins", []):
        if plugin not in plugins and plugin in installed:
            if claude(profile, "plugin", "uninstall", plugin, "--scope", "user"):
                say(profile, f"uninstalled plugin {plugin}")
                installed.pop(plugin)
    for name in state.get("marketplaces", []):
        if name in marketplaces or name not in known:
            continue
        users = [p for p in installed if p.endswith("@" + name)]
        if users:
            warn(profile, f"marketplace {name}: kept, still used by {', '.join(users)}")
        elif claude(profile, "plugin", "marketplace", "remove", name):
            say(profile, f"removed marketplace {name}")
    state["plugins"] = sorted(plugins)
    state["marketplaces"] = sorted(marketplaces)

    for name, spec in marketplaces.items():
        if name in known:
            continue
        source = marketplace_arg(spec.get("source", {}))
        if not source:
            warn(profile, f"marketplace {name}: unsupported source {spec.get('source')}")
            continue
        if claude(profile, "plugin", "marketplace", "add", source):
            say(profile, f"added marketplace {name}")
    for plugin, enabled in plugins.items():
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
        if dst.is_dir() and src.is_dir():
            same = same_tree(dst, src)
        else:
            same = dst.is_file() and src.is_file() and dst.read_bytes() == src.read_bytes()
        if not same:
            warn(profile, f"{dst} exists and differs from {src}; left alone")
            return False
    if args.dry_run:
        say(profile, f"would link {label}")
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_dir() and not dst.is_symlink():
        shutil.rmtree(dst)  # an identical copy, checked above
    elif dst.is_symlink() or dst.exists():
        dst.unlink()
    dst.symlink_to(src)
    say(profile, f"linked {label}")
    return True


def same_tree(a, b):
    cmp = filecmp.dircmp(a, b, ignore=[".DS_Store"])
    if cmp.left_only or cmp.right_only or cmp.common_funny:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    return not mismatch and not errors and all(same_tree(a / d, b / d) for d in cmp.common_dirs)


def unlink_if_ours(profile, dst, repo, label):
    if dst.is_symlink() and os.readlink(dst).startswith(str(repo) + os.sep):
        if not args.dry_run:
            dst.unlink()
        say(profile, f"{'would remove' if args.dry_run else 'removed'} stale link {label}")


def skill_project(skill_md):
    m = re.match(r"---\n(.*?)\n---\n", skill_md.read_text(), re.S)
    found = re.search(r"^project:\s*(\S+)", m.group(1), re.M) if m else None
    return found.group(1) if found else None


def outside_skills(repo):
    """Skills from profile/skill-sources.txt: name -> folder, plus the excluded names.

    Each line is a glob for a folder of skills or a single skill folder; `!name`
    excludes a skill (one a plugin already provides). The first source wins.
    """
    found, excluded = {}, set()
    sources = repo / "profile/skill-sources.txt"
    lines = sources.read_text().splitlines() if sources.exists() else []
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if line.startswith("!"):
            excluded.add(line[1:])
            continue
        for match in sorted(glob.glob(os.path.expanduser(line))):
            folder = Path(match)
            skills = [folder] if (folder / "SKILL.md").is_file() else (
                sorted(c for c in folder.iterdir() if (c / "SKILL.md").is_file()) if folder.is_dir() else [])
            for skill in skills:
                found.setdefault(skill.name, skill.resolve())
    return found, excluded


def wanted_skills(repo):
    """Skill name -> source folder for every global skill, plus the excluded names."""
    wanted = {p.parent.name: repo / p.parent.name for p in repo.glob("*/SKILL.md") if not skill_project(p)}
    outside, excluded = outside_skills(repo)
    for name, src in outside.items():
        if name not in excluded and src.parent != repo:
            wanted.setdefault(name, src)
    return wanted, excluded


def sync_skills(profile, repo, state):
    wanted, excluded = wanted_skills(repo)
    skills_dir = profile / "skills"
    managed = []
    for name, src in sorted(wanted.items()):
        dst = skills_dir / name
        if not dst.is_symlink() and dst.resolve() == src:
            continue  # the source lives in this profile; nothing to link
        if link(profile, src, dst, f"skill {name}"):
            managed.append(name)
    if skills_dir.is_dir():
        for entry in skills_dir.iterdir():
            if entry.name in wanted:
                continue
            if entry.is_symlink() and (entry.name in excluded or entry.name in state.get("skills", [])):
                if not args.dry_run:
                    entry.unlink()
                say(profile, f"{'would remove' if args.dry_run else 'removed'} skill link {entry.name}")
            else:
                unlink_if_ours(profile, entry, repo, f"skill {entry.name}")
    state["skills"] = managed


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

# ---- drift and pull --------------------------------------------------------

def report_drift(profile, repo):
    """Print what this profile has that the repo does not, so it can be promoted or removed."""
    shared = read_json(repo / "profile/settings.json", {})
    settings = read_json(profile / "settings.json", {})
    only = [f"plugin {p}" for p, on in settings.get("enabledPlugins", {}).items()
            if on and p not in shared.get("enabledPlugins", {})]
    config = HOME / ".claude.json" if is_default(profile) else profile / ".claude.json"
    servers = read_json(repo / "profile/mcp.json", {}).get("mcpServers", {})
    only += [f"MCP server {m}" for m in read_json(config, {}).get("mcpServers", {}) if m not in servers]
    wanted, _ = wanted_skills(repo)
    skills_dir = profile / "skills"
    if skills_dir.is_dir():
        only += [f"skill {e.name}" for e in sorted(skills_dir.iterdir())
                 if e.name not in wanted and (e / "SKILL.md").is_file()]
    only += [f"settings key {k}" for k in settings
             if k not in shared and k not in ("enabledPlugins", "extraKnownMarketplaces")]
    for item in only:
        print(f"{profile.name}: only here: {item}")


def pull(repo):
    """Fast-forward the main checkout so a merged PR reaches the profiles. Returns True if HEAD moved."""
    def git(*cli):
        return subprocess.run(["git", "-C", str(repo), *cli], capture_output=True, text=True, timeout=30)
    try:
        if git("branch", "--show-current").stdout.strip() != "main":
            return False
        if git("status", "--porcelain").stdout.strip():
            warn(None, f"{repo} has local changes; not pulling")
            return False
        before = git("rev-parse", "HEAD").stdout
        res = git("pull", "--ff-only", "-q")
        if res.returncode:
            warn(None, f"git pull failed: {res.stderr.strip()[-200:]}")
            return False
        return git("rev-parse", "HEAD").stdout != before
    except subprocess.TimeoutExpired:
        warn(None, "git pull timed out")
        return False


def main():
    global args
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--current", action="store_true", help="only the profile in CLAUDE_CONFIG_DIR (or ~/.claude)")
    parser.add_argument("--profile", action="append", type=Path, help="sync this profile dir (repeatable)")
    parser.add_argument("--only", action="append", choices=STEPS, help="run only this step (repeatable)")
    parser.add_argument("--repo", type=Path, help="source checkout (default: the main checkout)")
    parser.add_argument("--dry-run", action="store_true", help="print what would change")
    parser.add_argument("-q", "--quiet", action="store_true", help="print warnings only")
    parser.add_argument("--pull", action="store_true", help="fast-forward the main checkout first (clean, on main)")
    parser.add_argument("--drift", action="store_true", help="only report what profiles have that the repo does not")
    args = parser.parse_args()

    main_repo = main_checkout()
    if not (args.repo or main_repo):
        parser.error("this script is not in a git checkout; pass --repo")
    repo = (args.repo or main_repo).resolve()
    is_main = main_repo is not None and repo == main_repo
    steps = args.only or STEPS
    profiles = args.profile or ([current_profile()] if args.current else discover_profiles())

    if args.pull and not args.dry_run and is_main and pull(repo):
        # The script itself may have changed: rerun the new one, without --pull.
        argv = [a for a in sys.argv[1:] if a != "--pull"]
        os.execv(sys.executable, [sys.executable, str(repo / "scripts/sync_profiles.py"), *argv])

    if args.drift:
        for profile in profiles:
            report_drift(profile.expanduser(), repo)
        return 0

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
    if is_main:
        if "skills" in steps:
            sync_project_skills(repo)
        if not args.dry_run:
            link(Path("bin"), repo / "scripts/sync_profiles.py", BIN_LINK, str(BIN_LINK))
    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
