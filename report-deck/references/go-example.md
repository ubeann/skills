# Go example

One implementation of the pipeline: Go renderer, chromedp printer, `go test` gates. Treat it as a worked example, not the only shape.

## Layout

```
cmd/analysis/   slow pass; writes out/analysis/report.json
internal/report/ the JSON schema as Go types, plus Load()
cmd/report/
  main.go        flags, Load, render, printPDF
  pages.go       one func per page, each returning a section.page string
  format.go      num, pct, rupiah and friends
  style.css      embedded
  main_test.go   gates
```

## Print with the overflow gate

```go
//go:embed overflow.js
var overflowJS string

func printPDF(ctx context.Context, htmlPath, pdfPath string) error {
	abs, err := filepath.Abs(htmlPath)
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(ctx, 2*time.Minute)
	defer cancel()
	allocCtx, cancelAlloc := chromedp.NewExecAllocator(ctx, chromedp.DefaultExecAllocatorOptions[:]...)
	defer cancelAlloc()
	tabCtx, cancelTab := chromedp.NewContext(allocCtx)
	defer cancelTab()

	var overflow string
	var pdf []byte
	err = chromedp.Run(tabCtx,
		chromedp.Navigate((&url.URL{Scheme: "file", Path: abs}).String()),
		chromedp.Evaluate(overflowJS, &overflow),
		chromedp.ActionFunc(func(ctx context.Context) error {
			if overflow != "[]" {
				return fmt.Errorf("elements leave their page:\n%s", overflow)
			}
			var err error
			pdf, _, err = page.PrintToPDF().WithPrintBackground(true).WithPreferCSSPageSize(true).Do(ctx)
			return err
		}))
	if err != nil {
		return err
	}
	return os.WriteFile(pdfPath, pdf, 0o644)
}
```

The script returns a JSON string, so `Evaluate` decodes into a `string`. Print it raw on failure; the `page` and `el` fields point at the offender and `text` matches it to the PNG.

## Gates as tests

