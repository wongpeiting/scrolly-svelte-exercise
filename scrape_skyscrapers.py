"""
Scrape SkyscraperPage city diagram: building metadata + illustrations.
Data lives in embedded data['...'] JS arrays in the page source (no HTML parsing needed).
Illustrations are served from https://skyscraperpage.com/diagrams/images/<drawingID>.gif
"""
import re
import csv
import html as htmllib
import json
import time
import random
from pathlib import Path

import requests

CITY_ID = 8  # New York City
BASE = "https://skyscraperpage.com/diagrams/"
OUT = Path(__file__).parent / "scrape"
IMG_DIR = OUT / "illustrations"
OUT.mkdir(exist_ok=True)
IMG_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
})


def parse_js_array(raw):
    """Parse a JS array literal body like  1,2,,'a','b'  into a Python list.
    Handles empty slots (-> None) and quoted strings with HTML entities."""
    items, buf, in_str, quote, esc = [], "", False, "", False
    for ch in raw:
        if in_str:
            if esc:
                buf += ch; esc = False
            elif ch == "\\":
                buf += ch; esc = True
            elif ch == quote:
                in_str = False
            else:
                buf += ch
        else:
            if ch in "'\"":
                in_str = True; quote = ch
            elif ch == ",":
                items.append(buf); buf = ""
            else:
                buf += ch
    items.append(buf)

    def clean(v):
        v = v.strip()
        if v == "":
            return None
        return htmllib.unescape(v)
    return [clean(x) for x in items]


def extract_data_arrays(page_html):
    """Return dict {top: {key: [values]}} for all data['top']['key'] = [...] arrays."""
    result = {}
    for top, key, body in re.findall(
        r"data\['(\w+)'\]\['(\w+)'\]\s*=\s*\[([^\]]*)\]", page_html):
        result.setdefault(top, {})[key] = parse_js_array(body)
    return result


def get_search_id():
    r = session.get(BASE, params={"cityID": CITY_ID}, timeout=30)
    r.raise_for_status()
    m = re.search(r"searchID=(\d+)", r.text)
    if not m:
        raise RuntimeError("Could not find searchID on city page")
    pages = [int(p) for p in re.findall(r"page=(\d+)", r.text)]
    return m.group(1), (max(pages) if pages else 1), r.text


def rows_from_page(page_html):
    """Zip the parallel arrays into one dict per building."""
    d = extract_data_arrays(page_html)
    b = d.get("building", {})
    img = d.get("image", {})
    ill = d.get("illustrator", {})
    arch = d.get("architect", {})
    n = len(b.get("buildingID", []))
    rows = []
    for i in range(n):
        def g(sub, key):
            arr = sub.get(key, [])
            return arr[i] if i < len(arr) else None
        rows.append({
            "buildingID": g(b, "buildingID"),
            "name": g(b, "name"),
            "architect": g(arch, "name"),
            "illustrator": g(ill, "illustrator"),
            "illustrator_memberID": g(ill, "memberID"),
            "drawingID": g(img, "drawingID"),
            "img_width": g(img, "width"),
            "img_height": g(img, "height"),
            "img_added": g(img, "timeAdded"),
            "threadID": g(b, "threadID"),
            "timeCreated": g(b, "timeCreated"),
        })
    return rows


def polite_sleep():
    time.sleep(random.uniform(1.0, 2.0))


def main():
    print("Fetching city page to get searchID...")
    search_id, max_page, first_html = get_search_id()
    print(f"searchID={search_id}, pages=1..{max_page}")

    all_rows = []
    for page in range(1, max_page + 1):
        if page == 1:
            page_html = first_html  # reuse; page 1 already fetched
        else:
            r = session.get(BASE, params={"searchID": search_id, "page": page}, timeout=30)
            r.raise_for_status()
            page_html = r.text
        rows = rows_from_page(page_html)
        all_rows.extend(rows)
        print(f"  page {page}/{max_page}: +{len(rows)} buildings (total {len(all_rows)})")

        # incremental save of metadata
        with open(OUT / "buildings.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            w.writeheader()
            w.writerows(all_rows)
        polite_sleep()

    with open(OUT / "buildings.json", "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2, ensure_ascii=False)
    print(f"\nMetadata: {len(all_rows)} buildings -> {OUT/'buildings.csv'}")

    # Download illustrations
    print("\nDownloading illustrations...")
    ok = skip = fail = 0
    for row in all_rows:
        did = row["drawingID"]
        if not did:
            skip += 1
            continue
        dest = IMG_DIR / f"{did}.gif"
        row["illustration_file"] = f"illustrations/{did}.gif"
        if dest.exists():
            ok += 1
            continue
        url = f"https://skyscraperpage.com/diagrams/images/{did}.gif"
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                dest.write_bytes(resp.content)
                ok += 1
            else:
                fail += 1
                print(f"  ! {row['name']} (drawing {did}): HTTP {resp.status_code}")
        except Exception as e:
            fail += 1
            print(f"  ! {row['name']} (drawing {did}): {e}")
        polite_sleep()

    # rewrite metadata with illustration_file column
    with open(OUT / "buildings.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)

    print(f"\nDone. images: {ok} saved, {skip} had no drawing, {fail} failed")
    print(f"Illustrations -> {IMG_DIR}")


if __name__ == "__main__":
    main()
