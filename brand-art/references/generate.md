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