```go
func TestFormat(t *testing.T) {
	for _, c := range []struct{ got, want string }{
		{num(2984202), "2.984.202"},
		{num(int64(-1500)), "-1.500"},
		{pct(0.2043, 1), "20,4%"},
		{pct(0.0000003, 2), "<0,01%"},
		{pct(0.99998, 1), ">99,9%"},
		{rupiah(65_100_000_000_000), "Rp 65,1 T"},
		{rupiah(-2_600_000_000), "-Rp 3 M"},     // sign before the unit
		{rupiah(999_999_999), "Rp 1 M"},         // rounds across the unit boundary
		{rupiah(999_950_000_000), "Rp 1,0 T"},
		{pct(0, 1), "0,0%"},
		{pct(1, 1), "100,0%"},
	} {
		if c.got != c.want {
			t.Errorf("got %q, want %q", c.got, c.want)
		}
	}
}

func TestRender(t *testing.T) {
	d := fixture() // small hand-built report.Data with one row per shape
	html := render(d, "Author")
	if n := strings.Count(html, `<section class="page`); n != 14 {
		t.Errorf("rendered %d pages, want 14", n)
	}
	for _, want := range []string{
		"14 Oktober 2026",        // cover date
		"Rp 3,0 T",               // page 9 total
		"Rencana &lt;Rp 0&gt;",   // data is escaped
	} {
		if !strings.Contains(html, want) {
			t.Errorf("report lacks %q", want)
		}
	}
	for _, bad := range []string{"NaN", "Inf", "%!"} {
		if strings.Contains(html, bad) {
			t.Errorf("report contains %q", bad)
		}
	}
}
```

Write the fixture so that every sentinel is a value the page computes from it, with the arithmetic in a comment beside the fixture field. A sentinel copied from real output tests nothing.

## Page function comment

```go
// realisasiPage is page 9, kicker "Realisasi": investment by quarter, 2025 vs 2026.
func (r *doc) realisasiPage() pageSpec {
```

## Pre-commit hook

GitButler runs `.git/hooks/pre-commit-user`; plain git runs `pre-commit`. Same script either way:

```sh
#!/bin/sh
set -e
bad=$(gofmt -l $(git ls-files '*.go'))
if [ -n "$bad" ]; then echo "gofmt: $bad"; exit 1; fi
golangci-lint run ./...
```

## Deck output

The deck is the same `render` with the controller inlined. Keep the Deck and print blocks in the embedded `style.css` so one stylesheet serves both outputs.

```go
//go:embed deck.js
var deckJS string

// renderDeck is render plus the controller: one file, opened from disk.
func renderDeck(d *report.Data, author string) string {
	html := render(d, author)
	return strings.Replace(html, "</body>", "<script>"+deckJS+"</script></body>", 1)
}
```

`main` writes it next to the PDF:

```go
deck := flag.String("deck", "out/analysis/report-deck.html", "offline deck; empty to skip")
...
if *deck != "" {
	if err := writeAtomic(*deck, []byte(renderDeck(d, author))); err != nil {
		return err
	}
}
```

`printPDF`, the deck screenshot, and the deck test share one helper that opens a file in a fresh tab:

```go
// tab opens htmlPath#fragment in a new Chrome tab and runs actions in it.
func tab(ctx context.Context, htmlPath string, fragment string, actions ...chromedp.Action) error {
	abs, err := filepath.Abs(htmlPath)
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(ctx, 2*time.Minute)
	defer cancel()
	allocCtx, cancelAlloc := chromedp.NewExecAllocator(ctx, chromedp.DefaultExecAllocatorOptions[:]...)
	defer cancelAlloc()
	tabCtx, cancelTab := chromedp.NewContext(allocCtx)
	defer cancelTab()
	u := (&url.URL{Scheme: "file", Path: abs, Fragment: fragment}).String()
	return chromedp.Run(tabCtx, append([]chromedp.Action{chromedp.Navigate(u)}, actions...)...)
}
```

Screenshot page N of the deck, fragments shown, for step 4 (`-shot N` in main):

```go
func screenshotDeck(ctx context.Context, deckPath string, n int, pngPath string) error {
	var png []byte
	err := tab(ctx, deckPath, strconv.Itoa(n),
		chromedp.EmulateViewport(1280, 720),
		chromedp.Evaluate(`document.querySelectorAll('.page.current .fragment').forEach(f => f.classList.add('shown'))`, nil),
		chromedp.CaptureScreenshot(&png))
	if err != nil {
		return err
	}
	return os.WriteFile(pngPath, png, 0o644)
}
```

The deck test behind step 3's criterion. It drives the installed Chrome, so it runs only when asked; the page count is read from the PDF bytes, which is enough for Chrome's output:

```go
func TestDeckInChrome(t *testing.T) {
	if os.Getenv("REPORT_CHROME") == "" {
		t.Skip("set REPORT_CHROME=1 to drive the installed Chrome")
	}
	deck := "../../out/analysis/report-deck.html"
	var at, after string
	var pdf []byte
	err := tab(context.Background(), deck, "5",
		chromedp.EmulateViewport(1280, 720),
		chromedp.Evaluate(`document.querySelector('.page.current footer .tn').textContent`, &at),
		chromedp.KeyEvent(kb.PageDown),
		chromedp.Evaluate(`document.querySelector('.page.current footer .tn').textContent + ' ' + location.hash`, &after),
		chromedp.ActionFunc(func(ctx context.Context) error {
			var err error
			pdf, _, err = page.PrintToPDF().WithPrintBackground(true).WithPreferCSSPageSize(true).Do(ctx)
			return err
		}))
	if err != nil {
		t.Fatal(err)
	}
	if at != "5" {
		t.Errorf("#5 landed on page %q", at)
	}
	if after != "6 #6" {
		t.Errorf("PageDown from 5 gave %q, want \"6 #6\"", after)
	}
	if n := strings.Count(string(pdf), "/Type /Page\n") + strings.Count(string(pdf), "/Type /Page/"); n != 14 {
		t.Errorf("printed deck has %d pages, want 14", n)
	}
}
```

The one-file gate as a test:

```go
func TestDeckIsOneFile(t *testing.T) {
	html := renderDeck(fixture(), "Author")
	for _, bad := range []string{"<script src", `<link rel="stylesheet"`, `src="http`, "url(http", `type="module"`, "fetch("} {
		if strings.Contains(html, bad) {
			t.Errorf("deck is not one file: contains %q", bad)
		}
	}
	if got, want := strings.Count(html, `<section class="page`), strings.Count(render(fixture(), "Author"), `<section class="page`); got != want {
		t.Errorf("deck has %d pages, PDF html has %d", got, want)
	}
}
```
