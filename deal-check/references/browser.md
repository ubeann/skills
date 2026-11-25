# Browser idioms for a deal run

Reference for step 3 of [`deal-check`](../SKILL.md): how the yab-browser MCP behaved across two runs on 2026-11-25. Store pages block plain `curl`, so listings and product pages go through the browser.

## Inside `run`

| Call | Shape that worked |
|---|---|
| open a tab | `const t = open(url)`; `t.id` is the tab id |
| reuse a tab | `tab(id)` with a stored or literal id |
| move it | `t.navigate(url)` then `sleep(2500)` |
| read text | `t.text()`: title and URL, then the visible text one line per node |
| run page code | `t.eval(js)`; an async function in the page code is awaited |
| find a ref | `t.locate(['Visible text'])` returns `{"Visible text": "e286"}` |
| output | `console.log` only; raise the `outputLimit` tool parameter (up to 32000 was used) for long output |
| state | `keep.anything = value` survives between `run` calls |

`await` is optional on all of them.

**`eval` returns a JSON string.** Page code that returns an object needs one `JSON.parse`; page code that returns `JSON.stringify(...)` needs two. This cost three failed runs. One idiom covers both:

```js
let r = t.eval(js);
if (typeof r === 'string') r = JSON.parse(r);
if (typeof r === 'string') r = JSON.parse(r);
```

**`keep` lasts one turn.** It was empty at the start of both later user turns. Write results into `keep` inside the loop, never after it (a failed run keeps what was already assigned), and put the data on disk before the turn ends.

## Errors and what they meant

| Error | Cause | Fix |
|---|---|---|
| `The requested page changed. Take a new snapshot before continuing.` | The page was still loading, or the loop asked for one page past the end of a listing | `sleep(4000)` and read with `t.text()`; wrap each page in `try`/`catch`; stop when a page adds no new items |
| `CDP timeout` | One `eval` ran longer than about 18 s | Smaller batches: 6 listing pages or 8 product pages per `eval` |
| `... is not a function`, `undefined is not an object` right after an `eval` | The result was still a string | The parse idiom above |
| `no tab yet: const t = open(url)` after a failed run | The tab handle did not survive the failure | Call the standalone `open` tool, read the id from its reply (`tab: 8e860471 · ...`), use `tab('8e860471')` |
| `no answer within 25 s` on `open`, even for a blank test page | The browser app is not answering; the store is not the cause | Tell the user and continue from files on disk; retrying stores does not help |
| `no tab "${keep.tid}"` on the standalone `eval` tool | Tool arguments are not interpolated | Pass the literal id; the standalone `eval` also has no top-level `await` |

In a document built with `DOMParser`, `innerText` is empty: use `textContent` and selectors.

## Many pages: fetch inside the page

Opening a tab per page costs 15 to 35 seconds each. From a tab already on the store, `fetch` of same-origin pages inside `eval` carries the browser's cookies and costs about 1 second per product page in parallel batches. Use it past ten pages on one store. The Foot Locker section of `stores.md` has both loops as they ran.

## Rows to disk

`run` cannot write files. Put the rows in a `data:` link on the page and download it:

```js
const t = tab('e038792d');
const data = JSON.stringify(keep.shoes);
t.eval(`(()=>{const a=document.createElement('a');a.textContent='DOWNLOAD ROWS';a.download='rows.json';a.href='data:application/json;charset=utf-8,'+encodeURIComponent(${JSON.stringify(data)});a.style.cssText='position:fixed;top:0;left:0;z-index:99999;background:red;padding:20px';document.body.appendChild(a);return 'ok'})()`);
console.log(JSON.stringify(t.locate(['DOWNLOAD ROWS'])));
```

Then the `download` tool with that tab and ref. It replies with the saved path under `~/Downloads/yab/Task <id>/`; copy the file into the run folder.

## Photos

1. **Find the URL.** One pass over the product pages, which also re-reads the visible prices:

   ```js
   const js = `({og:(document.querySelector('meta[property="og:image"]')||{}).content||'', img:[...document.images].filter(i=>i.naturalWidth>=300).map(i=>i.currentSrc||i.src).slice(0,3), price:(document.body.innerText.match(/Rp\\.?\\s?[\\d.,]+/g)||[]).slice(0,3)})`;
   keep.img = {};
   for (let i = 0; i < urls.length; i++) { try { t.navigate(urls[i]); sleep(2200);
     let r = t.eval(js); if (typeof r === 'string') r = JSON.parse(r);
     keep.img[i] = r; console.log(i, r.og || r.img[0], JSON.stringify(r.price)); } catch (e) { console.log(i, 'ERR', e.message); } }
   ```

   `og:image` is right on most stores. The exceptions are in each store's section of `stores.md`.
2. **Download** with `curl -sL -m 25 -A "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/130 Safari/537.36" -o <file> <url>`, then `file -b <file>`. "HTML document" means the store blocked curl: use the `download` tool with `{tab, url}` instead. The tab can sit on any page; it does not have to be on the image's host.
3. **Leave the size alone.** `cards.py` resizes each photo to 360 px.
4. **Look at every photo** in the `html_preview` of the cards. Listing colour names were wrong often enough ("Black" for a purple bag, "Core Black" for black and camo) that the card's colour comes from the photo, with the listing's name in the note when they differ.
