---
name: report-changelog
description: Build a before/after report of a change to an app (copy, UI, bug fix or new feature) and file it in the project as a changelog entry. Screenshots are captured before the first edit and after it by one script, rendered as a PNG album to send in chat and, when asked, a portrait or landscape PDF, while the change's context (background, reason, source, PIC, decisions, PR) stays in the repository for backtracking. Use when a change or release needs explaining to a stakeholder, when the user asks for a before/after or a changelog, or when tracing why something changed. A report from computed data is report-web (scrolling) or report-deck (paged).
---

# Report changelog

An **entry** is one folder in the project, `docs/changelog/<date>-<slug>/`: a `changelog.json`, the `capture.mjs` that took the screenshots, the `shots/`, the `evidence/` the request came with, and a generated `README.md`. The JSON is the single source of truth. `references/render.mjs` turns it into the outputs in seconds, so a language, an orientation or a wording fix is a re-render and never a hand edit of HTML. The layout and every field are in `references/entry.md`.

Two readers, two records. The **outputs** go to the stakeholder and show only the project update: what changed, where, and what did not. The **context** is the repository's backtrack record, with its evidence: it always lives in `changelog.json` and the generated `README.md`, and reaches an output only when the user asks for it with `--context`.

## What the project provides

The project's agent doc names these, or you add them:

- the app URL and how to start it;
- a seeded login for screenshots;
- a seeded record in each state a screen needs (a seeder or factory state), so a capture never edits real rows;
- `playwright-core` installed somewhere the scripts can run from (a dev dependency, or the scratchpad);
- the reader's languages, e.g. "PIC reports: Indonesian; app text stays English".

Done when each is a line in the agent doc. Ask the user for the languages the first time; the rest you can find and then write down.

## Steps

### 1. Open the entry

Classify the change as the entry's `type`: `copy`, `ui`, `fix` or `feature`. It shows as a coloured badge on the cover, and it decides the sections: a feature has no "before" and shows where to find it and how to use it; a fix's "before" shows the wrong behaviour. Create the folder, copy `references/example.json` in as `changelog.json`, and fill `context` from what the conversation, ticket and user have said so far: background, reason, source (the request and this session or thread), people. Save the **evidence**: copy every image the user attached that shows the request, the bug or a decision (a chat screenshot, an error page, what the PIC saw) into `evidence/` under a name that says what it is, and describe each in `context.evidence`; `references/entry.md` says where attachments live and when to keep them out of git. List every screen the change touches: search for each string or component you will change and follow it to every page that renders it.

Done when the screen list covers every file that renders a changed string, every attached image that shows the request, bug or decision is in `evidence/`, and every context field holds something the user or a source said; fields nobody supplied are left out.

### 2. Capture the before

Copy `references/capture.mjs` into the entry and fill in one `SCREENS` entry per screen: its path, the action that brings it into the state to show, the element to crop, and the text that proves the crop holds the change. Run `node capture.mjs before` before your first edit. If the before state is already gone, run it against a worktree checked out at the parent commit.

Done when `shots/before/` has one PNG per screen and the script exited 0.

### 3. Change, then capture the after

Make the change. Run `node capture.mjs after` with the same script, viewport and seeded records, so each pair differs only by the change. A feature captures its new screens here as `single` sections.

Done when every before has an after of the same name, and every crop passed its text check.

### 4. Write the copy

Fill `head` and each section's `text` for every language in `langs`: a title, at most three summary cards, a section per screen with its breadcrumb and bullets, one `table` section for wording no screenshot shows, and a footer that says what did not change. The footer is the line a PIC looks for. The app's own words stay in the app's language in every locale, in `**bold**`.

Done when every language has a head and text for every section.

### 5. Render and look

From a folder with `playwright-core`:

```sh
node <skill>/references/render.mjs docs/changelog/<entry> [--pdf portrait|landscape] [--context]
```

It inlines `references/style.css`; to match the product, change only its palette tokens. It always writes the entry's `README.md`, and for each language `out/<lang>/`: a tall PNG, and an `album/` with a cover and one image per section, each under 2000px tall, to send in chat as one album. The album is the default and is enough for a small change: it reads in a chat with no zooming. Add `--pdf` only when the user asks for one, or when the report runs past four sections and a paged document reads better than a long album. Choose **landscape** when the screens are wider than tall, so each pair sits side by side, and **portrait** when the screens are tall or phone-sized, or the report is mostly text: portrait stacks the after under the before. Add `--context` only when the user asks for it: it appends the context and the evidence as the last album image and the last PDF pages.

Read every album PNG and every PDF page. If a pair shrinks past reading size, switch the orientation or crop the shots in `capture.mjs`.

Done when the render exits 0 and you have seen every output.

### 6. File it

Open the PR first, then fill `context.scope` (PR, branch, commits, files), `verification`, `decisions` with who chose what over what, `unchanged`, `risks` and `rollback`, and re-render. Add the changelog line from `references/entry.md` and `docs/changelog/*/out/` to `.gitignore`. Commit the entry as its own docs commit on the change's branch, and link the entry folder from the PR body.

Done when the entry and the changelog line are committed on the branch and the PR body links the entry.

### 7. Hand over

Give the user the paths: the album folder per language, the tall PNG, and the PDF. Tell them to send the album as photos and the PDF or tall PNG as a document, because a chat app compresses a tall photo until its text blurs.

If the stakeholder later asks why, who decided, or for evidence, answer from the entry's `README.md` and `evidence/`, or re-render with `--context` if the user wants it as a file.

Done when the user has the paths for every language and output.
