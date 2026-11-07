# Cast: one character, a costume for each skill

The repo's art: one ink-navy character, dressed for each skill's job. It replaced the glossy 3D vinyl set (the toolbox and one object per skill) on 2026-11-04; on 2026-11-07 the cards and banner moved it into one valley world drawn in its own style. Made with the `brand-art` skill as its pilot; what the pilot taught is in [Notes for the brand-art skill](#notes-for-the-brand-art-skill).

## Files

| Path | What |
|---|---|
| `hero/hero-v1.webp` | the approved hero: front view, waving, no costume |
| `sheet/face-kit.webp` | 16 expressions; every costume's face is built from one of them |
| `raw/<skill>.webp` | the approved costume per skill, as generated |
| `scene/<skill>.webp` | that costume in its own spot of the valley world, for its card |
| `scene/banner.webp` | the whole cast around the giant toolbox, for the banner |
| `cast.json` | per skill: colour, costume name, tagline, expression, card line, peek crop (scale, centre x, top, angle); the banner's scene and copy |
| `cutout.py` | removes the plain white background, keeping enclosed whites (eyes, shoes, mittens) |
| `build.py` | builds everything below from the sources; `out/` is its cache and is not committed |
| `rounds/` | contact sheets of the exploration rounds |
| `log.jsonl` | one line per generation call, with model and credits (exploration files it names were replaced by `rounds/`) |

`python3 art/cast/build.py --check <png>` writes:

| Output | Size | Where |
|---|---|---|
| `assets/skills/<skill>.png` | 256 px peek-crop tile | README skill table, at 48 px |
| `assets/icon-512.png`, `assets/favicon.ico` | 512 px, 16 to 64 px | the brand icon: the hero on cobalt |
| `assets/cards/<skill>.png` | 900 x 1200, transparent corners | the cast section of the README, social posts: the scene in a square window, then name, expression and line on a paper plate |
| `assets/banner.png` | 1280 x 640 | README top, GitHub social preview: `scene/banner.webp` with the title in its calm upper-left sky |

## Identity

Paste verbatim at the start of every prompt, with `hero/hero-v1.webp` as the only reference:

> This exact character: a dark ink navy blob body with two-tone cel shading (lighter navy on the upper left, deeper navy underneath), a hand-inked outline thick outside and thin inside, big white round eyes with black pupils and tiny shine dots, white eyebrow strokes, a mouth drawn in white or open with a dark interior and red tongue, short navy tube arms ending in white mitten hands, short navy legs, white rounded shoes.

Then one change (the costume, its pose and its expression from the face kit), then:

> Full body, one figure, centred, filling about 75 percent of the frame, plain white background, a soft small oval shadow under it. The costume and props are bright and shaded with two tones, never navy. No text, letters or numbers.

Model: `gpt_image_2_medium` through Recraft's `image_edit`, 1:1, 7 credits per image.

## World

Every scene is one spot in the same valley, drawn exactly like the character. `scene/design-direction.webp` is the world reference: pass it third, after the hero and the costume, as "the third image shows the world style only: copy its drawing style, flat sky, rounded hills, path and colours, never its character or props". Then the spot (the skill's own props, three to five of them), then:

> World rules, strictly: every object has the same bold, even ink #141414 outline as the character's silhouette; no thin sketchy lines, no hatching, no texture, no grain, no gradients; every surface is exactly two flat tones, light and shadow, light from the upper left; simple rounded shapes. World colours only: sage green #a8c79a, sand #e8d3a8, warm grey #cfc6b8, pale sky blue #cfe3f7, cream #f6f1e7, plus small touches of the costume colours. The costume is the strongest colour in the image.
>
> Composition: square. The top 20 percent is plain flat pale sky with nothing in it: no sun, no clouds, no birds, no props. A low horizon of soft rounded hills at about half height. The character stands in the lower middle, filling about 60 percent of the frame height, feet a little above the bottom edge, never cropped. No text, letters or numbers anywhere.

The first scene test drew each costume on a floating island with a dirt cliff, hatching and earthy colours; it read as a stock diorama under a flat-shaded character (`rounds/round5-scene-test.jpg`). Three world treatments of one card (`rounds/round6-world-frames.jpg`) picked this one: a full-bleed scene in the character's own line and shading.

## Art bible

| Field | Rule |
|---|---|
| Adjectives | **expressive**: every costume pulls a face from the kit and a pose with a line of action; **crafted**: hand-inked line, thick outside, thin inside, two-tone cel shading; **bold**: one dark silhouette that every costume colour pops off |
| Nots | no flat unshaded fill; no navy props (they vanish on the body); no stiff front pose for a costume; no text in the art |
| Shape | a soft bean, wider at the bottom; short tube arms, white mittens, short legs, white shoes |
| Face | white round eyes, black pupils with shine dots, white brow strokes; open mouths dark inside with a red tongue; marks around the head (question mark, sweat drop, sparkles, music notes) carry the emotion at small sizes |
| Line | ink `#141414`, thick on the silhouette, thin and tapered inside |
| Rendering | two-tone cel shading per colour, light from the upper left |
| Sticker | icon tiles and the favicon get a white outline with a thin ink rim (`build.py`), so the navy body reads on dark grounds; scenes need none |
| Composition | tile: peek crop, tilted 8 degrees, on the skill colour mixed 55% with white; card: the scene in a square window with an ink border, the number in a skill-colour disc, name, expression chip and line on a paper `#f6f1e7` plate below, the skill colour as the card's rim; banner: the cast around one giant open toolbox in the valley sky, the plain hero on the lid as the lead, the title in the calm upper-left third |

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
3. Save the pick as `raw/<skill>.webp`, add the skill to `cast.json` with its expression and a line in its own voice, and append the call to `log.jsonl`.
4. Generate its scene: the hero, `raw/<skill>.webp` and `scene/design-direction.webp` as references, the identity text, the costume, the spot, and the World text above, 1:1. Save it as `scene/<skill>.webp` at WebP quality 90.
5. Regenerate the banner from `scene/banner.webp` with the new costume added as the one change, so the whole cast stays in it.
6. Run `python3 art/cast/build.py --check /tmp/check.png`. Look at the tile at 48 px on both grounds, the card and the banner; tune the skill's `peek` in `cast.json` until the face fills the tile.
7. Add the README rows: the skill table and the cast grid.

## Notes for the brand-art skill

What the pilot taught is now in the `brand-art` skill (2026-11-07): face formulas in `references/expressions.md`, costume and dark-body rules in the art bible, the costume pattern and sheet layout in the identity pack, Recraft costs and billing in the vendors file, and the layout round with `compose_check.py` in `references/compose.md`, after the banner and cards here shipped without one.

One gotcha stays with this folder: `cutout.py` floods from the border over light, unsaturated pixels, which removes the white ground and the soft shadow and keeps enclosed whites; `Image.fromarray` can share a read-only buffer, so it copies before `ImageDraw.floodfill`.

## Rounds

| Round | Credits | What | Decision |
|---|---|---|---|
| 1 | 42 | the old toolbox redrawn in 2D on four models | the owner dropped the toolbox for a cast |
| 2 | 29 | three object characters as one lineup, two face kits, two models | big eyes on GPT Image 2 medium |
| 3 | 28 | four base characters, each neutral, happy and in a test costume | the ink blob, one character in costumes |
| 4 | 14 | the ink blob with richer rendering, then in sticker poses | keep the shading and the poses |
| Final | 77 | face kit, hero, nine costumes | shipped |
| 5 | 28 | three cards and the banner as generated scenes | scenes, not collages; the island world reads generic |
| 6 | 28 | one card in three world treatments, the banner redrawn flat | B: a full-bleed scene in the character's own style |
| 7 | 63 | nine card scenes in that world | shipped, with the text on a plate below the art |

Balance: 911 credits before the pilot, 714 after its final round, 595 after round 7. That is 7 more than the logged calls add up to: the first face-kit call was interrupted, `get_user` showed no charge right after, and it was most likely billed later.
