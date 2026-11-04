# Motion tokens

## Rules

1. **One token per job.** Name a token for what it does (`panel`, `exit`, `feedback`, `reveal`), never for its value (`fast`, `200`). Two tokens with the same job are drift.
2. **Two modes.** Productive tokens serve operate surfaces: short, decelerating, no overshoot. Expressive tokens serve persuade surfaces and the focal moment: longer, may settle or overshoot. IBM Carbon splits its motion the same way ([Carbon motion](https://carbondesignsystem.com/elements/motion/overview/)).
3. **Duration follows distance and consequence.** A small change near the pointer is fast; a large surface crossing the screen takes longer; leaving is faster than arriving.
4. **Delays and staggers are tokens too.** Choreography written as `animation-delay` arithmetic stays readable only when each delay has a name.
5. **Exits are faster than entrances**, and a deliberate action (hold to confirm, destructive confirm) is slower than the system's reply.
6. **Durations past 300 ms on an operate surface need a reason** written beside the token.
7. **The code is the source.** Tokens live where the runtime reads them (CSS custom properties, a theme file, native constants); `DESIGN.md` mirrors them, and a test keeps a JS mirror in step when one exists.

## Preset

Use when the product has no tokens. Values are a starting point; the brief's adjectives move them.

### Durations

| Token | Value | Job |
|---|---|---|
| `--duration-feedback` | 110 ms | press, toggle, copied value |
| `--duration-state` | 150 ms | hover-capable colour and opacity changes, icon swaps |
| `--duration-panel` | 240 ms | dialog, sheet, popover, toast arriving; card contents changing |
| `--duration-exit` | 160 ms | any of those leaving |
| `--duration-route` | 300 ms | a route or layout change, shared-element moves |
| `--duration-reveal` | 700 ms | the focal entrance's main reveal (expressive) |
| `--duration-settle` | 1200 ms | drifting parts coming to rest in a focal scene (expressive) |
| `--stagger` | 40 ms | between siblings of one list entrance; cap the whole list at 300 ms |

Carbon's own scale is 70, 110, 150, 240, 400 and 700 ms; snap custom values to it when in doubt.

### Easings

| Token | Value | Job |
|---|---|---|
| `--easing-standard` | `cubic-bezier(0.2, 0, 0, 1)` | most UI motion: decelerates into place |
| `--easing-enter` | `cubic-bezier(0.16, 1, 0.3, 1)` | confident arrivals |
| `--easing-exit` | `cubic-bezier(0.4, 0, 1, 1)` | leaving, quick start |
| `--easing-reveal` | `cubic-bezier(0.65, 0, 0.35, 1)` | a reveal across a whole surface (expressive) |
| `--easing-spring` | `linear(...)` | a damped settle where the runtime has no springs |

A `linear()` spring is a list of sampled points. Generate it from a stiffness and damping in a spring tool, then keep the stiffness, damping and overshoot in the token's comment so it can be regenerated.

### Springs

Runtimes with real springs (Svelte `Spring`, Motion, SwiftUI, Compose, Rive) take springs for anything the user can interrupt: drags, toggles pressed twice, sheets dismissed mid-flight. A spring retargets from where it is; a keyframe restarts from zero. Record springs as a token too: stiffness, damping and mass, or the platform's response and damping fraction, with overshoot at zero for operate surfaces.

## Existing tokens

On the existing branch, the code's tokens are the preset. Map each job in the brief to an existing token first. Add a token only for a job none covers, and record why in the token's comment and, where the project keeps them, a decision record. Literals the inventory reports off-scale are snapped to the nearest token with the same job, or promoted when the same value recurs for one job in three or more places.

Vendored components (shadcn, a UI kit) arrive with their own literals. Snap them to tokens when the component is touched, not in a sweep that rewrites the kit.
