# Store playbook, Indonesia

Reference for steps 2 and 3 of [`deal-check`](../SKILL.md): what worked on each store on 2026-11-25. Stores change their pages. When a fact here fails, correct it in the same run; a store that is not here gets a section before the run ends. "Not tried" marks what nobody has tested yet.

Read only the sections for the stores in the run.

| Store | Access | Photo | curl for photos |
|---|---|---|---|
| [Foot Locker](#foot-locker-footlockerid) | browser, in-page fetch | `og:image` | works |
| [Zalora](#zalora-zaloracoid) | browser text | `og:image`, inner URL | works |
| [Tokopedia Mall](#tokopedia-mall) | browser text | not tried | not tried |
| [adidas](#adidas-adidascoid) | browser text | not tried | not tried |
| [Nike](#nike-nikecomid) | browser text | `og:image` | works |
| [Planet Sports](#planet-sports-planetsportsasia) | browser | `og:image` | blocked |
| [Sports Station](#sports-station-sportsstationid) | browser | second large image | works |
| [Eiger](#eiger-eigeradventurecom) | browser | `og:image` | works |
| [Samsonite](#samsonite-samsonitecoid) | browser | regex on product id | blocked |
| [Decathlon](#decathlon-decathloncoid) | browser | `og:image` | works |

Shopee was never opened: whether it needs a login is not tried.

## Foot Locker (footlocker.id)

A Magento store. `curl` on a listing returns a 3 KB stub; `/graphql` returns an empty body and `/rest/V1/products` a 401.

**Listings.**

- Sale: `/sale.html?gender=Pria&productDivision=Sepatu&p=1`. A promo: `/promo/id/<slug>.html` with the same parameters.
- `gender=Pria` | `Unisex` | `Wanita`, and `gender=Pria,Unisex` selects both. `productDivision=Sepatu` | `Aksesoris`. `accessories=Tas` for bags. `brand=Lacoste`. `p=N` pages.
- 28 cards per live page. `product_list_limit` and `q=` are ignored.
- **The `size=` filter undercounts**: `size=UK+8` returned 6 shoes where the per-product check found 125. Check sizes per product.
- The count is in the text `Menunjukkan 2089 hasil pencarian`.
- Live promos: homepage links matching `/promo/id/`.

**A card** is `li.product-item`. Brand: `h3`. Name: `img.product-image-main` `alt`. URL: `a.product-item-photo` (in fetched HTML, `a.product-item-link`). Prices: `/Rp\.?\s?([\d.]+)/g` on the card text, now then was (in fetched HTML, `.price` elements, digits only, de-duplicated). Discount: `/(\d+)% OFF/`. Rating: `/([\d.]+) dari 5 bintang/` on `innerHTML`. Review count: `/\((\d+)\)\s*$/`. `0.0` and `(0)` mean no reviews, which is most Lacoste items. Promo label: `.amasty-label-image` `title`.

Fetching listing pages inside the page, six at a time (24 pages in 59 s; a tab per page took 13 s each). This and the size loop below are the code that ran, with the URL lifted into `BASE` and the retry folded in; the edited form has not been re-run:

```js
const t = open(BASE + '2'); sleep(3000); keep.tid = t.id;   // BASE ends in "&p="
const fn = `async(pages)=>{const res=await Promise.all(pages.map(async p=>{const h=await (await fetch(${JSON.stringify(BASE)}+p)).text();const d=new DOMParser().parseFromString(h,'text/html');
return [...d.querySelectorAll('li.product-item')].map(li=>{const a=li.querySelector('a.product-item-link')||li.querySelector('a');
const prices=[...li.querySelectorAll('.price')].map(x=>x.textContent.replace(/[^0-9]/g,'')).filter(Boolean).map(Number);
return {n:(a?.textContent||'').trim(),u:a?.href,b:(li.querySelector('.product-brand, .brand, [class*=brand]')?.textContent||'').trim(),pr:[...new Set(prices)],rv:((li.textContent.match(/\\((\\d+)\\)/)||[])[1])}})}));
return JSON.stringify(res.flat())}`;
keep.L = [];
for (const ch of [[1,2,3,4,5,6],[7,8,9,10,11,12]]) {
  let a = JSON.parse(t.eval(`(${fn})(${JSON.stringify(ch)})`)); if (typeof a === 'string') a = JSON.parse(a);
  keep.L.push(...a); console.log(ch[0], a.length);
}
```

Fetched pages hold 30 cards with repeats: 720 rows were 668 unique URLs. De-duplicate by URL. Ratings and photos are missing from fetched cards (lazy loaded); take them from the product page.

**Sizes in stock, the fast way.** Each product page embeds Magento `jsonConfig`; a size option with a non-empty `products` array is in stock. Eight pages per `eval`: 256 products took 4.6 minutes. Sixteen per `eval` hit `CDP timeout`.

```js
const t = tab(keep.tid);   // a tab on footlocker.id; keep.C = candidates with .u
const fn = `async(urls)=>{const res=await Promise.all(urls.map(async u=>{try{const h=await (await fetch(u)).text();
const i=h.indexOf('"jsonConfig"');let sz=null;
const m=h.slice(i).match(/"options":(\\[.*?\\]),"position"/);
if(m){sz=JSON.parse(m[1]).filter(o=>o.products&&o.products.length).map(o=>o.label)}
return {u,sz,og:(h.match(/og:image" content="([^"]+)/)||[])[1]}}catch(e){return {u,err:String(e)}}}));return JSON.stringify(res)}`;
keep.S = keep.S || {};
const todo = keep.C.map(x => x.u).filter(u => !keep.S[u] || keep.S[u].err);
for (let i = 0; i < todo.length; i += 8) {
  let a = JSON.parse(t.eval(`(${fn})(${JSON.stringify(todo.slice(i, i + 8))})`)); if (typeof a === 'string') a = JSON.parse(a);
  for (const x of a) keep.S[x.u] = x;
}
```

Rerun it until `todo` is empty. A page with `sz: null` has no `jsonConfig` (8 of 256): treat it as unknown, not as in stock. The in-stock rule was checked against the visible page on one product only.

**Size labels differ by brand**: adidas `EU 42 2/3` (some products `UK 8.5`); Nike, New Balance, ASICS, Vans `US 9` (half sizes as `US 8H`); PUMA and Lacoste `UK 8`; Converse `US M8.5 / W10.5` with varying spacing. Match the labels in the profile.

**Product page.** Text order: brand, name, SKU, price now, price was with `NN% OFF`, the rating line, `Panduan Ukuran`, `Ukuran`, one line per in-stock size, then `Pengembalian` (shoes) or `Kuantitas` (bags), then the description, which holds a bag's capacity and laptop size. The `Panduan Ukuran` size chart is in the HTML (`#sizechart-id`) and has never been read: read it before trusting a size conversion.

**Photos.** `og:image`; set `width` and `height` in its query to 480.

**Terms.** Not in the listing text, not on product pages. They are an image at the top of the promo page. List the candidates from a tab on the store:

```js
t.eval(`(async()=>{const h=await (await fetch('https://www.footlocker.id/promo/id/<slug>.html')).text();return [...h.matchAll(/src="([^"]*tnc[^"]*)"/gi)].map(m=>m[1])})()`)
```

Download the mobile version with curl and read it as an image. The homepage carousel banner carries only the headline and dates: it left out "cheapest item free" and "no returns".

**Traps.** One model is listed per colour at different discounts (Samba OG from 1.0M to 1.76M). Colour names disagree with photos. The item count of a promo moves during the day. A coupon label such as `Disc $20: FLSGSP20` on a card is untested.

## Zalora (zalora.co.id)

- Search: `/search?q=<terms>&gender=men`; read the text after `Barang ditemukan`. Per item: badges, rating, voucher line and its terms, brand, name, price now, price was, percent.
- No hits reads `Tidak ada item yang ditemukan`, followed by suggestions with prices: those are not results. A brand and model search can return another category.
- **Prices shown include the best voucher**, even one with a minimum spend: 429.025 shown, 504.735 payable alone. Use the price before the voucher.
- Product URL: `/p/<brand>-<slug>-<colour>-<id>`. Photo: `og:image`; the inner `https://static-id.zacdn.com/p/...-1.jpg` downloads with curl.
- A helper read the whole backpack category (about 3,100 items with seller, rating, review count, stock left and voucher codes) from Zalora's product feed in 9 minutes. The feed URL was not recorded: find it in the page's network requests and write it here.
- **Sellers.** Coach and Michael Kors come from a reseller with inflated "original" prices. Hush Puppies, Nixon, Navy Club, Hamlin and Obermain show a discount on nearly every listing. Official brand stores: Samsonite, Herschel, Hedgren, Eiger, PUMA.
- Sale pages: `/sale/black-friday`, `/sale/1111-sale`, `/sale/harbolnas`, `/sale/big-sale`. Check the year in the page text: the Black Friday page still showed last year's.

## Tokopedia Mall

- Search: `https://www.tokopedia.com/search?q=<terms>&ob=3&shop_tier=2`. `ob=3` sorts by lowest price; `shop_tier=2` keeps Mall (official) shops. Read the text after `Menampilkan`. Per item: percent, name, price now, price was, rating, `N terjual`, shop, city.
- Without `shop_tier=2` the lowest prices are fakes and used pairs.
- Mall shops seen for sneakers: Sneakers Dept, Sneakers Flash, Hoops Indonesia, Ncr Sport, Arkais. Arkais listings were pre-order.
- Compare by the article code in the title. Shop pages and photos: not tried.

## adidas (adidas.co.id)

Search: `/id/search?q=<terms>` (the form without `/id/` redirects). Read after `produk ditemukan`. Sale items show `Harga penjualan`, `Rp.1.540.000,00`, `Rp.2.200.000,00 Harga asli`, `-30%`: note the `,00`. A cookie banner sits at the top of the text and does not block reading.

## Nike (nike.com/id)

Search: `/id/w?q=<terms>`; read after `Search results for`. Per item: an optional `Bestseller`, `Just In` or `Sold Out`, name, category, price, and on sale items the sale price, list price and `NN% off`. Product URL: `/id/t/<slug>/<style-colour>`. Photo: `og:image`, a PNG that curl downloads.

## Planet Sports (planetsports.asia)

Magento, same owner as Sports Station. Bags: `/men/accessories/bags.html`; 24 items load, then a `LOAD MORE` button. The `DISKON` filter is broken: use `/sale.html` and its category instead. Listing prices can be stale (50% on the list, 30% on the product page): trust the product page. Photo: `og:image`, but curl gets HTML, so use the browser `download` tool.

## Sports Station (sportsstation.id)

Bags: `/men-accessories-bags.html`, with discount buckets in the facets. Product URL: `/pdp/<Name-With-Dashes>/<SP + digits>`. **`og:image` is the site logo**: the photo is the second image over 300 px wide, on `bb-scm-prod-pim.oss-ap-southeast-5.aliyuncs.com`; drop its query string and curl works. Product pages have no description, so no capacity or laptop size. Sold-out items stay listed with their discount: check stock on the product page.

## Eiger (eigeradventure.com)

Product URL: `/d/<slug>`. The product data gives sale and list price, capacity, laptop size, sold count, rating and stock per colour. Prices have no space: `Rp381.750`. Photo: `og:image`. **Flash sales end during the day**: two bags went from 30% off to full price and to 10% off inside two hours. Listing URL: not recorded.

## Samsonite (samsonite.co.id)

Product URL ends `ss-<product id>-<colour id>.html`. Sale prices carry no end date; many discounted items are out of stock. `og:image` is empty and the first large images are a sign-up popup. Find the photo by the product id in the page HTML:

```js
t.eval(`(()=>{const h=document.documentElement.innerHTML;const m=h.match(/https?:[^"' )]*${id}_[^"' )]*\\.(?:jpg|png|webp)/g)||[];return [...new Set(m)].slice(0,2)})()`)
```

Append `?sw=400` to resize. curl gets HTML: use the browser `download` tool. Zalora's Samsonite store had the same prices.

## Decathlon (decathlon.co.id)

Product URL: `/p/<slug>-<id>.html`. Prices have no space: `Rp560.000`. Photo: `og:image`. Promo codes appear on the homepage with a minimum spend (`PD40K`: 40.000 off from 800.000). "Turun Harga" items show no struck-out price.

## Finding a store's promos

A web search for a sale event returned nothing useful. Open the stores' homepages in one `run` and filter each page's text:

```js
for (const [k, id] of Object.entries(keep.tabs)) {
  const s = String(tab(id).text());
  console.log('=== ' + k + '\n' + s.split('\n').filter(l => /black|friday|11\.11|12\.12|sale|diskon|promo|off|%/i.test(l)).slice(0, 15).join('\n').slice(0, 900));
}
```
