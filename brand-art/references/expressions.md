# Expressions

Ask a model for "happy" and it returns its default face: the same open smile, round eyes, a still body. Build each expression from parts, give it a situation, and let the body act with the face.

## Face formula

Write every expression as one line: brows, lids, pupils, mouth, mark. In this repo's cast, 16 formulas in one call returned 16 correct faces (`art/cast/sheet/face-kit.webp`).

| Part | What it signals |
|---|---|
| Brows | The strongest signal. Inner ends up: worry or sadness. Inner ends down: anger or focus. One raised: doubt or curiosity (Scott McCloud, *Making Comics*; Ekman's facial action coding) |
| Lids | They cut the eye white. A lowered top lid reads bored, smug or tired; a raised bottom lid reads happy; a flat top lid across the pupil reads angry (Preston Blair, *Cartoon Animation*) |
| Pupils | Direction is attention (at the prop, at the viewer, away); size is intensity, tiny for shock |
| Mouth | Shape plus inside: dark interior, teeth, tongue. Asymmetry makes it alive. Without a nose, disgust is the upper lip lifted into an M, even with the mouth closed ([video at 5:45](https://www.youtube.com/watch?v=2OdCGrQGlHs&t=345s)) |
| Mark | The emanata around the head (sweat drop, anger vein, question mark, sparkles, Zz, a flush) carry the emotion at icon size (Mort Walker, *The Lexicon of Comicana*) |

## Rules

- **The situation, not the word.** "Just realised the stove is still on", "doing mental math", "saw something extremely cute". An emotion word returns the default face; a situation returns a specific one ([video at 12:33](https://www.youtube.com/watch?v=9WikScTxdbs&t=753s)).
- **Six basics, blended.** Joy, surprise, fear, sadness, anger and disgust mix into most others. Make a blend by swapping one feature of a kit face: surprise with worried brows is fear, sad eyes with a smile are bittersweet ([video at 3:17](https://www.youtube.com/watch?v=9WikScTxdbs&t=197s)).
- **Intensity is a ladder**: brows lower, teeth bare, a flush appears. On a cute character, creases appear only at the peak ([video at 3:34](https://www.youtube.com/watch?v=9WikScTxdbs&t=214s); [video at 2:41](https://www.youtube.com/watch?v=2OdCGrQGlHs&t=161s)).
- **Tension is irregular.** Lumpy brows and a wobbly mouth read fear or rage; smooth arcs read relaxed. Fear differs from surprise by tension, not by size ([video at 8:43](https://www.youtube.com/watch?v=2OdCGrQGlHs&t=523s)).
- **A real smile narrows the eyes**; a happy face with fully round eyes reads forced ([video at 1:38](https://www.youtube.com/watch?v=2OdCGrQGlHs&t=98s)).
- **The body acts with the face**: head lowered, shoulders up ("the shoulders are the eyebrows of the body"), hands clench, cover the eyes, grab the head. A strong face on a still body reads fake ([video at 8:23](https://www.youtube.com/watch?v=9WikScTxdbs&t=503s); [video at 3:13](https://www.youtube.com/watch?v=2OdCGrQGlHs&t=193s)).
- **A new head angle per expression**, and brows that tilt with the pose's line of action ([video at 12:19](https://www.youtube.com/watch?v=9WikScTxdbs&t=739s)).
- **A personality emotes its own way.** Pick three to five attributes for the character (an emoji each), decide how it shows anger or joy (yells or grits its teeth, laughs or smirks), and keep every expression inside that persona; the sheet's expressions follow the same mix as the attributes ([video at 1:27](https://www.youtube.com/watch?v=qO1DZCi27Xg&t=87s); [video at 8:52](https://www.youtube.com/watch?v=9WikScTxdbs&t=532s)).
