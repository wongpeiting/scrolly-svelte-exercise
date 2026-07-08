"""One-off: curate the scrolly cast from scrape/buildings.csv into the Svelte app.
Facts (year/floors/height_ft/uses) verified against SkyscraperPage detail pages
on 2026-07-07 — see docs/superpowers/specs/2026-07-07-conversion-scrolly-design.md.
"""
import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CSV = ROOT / "scrape" / "buildings.csv"
GIF_SRC = ROOT / "scrape" / "illustrations"
JSON_OUT = ROOT / "src" / "lib" / "data" / "conversions.json"
STATIC_OUT = ROOT / "static" / "illustrations"

# buildingID -> verified facts + group; array order below = display order
CAST = [
    ("3149",  {"year": 1907, "floors": 23, "height_ft": 325, "uses": "residential",          "group": "downtown"}),  # 90 West
    ("832",   {"year": 1913, "floors": 57, "height_ft": 792, "uses": "mixed, incl. residential", "group": "downtown"}),  # Woolworth
    ("17171", {"year": 1928, "floors": 38, "height_ft": 495, "uses": "residential",          "group": "downtown"}),  # 20 Pine
    ("231",   {"year": 1931, "floors": 57, "height_ft": 748, "uses": "office (converted)",   "group": "downtown"}),  # 20 Exchange (748 = antenna; 846 was never-built "intended height")
    ("131",   {"year": 1932, "floors": 67, "height_ft": 952, "uses": "mixed, incl. residential", "group": "downtown"}),  # 70 Pine
    ("10262", {"year": 1958, "floors": 34, "height_ft": 436, "uses": "office to 680 apartments (2029)", "group": "midtown"},),  # 750 Third
    ("7409",  {"year": 1988, "floors": 31, "height_ft": 430, "uses": "office to residential", "group": "midtown"}),  # 135 E 57th
    ("5279",  {"year": 2002, "floors": 40, "height_ft": 574, "uses": "office to residential", "group": "midtown"}),  # 5 Times Sq
    ("42701", {"year": 1961, "floors": 33, "height_ft": 409, "uses": "office to about 1,600 apartments", "group": "hero"}),      # Pfizer / 235 E 42nd
]

with open(CSV, encoding="utf-8") as f:
    rows = {r["buildingID"]: r for r in csv.DictReader(f)}
out = []
for bid, facts in CAST:
    if bid not in rows:
        sys.exit(f"FATAL: buildingID {bid} not in {CSV}")
    r = rows[bid]
    gif = GIF_SRC / f"{r['drawingID']}.gif"
    if not gif.exists():
        sys.exit(f"FATAL: missing illustration {gif}")
    out.append({
        "id": bid,
        "name": r["name"],
        "drawingID": r["drawingID"],
        "file": f"/illustrations/{r['drawingID']}.gif",
        "w": int(r["img_width"]),
        "h": int(r["img_height"]),
        "illustrator": r["illustrator"],
        **facts,
    })

# Guard the to-scale invariant the whole graphic depends on (~0.305 px/ft)
for b in out:
    ratio = b["h"] / b["height_ft"]
    if not 0.29 <= ratio <= 0.32:
        sys.exit(f"FATAL: {b['name']} breaks scale: {b['h']}px / {b['height_ft']}ft = {ratio:.3f} px/ft")

STATIC_OUT.mkdir(parents=True, exist_ok=True)
for b in out:
    shutil.copy2(GIF_SRC / f"{b['drawingID']}.gif", STATIC_OUT / f"{b['drawingID']}.gif")

JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
JSON_OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {JSON_OUT.relative_to(ROOT)} ({len(out)} buildings)")
print(f"copied {len(out)} gifs -> {STATIC_OUT.relative_to(ROOT)}")
for b in out:
    print(f"  {b['group']:9} {b['name']:28} {b['year']}  {b['height_ft']}ft  {b['w']}x{b['h']}px")
