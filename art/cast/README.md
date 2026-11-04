# Cast: one character, a costume for each skill

The repo's art: one ink-navy character, dressed for each skill's job. It replaced the glossy 3D vinyl set (the toolbox and one object per skill) on 2026-11-04. Made with the `brand-art` skill as its pilot; what the pilot taught is in [Notes for the brand-art skill](#notes-for-the-brand-art-skill).

## Files

| Path | What |
|---|---|
| `hero/hero-v1.webp` | the approved hero: front view, waving, no costume |
| `sheet/face-kit.webp` | 16 expressions; every costume's face is built from one of them |
| `raw/<skill>.webp` | the approved costume per skill, as generated |
| `cast.json` | per skill: colour, costume name, card tagline, peek crop (scale, centre x, top, angle); the banner rows |
| `cutout.py` | removes the plain white background, keeping enclosed whites (eyes, shoes, mittens) |
| `build.py` | builds everything below from the sources; `out/` is its cache and is not committed |
| `rounds/` | contact sheets of the four exploration rounds |
| `log.jsonl` | one line per generation call, with model and credits (exploration files it names were replaced by `rounds/`) |

`python3 art/cast/build.py --check <png>` writes:

| Output | Size | Where |
|---|---|---|
| `assets/skills/<skill>.png` | 256 px peek-crop tile | README skill table, at 48 px |
| `assets/icon-512.png`, `assets/favicon.ico` | 512 px, 16 to 64 px | the brand icon: the hero on cobalt |
| `assets/cards/<skill>.png` | 900 x 1200 | the cast section of the README, social posts |
| `assets/banner.png` | 1280 x 640 | README top, GitHub social preview |

## Identity

Paste verbatim at the start of every prompt, with `hero/hero-v1.webp` as the only reference:

> This exact character: a dark ink navy blob body with two-tone cel shading (lighter navy on the upper left, deeper navy underneath), a hand-inked outline thick outside and thin inside, big white round eyes with black pupils and tiny shine dots, white eyebrow strokes, a mouth drawn in white or open with a dark interior and red tongue, short navy tube arms ending in white mitten hands, short navy legs, white rounded shoes.

Then one change (the costume, its pose and its expression from the face kit), then:

> Full body, one figure, centred, filling about 75 percent of the frame, plain white background, a soft small oval shadow under it. The costume and props are bright and shaded with two tones, never navy. No text, letters or numbers.

Model: `gpt_image_2_medium` through Recraft's `image_edit`, 1:1, 7 credits per image.

## Art bible

| Field | Rule |
|---|---|
| Adjectives | **expressive**: every costume pulls a face from the kit and a pose with a line of action; **crafted**: hand-inked line, thick outside, thin inside, two-tone cel shading; **bold**: one dark silhouette that every costume colour pops off |
| Nots | no flat unshaded fill; no navy props (they vanish on the body); no stiff front pose for a costume; no text in the art |
| Shape | a soft bean, wider at the bottom; short tube arms, white mittens, short legs, white shoes |
| Face | white round eyes, black pupils with shine dots, white brow strokes; open mouths dark inside with a red tongue; marks around the head (question mark, sweat drop, sparkles, music notes) carry the emotion at small sizes |
| Line | ink `#141414`, thick on the silhouette, thin and tapered inside |
| Rendering | two-tone cel shading per colour, light from the upper left |
| Sticker | every placement gets a white outline with a thin ink rim (`build.py`), so the navy body reads on dark grounds |
| Composition | tile: peek crop, tilted 8 degrees, on the skill colour mixed 55% with white; card: the skill colour at 32% with a 62% panel the character breaks out of; banner: two staggered rows on cobalt `#2a46ff` |

| Skill | Costume | Expression | Colour |
|---|---|---|---|
| report-deck | the presenter: slide board with a bar chart, pointer | proud | tomato `#ff6b35` |
| report-web | the reader: a long scroll as a cape, reading glasses | focused | lemon `#ffd23f` |
| learn | the student: an open notebook as a hat, pencil | curious | mint `#3ecf8e` |
| video-context | the film buff: film-reel hat, film-strip scarf | delighted | hot pink `#ff5fa2` |
| ux-behaviour-audit | the detective: deerstalker, cape, magnifier, footprints | suspicious | teal `#14b8a6` |
| design-direction | the explorer: explorer hat, compass, pointing ahead | determined | violet `#8b5cf6` |
| moodboard | the collector: a pin board of swatches, pinning a card | happy | cork `#d9a066` |
| brand-art | the artist: beret, paint tube, brush, paint smear | smug | red `#ef3b36` |
| motion-direction | the conductor: baton, a swinging metronome | laughing | lime `#b6e33b` |

## Adding a skill

1. Pick a costume that wears or holds the skill's own object, a colour no other skill uses, and an expression from `sheet/face-kit.webp`.
2. Upload `hero/hero-v1.webp` to Recraft (`request_upload_url`) and run `image_edit` on `gpt_image_2_medium`, 1:1, with the identity text, the one change, and the closing text above. Check `get_user` before a retry: a dropped call can still be charged.
3. Save the pick as `raw/<skill>.webp`, add the skill to `cast.json` (and to a banner row), and append the call to `log.jsonl`.
4. Run `python3 art/cast/build.py --check /tmp/check.png`. Look at the tile at 48 px on both grounds, the card and the banner; tune the skill's `peek` in `cast.json` until the face fills the tile.
5. Add the README rows: the skill table and the cast grid.

## Notes for the brand-art skill

Kept for the skill update after the pilot. The owner is collecting more material on mascot design first.

- **Expression theory.** The skill asks for a face kit and emanata but does not teach how to build them. Add `brand-art/references/expressions.md`:
  - Brows are the strongest signal: inner ends up for worry or sadness, down for anger or focus, one raised for doubt or curiosity (Ekman's FACS; Scott McCloud, *Making Comics*).
  - Lids cut the eye white: a lowered top lid reads bored, smug or tired; a raised bottom lid reads happy; a flat top lid over the pupil reads angry (Preston Blair, *Cartoon Animation*).
  - Pupils: direction is attention, size is intensity (tiny means shock).
  - Mouth: shape plus interior (dark inside, teeth, red tongue); asymmetry makes it alive.
  - Emanata carry the emotion at icon size: sweat drop, anger vein, question mark, sparkles, Zz, a flush (Mort Walker, *The Lexicon of Comicana*).
  - McCloud's six basic emotions (joy, surprise, fear, sadness, anger, disgust), mixed, cover most sticker expressions.
  - One face formula per state (brows, lids, pupils, mouth, mark) generated all 16 of `sheet/face-kit.webp` correctly in one call.
- **Pose theory.** One line of action, squash and stretch, a silhouette that reads filled black, one idea per image (Disney's 12 principles; Blair).
- **Model sheet.** The owner's juice-box reference is the target layout: construction, turnaround, face kit, props, walk cycle on one sheet.
- **Rendering on a dark body.** Two-tone cel shading on navy is subtle but the owner preferred it to flat; props on a dark body need bright colours, since a navy notebook and a blue chair vanished.
- **One character, many costumes.** A single hero changed by costume per skill held identity on `gpt_image_2_medium` `image_edit` from one reference, 9 of 9 on the first try. The skill's mascot section assumes one mascot or a family of different mascots; add the costume-cast pattern.
- **Vendors.** Recraft MCP spends subscription credits; the REST API has its own balance (0 here), so an API key does not unlock the MCP's credits. When the MCP fails to connect in one session, a delegated fresh session connects. Measured costs: Recraft V4.1 vector 4, GPT Image 2 medium 7, Nano Banana 2 11, Nano Banana Pro 20. A call dropped mid-transport can still be charged; check `get_user` before retrying.
- **Rounds by lineup.** Judging three characters in one image showed family fit that single images could not.
- **Build, do not generate, the layout.** Tiles, cards and the banner are composed from cutouts in code (`build.py`), so text is never garbled and every figure stays exact. The skill's handover step could ship a template like it.
- **Cutouts.** A flood fill from the border over light, unsaturated pixels removes a plain white ground and the soft shadow and keeps enclosed whites; `Image.fromarray` can share a read-only buffer, so copy before `ImageDraw.floodfill`.

## Rounds

| Round | Credits | What | Decision |
|---|---|---|---|
| 1 | 42 | the old toolbox redrawn in 2D on four models | the owner dropped the toolbox for a cast |
| 2 | 29 | three object characters as one lineup, two face kits, two models | big eyes on GPT Image 2 medium |
| 3 | 28 | four base characters, each neutral, happy and in a test costume | the ink blob, one character in costumes |
| 4 | 14 | the ink blob with richer rendering, then in sticker poses | keep the shading and the poses |
| Final | 77 | face kit, hero, nine costumes | shipped |

Balance: 911 credits before, 714 after. That is 7 more than the logged calls add up to: the first face-kit call was interrupted, `get_user` showed no charge right after, and it was most likely billed later.
