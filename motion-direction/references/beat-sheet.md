# Beat sheets

## The build contract

What the builder receives, whether it is you, a subagent, `impeccable`, the Rive CLI or `hyperframes`: the beat sheet, the tokens, the runtime from step 4, and the style frames when there is art. Nothing else; another reference at this point pulls the build away from the sheet.

```text
Build <sequence> exactly as the beat sheet says, in <runtime>.
Every duration, delay and easing is a token from <token file>; no literals.
Each beat ends on the end state in its row. Stateful pieces return to rest.
Implement the interruption and reduced-motion rows as written.
When you deviate on purpose, keep going, and list each deviation:
| Beat | What the sheet says | What you built | Why |
```

## Sequence

```markdown
### <sequence name>

One line: <what the viewer should feel or understand, in one sentence>
Surface and mode: <surface>, <persuade|operate>
Trigger: <first paint | route change | click on X | element enters viewport | state change>
Total: <ms until the user can act> / <ms until everything rests>

| # | Start | Duration | Element | From → to | Technique | Easing | Sound |
|---|---|---|---|---|---|---|---|
| 1 | 0 | --duration-reveal | hero plate | mask at 0% → 100%, left to right | mask reveal | --easing-reveal | none |
| 2 | --delay-sky | --duration-settle | sky layer | opacity 0, x +2.5rem → 1, 0 | settle | --easing-settle | none |

Interruption: <what happens when the user acts mid-sequence: it jumps to the end state, it retargets, it keeps playing>
Reduced motion: <what is shown instead: the finished state, a cross-fade>
Never moves: <what stays still during this sequence>
```

Name each technique with one term from `animation-vocabulary` or this list: fade, slide, scale-in, pop, mask reveal, clip reveal, stroke draw, stagger, shared element, layout (FLIP), cross-fade, morph, follow path, parallax, scrub, pin, spring settle, overshoot, particles, shader, flipbook, rig.

## State table

For anything with states: a Rive character, a toggle with a drawn icon, a multi-step form's progress mark.

```markdown
| State | Enters from | Input | Motion | Returns to | Loops |
|---|---|---|---|---|---|
| rest | start, every state | | breathing on its own layer | | yes, pauses off screen |
| wave | rest | trigger `hover` | arm up, two waves, arm down | rest | no |
| celebrate | rest, wave | trigger `streakLanded` | jump, squash on landing, sparkle | rest | no |
| streak | any | number `streakDays` | badge counts up to the value | (layer) | no |
```

Every row except `rest` names `rest` (directly or through another row) in "Returns to". A state that cannot get back to rest is the bug to fix before any motion is built.

## Video

A launch video adds three things to the sequence sheet.

**Director's brief.** Film in one line; the references, each with its job; the tools and skills to load; a character bible (every angle, proportion and expression of each character, from `brand-art`); the beat sheet; every line of on-screen text; the gates; the critique loop; the deliverables (sizes, lengths, formats). A brief with this skeleton gave much better results than a one-line prompt ([video at 16:30](https://www.youtube.com/watch?v=747ZnEtsRbg&t=990s)).

**Shot list.**

| Shot | Start | Length | What is on screen | Camera or container move | Transition out | Text on screen |
|---|---|---|---|---|---|---|

**Beat grid.** When there is music, measure it first and write `beats.json` (BPM, beats, downbeats, hits), then put every cut and every entrance on a beat ([video at 14:37](https://www.youtube.com/watch?v=747ZnEtsRbg&t=877s)). Without music, use one tempo for the whole film.

Gates, in order, each approved before the next: style frames as stills, the beat sheet, a 480p draft, the final render ([video at 19:30](https://www.youtube.com/watch?v=J4oygRI6mN0&t=1170s)). Generated footage follows the same order: character sheet, location, the two combined, every shot as a still, then motion ([video at 13:01](https://www.youtube.com/watch?v=J4oygRI6mN0&t=781s)).

## Reading a reference clip's grammar

Take the grammar of the reference, never its content, logos or characters ([video at 11:32](https://www.youtube.com/watch?v=747ZnEtsRbg&t=692s)). Extract frames finely enough to time it:

```sh
INTERVAL=0.5 sh ~/.claude/skills/video-context/references/extract.sh <url-or-file> <tmp-dir>
```

For a stretch under five seconds, trim it and extract at `INTERVAL=0.1`. From the frames, write:

| Measure | How to read it from frames |
|---|---|
| Shot length | frames between cuts × interval |
| Entrance duration | frames from first visible to settled × interval |
| Easing personality | where the distance is covered: early (decelerating), evenly (linear), late (accelerating), past and back (overshoot) |
| Transition types | cut, cross-fade, push, mask, shared element, morph |
| How text enters and exits | whole, per line, per word, per letter; from which side |
| Camera and container moves | static, push in, pan, one container that never cuts |
| Texture | grain, blur, light, colour treatment |

Write the readings into the sequence's notes, snap each duration to the nearest token, and drop everything else the clip shows.
