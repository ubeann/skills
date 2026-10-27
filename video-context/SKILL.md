---
name: video-context
description: Turn a video URL or video file into context an agent can read, as one bundle folder with the post text, captions or a whisper transcript, and deduplicated frames. Use when the user shares a video link (x.com, YouTube, any site yt-dlp supports) or a video file and asks what it shows, to summarise or explain it, or to learn from it. Filing what was learned as a study note is the learn skill.
---

# Video context

A model reads text and images, so a video becomes three **channels**: the post around it, what was said (captions, else a transcript), and what was shown (frames). The script probes the file and routes by what it finds. A silent screen recording, or an animation with sound effects, yields no transcript, and the frames carry everything. Read the channels the bundle says are present, then write a summary the next reader can use without opening the video.

## Steps

### 1. Extract

```sh
sh ~/.claude/skills/video-context/references/extract.sh <url-or-file>
```

It prints the bundle path (default `/tmp/video-context/<slug>/`). Defaults: one frame every 3 s, at most 60 frames with the interval stretched to fit, download capped at 1080p. Knobs are documented at the top of the script: `INTERVAL`, `MAX_FRAMES`, `MAX_HEIGHT`, `FORCE_TRANSCRIBE`, `WHISPER_MODEL`, `SUB_LANGS`. Exit code 2 names a missing tool; install it from `references/setup.md` and rerun.

Done when `README.md` in the bundle lists every channel as present, absent, empty, or skipped.

### 2. Read the channels

Read `README.md` first: the post text and the channel table decide what to open.

- **Said.** Read `captions.txt` or `transcript.txt` in full. Auto-captions misspell product names; the post text and frames correct them.
- **Shown.** Read `frames/` in timestamp order. Past 20 frames, read every third first, then return to the stretch the question is about. When both channels are present, check the transcript's claims against the frames: a demo says one thing and the screen shows another.

Done when every channel marked present has been read, and every frame has been opened or sits in a stretch you named as skipped.

### 3. Summarise

Write `summary.md` in the bundle:

- One paragraph: the format (demo, talking head, animation, screen recording) and the point the video makes.
- A timeline of bullets in `[m:ss]` order, one thing shown or said per bullet, transcript quotes verbatim.
- One line naming what the channels did not carry: no audio, a sponsor stretch, frames too coarse for a fast edit.

Done when every timeline bullet has a timestamp that maps to a frame file or a transcript line, and the empty-channels line matches the README table.

### 4. Reply

Answer the question at the size it was asked, and give the bundle path so the user can open the frames. A learning question continues in the `learn` skill with `summary.md` as the fetched source of its article branch.

## Working habits

- A stretch that needs finer frames gets its own run: trim it with `ffmpeg -ss <start> -t <length> -i clip.mp4 -c copy part.mp4`, then extract `part.mp4` with `INTERVAL=1`. Re-running the whole video at a finer interval multiplies the frames you must read.
- The transcript is English by default. Another language needs a multilingual model; `references/setup.md` says which.
- Twitter captions never exist, so an x.com clip with speech always runs whisper. Budget about a fifth of the clip's length for it.
