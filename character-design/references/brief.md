# The character brief

Ten fields and one table. Each is a decision the image model would otherwise make by averaging every mascot it has seen. Write them into `art/<name>/character.md`, under a first line `Status: draft`. Fields 1 to 5 hold for any form; fields 6 to 10 are written for the form the owner picked.

The examples follow one invented product: a plant-care app whose bet is that people overwater, so it tells them when to leave the plant alone.

## 1. Role

One sentence with a verb: what the character does for the user. It acts out the product's bet. Then every placement where it appears (app icon, onboarding, empty state, notification, widget, marketing).

> A toad that lives in the pot and tells you the soil is still wet. Icon, the home card of each plant, the "leave it alone" notification, the widget.

## 2. Personality

Three or four traits, each with a behaviour in a product moment, and one flaw. A trait with no behaviour is an adjective, and the model cannot draw an adjective.

| Trait | How it shows |
|---|---|
| Lazy on purpose | sprawls on the soil when nothing needs doing, which is most days |
| Protective | puffs up and blocks the watering can when the soil is wet |
| Flaw: naps through its own alarm | the reminder arrives with it yawning, a minute late |

## 3. Moments

The product moments the character acts, taken from `PRODUCT.md`'s key and hard moments. Each row names the moment, what the character is doing as a situation ("just noticed the can tipping"), and the placement. These rows become the expression list in `brand-art`, so an emotion word here returns the model's default face there.

## 4. Voice

Whether it speaks, in which person, how long its sentences are, and three sample lines for three moments (a success, a lapse, an error). A character that never speaks says so here.

## 5. Form shortlist

Three or four species or forms, at least one from the product's own world (its object, its place) rather than the animal kingdom.

| Form | Why it fits the bet or the name | Rivals holding it | Likely misread | Story in one line |
|---|---|---|---|---|

Count the rivals from the category. An App Store search for the product's job returns about 20 icons; save each app's `artworkUrl512` into `art/<name>/rivals/`:

```sh
curl 'https://itunes.apple.com/search?entity=software&limit=25&term=<job>'
```

A form several rivals already hold needs a reason strong enough to carry it, and its Forbidden rows (below) name what those rivals do with it.

## 6. Story

One paragraph: where it comes from, what it wants, why it is in this product. It explains at least one feature of the body and the role, and it can be retold in two sentences.

## 7. Body mechanic

The one thing the body does that shows the product's state. One simple body that squashes, stretches, puffs or melts carries more than any accessory: Duolingo's Duo is "very geometric and basically just a body with wings" ([Duolingo, Building character](https://blog.duolingo.com/building-character/)).

| Product state | The body |
|---|---|
| soil wet | puffed round, twice as wide |
| soil dry for days | flat, cracked at the edges |

The dynamic icon, the widget and the expressions all draw from this table.

## 8. Anatomy

Numbers, so the pick can be measured and the hero scored against it:

- **Height in heads**, and width against height.
- **Head and body**: one lump, or a head on a body, and where they join.
- **Eyes**: width as a share of the head, how far apart, how high on the head.
- **Limbs**: length against the body, and whether they have joints.
- **The pushed proportion**: the one feature exaggerated well past natural. Push it further than feels right; the model pulls every proportion back toward the average.

When the brief asks for cute, build it from the baby schema: "a large head, a high and protruding forehead, large eyes, chubby cheeks, a small nose and mouth, short and thick extremities, and a plump body shape". Large eyes alone raise perceived cuteness across expressions and ages ([Yao et al. 2022](https://www.frontiersin.org/articles/10.3389/fpsyg.2021.674456/full), which quotes Lorenz's list). In numbers: under two heads tall, eyes at or below the middle of the head, limbs shorter than the head is wide.

## 9. Signature and props

- **Signature**: one feature on the body that no rival has, on or near the head, because icons and avatars crop to the head. It comes from the story.
- **Props**: three to five tools from the business, each tied to a moment in field 3, each held or worn. A prop supports a moment; it never identifies the character.

## 10. Locked, flexible, forbidden

| Element | Rule |
|---|---|
| Locked | what never changes: the build in numbers, the eyes, the signature, the colours in hex |
| Flexible | what a moment may change: the body mechanic's range, pose, props, expression |
| Forbidden | the likely misreads from field 5, and the category's crowded symbols |

`brand-art` writes its identity text from the Locked rows and its nots from the Forbidden rows.

## References

| Reference | Job | What is taken | Everything else |
|---|---|---|---|

One reference per job, from the moodboard cards: `anatomy` (a build), `shape`, `pose`, `technique`.

## Three tests before the owner sees it

- **Swap**: put a rival's product name into the story. It stops making sense.
- **Bare**: cross every prop and accessory out of the description. What identifies the character is still there.
- **Meter**: cover the face. The body alone tells two product states apart.

A failed test changes the brief, and the round is drawn after it passes.

## Sketch prompt

```text
Pencil character sketch on plain white paper, one figure, full body, three-quarter front view.
<the form>, <the build: this sketch's proportions as numbers, the pushed one first>.
<the lead trait as a situation: what it is doing>.
<the signature, and where on the body it sits>.
Loose graphite line, one flat accent colour <hex> on the signature only. No text, letters or numbers.
```

One change per sketch: the form in the form round, the build in the anatomy round. Everything else in the prompt stays word for word, so the gallery compares one thing.
