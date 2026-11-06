# Case studies

Worked before-and-after cases from UX Peak and Tim Gabe breakdowns, each linked to the moment in the video, and desktop cases from an audit of the Search browser (a native macOS app), each linked to its pull request. Use them three ways:

- **Start from a symptom.** When the user brings a real problem ("people abandon the filter", "trials don't convert"), find the symptom in the index, audit the checks it names first, and read the cases beside it.
- **Cite a precedent.** Every finding names the closest case by id, so the fix has a worked example behind it. Search this file for the check id (`D2`, `A4`) to find the cases that fixed it.
- **Say what to measure.** Each case ends with the metric that shows whether the fix worked in a live product. Put that metric beside the top fixes in the report.

The before-and-after screens are design exercises and A/B framings from a design-education channel, not published experiments. Treat each case as a precedent for the reasoning, and let the project's own metric decide. The Search cases are real changes judged by the app's maintainer; the app has no telemetry, so their watch is a test.

## Symptom index

| What the project sees | Check first | Cases |
|---|---|---|
| Users open filters and leave, or get zero results | D2, D3, D6, A1, O1 | CS01, CS02 |
| Users scroll a list without opening anything | S1, S3, D7, D5 | CS02, CS20, CS25 |
| Low trial starts, or high cancellations right after the trial | T2, C6, S4 | CS03 |
| Users compare options and close the app | D4, D8, T3 | CS04 |
| Visitors view a listing but don't book or buy | S3, T4, D2, C3 | CS05, CS06, CS07 |
| Drop-off on long forms or the first onboarding screen | D1, C1, C2, A6, D5 | CS08, CS09, CS11, CS16 |
| Drop-off at a signup or email gate | T1, C2 | CS10, CS11 |
| Low add-on or upgrade take rate | C3, T4 | CS13, CS12 (counter-example) |
| Payments sent to the wrong person or account, or support tickets about it | T7, S7, D2 | CS14 |
| Daily logging falls off after the first week | A6, A7, C5 | CS15, CS21 |
| Searches that end with nothing tapped | A8, O4 | CS18 |
| "Where is my order?" tickets | O6 | CS19 |
| New users bounce from an empty or generic home | O4, O5, A1 | CS17, CS22, CS23 |
| Mis-taps, or users lost between sections | A3, O2, O3, S8 | CS24 |
| Product images or cards that look messy across the catalogue | S5, T6, S4 | CS06, CS20 |
| Users hit a limit and contact support or leave | O8, T2 | CS27 |
| Failed payments or actions become tickets or churn | T8, O6 | CS28 |
| Users drop off after missing a day or a target | C8, C7 | CS29, CS30 |
| Users finish the core task and don't come back the next day | C9, C7 | CS31, CS30 |
| Engagement rises while complaints, opt-outs or uninstalls rise too | Persuasion tests 2 and 3 | CS32, CS33 |
| Undo or reopen brings back less than was lost | T9, O1 | CS34 |
| A repeated shortcut does something destructive | A10 | CS35 |
| Drags land somewhere other than where the user aimed | A11, C5 | CS36 |
| The owner turns a fix down as against the product's style | The philosophy from step 1 | CS37 |

## Decide and compare

