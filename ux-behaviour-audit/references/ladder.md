# The ladder

Rate each screen by **who does the work of the decision**. As the level rises, work moves from the user to the product. Pick the highest level whose test the screen fully passes.

| Level | Test | Typical signals |
|---|---|---|
| Junior | Looks simple, but the simplicity comes from moving work onto the user | One decision per page, options behind dropdowns, no outcome before the commit, flat hierarchy, mixed visual system, layout chosen to fit more above the fold |
| Mid | Related decisions sit together and the screen is easy to scan | Choices on one screen or sheet, visible options, clear hierarchy, one visual system, the outcome on the CTA ("Show 41 homes") |
| Senior | The interface gives the user context for the decision | Distribution behind a range slider, controls that match intent ("3+", icons for types), recognition cues, a user-chosen view where no default fits, specific trust signals in place |
| Staff | The product turns what the user actually knows into the decision it needs, and shows consequences before they choose | Budget from deposit and monthly payment drawn on the histogram, a count on every option, a "best match" from what is known about the user, a layout that holds whatever content arrives |

The staff level carries a cost: every extra piece of context makes the screen busier. A staff rating names that cost, and a screen that adds context that does not help this task's decision drops back a level.

## Calibration

The ladder cases in `case-studies.md` show one screen at four levels: CS01 (filter sheet), CS02 (restaurant list), CS03 (paywall), and CS06 (product page). Read the one closest to the screen you are rating before you rate it.
