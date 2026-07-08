"""
Second pass: enrich scrape/buildings.csv with per-building detail fields
(status, year built, floor count, basement floors, height, uses, structural types)
scraped from each building's detail page: skyscraperpage.com/cities/?buildingID=<id>

These fields are NOT on the city listing page — only on individual detail pages.
Resumable: skips buildingIDs already present in buildings_enriched.csv.
"""
import re
import csv
import time
import random
import html as H
from pathlib import Path

import requests

OUT = Path(__file__).parent / "scrape"
SRC = OUT / "buildings.csv"
DEST = OUT / "buildings_enriched.csv"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
})

DETAIL_FIELDS = ["status", "year_began", "year_finished", "floor_count",
                 "basement_floors", "height_ft", "uses", "structural_types"]


def parse_detail(bid):
    r = session.get("https://skyscraperpage.com/cities/", params={"buildingID": bid}, timeout=30)
    r.raise_for_status()
    t = H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text)))

    def g(p):
        m = re.search(p, t, re.I)
        return m.group(1).strip() if m else None

    def block(start, end):
        m = re.search(start + r"(.+?)" + end, t, re.I)
        if not m:
            return None
        items = [x.strip(" -").strip() for x in m.group(1).split("-") if x.strip(" -").strip()]
        return "; ".join(items) if items else None

    return {
        "status": g(r"Status:\s*([A-Za-z]+)"),
        "year_began": g(r"Began\s*(\d{4})"),
        "year_finished": g(r"Finished\s*(\d{4})"),
        "floor_count": g(r"Floor Count\s*(\d+)"),
        "basement_floors": g(r"Basement Floors\s*(\d+)"),
        "height_ft": g(r"([\d,]+)\s*ft"),
        "uses": block(r"Building Uses", r"(?:Structural Types|Companies|Height|Construction)"),
        "structural_types": block(r"Structural Types", r"(?:Companies|Height|Building|Related|$)"),
    }


def main():
    with open(SRC, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"{len(rows)} buildings to enrich")

    done = {}
    if DEST.exists():
        with open(DEST, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("status") or r.get("year_finished"):
                    done[r["buildingID"]] = r
        print(f"resuming: {len(done)} already enriched")

    fieldnames = list(rows[0].keys()) + DETAIL_FIELDS
    out_rows = []
    for i, row in enumerate(rows, 1):
        bid = row["buildingID"]
        if bid in done:
            merged = {**row, **{k: done[bid].get(k) for k in DETAIL_FIELDS}}
        else:
            try:
                detail = parse_detail(bid)
                merged = {**row, **detail}
                if i % 20 == 0 or i < 5:
                    print(f"  [{i}/{len(rows)}] {row['name'][:32]:32} "
                          f"{detail['status']}, {detail['year_finished']}, "
                          f"{detail['floor_count']} fl")
                time.sleep(random.uniform(1.0, 2.0))
            except Exception as e:
                print(f"  ! {bid} {row['name']}: {e}")
                merged = {**row, **{k: None for k in DETAIL_FIELDS}}
        out_rows.append(merged)

        # incremental save every row
        with open(DEST, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(out_rows)

    print(f"\nDone -> {DEST} ({len(out_rows)} rows)")


if __name__ == "__main__":
    main()