### CS01 Filter sheet for a home search
[Video at 8:12](https://www.youtube.com/watch?v=U7jTCgIWS4w&t=492s) · Checks D2 D3 D6 A1 O1 · A ladder case with all four levels

- **Context.** Someone browsing 1,500+ homes in the evening, with soft requirements (3 bedrooms, but 2 would do if the price is right).
- **Junior.** Each filter on its own page: 7 taps for 2 filters. The user can't see earlier choices while making the next one, the results disappear, and "Show homes" gives no count.
- **Mid.** One sheet over the results with every filter in one scroll, a slider plus number inputs for price, and "Show 41 homes". Steppers remain, so a known value means tapping up to it.
- **Senior.** A histogram behind the price slider shows where the market sits. Bedroom chips read "3+" so 4-bedroom homes stay in. Home types get icons.
- **Staff.** The user enters deposit, monthly payment and rate, and the product draws the affordable price as a line on the histogram. "459 of 1,557 homes fit" sits beside it. Every bedroom option shows its count before it is tapped, and the user can select a range (2 to 4).
- **Behaviour.** Requirements are negotiable while the user searches. A filter that hides trade-offs forces a loop: choose, see, go back.
- **Transfers to.** Any search with soft constraints: flights, jobs, rentals, catalogues.
- **Watch.** Filter apply rate, zero-result rate, filter reopens per session, time to the first opened result.
- **Trade-off.** Each level adds context and makes the sheet busier. Keep only what helps this decision.

### CS02 Restaurant list in food delivery
[Video at 0:09](https://www.youtube.com/watch?v=U7jTCgIWS4w&t=9s) · Checks S1 S3 S5 D5 D7 T6 · A ladder case

- **Junior.** 56px food photos chosen to fit six restaurants above the fold. Filters and sort sit in two dropdowns hiding 17 options. A 13px name over 11.5px grey metadata. Square cards beside round category images.
- **Mid.** Photos three times wider and the largest thing on the card. One corner radius. The name steps up and the rating takes the star and the weight. Eight filter chips are visible.
- **Senior.** Full-width photos. Categories become an icon set, so six category photos stop competing with the food photos below. Filter and sort buttons, a "640 places" count, and a card or list toggle.
- **Staff.** A search placeholder that names what can be searched (places, dishes, cuisines). Quieter category icons. A "best match" label. Name and numbers moved off the photo, so every card reads the same whatever the restaurant uploads.
- **Behaviour.** The photo's job is appetite, not identification. Fitting more above the fold trades away the reason to scroll.
- **Transfers to.** Any feed where a picture sells the item: listings, recipes, products.
- **Watch.** List-to-detail tap rate, scroll depth before the first tap, filter chip use.

### CS04 Ride options with price ranges
[Video at 7:08](https://www.youtube.com/watch?v=zr37ibqXl1U&t=428s) · Checks D4 D8 T3 C3

- **Before.** Each ride shows a range ($13 to $17, $17 to $22, $16 to $21). The user anchors on the high end and weighs three uncertain prices.
- **After.** One price per ride, a pickup time ("2 min away"), a small green "cheaper" badge, and the destination card shown first, so the only question left is which car.
- **Behaviour.** A range reads as its maximum. Easy comparisons get fast answers, and a confirmed destination narrows the decision to "which", not "whether".
- **Transfers to.** Quotes, delivery estimates, shipping options, plan pickers.
- **Watch.** Quote-to-booking rate, time on the options screen.

### CS08 Booking form with smart defaults
[Video at 0:25](https://www.youtube.com/watch?v=2TlIg3VokY8&t=25s) · Checks D1 D2 D8

- **Before.** Five empty fields, each a decision before anything happens.
- **After.** Every field pre-filled with the most common choice, and the button reads "Search, 12 results".
- **Behaviour.** A visible default reads as a recommendation. The task changes from filling in to scanning and adjusting.
- **Transfers to.** Search forms, settings, checkout, any form whose usual answer is known.
- **Watch.** Form completion rate, the share of users who change each default (a default most people change is the wrong default).
- **Persuasion line.** A default that picks the costlier option or consent is a flag; see `persuasion.md`.

### CS16 Job title in onboarding
[Video at 15:18](https://www.youtube.com/watch?v=YlN28RNChl0&t=918s) · Checks D5 A1

- **Before.** A free-text field for job title: effort, typos, inconsistent data.
- **After.** The most common titles as tappable options with icons, plus "Other" for typing.
- **Transfers to.** Any field with a known short list: country, role, industry, reason for cancelling.
- **Watch.** Time on the step, completion of the step, the share choosing "Other" (high means the list is wrong).

## Trust and commitment

### CS03 Trial paywall
[Video at 0:59](https://www.youtube.com/watch?v=zr37ibqXl1U&t=59s) · Checks T2 T3 C6 S4 · A ladder case

- **Before.** Decorative space art, "Get access to 1,000+ games", $19 a month, three feature bullets, "Subscribe and start 7 days for free". The user faces "is this worth $19 a month?" thirty seconds after opening the app.
- **After.** "How your free trial works" with a timeline: today you unlock everything, on day 5 we remind you, on day 7 the first charge. Real game characters in the image. "Start my free trial" with "Start in two taps" beneath.
- **Behaviour.** The screen swaps a hard question for an easy one ("can I try it free?"). Promising a reminder before the charge proves good faith instead of claiming it.
- **Transfers to.** Any trial, deposit, or recurring charge.
- **Watch.** Trial start rate, and also trial-to-paid, refunds and chargebacks. A paywall that lifts starts while raising refunds has moved the problem, not solved it.

### CS05 Stay booking screen
[Video at 10:06](https://www.youtube.com/watch?v=zr37ibqXl1U&t=606s) · Checks S3 T4 D2 C3

- **Before.** A small thumbnail, "Beach house with garden", €89 a night, two date fields, "Reserve". Nothing is wrong, and it reads like a form.
- **After.** The photo takes the top half with Superhost, Guest favourite and "1 of 24" badges. The title becomes "Beachside escape steps from the sand". €129 crossed out beside €89 and "-31%". "Fri 28 Mar to Wed 2 Apr, 5 nights". "Reserve, €445 total" with "Free cancellation before 26 March" underneath.
- **Behaviour.** Day names and the night count make the trip concrete. The total removes the fear of fees, and the cancellation line answers the top objection where it arises.
- **Watch.** Listing-to-reserve rate, abandonment at the payment step.
- **Persuasion line.** The crossed-out price must have been real; see `persuasion.md`.

### CS07 Supplement product page
[Video at 0:53](https://www.youtube.com/watch?v=oYskl2ZBoBc&t=53s) · Checks S4 T3 T4 T5 D5 C4

- **Before.** An isolated tub on a blank background, round review numbers, flavours in a dropdown, stacked radio buttons for one-time or subscribe, "Add to cart" over generic badges (free shipping, money back).
- **After.** A best-seller badge. The tub beside a mixed glass and sliced pineapple, to close the imagination gap. "4.9 stars, 221 reviews" and "500+ sold this week". Flavour swatches with a taste tooltip ("light, tart, not overly sweet"). Side-by-side purchase cards with "Save 15%, cancel anytime" inside the subscribe card. Choosing one-time reveals 1, 2 and 3-month bundles. Badges the buyer cares about: vegan, 60-day guarantee, third-party tested for heavy metals.
- **Behaviour.** Each change answers a question the buyer would otherwise leave to ask elsewhere: what is it like, does anyone buy it, will it taste bad, am I locked in.
- **Watch.** Add-to-cart rate, subscription share, average order value, and subscription cancellations in the first 60 days.
- **Persuasion line.** The video preselects subscribe and tints it. Test it against `persuasion.md` (preselection, even exit) before recommending it.

### CS09 Onboarding progress that starts at zero
[Video at 1:49](https://www.youtube.com/watch?v=2TlIg3VokY8&t=109s) · Checks C1 C5

- **Before.** "0% complete" with five empty steps.
- **After.** Account creation counted as step one, so the user starts at 20% with one step ticked.
- **Behaviour.** People speed up as they near a goal, and the starting line is a design choice.
- **Watch.** Completion per onboarding step, completion of the whole flow.
- **Persuasion line.** Count only steps that really happened. The video's phrase "even a fake one" is the line to stay behind.

### CS10 Value before the signup wall
[Video at 3:56](https://www.youtube.com/watch?v=2TlIg3VokY8&t=236s) · Checks T1 C2

- **Before.** The user enters a URL, waits for the scan, and the report is blurred behind "Create an account".
- **After.** A real partial report (score, top issues, what passed), then "Want the full breakdown with steps? Save your report."
- **Behaviour.** Reciprocity: a useful gift first makes the ask feel fair. A wall after the user's effort reads as holding the result hostage.
- **Transfers to.** Calculators, audits, quizzes, generators, trials.
- **Watch.** Signup rate per completed scan, and the return rate of those signups.

### CS11 Building before signing up
[Video at 5:38](https://www.youtube.com/watch?v=2TlIg3VokY8&t=338s) · Checks C2 C6

- **Before.** Email, password, Sign up. Nothing on the screen belongs to the user.
- **After.** The user picks a name, title, palette and card style first, and the button says "Continue".
- **Behaviour.** The IKEA and endowment effects: what the user made, they value and want to keep.
- **Watch.** Signup completion, and activation in the first week.

### CS13 An add-on price in context
[Video at 9:43](https://www.youtube.com/watch?v=2TlIg3VokY8&t=583s) · Checks C3

- **Before.** A protection plan alone on its own page: $50 a month, which the user turns into $600 a year.
- **After.** The same plan under the $1,900 laptop in the cart, labelled "just 2.6%".
- **Behaviour.** Prices are judged against whatever the user saw just before.
- **Watch.** Attach rate, and also cancellations and refunds on the add-on.

### CS12 Counter-example: a loss-framed upgrade
[Video at 8:44](https://www.youtube.com/watch?v=2TlIg3VokY8&t=524s) · Persuasion tests 2, 3 and 4

- **What the video recommends.** In place of "Upgrade now / Maybe later", the storage app shows the user's own files by name with a countdown, and the dismiss button reads "I'll risk it".
- **Why the audit flags it.** It threatens the user's data to force a decision, and the dismiss copy shames them for declining (confirmshaming). Use this case to recognise the pattern, never as a fix.
- **Honest version.** State the real consequence plainly ("Files over 5 GB stop syncing on 1 June"), offer a neutral "Not now", and show what free users keep.

### CS14 Money transfer
[Video at 9:55](https://www.youtube.com/watch?v=YlN28RNChl0&t=595s) · Checks A8 D2 S1 S7 T7

- **Before.** Two buttons and redundant text to start a transfer. The currency and the amount as two equal fields. Only a name for the recipient, and one account shown.
- **After.** Recent recipients and search on the first screen. The amount large, with currency tucked into the field's corner. A photo beside the recipient's name. "Your new balance" shown before confirming. Both from-account and to-account visible when the user has several.
- **Behaviour.** Fewer steps for the common case, recognition instead of recall for the risky part, and no surprise after sending.
- **Watch.** Time to send, the cancel rate on the confirmation screen, support tickets about wrong recipients.

### CS06 Grocery product page, 15 mistakes
[Video at 0:37](https://www.youtube.com/watch?v=GGg61sdEjeI&t=37s) · Checks T6 S4 S5 S6 D2 A4 A5 A7 O1 · A ladder case

- **Before.** Nav icons sitting on a full-bleed photo (they vanish on a bright product). Inconsistent catalogue photos. Off-grid alignment, saturated colour, several fonts. The rating far from the title. A "Price:" label. "1 kg" in the title while a quantity selector also exists. Quantity far from an all-caps Add to cart.
- **After.** Icons in containers with contrast. One photo style for the catalogue. A 24px grid, a soft palette, one font. The rating under the title and the price early. The quantity, with its unit, beside the button, and the total inside it. A content card that slides over the image, with the title moving into a sticky header. A sticky bottom action bar, and 500 g, 1 kg, 2 kg presets.
- **Behaviour.** The user's three questions (what is it, can I trust it, what does it cost) are answered in the first screen, and the buy controls follow them down the page.
- **Watch.** Add-to-cart rate, scroll depth at the time of add, the share using quantity presets.

## Effort and input

### CS15 Daily sleep log
[Video at 0:56](https://www.youtube.com/watch?v=YlN28RNChl0&t=56s) · Checks A6 C5 S1

- **Before.** Radio buttons labelled great to bad, with the hours secondary. It works, and it is a chore.
- **After, in steps.** "Hi Emily, how long did you sleep last night?" with the hours made primary, controls on the left and emojis. Then a curved swipe slider. Then a large central emoji with feedback ("Aim for 8 hours"). Then a slider with comparison feedback ("2 hours more than last night").
- **Behaviour.** A daily input has to be fast and has to answer back, or the habit stops.
- **Watch.** Day-7 and day-30 logging retention, time per entry.

### CS21 Numeric input by frequency
[Video at 8:12](https://www.youtube.com/watch?v=Xzh8xjimmp8&t=492s) · Checks A6 A7 D6

- **Rule.** Scroll wheels and sliders for one-off setup values in a known range (age, height). Text fields, steppers or number inputs for frequent, precise entry (350 g of food every day).
- **Watch.** Time per entry, edit rate after entry.

### CS22 Content hidden behind a banner
[Video at 1:24](https://www.youtube.com/watch?v=gG4urkinFQI&t=84s) · Checks A1 O5

- **Before.** "Discover 100+ recipes selected by our chefs" as a banner the user must tap.
- **After.** The top 10 recommended recipes shown directly.
- **Watch.** Time to the first content tap, new-user day-1 engagement.

### CS24 Bottom navigation
[Video at 2:48](https://www.youtube.com/watch?v=wLJ40GV2XEc&t=168s) · Checks O2 O3 A3 S8 O7

- **Rules from the case.** Only core, frequent destinations (home, search, create, messages, profile). Help, logout, legal and back buttons go elsewhere. Three to five tabs. Tap areas of at least 44 by 44. 24px icons with 10 to 12px labels. Clear of the home indicator. The active tab differs in at least two ways. One icon style, filled only for the active tab. Inactive contrast of at least 3:1. Separated from content by a border, a tint or a soft shadow. Labels for less tech-confident audiences.
- **Watch.** Mis-tap rate (quick back after a tab change), the share of sessions that reach each tab.

## Orientation and states

### CS17 Home by life-cycle stage
[Video at 0:25](https://www.youtube.com/watch?v=Xzh8xjimmp8&t=25s) · Checks O5

- **Pattern.** A new user gets a welcome, weekly goal setup and a few trending programmes. A returning user gets today's plan with its duration and calories. A power user gets stats first, then the plan and diet suggestions.
- **Watch.** Activation for new users, and return frequency for each segment.

### CS18 Search before typing
[Video at 2:14](https://www.youtube.com/watch?v=Xzh8xjimmp8&t=134s) · Checks A8 O4

- **Before.** A blank screen under the search bar.
- **After.** Recent searches, popular items, and personalised suggestions that stay out of the way of typing.
- **Watch.** The share of search sessions that end with a tap, and suggestion use.

### CS19 Order tracking after purchase
[Video at 3:39](https://www.youtube.com/watch?v=Xzh8xjimmp8&t=219s) · Checks O6 T3 S7

- **Before.** The order number, a plain item list, courier text and a list of dates.
- **After.** "Your order is on the way" with a delivery window and the address. The courier's photo and name with call and message buttons. Item thumbnails. A visual timeline.
- **Watch.** "Where is my order" tickets, and how often the order page is reopened.

### CS23 Empty project list
[Video at 4:03](https://www.youtube.com/watch?v=gG4urkinFQI&t=243s) · Checks O4

- **Before.** "You have no projects."
- **After.** "Start managing your projects and stay organized", an illustration, two tips (invite team members, set deadlines), and a "Create new project" button.
- **Watch.** First-project creation rate for new accounts.

## Scanning and visual system

### CS20 Category screen
[Video at 6:30](https://www.youtube.com/watch?v=Xzh8xjimmp8&t=390s) · Checks S5 S7 S8 T6

- **Three versions.** A plain text list puts all the work on reading. Photo tiles with dark overlays look designed but fail on contrast and mix photo styles. Soft colour cards, each with one isolated image in a unified style, can be scanned in seconds.
- **Watch.** Category tap-through and time to the first category tap.

### CS25 Dashboard metrics
[Video at 1:41](https://www.youtube.com/watch?v=8pMUkEbAM7g&t=101s) · Checks S1 S2

- **Before.** Large labels (Sales, Earnings, Views) with small values.
- **After.** Large values (591) with small muted labels. Rank the content by importance before styling it.
- **Watch.** Usability-test time to answer "how many sales today?".

### CS26 Showing what the user will get
[Video at 4:15](https://www.youtube.com/watch?v=8pMUkEbAM7g&t=255s) · Checks S4 T1

- **Case.** The channel's own ebook landing page. A cover on a plain background, then the cover with value points (the channel reports 22% conversion), then real inside pages (it reports 48%).
- **Behaviour.** A preview of the real thing beats a description of it.
- **Watch.** Conversion on the page, with the preview as the variable in an A/B test.

## Retention and recovery

### CS27 Session limit in a practice app
[Video at 5:42](https://www.youtube.com/watch?v=8EAYZe6y3I8&t=342s) · Checks O8 T2 O6

- **Before.** Running out of sessions sent the user to one of two separate screens, both reading "You've used all your sessions", with no count and no date. A mic test that was too short ended with nothing at all; one founder's summary of users' reaction: "I was expecting anything instead of nothing" ([at 2:47](https://www.youtube.com/watch?v=8EAYZe6y3I8&t=167s)).
- **After.** One pattern for every limit: a "2 of 2 sessions used" badge, "You've used both sessions this month", and the exact date they refresh.
- **Behaviour.** A limit with a count and a date is a plan; a limit without them reads as a broken product. Two screens for one situation tell the user nobody owns it.
- **Transfers to.** Quotas, free tiers, rate limits, storage caps, credits.
- **Watch.** Support tickets about limits, upgrade rate from the limit screen, return rate on the refresh date.

### CS28 Declined card payment
[Video at 8:17](https://www.youtube.com/watch?v=8EAYZe6y3I8&t=497s) · Checks T8 O6

- **Before.** A failed transaction gave, in the support lead's words, "zero information on what you should do. You're just left alone", in a product people trust with their own money.
- **After.** A decline alert that tells the user to check their balance, with a Contact support button beside it. The agency reports new accounts up 60% and money loaded up 79% after this and other changes together.
- **Behaviour.** A failure handled well can leave people as satisfied as if nothing had failed (the service recovery paradox). The scariest moment is where trust is won or lost.
- **Transfers to.** Payments, uploads, syncs, bookings, anything that can fail after the user commits.
- **Watch.** Tickets per decline, retry success after a decline, deposits in the week after a decline.

### CS29 Food tracking without shame
[Video at 7:23](https://www.youtube.com/watch?v=HA4yB_sd62Q&t=443s) · Checks C8 C5

- **Category default.** Red numbers over target, broken streaks after a skipped day, notifications about missed goals.
- **What MacroFactor built.** It assumes users will miss targets. It combines what was logged with a trend weight smoothed over about three weeks to work out real metabolism, then adjusts the targets.
- **Behaviour.** Shame makes people stop logging or log what they wish they had eaten. Removing it kept users and gave cleaner data than competitors.
- **Transfers to.** Habit, fitness, finance and learning apps: any product where the user will slip.
- **Watch.** Logging retention after the first missed day, the share of days logged per active user.

### CS30 Surprise inside a predictable system
[Video at 2:52](https://www.youtube.com/watch?v=yBpv5rZoBjA&t=172s) · Checks C7 C5 · Persuasion row "Surprise reward"

- **Pattern.** In Finch the user raises a virtual bird by finishing real self-care tasks. The bird adventures in a location the user picks and brings back one of 15 to 20 discoveries, and its six-trait personality develops in ways the user did not choose.
- **The design rule the case teaches.** Keep the reward system mostly predictable and trackable, add controlled surprise on top, and give users one system to follow instead of many badges ([at 5:47](https://www.youtube.com/watch?v=yBpv5rZoBjA&t=347s)).
- **Transfers to.** Habit and wellbeing apps, learning streaks, loyalty programmes.
- **Watch.** Day-7 and day-30 retention, and also notification opt-outs and uninstalls.
- **Persuasion line.** The surprise must stay a bonus. When progress itself becomes random, or the user pays for a chance at it, it is a flag.

### CS31 Ending the ride
[Video at 6:07](https://www.youtube.com/watch?v=11h4H3TAGkM&t=367s) · Checks C9

- **Pattern.** The peak of a ride is arriving. Uber then closes the journey with a vibration and two optional, polite steps: rate the driver and leave a tip. In the same video, Ahead builds a personal report in front of the user as the peak and ends with a gentle nudge to come back tomorrow.
- **Behaviour.** People remember the peak and the end of an experience. A flow that simply stops wastes the last moment the user will remember.
- **Transfers to.** Checkouts, lessons, workouts, any completed core task.
- **Watch.** Rating and tip rate, return within seven days of a completed task.

### CS32 Counter-example: a hidden ranked ladder
[Video at 4:37](https://www.youtube.com/watch?v=yBpv5rZoBjA&t=277s) · Persuasion tests 1 and 3

- **What the video describes.** League of Legends' visible rank sits on a hidden rating that shapes matchmaking to hold players near a 50% win rate. Players climb 100 points, drop 200 and climb again, and the unpredictability keeps them playing.
- **Why the audit flags it.** The visible score is not what decides the outcome (test 1), and players would not endorse the rule if they saw it (test 3). Recognise the pattern; never recommend it.
- **Honest version.** Show the rating that drives matching, or explain plainly how players are matched.

### CS33 One workout for the whole team
[Video at 10:00](https://www.youtube.com/watch?v=HA4yB_sd62Q&t=600s) · Checks C7 · Persuasion row "Leaderboard and social visibility"

- **Pattern.** Most workout apps treat motivation as solo. Ladder puts every member of a team (about 5,000 people) on the same workout on the same day. The CEO credits the shared calendar, not the funnel, with keeping users.
- **Behaviour.** A shared ritual makes skipping visible to others, which turns a private goal into a social one.
- **Transfers to.** Courses with cohorts, challenges, group savings, study apps.
- **Watch.** Week-4 workout completion, and also the rate of users leaving their team.
- **Persuasion line.** Visible absence works only with consent: the user joins the cohort knowingly and can train privately.

## Desktop and browser chrome

### CS34 Reopening a closed tab with its history
[PR #895](https://github.com/driceroland/Search/pull/895) · Checks T9 O1

- **Before.** ⇧⌘T brought a closed tab back with its address only: Back history went from 3 entries to 1 and the scroll position from 6000 to 0. Pinned tabs that were put down showed Back lit with nothing behind it ([#896](https://github.com/driceroland/Search/pull/896)), and the app's own pages did not come back at all ([#897](https://github.com/driceroland/Search/pull/897)).
- **After.** The reopened tab wakes with its history and scroll, the way a slept tab does. All three landed.
- **Same rule, later.** Closing a Split View pair with Close Both brought back one page on ⇧⌘T; the fix brings back the pair ([#930](https://github.com/driceroland/Search/pull/930), in review).
- **Behaviour.** Undo is used right after a mistake. When it restores less than the mistake took, the user loses twice and learns not to trust it.
- **Transfers to.** Any close, archive or delete with an undo: mail, rows in a table, documents, panes.
- **Watch.** Test: navigate three pages, close, reopen, and compare history length and scroll with the values before closing. With telemetry: a Back press within 10 s of a reopen.

### CS35 The key that brings the field up puts it away
[PR #912](https://github.com/driceroland/Search/pull/912) · Checks A10 O1

- **Before.** Pressing ⌘K twice switched tabs, and ⌘L then ⌘W closed the page underneath the field instead of the field.
- **After.** The key that raised the field puts it away and keeps what was typed; ⌘W puts a raised field away whichever key raised it ([#910](https://github.com/driceroland/Search/pull/910)). Both landed.
- **Behaviour.** Keyboard users undo a shortcut by pressing it again. A second press that acts again turns a reflex into a destructive action.
- **Transfers to.** Command palettes, search overlays, quick switchers, any panel opened by a key.
- **Watch.** Test: press each key twice and check that nothing but the field changed. With telemetry: a reopen within 10 s of a close by key.

### CS36 A carried tab stays under the pointer
[PR #884](https://github.com/driceroland/Search/pull/884) · Checks A11 C5

- **Before.** A tab dragged past a Split View pair drifted a row away from the pointer, because the drag assumed every row was one row tall. A pair let go just past its edge came apart with no warning.
- **After.** The drag measures each row it passes, so the tab stays under the hand. A pair separates only after the pointer rests 0.3 s and the staying half dims with a haptic tick, so the drop shows before release ([#887](https://github.com/driceroland/Search/pull/887)). Both landed.
- **Behaviour.** Direct manipulation is trusted only while the thing stays under the hand. A drop whose result was not shown first is a surprise the user has to undo.
- **Transfers to.** Reordering lists, boards and tabs; drag to split, group or file.
- **Watch.** Test: render frames mid-drag and measure the offset between the pointer and the item. With telemetry: pairs separated by a drag and paired again within a minute.

### CS37 Counter-example: the product's philosophy wins
[PR #913](https://github.com/driceroland/Search/pull/913) · Check O3 · Step 1's philosophy

- **What the audit proposed.** A mark before the field's placeholder naming its mode, a key cap on every picked row ([#915](https://github.com/driceroland/Search/pull/915)), and open tabs listed in ⌘T.
- **What the owner did.** Landed #913 without the mark: "Search keeps the field as bare as it can, and the placeholder already says where Return goes." Asked #915 down to the one surprising case: "A key cap on every picked row is more than the list needs", then it was closed. Open tabs in ⌘T broke a founding rule written in the code (`placeOffers`: "⌘K exists for those"). A new list in an empty ⌘T was accepted only behind a switch, off by default ([#914](https://github.com/driceroland/Search/pull/914)).
- **Behaviour.** Staff-level context on a surface the owner keeps deliberately bare reads as noise to the people who chose the bareness. Say only what surprises.
- **Lesson for the audit.** Read the product's stated rules before writing fixes, and ship new visible behaviour behind an off-by-default switch when the owner guards a minimal surface.
