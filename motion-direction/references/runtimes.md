# Runtimes

Pick the cheapest runtime that does the job, and only one per job. A decision record the project already has outranks this file.

## By job

| Job | First choice | Step up when | Step up to |
|---|---|---|---|
| Press, hover, toggle, copied value | CSS transition | never | |
| Dialog, sheet, popover, toast | CSS, or the framework's transitions | it must be dismissed by drag, mid-flight | a spring (Svelte `Spring`, Motion) |
| List add, remove, reorder | FLIP: `animate:flip`, Motion `layout`, View Transitions | | |
| Route or layout change | View Transitions API (`onNavigate` in SvelteKit, the router's hook elsewhere) | the browser lacks it | let it cut; it is an enhancement |
| Entrance on the first paint | CSS keyframes | | |
| Line art drawing itself in | SVG `stroke-dashoffset` in CSS | | |
| Scroll-linked progress or reveal | CSS scroll-driven animations behind `@supports` | pinning, scrubbed choreography across sections, split text | GSAP ScrollTrigger |
| Interactive or stateful character, illustration with states | Rive | | |
| A loop or loader reused across web and native | dotLottie | web only | CSS or SVG |
| Launch video, social clip, product explainer | HyperFrames | the team writes React video | Remotion |
| A flat mascot or mark turning in depth | SVG plane stack (below) | it must turn all the way round or take real light | Three.js |
| 3D | one Spline or Three.js hero | a 3D character with a rig | Blender (driven through Blender MCP) to GLB, `gltfjsx` to components, React Three Fiber to stage it |

## Weights and terms

Measured 2026-09-30 with esbuild and gzip or brotli ([VMB research](https://github.com/ubeann/vmb/blob/main/docs/research/motion-library-for-ui-feedback.md)). Re-measure before quoting them in a new decision record.

| Runtime | JS, gzipped | Other | Terms and gotchas |
|---|---|---|---|
| CSS, View Transitions, WAAPI | 0 | | Only CSS plays before hydration. |
| Svelte built-ins | in the framework | | Svelte transitions do not play on the hydrated first paint. |
| Motion, vanilla `animate` | 3.9 kB (mini), 20.2 kB (hybrid) | | MIT. Does not honour reduced motion on plain elements by default (tested). |
| GSAP | 27.6 kB core, up to 43.2 kB with SVG plugins | | Free for commercial use since 2025-04-30 under Webflow's own licence, which Webflow may change; not open source. |
| Rive | 49.5 to 57.8 kB | 279 to 717 kB brotli WASM | Runtime MIT. The canvas is blank until the WASM arrives; CSS masks and tokens do not reach inside it. Exporting without the splash needs a paid plan. |
| lottie-web | 48.9 to 78.7 kB | | Authoring needs After Effects with Bodymovin, or Lottie Creator. |
| dotLottie | | 388 kB brotli WASM | State machines and theming live in the `.lottie` file. |
| HyperFrames | renders offline | headless Chrome and FFmpeg | Apache 2.0; renders HTML with GSAP, Lottie or WAAPI to MP4. |
| Remotion | renders offline | | Check its licence page before commercial use by a company. |

## Library skills install per project

A runtime's official skill goes into the project that adopted it, from that project's root, without `-g`:

```sh
npx skills add greensock/gsap-skills -a claude-code -y -s gsap-core -s gsap-scrolltrigger -s gsap-timeline
```

GSAP's skills tell the agent to recommend GSAP whenever no library is named, so a global install argues against every project that ruled it out. Principle skills (`review-animations`, `animation-vocabulary`, `find-animation-opportunities`, `motion-design`) and video skills (`hyperframes`, `hyperframes-cli`) are global.

## Scroll motion

- Scroll-linked motion earns its place when the scroll itself carries meaning: progress through a story told in order, a pinned before-and-after, a number that grows as the reader reaches it. A reveal on every section is the average.
- Content is visible in the default state; motion is the enhancement. Gate CSS scroll timelines with `@supports (animation-timeline: view())`: Chrome has shipped them since 2023 and Safari since 26, but Firefox still kept them behind a preference in mid-2026 ([status, June 2026](https://www.buildmvpfast.com/blog/css-scroll-driven-animations-replace-js-2026)).
- Never change the scroll speed or capture the wheel. Keep pinned stretches short on phones.
- Reduced motion drops parallax, scrub and pinning, and shows every section finished.

## SVG plane stack

Depth from a flat shape with no 3D runtime ([post](https://x.com/dom_scholz/status/2117683798678835316)): each subpath of the character's SVG (each `M` command starts one) becomes a part; each part is copied into many flat planes stacked front to back with CSS 3D transforms (`transform-style: preserve-3d`, a `translateZ` step per plane). Filled in one flat colour, the planes merge into a solid with no visible seams. Plane spacing sets the thickness, and the part with the eyes sits on the front plane. Past about 45° the stack shows its slices edge-on, so turning further swaps in side planes or stops there. Each frame then moves a few transforms on the whole stack, so it costs what a CSS transition costs. It suits flat-vector mascots from `brand-art`; shaded or soft-3D art reads as a stack of cutouts.

## Rive for a stateful character

- **Art arrives as parts.** One flat image does not rig: a mascot built from one generated image moved clunkily, and got cleaner only when the same character was generated in more poses ([video at 8:30](https://www.youtube.com/watch?v=Hrcq00y9EhU&t=510s)). Ask `brand-art` for the parts pack: body, head, each eye open and closed, mouth shapes, limbs and props on separate layers, as SVG, plus a style frame per state.
- **Every state returns to rest.** Design the state machine with one rest (idle) state, and give every reaction a way back to it, so any reaction can start from any moment ([video at 19:01](https://www.youtube.com/watch?v=f-Ar8mwm3kQ&t=1141s)). Put the always-on layers (breathing, blinking) on their own layer so they run under every state.
- **Inputs, not timelines.** Triggers for one-shot reactions (wave, celebrate), booleans for modes (hovered, asleep), numbers for levels (a streak count), bound through a view model so the app sets values and Rive decides the motion.
- **Author with the CLI.** `rive create <name>` scaffolds a project with `AGENTS.md` and `CLAUDE.md`; the agent writes RML, scripts and shaders; `rive <dir>` previews and reloads on save; `rive <dir> --verify`, `rive inspect --summary` and `rive <dir> --screenshot` check the work; `rive docs` and `rive schema` look up types ([Rive CLI](https://rive.app/docs/cli/agents)). The desktop editor also has an MCP in early access.
- **Ship it lazily.** Self-host the WASM, load it after the page is usable, show the rest pose as a static image until it is ready, pause it off screen, and set a reduced-motion input from the media query that holds the rest pose.
- **When not to use it.** A one-shot entrance is simpler in CSS, and hand-built Rive art can come out weaker than generated art: VMB tried both and kept CSS ([VMB design workflow](https://github.com/ubeann/vmb/blob/main/docs/agents/design-workflow.md)).
