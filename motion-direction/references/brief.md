# The motion brief

Eight fields. Each one is a decision a builder would otherwise make by averaging, one component at a time. Write answers in the product's language, and give every field something a recording could show.

## Fields and where they go

| # | Field | Answer shape | Goes to |
|---|---|---|---|
| 1 | Mode per surface | Each surface, and whether it is **persuade** (landing, onboarding, launch video, celebration) or **operate** (lists, forms, settings, dashboards) | `DESIGN.md` → Motion |
| 2 | Three motion adjectives | Each with what it does on screen: "cozy: the hero takes its time, characters sway, nothing snaps" | `DESIGN.md` → Motion |
| 3 | Focal moment | One screen and one event that gets authored motion | `DESIGN.md` → Motion, and the first beat sheet |
| 4 | Frequency map | Each recurring interaction with how often a user meets it | `DESIGN.md` → Motion, as a short table |
| 5 | What never moves | Concrete places: "nothing near a focused field", "table rows never animate in" | `DESIGN.md` → Do's and Don'ts |
| 6 | Reduced motion | What a reduced-motion user sees for each kind of motion | `DESIGN.md` → Motion |
| 7 | Budget | Runtime weight per page, art weight per page, and the first-paint rule | `DESIGN.md` → Motion, or the motion decision record |
| 8 | Signature motion | One movement that is the product's own, reused where the brand speaks | `DESIGN.md` → Motion and Components |

An adjective with no visible consequence ("smooth", "modern", "premium") is a placeholder. Push until it changes a token, a runtime or a rule.

## 1. Mode

Persuade surfaces may carry the brand's voice in motion: one rehearsed focal sequence beats a reveal on every section. Operate surfaces use motion for feedback, state and continuity, stay fast, and never make the user wait for choreography. One product usually has both, so the mode goes per surface. A system of record's sign-in page can persuade once; its tables operate all day.

## 3. Focal moment

Take it from `design-direction`'s peak and end moments when they exist. One focal moment per surface; two cancel out. Good candidates: the first arrival (the hero, the sign-in plate), the core task succeeding (a streak landed, a puzzle finished, an order approved), an empty state turning into a first item. The focal moment is the only place the expressive tokens and a stateful runtime are allowed by default.

The first landing earns patience when the product's feel is calm: it is not rushed because the point is that people stop and look ([video at 2:30](https://www.youtube.com/watch?v=f-Ar8mwm3kQ&t=150s)).

## 4. Frequency map

| Meets it | Motion |
|---|---|
| 100+ times a day: keyboard shortcuts, command palette, tab switches, typing | None |
| Tens of times a day: hovers, row selection, toggles | Instant, or one fast colour or opacity change |
| Occasionally: dialogs, sheets, toasts, route changes | Productive tokens |
| Rarely or once: first arrival, success, celebration, empty to first item | Expressive tokens; the delight budget lives here |

## 6. Reduced motion

Reduced motion means fewer and gentler, not none. Movement, scale, parallax and loops go; opacity, colour and the state change itself stay. An entrance shows its finished state. A stateful character holds its rest pose and still changes state on input. A video keeps its cuts and drops its camera moves. Every runtime that is not plain CSS gates on the preference explicitly: Svelte's `prefersReducedMotion`, React's `useReducedMotion`, GSAP's `matchMedia`, a Rive input set from the media query.

## 7. Budget

Write three numbers and one rule: the motion runtime's weight per page (kB gzipped, plus any WASM), the art's weight per page, the longest a sequence may run before the user can act, and whether motion may depend on JavaScript for the first paint. The first paint rule decides more than any library comparison: only CSS plays before hydration.

## 8. Signature motion

One movement, reused so the product is recognisable in motion: a press-roller sweep that reveals art left to right, one spring that every panel settles with, a mark that draws itself in when a step completes. Good candidates come from what the brand already owns: its logo's construction, its illustration style, its material. It must survive on operate surfaces in a small form (a check drawing in, a panel's settle), so it cannot be a hero animation alone.
