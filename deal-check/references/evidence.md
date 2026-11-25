# Evidence card and verdict

Reference for steps 5 and 6 of [`deal-check`](../SKILL.md). Source notes marked "tested" are from 2026-11-25.

## The evidence card

Five fields per shortlisted item, each a short value (60 characters at most) that names its source. They print on the photo card. A value comes from a page fetched this run; with no source it reads "not found".

| Field | The question | Where to look, in order |
|---|---|---|
| `year` | Current model, or old stock being cleared? | Two facts: the silhouette's first year and this version's or colour's release. The brand's own product page (New, Just In, Terbaru badges; the style code), then a search for `<brand> <model> <style code> release date`. Release calendars list colourways with dates (soleretriever.com, tested on the adidas Handball Spezial). Bags and gear: the version or season in the name, the brand site's current range. |
| `stars` | Do buyers rate it? | Rating and count from the selling store's listing and one more: another official store (Zalora, Tokopedia Mall), the brand's own site, or a foreign retailer selling the same model. Fewer than 20 reviews in total: write the count and "too few to rate". |
| `review` | How does it fit, wear and last? | One source that used the product: an expert review, else owner reviews with text. Take fit (runs small or large), comfort, durability, defects. Lifestyle sneakers and fashion bags often have no expert review (tested: none for the Lacoste Baseshot or the Herschel Rome Packable); owner reviews on a foreign retailer (Zappos shows fit votes) or the brand's site then count, with their number. A page that restates retailer copy is not a source. |
| `trend` | Is this price the real low? | (a) `prices.py history`: earlier prices of this listing and of this model at any store. (b) The list price on the brand's own Indonesian site against the "was" price here. (c) The lowest price for the same article code at other official stores today. No public tracker covers Indonesian official stores (tested: only browser extensions for Tokopedia and Shopee), so (a) is the only history. |
| `popularity` | Is it in demand, and which way is it moving? | The level: rank in the store's popularity sort, a badge (Zalora "Paling Populer", Nike "Bestseller"), a sold count (Tokopedia "terjual", Eiger). The direction only when a source shows it: a rank or sold count against an earlier run's `run.json`, or search interest over 12 months for Indonesia on Google Trends (untested). Otherwise write the level alone. |

How to write each value:

- `year`: "1979 silhouette, this colour 2024". A classic at 50% off is a colour being cleared, which is fine. A superseded version of a performance product (v3 when v5 is out) is old stock: say so.
- `stars`: "4.6 (212) Foot Locker, 4.8 (95) Zalora".
- `review`: "True to size, flat insole (Zappos, 3 owners)".
- `trend`: "Lowest of 3 runs; Zalora 1.675.000 today", or "no history; brand list price matches", or "was-price inflated: brand lists 1.299.000".
- `popularity`: "Rank 12 of 250; 1.2K sold on Tokopedia".

## Verdict gates

| Verdict | Every condition holds |
|---|---|
| `buy` | In stock in the buyer's size or spec. Lowest price among the official stores checked today, or within 5% of it. The log shows no lower price in the last 90 days. The was-price is not inflated. Stars at 4.3 or more from 50 or more reviews, or a review with no defect that matters for the use. No term costs the buyer something they have not accepted: a no-returns promo needs a size the buyer has worn in that brand. |
| `consider` | The price gates of `buy` hold, and `stars` or `review` is "not found" or too few to rate. The note says which, and what would settle it. |
| `wait` | One of: a cheaper official price exists today; the log shows a lower price in the last 90 days; the discount is 30% or less while other colours of the model sit at 40% or more; a sale event inside three weeks is likely to beat it. The note names the store, the event and the date. |
| `skip` | One of: under 3.8 stars from 20 or more reviews; a defect that matters for the use; an inflated was-price with no real saving; a seller that is not official; wrong for the use. Listed under the cards with its note, no card. |

## Sellers and prices

- Official and brand-authorised sellers only. On Tokopedia that is the Mall filter: without it the lowest prices are fakes and used pairs.
- **Inflated was-prices.** Two patterns: a reseller of luxury brands quoting its own "original" price, and a brand that shows a discount on nearly every listing all year. Zalora has both (`references/stores.md`). Check the was-price against the brand's own site before counting a discount.
- **Voucher-inclusive prices.** Some stores show the price after a voucher that needs a minimum spend. `price` is what the buyer pays for this item alone; the voucher and its minimum go in the note.
- **Pre-order** listings are not a price for today: label them.
- A voucher code nobody tried at checkout is "untested" wherever it is mentioned.

## Bundle promos

For "cheapest item free" on three items: the buyer pays for the two dearest, so the third is free up to the price of the cheaper paid one. Three prices close together save the most, a third of the total at best. Because such promos are usually final sale, every item in a set needs a `buy` or `consider` verdict and a confirmed size.

Put two or three sets in `run.json` under `sets`, each covering the different uses or tones the buyer asked for; `cards.py` adds the sums. Then compare each set's price per item with the best single-item price found elsewhere: the bundle only wins when it beats that.

## Sale calendar, Indonesia

For a `wait`, the events worth naming: the twin dates 9.9, 10.10, 11.11 and 12.12 (Harbolnas); Black Friday to Cyber Monday in late November; payday sales from the 25th to month end; year-end sales; Ramadan and Lebaran; 17 August. This list says which events exist. An event's dates and terms come from the store's own page.
