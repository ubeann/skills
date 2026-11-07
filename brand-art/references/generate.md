# The generation loop

## One call

1. **References**: the hero first, then the one sheet panel closest to the new pose or subject. Two references by default, never more than three: one strong reference holds identity, several references get blended.
2. **Prompt**, from the template below.
3. **Cost**: quote it before the call (`higgsfield generate cost`, or the Recraft rate in `references/vendors.md`). A batch of more than five calls gets the owner's yes first.
4. **Call**, download into `raw/`, append the log line.
5. **Score** the raw file with `check.py` before the next call, so drift is caught one image in, not ten.

## Prompt template

```text
<identity_text, verbatim>                       mascot
<subject, from the subject vocabulary>          set and scene
<the one change: pose, action, prop or scene>
<rendering and light, from the bible>
Colours: <hex values with their roles>.
<composition: background, fill, safe zones>.
<prompt_suffix, verbatim>                       set and scene
No text, letters or numbers.
```

Add a line only when a result showed it was needed, and record why in the README (the handbook needed "the laptop body is navy or silver-grey, not orange").

## One change per call

Each call changes **one** thing from its reference: the pose, then the prop, then the background, each in its own call. A request that changes four things at once is followed literally and drops the style ([video at 7:14](https://www.youtube.com/watch?v=JDwxt9fHofk&t=434s)). Variations drift further from the base the longer a chain runs ([video at 5:48](https://www.youtube.com/watch?v=JDwxt9fHofk&t=348s)); when two in a row fail the check, start a fresh chat or call from the hero ([video at 3:06](https://www.youtube.com/watch?v=JDwxt9fHofk&t=186s)).

## Draft, rank, pick

For every target the owner chooses between (a hero, a world style frame, a banner, the first card of a set), the owner sees a ranked shortlist, never a raw batch:

1. **Draft** three or four candidates from one prompt in one call (`n` on Recraft's `generate_image` and `image_edit`) on a draft model from `references/vendors.md`: `gpt_image_2_low` with the hero for poses and expressions (each image tends to come back as a sheet of several poses), `recraftv4_1_flash_raster` for layouts that need no identity. Quote `n` times the rate first. A pick from a pose sheet is redrawn alone on the final model in step 4.
2. **Rank.** Run `check.py` on each, then the `art-critique` skill in a fresh subagent, handing it the candidates, the bible, the hero and the benchmark as paths and nothing else: no prompt, no plan, no opinion of yours. It drops every candidate it would regenerate and ranks the rest two at a time.
3. **Shortlist.** Show the owner the top two large, each with the critic's findings and its one change, and the others small beneath. When the critic drops every candidate, make the change its findings name (one change) and draft again; a round where nothing passed never reaches the owner.
4. **Finish the pick.** A pick drafted on a cheaper model or quality is redrawn on the final model as an edit of the pick, with "keep everything, final quality" as the one change, and critiqued again.
5. **Spread.** The pick becomes the reference for every sibling target: the world style frame in `references/compose.md`, a set's siblings, the rest of the cards. Each sibling is critiqued against the pick, so a sibling that drifts from it fails the One hand axis before the owner sees the set.

In the cast pilot every round went straight from generation to the owner, and the owner was the only critic: the world that read as AI slop, the stray rod and the smudge in the banner, the title over the art.

**Hero or chain.** Practitioners disagree on whether each image should come from the hero or from the previous approved image. Start every image from the hero; switch a run to chaining only when hero-based images keep failing the same check, and record which worked in the README.

## Poses

Describe the movement before the costume: the line of action and its energy, then the camera angle, then what the character wears ([video at 1:15](https://www.youtube.com/watch?v=t-8FuHla3H0&t=75s)). Vary the camera across a set ([video at 3:14](https://www.youtube.com/watch?v=t-8FuHla3H0&t=194s)). Tension comes from a lowered head, raised shoulders, straight arms and a curved spine ([video at 8:31](https://www.youtube.com/watch?v=t-8FuHla3H0&t=511s)); when a costume forces a calm pose, push the camera instead of the limbs ([video at 9:46](https://www.youtube.com/watch?v=t-8FuHla3H0&t=586s)). Faces follow `expressions.md`.

## Thumbnail round

Before a hero exists: four to six silhouettes on the cheapest model and quality, small, flat, no detail, as a gallery, numbered so the owner can answer with a number. Each differs from the last in its main shape. A family is judged as a lineup of three or more in one image: fit across a cast does not show in single images. The owner picks a silhouette and a direction, not a finished image. Sketching first keeps creative control; without a silhouette the model gives you something random.

## Where the mascot appears

Plan the uses before generating poses, so each expression maps to a state: the app icon, onboarding, empty states, loading, errors, success, and marketing ([video at 11:24](https://www.youtube.com/watch?v=JDwxt9fHofk&t=684s)). A mascot that appears in one place is a logo; one that recurs is a character people attach to.

## Log line

```json
{"t": "2026-11-03T10:00:00Z", "target": "empty-state", "vendor": "higgsfield", "model": "nano_banana_2",
 "refs": ["hero/hero-v1.png", "sheet/thinking.png"], "prompt": "...", "change": "holding a receipt",
 "cost": 2, "job": "<id>", "file": "raw/empty-state-1.png", "check": "pass", "kept": true}
```

The log is how the owner sees what a pack costs, and how a later session repeats a result.

## Comparing vendors

Run the same pack through each vendor before committing to one:

1. Six prompts from the targets, identical per vendor, each from the same hero and sheet panel.
2. Score every result with `check.py`, and have the owner rate each one 1 to 10 from the contact sheet.
3. Record per vendor: passes, average owner score, total cost, and time per image in `art/<name>/bakeoff.md`.

The vendor with the most passes and the highest owner score wins the family; a tie goes to the cheaper one.
