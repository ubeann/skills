---
name: character-design
description: Design a product mascot's character before it is drawn. Writes a character brief (role in the product, personality with behaviours, moments, voice, a form checked against the category, story, body mechanic, anatomy in numbers, signature, props) and gets the owner's pick of an anatomy from sketch rounds. Use when a product needs a mascot or a character icon, when a mascot reads generic, lacks appeal or has no story, or when the owner asks for anatomy, backstory or personality. Drawing the approved character (hero, turnaround, expressions, icon) is brand-art; judging it cold is art-critique; collecting references is moodboard; the product's own brief is design-direction.
---

# Character design

An image model asked for a mascot returns **an animal with an accessory**: a pig in glasses, a fox in a scarf, a character any product could wear. What makes a mascot one product's own is decided in words and rough sketches before anything is rendered: what it does for the user, how it behaves, and why its body is built the way it is. This skill ends on a **character brief** the owner approved and an **anatomy** they picked. `brand-art` draws from both.

In a mascot pilot on 2026-11-24, 234 of 364 credits were spent and a finished icon was archived before a brief existed. The owner asked for character-first work three times, then approved the first brief in one reply.

The work lives in the product repo under `art/<name>/`: the brief in `character.md`, the category in `rivals/`, galleries in `rounds/`, the pick in `seed/`. `<skill-dir>` below is the folder holding this file. The gallery script needs Pillow.

## Steps

### 1. Read the product

Read `PRODUCT.md` for the users, the **bet** and the key moments. When it is missing or lacks one of them, write those fields with the `design-direction` skill's brief (its step 2) from the conversation, and get the owner's yes on the bet. Write down what the product's name means.

Collect the **category** into `art/<name>/rivals/` with the command in `references/brief.md` (Form shortlist), and write in `art/<name>/README.md` what it is crowded with: species, colours, props. Send every reference the owner shared through the `moodboard` skill's fetch and breakdown, so the batch is read as one board; the jobs a character takes are `anatomy`, `shape`, `pose` and `technique`. Write the vendor's credit balance in the README.

Done when `PRODUCT.md` holds the users, the bet and the key moments, the README names what about 20 rivals are crowded with, every owner reference has a moodboard card with a job, and the credit balance is written down.

### 2. Draft the brief

Fill fields 1 to 5 of `references/brief.md` into `art/<name>/character.md`, under a first line `Status: draft`: role, personality, moments, voice and the form shortlist. These hold whichever form is picked.

Done when every trait names a behaviour in a product moment, every moment names its placement, and the shortlist has three or four forms, each with its rival count, its likely misread and a one-line story.

### 3. Form round

When the owner already named the form, record it and go to step 4. Otherwise draw one sketch per shortlisted form as a **sketch round** (below).

Done when the owner picked or named a form, and a round that ran is saved as `rounds/forms.png`.

### 4. Finish the brief, then the anatomy round

Fill fields 6 to 10 for the picked form: story, body mechanic, anatomy, signature and props, and the locked, flexible, forbidden table. Run the three tests at the end of `references/brief.md`. Then draw four to six builds of the form as a sketch round, each pushing a different proportion from the Anatomy field. Put the story, the personality and the body mechanic above the gallery in a few lines, so the owner judges the character and its body together.

Done when the owner approved the story in words and picked a build. A pick that mixes sketches ("head of 4, belly of 2") is redrawn once as one sketch and confirmed.

### 5. Lock

Save the pick in `art/<name>/seed/`. Measure its proportions and write them as numbers into the Anatomy field and the Locked rows. Set the first line to `Status: approved by the owner on <date>`. Hand over to `brand-art`, whose `pack.json` names the brief as `"character": "character.md"`.

Done when `character.md` starts with `Status: approved`, every Locked row is a number or a named shape, and `seed/` holds the pick.

## Sketch rounds

Both rounds ask the owner for a direction before anything is finished, and run the same way:

- **Draft model only.** One call per sketch from the prompt in `references/brief.md` (Sketch prompt), on the cheapest model in the `brand-art` skill's `vendors.md`. Quote the round before running it.
- **One numbered gallery.** `python3 <skill-dir>/references/gallery.py art/<name>/rounds/<round>.png <sketches>` numbers each sketch, so the owner answers with a number. Give each sketch one line: what it pushes and its likely misread ("reads partly as a rabbit").
- **Labelled unreviewed.** A sketch round skips `art-critique`; the critique starts at the hero in `brand-art`.
- **The gallery ends the turn.** The reply is the gallery, your recommendation, and what the owner gives up with each other choice. The next call waits for the owner's number.

## Working habits

- A reference lends one cell (a build, a pose, a shading technique), never its character. Name what is taken and write "everything else ignored".
- When the owner's feedback is about appeal ("not cute", "no selling point", "like every other mascot"), change the brief first: the form, the anatomy numbers or the body mechanic. A new rendering style on the same character returns the same complaint.
- Check any fact the story leans on (a history, a word's origin) against a source, and leave out what scholars dispute.
