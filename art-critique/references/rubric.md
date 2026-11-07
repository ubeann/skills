# The rubric

Six axes, judged per image. Each gets a verdict: **pass**, **fix** (one named change makes it pass), or **regenerate** (no single change will). An image's verdict is its worst axis.

Write every finding as a row:

| Image | Axis | Severity | What is wrong, where | The one change |
|---|---|---|---|---|
| card-learn | One hand | critical | the island has thin hatched lines; the character has one bold outline | redraw the ground with the character's outline weight, two flat tones, no hatching |

Severity: **critical** blocks shipping (identity lost, a defect a viewer notices, text that cannot be read); **major** a professional would send back; **minor** worth fixing in the same pass. Name the place in the image (the lid, the left hand, the top-right sky) so the fix can be aimed.

## 1. Identity held

The character or set is still itself. Read it against the hero and the identity text in the art bible:

- Every feature the identity text names is present, and every feature it rules out is absent (a mouth on a mouthless mascot, a sixth colour on a five-colour set).
- Proportions: head-to-body, eye size and spacing, limb length. The model pulls every proportion back toward the average, so a hero's pushed proportions are the first to drift.
- The silhouette fills its frame the way the hero does, at the same scale relative to its props.

`check.py` in the `brand-art` skill measures palette, value, texture and silhouette; its numbers come first when a pack exists, and this axis judges what they miss.

## 2. One hand

Every element looks drawn by the same artist in the same session. Compare the figure with the world, props and background across:

| Property | Same when |
|---|---|
| Line | one outline weight and colour on figure, props and world; interior lines the same thinner weight |
| Shading | the same number of tones per surface (two-tone cel stays two-tone everywhere) |
| Palette | the world uses the bible's colours; no colours from nowhere (the earthy olive under a navy-and-cream cast) |
| Light | one direction and one key colour on every object |
| Texture | grain, hatching or gloss on all of it or none of it |
| Detail | the same density: a flat figure in a densely rendered world reads pasted in |

This is where generated scenes fail most: the model draws the character from the reference and the world from its own default. A mismatch on any row is a **major**; on three or more rows it is a **regenerate**.

## 3. AI-default motifs

Read the image against `references/motifs.md`. Each motif found is a **major**, because it is what makes art read as generated, and generated-looking art is not premium however clean it is. Name the motif and its replacement from the bible's subject vocabulary or world rules.

## 4. Defects

Find them in the crops, never in the whole image: open every crop `critique_sheet.py crops` wrote.

- Hands and grips: what each hand holds, and whether it holds it by a real part (a toolbox by its handle, not by a stray rod).
- Faces: smudges, a second mouth, eyes that disagree in shape or direction, a stray mark near the mouth.
- Props: objects merged into each other, held by nothing, cut by another object at an impossible depth, an item repeated.
- Letters: any glyph or text-like squiggle the prompt did not ask for.
- Edges: halos from background removal, jagged cutout edges, a cropped limb at the frame.

Any defect a viewer notices at the art's real size is **critical**; one visible only in a crop is **minor**.

## 5. Composition

Read the blurred greyscale copy first: hierarchy is a value question.

- **One lead**: in the blurred copy one shape reads first, and it is the figure that matters.
- **Value pattern**: the lead separates from its ground by value, not only by hue or an outline.
- **The eye path**: from the lead to the next stop, and nothing at the edges pulls the eye out (a bright accent at the bottom edge, a high-contrast corner).
- **Breathing room**: calm areas where the eye rests, and where text will sit.

For banners and cards, `brand-art`'s `references/compose.md` holds the full rules; judge against them when the target is composed.

## 6. In place

The art as it ships, not as it was generated: `critique_sheet.py inplace` at every real display width, on every ground it ships on (a README card at 260 px in GitHub's light and dark themes, a social preview at 600 px).

- The face and the job still read at the smallest size.
- Text on or beside the art is readable and sits on calm ground; no generated element runs under it. `compose_check.py --bare` in `brand-art` measures this; its numbers come first when the layout has a bare render.
- Edges and corners hold on both grounds (no white box on a dark page, no halo).

## Premium: the benchmark comparison

"Better" is only answerable against something. The benchmark is three to five professional pieces the owner approved as the bar, listed in the art's README with what each is the bar for. Put the image beside each one (`critique_sheet.py bench`) and, per axis, write where ours falls short in one sentence and the one change that closes it:

| Axis | Benchmark | Gap | Change |
|---|---|---|---|
| One hand | Comfortest banner | its clouds use the figures' outline weight; ours are outlined thinner than the cast | regenerate the sky with the cast's outline weight named |
| Composition | Kiwi card | its lead fills 60% of the height; ours 40% | crop the scene window tighter on the figure |

Rank the gaps by how much they move the whole piece, and lead the report with the top three. Judge the benchmark's craft, never its look: a gap is "their line is one weight everywhere", not "theirs is painterly". The owner's style decides the look; the benchmark decides how well it is executed.

## Ranking candidates

Several candidates for one target are ranked by comparing two at a time, never by scoring each 1 to 10: absolute scores from a model judge drift between calls, and a model judging a pair prefers whichever comes first ([Zheng et al. 2023](https://arxiv.org/abs/2306.05685)). So every pair is judged twice with the order swapped, and a pair counts only when both orders agree. Screen out every **regenerate** on the rubric first, so the pairs compare only images that could ship.
