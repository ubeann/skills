# System rules and platform presets

The rules hold on every platform. The presets are starting values; a reference measured in step 3 replaces the values its job covers. `drift.py` enforces the budgets in the last table.

## Rules for every platform

**Type**
- One family. A second only for a stated job: tabular or monospace figures for big numbers ([video at 13:07](https://www.youtube.com/watch?v=86PGRyQjdzQ&t=787s)), or a display face kept to selling surfaces.
- Few sizes and weights on any one screen: count them, then merge until the per-screen budget holds ([video at 3:10](https://www.youtube.com/watch?v=86PGRyQjdzQ&t=190s)).
- To borrow a scale, inspect a reference's text in DevTools Computed and copy family, size, weight, line height and letter spacing per role ([video at 1:15](https://www.youtube.com/watch?v=PGQnGEH7c-E&t=75s)).
- Copy says it once. A label never repeats its heading ("Votes" under a "Voting" heading, not "Last 10 votes") ([video at 10:43](https://www.youtube.com/watch?v=86PGRyQjdzQ&t=643s)).

**Spacing**
- Every value comes from a 4-based scale ([video at 4:03](https://www.youtube.com/watch?v=86PGRyQjdzQ&t=243s)).
- Space by relationship: a base gap inside a group, twice that between groups, more between sections ([video at 3:19](https://www.youtube.com/watch?v=PGQnGEH7c-E&t=199s)).

**Colour**
- Three roles: a base for backgrounds, a primary for actions and a few details, a neutral for text ([video at 9:40](https://www.youtube.com/watch?v=PGQnGEH7c-E&t=580s)).
- By area, roughly 60 neutral, 30 complementary, 10 brand ([video at 2:43](https://www.youtube.com/watch?v=86PGRyQjdzQ&t=163s)). A brand colour on every element stops meaning anything.
- New steps of hierarchy come from tints and shades of the same hue ([video at 9:36](https://www.youtube.com/watch?v=86PGRyQjdzQ&t=576s)), or from the neutral at reduced opacity for secondary text (about 80% and 60 to 70%) and the primary at about 5% for quiet surfaces ([video at 10:33](https://www.youtube.com/watch?v=PGQnGEH7c-E&t=633s)). Check contrast on every one.
- Error, warning and success colours are reserved for those meanings.
- Every role gets a dark-mode value when the product has a dark mode.

**Shape and depth**
- One radius family. A nested corner is concentric: inner radius = outer radius minus the padding between them. Use the platform's continuous corner where it has one ([video at 5:42](https://www.youtube.com/watch?v=doiaMtD80p8&t=342s)).
- One shadow recipe per elevation level, at most three levels.

**Composition (websites)**
- A max-width container and equal grid chunks give structure ([video at 6:45](https://www.youtube.com/watch?v=PGQnGEH7c-E&t=405s)); then break the grid once or twice on purpose, such as a carousel bleeding off the edge or one centred call to action ([video at 7:36](https://www.youtube.com/watch?v=PGQnGEH7c-E&t=456s)).

## Presets

| | App (phone) | Website | Desktop app |
|---|---|---|---|
| Type roles | display 28 to 34, title 20 to 22, body 16 to 17, caption 12 to 13 | H1 48 to 72 (36 to 40 on phones), H2 32 to 40, H3 20 to 24, body large 18 to 20, body 16, small 14 | heading 20 to 24, title 15 to 17, body 13 to 14, secondary 12 |
| Weights | regular and semibold | regular and semibold, plus one display weight | regular and semibold |
| Spacing scale | 4, 8, 12, 16, 24, 32 | 8, 16, 24, 32, 48, 64, 96, 128, 160 | 4, 8, 12, 16, 24, 32 |
| Key spacing | screen margin 16 to 20, group gap 8 to 12, section gap 24 to 32 | container 960 to 1200, text column at most 600 to 680 ([video at 5:04](https://www.youtube.com/watch?v=PGQnGEH7c-E&t=304s)), section padding 96 to 160 desktop and 64 to 96 phone ([video at 5:15](https://www.youtube.com/watch?v=PGQnGEH7c-E&t=315s)), card padding 24 to 32 | row height 28 to 36, toolbar 40 to 52, sidebar 220 to 280 |
| Targets | at least 44 pt (iOS) or 48 dp (Android) | 44 on touch, 24 minimum on pointer | 24 minimum, 28 to 32 typical; visible keyboard focus |
| Radius | 8, 12, 16, full for pills; sheets 16 to 24 | 8 to 16 on cards; buttons match the cards or go full | 4 to 8 on controls, follow the OS for windows |
| Check widths | 360, 390, 430 | 390, 768, 1280, 1440 | 1024, 1280, 1440 |

Sizes are in px, or pt and dp on native. The target minimums come from Apple's and Google's guidelines and WCAG 2.2.

## Budgets `drift.py` enforces

| | App | Website | Desktop |
|---|---|---|---|
| Font sizes on one screen | 4 | 6 | 5 |
| Font sizes in the token system | 6 | 8 | 7 |
| Weights on one screen | 2 | 3 | 2 |
| Families | 2 (one plus figures) | 2 | 2 |
| Radius values on one screen | 3 | 4 | 3 |
| Shadow recipes on one screen | 3 | 3 | 3 |
| Spacing values off the 4 grid | 0 | 0 | 0 |
| Text, background and border colours off the palette | 0 | 0 | 0 |

A screen that needs more than its budget is usually two screens, or a screen with a component from another system in it.

## DESIGN.md format

The file `impeccable` and other DESIGN.md-aware tools read: YAML frontmatter with the tokens, then up to eight sections in this order. Omit a section rather than fill it with invented rules.

```markdown
---
name: <product>
description: <one-line tagline>
colors:
  base: "#faf7f2"        # source: brief (calm)
  primary: "#1f6f5c"     # source: R2 colour reference
  neutral: "#1d1b18"     # source: preset
typography:
  title:
    fontFamily: "Inter, system-ui, sans-serif"   # source: R1 type reference
    fontSize: "22px"
    fontWeight: 600
    lineHeight: 1.25
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: "8px"
  md: "12px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.base}"
    rounded: "{rounded.md}"
    padding: "12px 20px"
---

## Overview
## Colors
## Typography
## Layout
## Elevation & Depth
## Shapes
## Components
## Do's and Don'ts
```

Token values are exact CSS values (hex, px, rem, unitless line height, `clamp()` for fluid type). `drift.py` reads `colors`, `typography`, `rounded` and `spacing`; component tokens reference those with `{group.name}`.
