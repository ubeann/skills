# The style round

An owner who cannot choose a style is usually being asked to choose between other people's art. References each carry their author's style, and a style copied from a reference brings that author's identity with it, so changing style toward a reference loses the owner's. The style round shows the owner **their own character** drawn in three or four researched directions, so the choice is between versions of their own work.

Run it when the bible's style fields (line, rendering, light, palette, texture) are not yet decided, when the owner wants to change them, or when a new kind of image (a world, a scene family) needs a style the bible does not cover. In the cast pilot the world's style was never chosen: the first scenes fell back to the model's default floating island, and the world style was picked only in round 6, after the owner called it AI slop.

## Identity and style

Split the art bible in two before anything is generated. Identity is locked; style is what the round varies.

| Locked: identity | Varied: style |
|---|---|
| silhouette and primary shape | line: none, one weight, or inked thick and thin, and its colour |
| proportions, written as numbers | rendering: flat, flat with grain, soft 3D, painterly, paper cut |
| the face: eyes, the face kit, what it never has | shading steps and the light's direction and colours |
| the one memorable feature | palette roles beyond the identity colours |
| costume logic and the signature quirk | texture, and the world's treatment |

A reference may lend only cells from the right column, each as a named technique. An identity cell borrowed from a reference is a new character, not a new style.

## Steps

1. **The subject.** The approved hero when one exists, else the owner's seed, else the silhouette picked in a thumbnail round (`references/generate.md`). One subject, one pose, for every direction.
2. **Research three or four directions.** Draw from the owner's references, the `moodboard` library's trend table (`library.py trends`) and the art's benchmark. Each direction gets a card:

   | Field | What goes in |
   |---|---|
   | Name | a working name plus its techniques from moodboard's vocabulary (`flat-vector` with a tinted ink line) |
   | Evidence | two or three references by author, and how many authors use it now from the trend count |
   | Lends | the style cells it sets, one value each |
   | Risks | what it costs the identity or the product: a painterly world under a flat character, grain that turns to noise at 48 px |
   | Cost | credits per image at the final model, and whether the rest of the targets can be made in it |

   Make the directions differ in at least two style cells each, so the gallery shows a real choice, and keep one close to what the owner has now as the baseline.
3. **Draw the subject in each direction.** One call per direction from the subject, with the style cells as the one change and the identity text verbatim; then one scene per direction, so the world is judged with the character in it. Quote the round first: about two calls per direction.
4. **Critique.** Run the `art-critique` skill cold on every frame, with the identity text and the hero as the brief. A direction whose frames fail Identity held is dropped, or redrawn once with the critic's fix; a direction whose world fails One hand is reported with that finding.
5. **Show one gallery.** A row per direction: its frames large, its card beneath, the critic's verdict in one line. Recommend one, and say what the owner gives up by choosing each of the others.

Done when the owner picked a direction, and its style cells are written into the art bible's line, rendering, light, palette and texture fields with the frames saved in `art/<name>/rounds/`.

A change of style on an approved hero starts a new pack version: `pack.json` `version` goes up and the picked frame becomes the new hero, still scored against the old one for identity.
