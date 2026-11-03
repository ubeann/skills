# Measuring a system

One recipe per input. `inventory.js` and `drift.py` sit beside this file; `<skill-dir>` is the folder holding `SKILL.md`.

## A rendered page: a reference URL, a website, a web app, Electron or Tauri

1. Open the page with the host's browser tools. In T3 Code: `preview_open`, `preview_resize`, `preview_evaluate`, `preview_snapshot`. Otherwise load the `chrome-browser` or `built-in-browser` skill, or use Playwright's `page.evaluate`.
2. Resize to each check width of the platform (`presets.md`), wait for fonts and images, and dismiss cookie banners and modals that are not part of the screen.
3. Evaluate the contents of `inventory.js` and save the returned object as `screen-<name>-<width>.json` in the scratchpad. Screenshot the same state.
4. Close any tab you opened.

On a **reference**, read only the parts its job needs:

| Job | Read from the inventory |
|---|---|
| Type | `roles` (family, size, weight, line height, letter spacing per element), then `type.sizes` for the full scale |
| Colour | `colour.areaShare` for the proportions, `colour.text` and `colour.background` for the values; the top non-neutral background is usually the primary |
| Surfaces and shape | `radius`, `shadow`, and the borders in `colour.border` |
| Pattern (one flow) | The screenshot only: which elements, in what order, at what size relative to each other |

On **your own screen**, run `drift.py` with every saved JSON. Mark user content and third-party embeds with `data-drift-ignore` so a user's avatar colours or an embedded map do not count as drift.

## A screenshot with no URL

Estimate. Take a phone screenshot as 390 wide and a desktop one as 1440 wide, and scale every measurement from that. Sample colours with an eyedropper (`sips` or Python's Pillow can read a pixel). Write "estimated from a screenshot" beside every value taken this way, and prefer a URL for the same product when one exists.

## A native app (SwiftUI, Jetpack Compose, Flutter, React Native)

There is no DOM, so read the code and confirm with screenshots.

1. Find where styles live: an asset catalog or `Color` extension, a `Theme`/`MaterialTheme`, `ThemeData`, a `StyleSheet` or theme object.
2. Search the UI code for literal values that bypass the theme. A literal where a token exists is drift.

   | Stack | Literal values to search for |
   |---|---|
   | SwiftUI | `.font(.system(size:`, `.padding(` with a number, `Color(red:`, `Color(hex:`, `.cornerRadius(` |
   | Compose | `.sp`, `.dp` literals outside the theme file, `Color(0x` |
   | Flutter | `fontSize:`, `EdgeInsets.all(` with a number, `Color(0x`, `BorderRadius.circular(` |
   | React Native | `fontSize:`, `padding`/`margin` numbers, `#` colour strings in `StyleSheet.create` |
   | Web (any) | Tailwind arbitrary values (`text-[13px]`, `p-[11px]`, `bg-[#...]`), inline `style=` |

3. Count the distinct sizes, weights, spacing values, colours and radii per screen file, and compare them with the budgets in `presets.md` by hand.
4. Run the app in the simulator and screenshot each core screen for the side-by-side check in step 6.

A React Native app with a web target can use the rendered-page branch on its web build.
