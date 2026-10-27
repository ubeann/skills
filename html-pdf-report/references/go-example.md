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
