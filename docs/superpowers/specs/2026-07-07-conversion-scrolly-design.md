# Scrolly: "The conversion that reached too high"

**Date:** 2026-07-07
**Exercise:** Scroller-component scrollytelly — ≥4 slides, background graphic updates per slide, real data, text speaks to the render.

## Narrative

News peg: on July 7, 2026, 235 East 42nd Street (the former Pfizer HQ, mid-conversion into ~1,600
apartments — the largest office-to-residential conversion in NYC history) buckled: a compromised
21st-floor beam, two buckling columns, a five-block "frozen zone" around Grand Central.

Argument, one beat per slide: conversions started downtown in old, narrow towers → the post-pandemic
wave moved to Midtown and got bigger → this project alone grew _upward_, adding 11 floors to the
adjoining 219 E 42nd — and that new load is what failed.

## The four slides

| #   | Beat                                                                                                                                                                                                                                          | Graphic state                                                                                |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 1   | **The buckle.** 235 E 42nd, 1961, was being converted to ~1,600 apartments — largest in NYC history. This morning its columns buckled.                                                                                                        | Hero illustration alone, annotated (409 ft · 1961 · office → residential)                    |
| 2   | **It began downtown, old and narrow.** First conversion wave (1990s–2000s): 90 West (1907), Woolworth (1913), 20 Pine (1928), 20 Exchange (1931), 70 Pine (1932). SkyscraperPage's `use` field already lists most as residential/mixed.       | Downtown five enter to scale; hero dims                                                      |
| 3   | **The new wave: Midtown, and bigger.** Post-pandemic, half of announced conversions are in Midtown — 5 Times Square, 135 E 57th, 750 Third — pushed by City of Yes (2024), the 467-m tax break, and the city's Office Conversion Accelerator. | Midtown trio enters highlighted; downtown five dim                                           |
| 4   | **This one reached too high.** Unlike every precedent, this project added floors — an 11-story extension on the adjoining 219 E 42nd. Under that new load, two columns bent and the floors sagged.                                            | All dim except hero; ghost-extension schematic beside hero + buckle marker at the 21st floor |

## Cast (from scrape/buildings.csv; illustrations on disk)

| Building                     | buildingID | drawingID | px (w×h) | Year | Ht (ft) | Group    |
| ---------------------------- | ---------- | --------- | -------- | ---- | ------- | -------- |
| Pfizer Building (235 E 42nd) | 42701      | 71359     | 70×125   | 1961 | 409     | hero     |
| 90 West Street               | 3149       | 36624     | 71×99    | 1907 | 325     | downtown |
| Woolworth Building           | 832        | 74220     | 84×241   | 1913 | 792     | downtown |
| 20 Pine                      | 17171      | 33086     | 67×151   | 1928 | 495     | downtown |
| 20 Exchange Place            | 231        | 4166      | 66×228   | 1931 | 748     | downtown |
| 70 Pine Street               | 131        | 74456     | 96×290   | 1932 | 952     | downtown |
| 5 Times Square               | 5279       | 74028     | 67×175   | 2002 | 574     | midtown  |
| 135 East 57th Street         | 7409       | 28644     | 67×131   | 1988 | 430     | midtown  |
| 750 Third Avenue             | 10262      | 32970     | 85×133   | 1958 | 436     | midtown  |

All years/heights verified against SkyscraperPage detail pages; illustrations verified on disk.

All SkyscraperPage drawings share ≈0.305 px/ft, so raw `img_height` values are mutually to scale:
render every image at `img_height × k` for one shared multiplier `k` and relative heights are true.

## Architecture

```
src/lib/data/conversions.json        curated cast (fields above + uses + blurb per building)
static/illustrations/<drawingID>.gif 9 GIFs copied from scrape/illustrations/
src/lib/components/ConversionSkyline.svelte   background graphic
src/routes/+page.svelte              Scroller wiring + step prose
```

**ConversionSkyline.svelte** — props: `index`, `count` (from Scroller bindables).

- Lays the 9 buildings on a shared baseline (flex row, align-end), each `<img>` height = `img_height × k`.
  `k` derived from container height so the tallest (70 Pine, 290px) fits with headroom.
- Per-slide state via `$derived` from `index`: which group is `active` (full opacity + label) vs
  `dimmed` (low opacity, grayscale). Buildings not yet introduced are hidden
  (`{#if}` + keyed `{#each}` with `transition:fade`).
- Slide 4 extras, drawn as an SVG overlay anchored to the hero:
  - **Ghost extension:** dashed translucent block _beside_ the hero, labeled
    "11-floor extension — 219 E 42nd (adjoining, not pictured)". Never drawn on top of the
    hero illustration — the extension is on the neighboring structure (per NYT diagram).
  - **Buckle marker:** line + label at 21/37 of hero height ("beam compromised, 21st floor").
- Labels: name, year, height; small-caps credit strip at the bottom listing SkyscraperPage +
  illustrator names (required attribution).

**+page.svelte** — headline + intro para (news peg), `<Scroller top={0} bottom={1} bind:index bind:count>`
with `background` snippet → `<ConversionSkyline {index} {count} />` and `foreground` snippet → four
`.step` divs (`min-height: 100vh`) carrying the slide prose. `debugger={false}` for the final piece.

## Data flow

`scrape/buildings.csv` (+ `buildings_enriched.csv` when done) → one-off build script writes
`src/lib/data/conversions.json` and copies the 9 GIFs to `static/illustrations/`. The Svelte app
imports the JSON statically; no runtime fetches of scraped data.

## Facts discipline

- News claims (1,600 apartments, largest conversion, 21st-floor beam, 11-story extension on 219,
  frozen zone) are sourced to NYT live coverage, 2026-07-07.
- Trend claims (~30M sq ft converted over two decades; post-pandemic half of conversions in Midtown;
  growing footprints) sourced to WSJ, 2025-12-01. City programs to nyc.gov Office Conversion
  Accelerator + City of Yes.
- SkyscraperPage supplies only physical stats + illustrations. Known discrepancy: SSP lists the
  Pfizer Building at 33 floors, NYT says 37 stories — prose follows NYT; the drawing is illustrative.
- 20 Exchange Place's `use` field still reads "office" though the building converted — cast
  membership comes from reporting, not the `use` field; the `use` flips are corroboration only.
- Sources listed in a footer note on the page.

## Error handling / edge cases

- Missing GIF → build script fails loudly (all 9 verified on disk already).
- `index` > 3 impossible (4 steps), but component clamps group lookups.
- Small screens: skyline row scales down via container-relative `k`; text steps stack full-width.

## Testing

- `npm run dev` → walk all four steps: correct group enters/dims each slide; ghost extension and
  buckle marker appear only on slide 4.
- Resize check (narrow viewport) — no overflow, baseline holds.
- Proofread step prose against the sources above.
