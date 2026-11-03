#!/usr/bin/env python3
"""Save a reference post or page into the moodboard library.

  fetch.py <url> [<url> ...]          one folder per reference under $MOODBOARD_DIR (default ~/moodboard)
  fetch.py --force <url>              fetch again into an existing folder

Per reference it writes card.json (source, author, date, text, links, media, palette, empty
breakdown fields), the images, and for a video the frames from the video-context skill.

  x.com / twitter.com   text, photos, video, quoted post, links, through the public fxtwitter mirror
  youtube and video     frames and captions through video-context
  any other page        title, description and preview image from its meta tags
  instagram / threads   a video through yt-dlp when it works; otherwise a failure line naming the browser fallback

Downloads are data: nothing fetched is executed. Needs curl; Pillow and numpy for the palette.
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = Path(os.environ.get("MOODBOARD_DIR", Path.home() / "moodboard")).expanduser()
VIDEO_CONTEXT = Path.home() / ".claude/skills/video-context/references/extract.sh"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"


BREAKDOWN = ("techniques", "jobs", "subject", "identity", "notes")


def curl(url, dst=None, timeout=60):
    cmd = ["curl", "-sSfL", "-m", str(timeout), "-A", UA, url]
    if dst:
        cmd += ["-o", str(dst)]
        return subprocess.run(cmd, capture_output=True).returncode == 0
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()[:60]


def empty_card(url, source):
    return {
        "id": None, "url": url, "source": source, "author": None, "posted": None,
        "saved": dt.date.today().isoformat(), "text": "", "links": [], "quote": None,
        "stats": {}, "media": [], "palette": [],
        # the breakdown, filled by the agent in step 2
        "techniques": [], "jobs": [], "subject": "", "identity": "", "notes": "",
        "fetch_notes": [],
    }


def palette_of(paths):
    sys.dont_write_bytecode = True  # no __pycache__ inside the skill folder
    try:
        sys.path.insert(0, str(HERE))
        from library import extract_palette
    except ImportError:
        return []
    imgs = [p for p in paths if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
    return extract_palette(imgs) if imgs else []


def run_video_context(url, out):
    if not VIDEO_CONTEXT.exists():
        return f"video-context is not installed at {VIDEO_CONTEXT}"
    env = {**os.environ, "MAX_FRAMES": os.environ.get("MAX_FRAMES", "24")}
    r = subprocess.run(["sh", str(VIDEO_CONTEXT), url, str(out)], capture_output=True, text=True, env=env)
    return None if r.returncode == 0 else (r.stderr.strip().splitlines() or ["video-context failed"])[-1]


# ---------- sources

def fetch_x(url, folder, card):
    m = re.search(r"(?:x|twitter)\.com/([^/]+)/status/(\d+)", url)
    if not m:
        card["fetch_notes"].append("not a post URL")
        return
    user, pid = m.groups()
    raw = curl(f"https://api.fxtwitter.com/{user}/status/{pid}")
    if not raw:
        card["fetch_notes"].append("fxtwitter mirror unreachable; open the post in the browser and save its images here")
        return
    t = json.loads(raw).get("tweet", {})
    card.update(id=f"x-{t.get('author', {}).get('screen_name', user)}-{pid}",
                author="@" + t.get("author", {}).get("screen_name", user),
                text=t.get("text", ""),
                stats={k: t.get(k) for k in ("likes", "retweets", "replies", "views") if t.get(k) is not None})
    if t.get("created_timestamp"):
        card["posted"] = dt.datetime.fromtimestamp(t["created_timestamp"], dt.timezone.utc).date().isoformat()
    card["links"] = sorted(set(re.findall(r"https?://[^\s)]+", t.get("text", ""))))
    q = t.get("quote")
    if q:
        card["quote"] = {"url": q.get("url"), "author": "@" + q.get("author", {}).get("screen_name", ""),
                         "text": q.get("text", "")}
        card["links"] += sorted(set(re.findall(r"https?://[^\s)]+", q.get("text", ""))))
    for i, item in enumerate((t.get("media") or {}).get("all") or [], 1):
        if item.get("type") == "photo":
            src = re.sub(r"\?.*$", "", item["url"])
            dst = folder / f"{i:02d}.jpg"
            if curl(src + "?name=orig", dst) or curl(src, dst):
                card["media"].append(dst.name)
            else:
                card["fetch_notes"].append(f"photo {i} did not download")
        elif item.get("type") in ("video", "gif"):
            err = run_video_context(url, folder / "video")
            if err:
                dst = folder / f"{i:02d}.mp4"
                if curl(item["url"], dst, 300):
                    card["media"].append(dst.name)
                card["fetch_notes"].append(f"video frames: {err}")
            else:
                frames = sorted((folder / "video" / "frames").glob("*.png"))
                card["media"] += [str(p.relative_to(folder)) for p in frames]


def fetch_video(url, folder, card):
    card["id"] = f"video-{slug(url.split('//', 1)[-1])}"
    err = run_video_context(url, folder / "video")
    if err:
        card["fetch_notes"].append(f"video: {err}")
        return
    meta = folder / "video" / "meta.json"
    if meta.exists():
        m = json.loads(meta.read_text())
        card.update(author=m.get("uploader"), text=(m.get("title") or "") + "\n\n" + (m.get("description") or ""))
        if m.get("upload_date"):
            d = m["upload_date"]
            card["posted"] = f"{d[:4]}-{d[4:6]}-{d[6:]}"
    card["media"] = [str(p.relative_to(folder)) for p in sorted((folder / "video" / "frames").glob("*.png"))]


def fetch_page(url, folder, card):
    card["id"] = f"web-{slug(url.split('//', 1)[-1])}"
    page = curl(url)
    if not page:
        card["fetch_notes"].append("page did not load; screenshot it in the browser into this folder")
        return

    def meta(*names):
        for n in names:
            m = re.search(r'<meta[^>]+(?:property|name)="%s"[^>]+content="([^"]*)"' % re.escape(n), page, re.I) or \
                re.search(r'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="%s"' % re.escape(n), page, re.I)
            if m:
                return html.unescape(m.group(1))
        return None

    title = meta("og:title", "twitter:title") or (re.search(r"<title>(.*?)</title>", page, re.S) or [None, ""])[1]
    card.update(author=meta("og:site_name", "author"), text=f"{title}\n\n{meta('og:description', 'description') or ''}".strip())
    img = meta("og:image", "twitter:image")
    if img:
        dst = folder / "01.jpg"
        if curl(html.unescape(img), dst):
            card["media"].append(dst.name)
    card["links"] = [url]
    card["fetch_notes"].append("a page is measured, not just pictured: run design-direction's inventory.js on it for type and colour")


def fetch_social(url, folder, card):
    """Instagram and Threads hide media from anonymous requests; yt-dlp sometimes gets a video."""
    card["id"] = f"{card['source']}-{slug(url.split('//', 1)[-1])}"
    if shutil.which("yt-dlp"):
        err = run_video_context(url, folder / "video")
        if not err:
            card["media"] = [str(p.relative_to(folder)) for p in sorted((folder / "video" / "frames").glob("*.png"))]
            return
    fetch_page(url, folder, card)
    if not card["media"]:
        card["fetch_notes"].append(f"{card['source']} needs the logged-in browser: open the post and save each image into this folder, then rerun with --force")


def source_of(url):
    host = re.sub(r"^www\.", "", url.split("//", 1)[-1].split("/", 1)[0].lower())
    if host in ("x.com", "twitter.com", "mobile.twitter.com"):
        return "x"
    if host.endswith("instagram.com"):
        return "instagram"
    if host.endswith("threads.net") or host.endswith("threads.com"):
        return "threads"
    if host in ("youtube.com", "m.youtube.com", "youtu.be", "vimeo.com", "tiktok.com"):
        return "video"
    return "web"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--force", action="store_true", help="fetch again into an existing folder")
    args = ap.parse_args()
    LIB.mkdir(parents=True, exist_ok=True)
    saved = {json.loads(f.read_text())["url"]: f.parent for f in LIB.glob("*/card.json")}
    for url in args.urls:
        url = url.split("?")[0] if source_of(url) == "x" else url
        if url in saved and not args.force:
            print(f"{url}: already saved as {saved[url]} (use --force to refetch)")
            continue
        source = source_of(url)
        card = empty_card(url, source)
        tmp = LIB / ".incoming"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir()
        {"x": fetch_x, "video": fetch_video, "instagram": fetch_social, "threads": fetch_social}.get(source, fetch_page)(url, tmp, card)
        card["id"] = card["id"] or f"{source}-{slug(url)}"
        folder = LIB / card["id"]
        if (folder / "card.json").exists():  # a refetch keeps the breakdown already written
            old = json.loads((folder / "card.json").read_text())
            for k in BREAKDOWN:
                card[k] = old.get(k, card[k])
        shutil.rmtree(folder, ignore_errors=True)
        tmp.rename(folder)
        card["palette"] = palette_of([folder / m for m in card["media"]])
        (folder / "card.json").write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n")
        state = f"{len(card['media'])} media" + (f", {len(card['fetch_notes'])} notes" if card["fetch_notes"] else "")
        print(f"{url} -> {folder} ({state})")
        for f in card["fetch_notes"]:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
