# Skill characters

The toolbox (`assets/icon-512.png`) is the repo's mascot. Each skill gets one character of its own: the object the skill's work produces or uses, given the toolbox's face and material. Made with the `brand-art` skill on 2026-11-03.

## Shared rules

Every character is generated with `identity.txt` pasted verbatim at the start of the prompt, then one subject sentence, with the toolbox as the only reference image. The rules it fixes:

- glossy soft vinyl toy, chunky and rounded, about one head tall, light from the upper left
- the face is exactly two black vertical oval eyes, each about one eighth of the character's height, set wide on the lower third of the front; no mouth, nose, brows, arms or legs
- one main colour from the toolbox palette (orange `#f1721a`, light orange `#fb9837`, red `#c02718`, blue `#2448e0`, navy `#292e76`), at most one secondary
- the object is the skill's own metaphor, and its silhouette differs from every other character

The eye-size clause was added after the first round; report-deck, report-web, video-context, design-direction and moodboard were made before it.

## Characters

`characters.json` holds each subject sentence, the model and the Higgsfield job ID.

| Skill | Object |
|---|---|
| report-deck | a stack of slides with a bar chart |
| report-web | an unrolled scroll |
| learn | a notebook with a ribbon bookmark |
| video-context | a film reel |
| ux-behaviour-audit | a footprint with a trail |
| design-direction | a pocket compass |
| moodboard | a cork pin board |
| brand-art | a paint tube |

## Adding a character for a new skill

1. Pick the object from what the skill does, not a stock symbol for its topic, with a silhouette unlike the others.
2. Generate three tries on Seedream 5.0 Pro (`higgsfield generate create seedream_v5_pro --resolution 1k --aspect_ratio 1:1 --image-references assets/icon-512.png --prompt "<identity.txt> <subject>"`), or the same model on BytePlus.
3. Pick the try that reads at 32 px and in greyscale, and stands beside the others as one family.
4. Remove the background (`image_background_remover` on Higgsfield, `remove_background` on Recraft). A remover can delete a white area enclosed by the object, such as the compass face: fill enclosed transparent holes back from the original.
5. Save the cutout as `hero/<skill>.png`, add the skill to `characters.json`, run `python3 art/mascots/export.py --check /tmp/check.png` from the repo root, and look at the check sheet on both backgrounds.
6. Add the icon row to the README table.
