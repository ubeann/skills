---
name: deal-check
description: Rank what is worth buying on a sale page, in a promo, or across stores for one wanted item, as photo cards in chat grouped by price range, each pick backed by an evidence card (model year, stars and review count, an independent review, price trend, popularity) and filed in a price log for the next sale. Use when the user shares a sale or promo link and asks what is worth it, asks whether a discount or promo is real, wants an item found or compared across stores, or plans a bundle promo such as buy 2 get 1. A chart of the price history is dataviz; one price fact filed as a study note is learn.
---

# Deal check

A deal is worth buying when four things hold: the buyer can use it, the price is the real low, the product is good, and the terms are acceptable. A discount percent proves none of them. Every run leaves three things: **photo cards** in chat, a reply with the picks, and the run's prices in the **price log**.

## Steps

### 1. Profile and brief

Read `~/.config/skills/deal-profile.md`: sizes per brand, country, seller rule, output and log folder. Then fix the brief from the request: category, the use (a seminar shoe, a second bag), budget, and the store or event. Ask only for a size the category needs and the profile lacks; for anything else, proceed, and state the assumption in the reply. A size, preference or purchase the user states goes into the profile the same turn.

Done when the brief names the category, the use, the size or spec to filter on, and the stores.

### 2. Terms

Before ranking anything, read the **terms** of every promo in scope: the mechanic (cheapest item free, percent off, a voucher with a minimum spend), what it stacks with, exclusions, returns and exchanges, start and end, channel. Terms usually sit in a banner image, not in page text: `references/stores.md` says where each store keeps them. List the store's other live promos from its homepage links, and the sale events inside the next three weeks.

Done when each term is written down with the page or image it came from, or as "not stated", and every voucher code is marked tested or untested.

### 3. Collect

Read `references/browser.md` once, then the section of `references/stores.md` for each store before opening it: the access method that works, URL parameters, selectors, timings, traps. Collect every item in scope from the listing, then from each comparison store, official and brand-authorised sellers only. Write rows to disk as you go. A store with no section gets one before the run ends; a fact there that failed gets corrected.

Done when the row count, de-duplicated by URL, matches the count the listing states, and the rows are in a file.

### 4. Shortlist

Cut to what the buyer can use: in stock in their size, checked per product (store size filters undercount); right for the use; inside the budget. Where one model is listed in several colours, keep the cheapest colour that fits the use. The **shortlist** is 10 to 15 items spread over the price ranges. Download each one's photo and name its colour from the photo.

Done when every shortlisted item has confirmed stock in the buyer's size or spec, a local photo, and a colour that matches the photo.

### 5. Evidence

Fill the **evidence card** of each shortlisted item by `references/evidence.md`: year, stars, review, price trend, popularity. Run `python3 ~/.claude/skills/deal-check/references/prices.py history run.json` for the price trend. Each value comes from a page fetched this run and names its source; a field with no source reads "not found". Last, re-read each price on its product page: prices have moved inside two hours.

Done when all five fields of every card hold a sourced value or "not found", and every price was read from its product page after the evidence was gathered.

### 6. Verdict

Give each item `buy`, `consider`, `wait` or `skip` by the gates in `references/evidence.md`, with a one-sentence note naming the gate that decided. A `wait` names what to wait for and its date. For a bundle promo, build the sets by the rule in the same file.

Done when every shortlisted item has a verdict and a note, and no `buy` rests on a "not found" price trend or an unconfirmed size.

### 7. Cards

Write `run.json` (the schema is the docstring of `references/cards.py`), then:

```sh
python3 ~/.claude/skills/deal-check/references/cards.py run.json --ranges 600000,1000000,1500000,2000000 --out cards
```

Pick the range boundaries that spread this run's items; the script writes one file per range and prints each file's path and title. For each file: `html_preview` with the path, compare every photo with its colour name and look for wrapped prices, then `html_render` with the path, the printed title, and the preview's `contentHeight` as `height`. Cards go in chat, never in an artifact.

Done when every file is rendered and no preview showed a wrong colour, a wrapped price, or a missing photo.

### 8. Log

```sh
python3 ~/.claude/skills/deal-check/references/prices.py add run.json
```

Copy the full listing rows from step 3 into the folder it prints. Pass `--dir` when the profile names a folder other than `~/deals`.

Done when the script prints the rows it added and the folder holds `run.json` and the listing file.

### 9. Reply

The cards are already above the reply, so write only what they do not say:

- the pick per use, with the evidence that decided it;
- which evidence was "not found" on a pick, and what would settle it (try it on in a store);
- the terms that can cost the buyer: no returns, a minimum spend, an end date, an untested code;
- what to wait for and when.

When a sale event starts or a promo ends inside the next three weeks, offer one scheduled re-check on that date (`schedule_task`), and create it only on a yes.

## Working habits

- **Helpers.** Several stores go to helpers, one store each, all in the foreground of one turn. Each brief carries the brief from step 1, the terms to find, the `run.json` item fields, that store's section of `references/stores.md`, a ten-minute budget, and "return what you have and list what you could not check". One helper with five stores took 56 minutes while two with one or two stores took 9 and 12.
- **Second look at the same sale.** A follow-up in a later turn starts from the files on disk: browser state from the earlier turn is gone.
- **Compare like with like.** Match a model across stores by its article code, not its name; colours rarely match, so say when the other store's price is for a different colour.
