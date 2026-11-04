---
name: moodboard
description: Collect design references from X, Threads, Instagram, YouTube or any site into one local library, break each into the technique it uses, flag techniques several designers are using at once, and assemble a project board where every reference has one job. Use when the user shares reference links or screenshots, asks what is trending in design, or wants a moodboard for an app, website, illustration, mascot or icon. Turning a board into UI tokens is design-direction; into art is brand-art; into motion is motion-direction; a video's full transcript is video-context.
---

# Moodboard

A reference copied whole hands over its author's identity. Copied as a **technique**, it lends one decision and leaves the rest to you. This skill turns each link into a card that names its technique, keeps every card in one library across projects, counts which techniques several authors use at the same time (a **trend**), and builds boards where each reference does exactly one job before `brand-art` or `design-direction` reads them.

The library is `$MOODBOARD_DIR`, default `~/moodboard`: one folder per reference with its media and `card.json`, plus `boards/<project>/`. It holds other people's work, so it stays outside every repository; boards cite references by URL. `<skill-dir>` below is the folder holding this file. The scripts need curl, Pillow and numpy.

## Steps

### 1. Fetch

```sh
python3 <skill-dir>/references/fetch.py <url> [<url> ...]
```

Each link becomes a folder with `card.json` (author, date, text, quoted post, links, engagement, media, a measured palette) and its images or video frames. X posts come through the public fxtwitter mirror; videos through the `video-context` skill; other pages through their preview tags. Instagram and Threads give anonymous requests the cover image only, and block yt-dlp: when a card's `fetch_notes` say so, follow `references/social.md` to save the slides or the video through the yab browser, then rerun with `--force`, which keeps any breakdown already written. A Pinterest pin names who saved it, rarely who made it: replace the placeholder `author` with the credit on the image or the page it was saved from, so the trend count tells designers apart. A link in the post (a portfolio, a live site) is fetched as its own reference.

Done when every link has a folder with `card.json` and at least one media file, or a `fetch_notes` line naming what is missing and the fallback tried.

### 2. Break down

Open every image and frame of each new card, then fill its breakdown fields from `references/breakdown.md`: `techniques` from the vocabulary, the `jobs` it could do, the `subject`, and `identity`, the part that makes it its author's own. A video card with the `motion` job also gets its motion readings, from frames extracted again at half a second.

Done when every new card has at least one technique, at least one job and an identity line, and every media file in it has been opened.

### 3. Report trends

```sh
python3 <skill-dir>/references/library.py trends --days 45 --min 3
```

A technique used by three or more different authors in the window is a trend. Render the table in chat with one line per trend naming where it came from and what it would lend a project. A trend enters a project as one ingredient, twisted with the owner's own seed, never as the whole style.

Done when the trend table is in chat and every new card's techniques were counted in it.

### 4. Build a board

Only for a project that asks for one. The board is a **creative argument**: every reference is a sentence in it, and one whose sentence you cannot say leaves. Pick references from the library (`library.py list --tag <technique>` or `--job <job>`), give each exactly one job, and prune: a reference with no job leaves, and each job keeps one reference.

```sh
python3 <skill-dir>/references/library.py board <project> <lead-id>=<job>:<what is taken> [<ref-id>=<job>:<what is taken> ...]
```

The first reference is the **lead**, drawn at four times the area: size is weight, so lead with the reference most central to the direction. What is taken is a measured value for palette and type (`design-direction`'s `inventory.js` on a live page) and a named technique for the rest; it captions the reference on `board.png` too, so a reader reacts to the part taken rather than the whole image.

Then look at `board.png` for ten seconds. A reader should be able to say the direction from it; a reference whose colour or tone pulls the eye away from the lead is cut, or recoloured to sit with the others. Hand the board to `brand-art` (its art bible's references table) or `design-direction` (its step 3).

Done when `library.py board` exits 0, the direction can be said from `board.png` in ten seconds, and no reference pulls away from the lead.

## Working habits

- Name the technique, never the look: "halftone dots on a classical subject", not "like Nexara".
- A post that promises a result from one prompt shares its template with everyone who copied it; its technique counts, its layout and copy do not.
- When the user shares a batch, fetch all of it before breaking any down, so the trend count sees the batch together.
- Weigh a reference by where it came from. A Dribbble shot, a Behance case study or a pin is one polished frame of a presentation, with no other pages, no mobile and no real content; Pinterest and Instagram serve every designer the same picks. For a `layout` or `type` job, fetch the live site the shot came from, or take it from a library of working sites (Land-book, SiteInspire, SaaS Landing Page, Mobbin for flows) or a hand-curated Are.na board.
