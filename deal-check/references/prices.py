#!/usr/bin/env python3
"""The price log behind deal-check's price trend: every run appends its prices,
and the next run reads them back.

    python3 prices.py history run.json   # before the verdict: what each item cost before
    python3 prices.py add run.json       # after the reply: file this run

run.json is the file cards.py documents. The log is <dir>/prices.csv, one row
per item per day (date, store, brand, model, colour, price, list_price, promo,
url); `add` also copies run.json to <dir>/<date>-<slug>/. <dir> is --dir, else
$DEALS_DIR, else ~/deals.

`history` prints, per item, the earlier prices of the same listing (same url)
and the lowest earlier price of the same brand and model at any store. An item
with no earlier row prints "no history": write that into its evidence, never a
guess.
"""
import argparse
import csv
import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path

FIELDS = ["date", "store", "brand", "model", "colour", "price", "list_price", "promo", "url"]


def norm_url(u):
    return (u or "").split("?")[0].split("#")[0].rstrip("/").lower()


def model_key(r):
    return (r["brand"].strip().lower(), r["model"].strip().lower())


def load(log):
    if not log.exists():
        return []
    with log.open(newline="") as f:
        return list(csv.DictReader(f))


def rp(n):
    return f"{int(n):,}".replace(",", ".")


def add(run, src, root):
    log = root / "prices.csv"
    rows = load(log)
    day = run.get("date") or date.today().isoformat()
    seen = {(r["date"], norm_url(r["url"])) for r in rows}
    new = []
    for x in run["items"]:
        if (day, norm_url(x["url"])) in seen:
            continue
        seen.add((day, norm_url(x["url"])))
        new.append({"date": day, "store": x["store"], "brand": x["brand"], "model": x["model"],
                    "colour": x.get("colour") or "", "price": int(x["price"]),
                    "list_price": int(x["list_price"]) if x.get("list_price") else "",
                    "promo": x.get("promo") or "", "url": x["url"]})
    root.mkdir(parents=True, exist_ok=True)
    fresh = not log.exists()
    with log.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if fresh:
            w.writeheader()
        w.writerows(new)
    folder = root / f'{day}-{run.get("slug", "run")}'
    folder.mkdir(exist_ok=True)
    if src.resolve() != (folder / "run.json").resolve():
        shutil.copyfile(src, folder / "run.json")
    print(f"added {len(new)} rows to {log} ({len(run['items']) - len(new)} already logged for {day})")
    print(f"run filed in {folder}")


def history(run, root):
    rows = load(root / "prices.csv")
    day = run.get("date") or date.today().isoformat()
    earlier = [r for r in rows if r["date"] < day]
    for x in run["items"]:
        same = sorted((r for r in earlier if norm_url(r["url"]) == norm_url(x["url"])),
                      key=lambda r: r["date"])
        model = [r for r in earlier if model_key(r) == model_key(x)]
        head = f'{x["brand"]} {x["model"]}, {x.get("colour") or "-"} @ {x["store"]}: now {rp(x["price"])}'
        if not same and not model:
            print(f"{head} | no history")
            continue
        parts = []
        if same:
            low = min(same, key=lambda r: int(r["price"]))
            last = same[-1]
            parts.append(f'this listing: {len(same)} earlier, lowest {rp(low["price"])} on {low["date"]}, '
                         f'last {rp(last["price"])} on {last["date"]}')
        if model:
            low = min(model, key=lambda r: int(r["price"]))
            parts.append(f'this model anywhere: lowest {rp(low["price"])} at {low["store"]} '
                         f'({low["colour"] or "-"}) on {low["date"]}')
        print(f"{head} | " + " | ".join(parts))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=["add", "history"])
    ap.add_argument("run", type=Path)
    ap.add_argument("--dir", type=Path)
    args = ap.parse_args()
    root = (args.dir or Path(os.environ.get("DEALS_DIR") or "~/deals")).expanduser()
    run = json.loads(args.run.read_text())
    missing = [f'item {i}: missing {k}' for i, x in enumerate(run["items"])
               for k in ("store", "brand", "model", "url", "price") if x.get(k) in (None, "")]
    if missing:
        print("\n".join(missing))
        sys.exit(1)
    add(run, args.run, root) if args.command == "add" else history(run, root)


if __name__ == "__main__":
    main()
