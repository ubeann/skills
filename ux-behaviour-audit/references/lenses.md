# The six lenses

Each lens is one kind of behaviour a screen can block. Every check has an id (used in findings and in the report matrix), the check, and the **failure signal** you can see on a screen. The examples come from UX Peak redesign breakdowns. They show what passing looks like, not the only way to pass.

## Decide: can the user choose without guessing?

| Id | Check | Failure signal | Passing example |
|---|---|---|---|
| D1 | Fields arrive pre-filled with the most common choice, and the user can see and change it | Several empty fields before anything happens | Booking form pre-filled with typical dates and guests, button reads "Search 12 results" |
| D2 | The outcome shows before the commit | CTA says only "Show results", "Reserve", "Send"; the count, total, or new state appears after the tap | "Show 41 homes", "Reserve €445 total", new balance shown before confirming a transfer, total price inside Add to cart |
| D3 | Each option shows its consequence before it is chosen | User picks, sees what happened, goes back, tries again | Bedroom chips that each carry their result count (3+: 459, 4+: 229) |
| D4 | Prices and estimates are one number, not a range | "$13 to $17" on each of several options | One fare per ride, plus the pickup time |
| D5 | Options are visible, not buried | A dropdown or a free-text field for a short, known set; filters hidden behind a menu with many options | Flavour swatches, job-title chips with an "Other" fallback, quick-filter chips on the list |
| D6 | The control matches how the user thinks | A stepper to reach a known value; "3" that excludes 4; a max price when the user thinks in monthly payments | "3+" chips, range select (2 to 4), deposit plus monthly payment converted to a price limit |
| D7 | Where no default suits everyone, the user gets control | One layout forced on browsers and comparers alike | Card and compact-list toggle on a results list |
| D8 | The number of options at once is small enough to compare | Long undifferentiated lists, more than about five peer choices with equal weight | Shortlist with a recommended option, the rest one tap away |

## Scan: can they tell what to read first?

| Id | Check | Failure signal | Passing example |
|---|---|---|---|
| S1 | One element per card or block is clearly first | Name and metadata at nearly the same size, weight, and colour | Name steps up, rating takes the star and weight, the rest drops back |
| S2 | Values outrank labels | Big "Sales" label, small "591" | The figure large, the label small and muted |
| S3 | Images are big enough for their job | Thumbnails that identify but do not sell (a 56px food photo) | Full-width photo that makes the user want the thing |
| S4 | Images and visuals answer "what will I get?" | Decorative hero art; a lone product on a blank background; one strawberry for a product sold by weight | Real game characters on a paywall; the drink mixed beside the tub |
| S5 | One visual system | Mixed corner radii, filled and outlined icons together, several fonts, colours that fight the content | One radius, one icon style, one font family, a palette that supports the product |
| S6 | Trust signals sit beside what they vouch for | Rating far from the title | Rating directly under the product name |
| S7 | Recognition over recall | Account numbers, names only, text-only lists the user must read in full | Recipient photos, sender logos, category icons |
| S8 | Contrast holds for every state | Faint inactive tabs; text on busy photos | Inactive at reduced opacity but at least 3:1; text off the photo |

## Act: what does it cost to do the thing?

| Id | Check | Failure signal | Passing example |
|---|---|---|---|
| A1 | The task takes the fewest taps the decision allows | Each filter on its own page (7 taps for 2 filters); a banner that must be tapped to see content | All filters in one sheet; recommended items shown directly |
| A2 | Primary actions sit where the thumb rests | Main CTA in the top corner of a tall phone screen | CTA in the lower third, central create action in the nav |
| A3 | Tap targets are at least 44 by 44 and clear of the home indicator | Small icons as the only target; nav crammed against the safe area | Generous hit area around each icon, nav above the safe area |
| A4 | Controls used together sit together | Quantity selector far from Add to cart | Quantity, unit, and total inside one bottom bar |
| A5 | The main action stays reachable on long pages | CTA only at the top or bottom of a long scroll | Sticky bottom action bar |
| A6 | The input method fits how often it is used | Scroll wheel for daily food logging; free text for a one-off pick from a known set | Wheel or slider for one-off setup; numeric field for frequent precise entry |
| A7 | Common values are one tap | Tapping a stepper up to the usual quantity | 500 g, 1 kg, 2 kg presets beside the custom selector |
| A8 | Recent and frequent items are offered | Blank search, blank recipient picker | Recent recipients, recent and popular searches |

## Trust: what doubt is left unanswered?

| Id | Check | Failure signal | Passing example |
|---|---|---|---|
| T1 | The user gets value before a wall | Results blurred behind "Create an account" | Score and top issues shown, full report offered for saving |
| T2 | The downside is disclosed before it bites | Trial with no word on when the charge comes | Timeline: today, a reminder on day 5, the first charge on day 7 |
| T3 | Claims are specific | Round numbers, "fast", "easy" | 4.9 from 221 reviews, "start in two taps", "2 min away" |
| T4 | The likely objection is answered where it arises | Fear of lock-in, taste, or plans changing left to the FAQ | "Cancel anytime" inside the subscribe card, flavour tooltip, "Free cancellation before 26 March" under Reserve |
| T5 | Reassurance is relevant to this buyer | Generic badges everyone expects (free shipping) | "Third-party tested for heavy metals" on a supplement |
| T6 | The UI survives any content | Nav icons that vanish over a bright photo; card text baked onto the image | Icon containers with contrast; details below the photo |
| T7 | The user can confirm the right target | Sending money with only a name; one account shown when several exist | Photo beside the recipient; from-account and to-account both visible |

## Commit: is there a reason to keep going?

| Id | Check | Failure signal | Passing example |
|---|---|---|---|
| C1 | Progress counts what is already done | Onboarding at 0% | Account creation counted as step one, so progress starts at 20% |
| C2 | The user invests before the ask | Signup is the first screen | Pick a goal, finish a first lesson, then save progress |
| C3 | Costs are shown against a meaningful reference | An add-on price alone on its own page | The add-on beside the item, as a share of its price |
| C4 | Choices unfold when the user signals interest | Every option at once | Bundles revealed after "one-time purchase" is chosen |
| C5 | Feedback answers the input | A selection with no response | The selected state changes clearly; a sleep entry answered with "2 hours more than last night" |
| C6 | Copy frames the action as the user's step forward | "Subscribe", "Submit", "Add to cart" where commitment weighs | "Start my free trial", "Continue" |

## Orient: do they know where they are and what is next?

| Id | Check | Failure signal | Passing example |
|---|---|---|---|
| O1 | Context survives the task | Filters on a full page that hides the results; title lost on scroll | Sheet over the results; title moves into a sticky header |
| O2 | Navigation holds the core destinations only | Help, logout, legal, or back buttons in the bottom nav; more than five tabs | 3 to 5 tabs, a central create action where creation is core |
| O3 | The current location is unmistakable | Active tab changes only its label colour | At least two changes: icon fill and colour, or colour and label weight |
| O4 | Every empty state has a next step | "You have no projects" | A line on the benefit, one or two tips, a "Create project" button |
| O5 | The screen fits where the user is in their life cycle | The same home for a first-day user and a power user | Goal setup for new users, today's plan for returners, stats for power users |
| O6 | After the main action, the user knows what happens next | Order screen as a data dump | "Your order is on the way", a delivery window, the courier with call and message, a visual timeline |
| O7 | Familiar patterns stay familiar | Novel navigation that has to be learned | Platform conventions, with creativity kept to surfaces that do not carry navigation |
