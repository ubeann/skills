---
name: moodboard
description: Collect design references from X, Threads, Instagram, YouTube or any site into one local library, break each into the technique it uses, flag techniques several designers are using at once, and assemble a project board where every reference has one job. Use when the user shares reference links or screenshots, asks what is trending in design, or wants a moodboard for an app, website, illustration, mascot or icon. Turning a board into UI tokens is design-direction; into art is brand-art; a video's full transcript is video-context.
---

# Moodboard

A reference copied whole hands over its author's identity. Copied as a **technique**, it lends one decision and leaves the rest to you. This skill turns each link into a card that names its technique, keeps every card in one library across projects, counts which techniques several authors use at the same time (a **trend**), and builds boards where each reference does exactly one job before `brand-art` or `design-direction` reads them.

The library is `$MOODBOARD_DIR`, default `~/moodboard`: one folder per reference with its media and `card.json`, plus `boards/<project>/`. It holds other people's work, so it stays outside every repository; boards cite references by URL. `<skill-dir>` below is the folder holding this file. The scripts need curl, Pillow and numpy.

## Steps

### 1. Fetch

```sh
python3 <skill-dir>/references/fetch.py <url> [<url> ...]
```

Each link becomes a folder with `card.json` (author, date, text, quoted post, links, engagement, media, a measured palette) and its images or video frames. X posts come through the public fxtwitter mirror; videos through the `video-context` skill; other pages through their preview tags. Instagram and Threads hide media from anonymous requests: when a card's `fetch_notes` say so, open the post in the logged-in browser (the yab browser), save each image into the folder, and rerun with `--force`, which keeps any breakdown already written. A link in the post (a portfolio, a live site) is fetched as its own reference.

Done when every link has a folder with `card.json` and at least one media file, or a `fetch_notes` line naming what is missing and the fallback tried.

### 2. Break down

Open every image and frame of each new card, then fill its breakdown fields from `references/breakdown.md`: `techniques` from the vocabulary, the `jobs` it could do, the `subject`, and `identity`, the part that makes it its author's own.

Done when every new card has at least one technique, at least one job and an identity line, and every media file in it has been opened.

### 3. Report trends

```sh
python3 <skill-dir>/references/library.py trends --days 45 --min 3
```

A technique used by three or more different authors in the window is a trend. Render the table in chat with one line per trend naming where it came from and what it would lend a project. A trend enters a project as one ingredient, twisted with the owner's own seed, never as the whole style.

Done when the trend table is in chat and every new card's techniques were counted in it.

### 4. Build a board

Only for a project that asks for one. Pick references from the library (`library.py list --tag <technique>` or `--job <job>`), give each exactly one job, and prune: a reference with no job leaves, and each job keeps one reference.

```sh
python3 <skill-dir>/references/library.py board <project> <ref-id>=<job> [<ref-id>=<job> ...]
```

Fill each row of `boards/<project>/board.md` with what is taken: measured values for palette and type (`design-direction`'s `inventory.js` on a live page), a named technique for the rest. Hand the board to `brand-art` (its art bible's references table) or `design-direction` (its step 3).

Done when `library.py board` exits 0, every row says what is taken, and `board.png` has been looked at.

## Working habits

- Name the technique, never the look: "halftone dots on a classical subject", not "like Nexara".
- A post that promises a result from one prompt shares its template with everyone who copied it; its technique counts, its layout and copy do not.
- When the user shares a batch, fetch all of it before breaking any down, so the trend count sees the batch together.
