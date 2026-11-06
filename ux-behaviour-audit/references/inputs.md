# Capturing the path

One branch per input: screenshots, a live URL, frontend code, or a native app. A mixed request (screenshots of the old flow plus the code for the new one) runs each branch it needs and labels every screen with where it came from.

## Screenshots

1. Open every image and put them in task order. Name each one by what the user is doing ("S3 choose bedrooms"), not by its filename.
2. Note the device class from the aspect ratio and status bar. Sizes are estimates: take a phone screenshot as 390pt wide and scale from there, and write "about" in any finding that uses a measured size.
3. List any state the task needs that is missing (the empty state, an error, the screen after the main action) and ask for those once, all together. Audit what you have while you wait.

The user's path is inferred from the images, so a tap count is a minimum. Say so on the report tile.

## Live URL

Walk the task for real. Each action you take is one the user takes, so the tap count comes from your own run.

1. Open the page with the browser tools the host offers. In T3 Code that is `preview_open`, `preview_navigate`, `preview_act`, `preview_snapshot`, and `preview_resize`. Otherwise load the `chrome-browser` or `built-in-browser` skill, or drive headless Chrome with Playwright.
2. Resize to 390 wide first and then to 1280. The phone pass is the one most findings come from.
3. At each screen, take a screenshot to a file, then evaluate `measure.js` (the file beside this one) in the page and keep the JSON for that screen. Record each action you take as one line: "tap Filters", "type 3 into Bedrooms".
4. Reach the states that matter: submit a form empty to see the error, clear the filters to see the empty state, complete the main action if it is safe and reversible. Do not complete a purchase, a payment, a message to a real person, or anything that cannot be undone. Stop at the confirmation screen and say that you did.
5. Close any tab you opened.

A page behind a login needs the user's session. Ask the user to sign in in the browser pane. Never ask for their password in chat.

## Frontend code

Rendered behaviour is the evidence, so run the app when you can.

1. Find the route or screen for the task: search the router config, page directories, and the component names that match the task's words.
2. Start the app with the `run` skill, open it, and follow the live URL branch. Cite the component file next to each finding so the fix has an address.
3. If the app cannot start (missing secrets, backend down), audit statically. Trace the task through the components and write each screen as the JSX tree the user would see. Every finding then carries a `file:line` and says that it was read from code, not seen.

Code signals that point at checks:

| Signal in code | Check |
|---|---|
| `<select>` or a dropdown component for a set of fewer than about eight options | D5 |
| Form state initialised to `''` or `null` where a common value is known | D1 |
| A submit button whose label has no count, total, or result | D2 |
| A stepper or counter component for a value users usually know | D6, A7 |
| One route or modal per filter or field in a multi-step flow | A1, O1 |
| A full-screen route for something that could be a sheet over its parent | O1 |
| An empty-list branch that renders only text (`length === 0 &&`) | O4 |
| Icon buttons with no `aria-label` or an explicit size below 44 | A3 |
| `position: fixed; bottom: 0` with no `env(safe-area-inset-bottom)` | A3 |
| Text drawn over an image with no scrim or container | T6 |
| A paywall, signup, or gate rendered before any result | T1 |
| Hard-coded counts, timers, or "was" prices in copy | Persuasion test 1 |
| Dismiss copy other than a neutral "Not now" | Persuasion test 4 |

## Native app (macOS, iOS, Android, desktop)

There is no DOM, so `measure.js` does not apply. The app is driven through whatever the project already uses to test itself.

1. Find the project's own driver before writing one: a skill or doc for agents in the repo (a `skill/` or `docs/agents/` folder), a test bench or socket the UI tests talk to, XCUITest or Espresso, or a script that launches a disposable copy of the app. Read its command list once and note the verbs for key presses, clicks, reading state, and screenshots.
2. Build the debug configuration and launch a disposable copy (a separate profile, data folder, or probe mode), never the user's own running app.
3. Capture each screen at the app's real window size, in light and in dark. Shrink each capture before reading it, as the working habit says.
4. Probe state with the driver rather than by looking: counts, focus, what a key did, what history holds. For a sweep over positions or cases, start with a handful of points, then refine only where the answer changes. A grid of hundreds of points over a socket takes minutes per run.
5. List what the driver cannot show. A hidden or off-screen window usually misses drags, context menus, system dialogs and motion; say so in the report's note, and use a recording or the user's hands for those.
6. Read the code beside each screen for what a picture cannot measure, and cite it as `file:line`: accessibility labels on icon buttons, the hit area of small controls, keyboard shortcuts and what a second press does.

On a desktop app the phone checks change meaning. A2 asks whether the main action sits where the pointer or the keyboard focus already is. A3 asks whether the hit area covers the whole visible control and whether every icon button has an accessible name. The frame's device names the platform and window size, not a phone width.

A second audit on the same app should not rediscover the driver: when the project keeps agent notes or memory, add the verbs and the capture recipe there once.
