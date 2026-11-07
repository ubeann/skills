---
name: art-critique
description: Judge illustrations, mascots, scenes, banners and cards cold, as a reviewer who never saw them made. Scores six axes (identity held, one hand, AI-default motifs, defects in full-size crops, composition, the art in its real placement with its copy), ranks candidates two at a time in both orders, and names the gap to premium per axis against a benchmark of professional work. Use when reviewing generated or hand-made art, picking the best of several generations, asking whether art looks premium or AI-made, or checking that copy on a card or banner does not break the art. Generating and fixing art is brand-art, which calls this skill at its gates; collecting the benchmark is moodboard; UI screens are impeccable or design-direction.
---

# Art critique

The agent that generated an image is the worst judge of it: it knows what it asked for and sees that. In this repo's cast pilot, the generating agent reported "character and world finally match" on a world that matched on nothing, then listed four mismatches as soon as the owner called it AI slop. The owner also caught two defects and a title over the art that the agent had shipped. This skill reads art **cold**: the pixels, the art bible and the benchmark, never the prompts, the plan or the maker's own verdict.

`<skill-dir>` below is the folder holding this file. The script needs Pillow.

## Steps

### 1. Gather the brief

Collect, by path:

- **The art**: every file to judge, at full resolution, and for a composed target its parts (the scene inside a card).
- **The art bible and hero**: `art/<name>/README.md`, `pack.json` and its hero when the art came from `brand-art`. Without a bible, ask the owner for the three words the art should be and the one thing it must never be, and judge against those.
- **The benchmark**: the three to five professional pieces the README lists as the bar, as moodboard folders (`$MOODBOARD_DIR/<id>/`). Without one, judge the six axes and say the premium comparison was skipped; offer to build a benchmark with `moodboard`.
- **The placements**: where each file ships and at what size (a README card at 260 px, a social preview at 600 px), and on which grounds.

When another skill or the maker asks for the critique, run it in a fresh subagent and hand it only these paths and the question. A brief that carries the maker's notes ("the world now matches the character") hands over the verdict it should be testing.

Done when every input above is a path that exists or is named as missing, and no prompt, plan or self-assessment is among them.

### 2. Look

```sh
python3 <skill-dir>/references/critique_sheet.py crops <art files> --out <scratch>/crops
```

Open every file it wrote: the whole image, the blurred greyscale value read, and every crop at full resolution. A defect that is a few pixels in a whole image read at 1024 is plain in a crop. Work one image at a time: open its files, write its findings down, then move to the next. Opened all at once, a set of ten layouts is more images than stay in view, and the first ones drop out before they are judged. For composed targets also write the placements sheet:

```sh
python3 <skill-dir>/references/critique_sheet.py inplace <art files> --width 260 --width 600 --out <scratch>/inplace.png
```

Done when every crop, value read and placement sheet has been opened.

### 3. Judge

Judge every image on every axis in `references/rubric.md`, reading `references/motifs.md` for axis 3. When the art has a pack, run `brand-art`'s `check.py` on it first and take its numbers as given; for a composed target take `compose_check.py`'s. Write each finding as a rubric row with its severity and the one change that fixes it, and give each image its verdict: pass, fix or regenerate.

On a re-critique, apply `references/rubric.md` (When to stop): only criticals and unwaived majors keep an image at fix, and a finding against something the owner chose goes to the owner as a question.

Done when every image has a verdict on all six axes, every fix names one change and a place in the image, and every motif row was checked.

### 4. Rank

Only when several candidates compete for one target. Drop every regenerate, keep at most six, then:

```sh
python3 <skill-dir>/references/critique_sheet.py pairs <candidates> --out <scratch>/pairs
```

Open the pair sheets in a shuffled order and judge each on its own: which of the two would you ship, by the rubric. Write the votes to a JSON file (`{"pair-01-ab": 1, "pair-01-ba": 2}`: 1 for the left, 2 for the right, 0 for a tie), then:

```sh
python3 <skill-dir>/references/critique_sheet.py tally <scratch>/votes.json --pairs <scratch>/pairs/pairs.json
```

Done when `tally` prints a ranking, every tie it lists is reported as a tie, and any position-bias warning was answered by judging the tied pairs again.

### 5. Benchmark

When there is a benchmark and the question is whether the art is premium, how to level it up, or this is a final pass before shipping:

```sh
python3 <skill-dir>/references/critique_sheet.py bench <image> --refs <benchmark images> --out <scratch>/bench-<name>.png
```

Fill the gap table in `references/rubric.md` (Premium) for each axis against each benchmark piece, then rank the gaps by how much each would move the whole piece.

Done when every benchmark piece was compared on every axis, and the top three gaps each name one change.

### 6. Report and record

Render in chat, worst first:

1. One line: ship, fix, or regenerate, and why.
2. The verdict table: one row per image, one column per axis.
3. The findings rows, critical first, then the top three benchmark gaps.
4. The ranking, when step 4 ran.
5. The sheets that show each finding: the crop with the defect, the bench sheet, the placements sheet.

When the art lives in `art/<name>/`, record each verdict for `brand-art`'s handover gate:

```sh
python3 <skill-dir>/references/critique_sheet.py record art/<name>/review.json <files> --verdict pass --note "<one line>"
```

Done when the report is in chat and every judged file in an `art/<name>/` folder has a critique entry in `review.json`.

## Working habits

- Judge the pixels. "Identity held" is a claim about the image, checked against the hero and `check.py`, never about the prompt that asked for it.
- Lead with the worst finding. A verdict that opens with what works buries the one thing that blocks shipping.
- One change per fix, aimed at a place: "redraw the sky with the cast's outline weight", not "make it more cohesive".
- A pass is a finding too: say which axis was closest to failing.
