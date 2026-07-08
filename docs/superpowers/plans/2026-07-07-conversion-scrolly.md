# Conversion Scrolly Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the 4-slide "conversion that reached too high" scrollytelly on the root page, driven by the existing `Scroller` component and the scraped SkyscraperPage data.

**Architecture:** A one-off Python build script curates 9 buildings from `scrape/buildings.csv` into `src/lib/data/conversions.json` and copies their GIFs into `static/illustrations/`. A new `ConversionSkyline.svelte` renders them to scale on one baseline and changes state per Scroller `index`. `src/routes/+page.svelte` wires the Scroller with four prose steps.

**Tech Stack:** SvelteKit + Svelte 5 runes (no new dependencies), Python 3 stdlib for the build script.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-07-conversion-scrolly-design.md` — follow its cast table, slide table, and facts-discipline section verbatim.
- Svelte 5 runes only (`$props`, `$state`, `$derived`); events as `onclick`-style attributes; snippets via `{#snippet}` / `{@render}`.
- No new npm dependencies.
- Git commits: plain messages, **no Co-Authored-By lines of any kind** (user global rule).
- All SkyscraperPage drawings share ≈0.305 px/ft — raw `img_height` px values are mutually to scale; render as `h * k` for a single shared `k`.
- Never draw added floors on top of the hero illustration — the 11-story extension belongs to the adjoining 219 E 42nd (own schematic, labeled).

---

### Task 1: Data build script → `conversions.json` + copied GIFs

**Files:**
- Create: `build_conversions.py`
- Create (output): `src/lib/data/conversions.json`
- Create (output): `static/illustrations/<drawingID>.gif` × 9

**Interfaces:**
- Consumes: `scrape/buildings.csv` (columns: `buildingID,name,architect,illustrator,…,drawingID,img_width,img_height,…`), `scrape/illustrations/<drawingID>.gif`
- Produces: `src/lib/data/conversions.json` — an **ordered array** of 9 objects:
  `{ id, name, drawingID, file, w, h, year, floors, height_ft, uses, group, illustrator }`
  where `file` is `"/illustrations/<drawingID>.gif"`, `w`/`h` are ints (raw px), `group` ∈ `"hero" | "downtown" | "midtown"`, array order = left-to-right display order (downtown by year, then midtown by year, hero last).

- [ ] **Step 1: Write the script**

```python
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
    ("231",   {"year": 1931, "floors": 57, "height_ft": 846, "uses": "office (converted)",   "group": "downtown"}),  # 20 Exchange
    ("131",   {"year": 1932, "floors": 67, "height_ft": 952, "uses": "mixed, incl. residential", "group": "downtown"}),  # 70 Pine
    ("10262", {"year": 1958, "floors": 34, "height_ft": 436, "uses": "office → 680 apts (2029)", "group": "midtown"},),  # 750 Third
    ("7409",  {"year": 1988, "floors": 31, "height_ft": 430, "uses": "office → residential", "group": "midtown"}),  # 135 E 57th
    ("5279",  {"year": 2002, "floors": 40, "height_ft": 574, "uses": "office → residential", "group": "midtown"}),  # 5 Times Sq
    ("42701", {"year": 1961, "floors": 33, "height_ft": 409, "uses": "office → ~1,600 apts", "group": "hero"}),      # Pfizer / 235 E 42nd
]

rows = {r["buildingID"]: r for r in csv.DictReader(open(CSV, encoding="utf-8"))}
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

STATIC_OUT.mkdir(parents=True, exist_ok=True)
for b in out:
    shutil.copy2(GIF_SRC / f"{b['drawingID']}.gif", STATIC_OUT / f"{b['drawingID']}.gif")

JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
JSON_OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {JSON_OUT.relative_to(ROOT)} ({len(out)} buildings)")
print(f"copied {len(out)} gifs -> {STATIC_OUT.relative_to(ROOT)}")
for b in out:
    print(f"  {b['group']:9} {b['name']:28} {b['year']}  {b['height_ft']}ft  {b['w']}x{b['h']}px")
```

- [ ] **Step 2: Run it and verify output**

Run: `python3 build_conversions.py`
Expected: `wrote src/lib/data/conversions.json (9 buildings)`, 9 gifs copied, table lists 5 downtown + 3 midtown + 1 hero, hero last.

Run: `ls static/illustrations | wc -l` → `9`
Run: `python3 -c "import json; d=json.load(open('src/lib/data/conversions.json')); assert len(d)==9 and d[-1]['group']=='hero' and all(k in d[0] for k in ('file','w','h','year','group')); print('json OK')"`
Expected: `json OK`

- [ ] **Step 3: Commit**

```bash
git add build_conversions.py src/lib/data/conversions.json static/illustrations/
git commit -m "Add conversion cast build script and curated data"
```

---

### Task 2: `ConversionSkyline.svelte` background graphic

**Files:**
- Create: `src/lib/components/ConversionSkyline.svelte`

**Interfaces:**
- Consumes: `$lib/data/conversions.json` (Task 1 schema).
- Produces: component with props `{ index = 0 }` — the Scroller's current step (0–3). No other props needed (`count` unused; slide logic is internal).

- [ ] **Step 1: Write the component**

```svelte
<script>
	import buildings from '$lib/data/conversions.json';
	import { fade } from 'svelte/transition';

	let { index = 0 } = $props();

	// Slide choreography (spec slide table):
	// 0: hero alone · 1: +downtown (active) · 2: +midtown (active) · 3: hero active + schematic
	const step = $derived(Math.max(0, Math.min(index, 3)));
	const introduced = $derived(
		step === 0 ? ['hero'] : step === 1 ? ['hero', 'downtown'] : ['hero', 'downtown', 'midtown']
	);
	const active = $derived(['hero', 'downtown', 'midtown', 'hero'][step]);
	const visible = $derived(buildings.filter((b) => introduced.includes(b.group)));

	// Shared scale: all drawings ~0.305 px/ft, so raw h values are mutually to scale.
	let containerH = $state(0);
	const TALLEST = Math.max(...buildings.map((b) => b.h)); // 290px (70 Pine)
	const k = $derived(containerH > 0 ? (containerH * 0.58) / TALLEST : 0);

	const hero = buildings.find((b) => b.group === 'hero');

	// Slide-4 schematic, same raw-px scale as the drawings:
	// 219 E 42nd (adjoining): 22 existing floors ≈ 275 ft ≈ 84px; extension +11 floors ≈ 138 ft ≈ 42px
	const NEIGHBOR_RAW = 84;
	const EXTENSION_RAW = 42;
	// Buckle marker: beam compromised on the 21st of 37 stories (NYT)
	const BUCKLE_FRAC = 21 / 37;

	const credits = [...new Set(buildings.map((b) => b.illustrator))].join(', ');
</script>

<div class="stage" bind:clientHeight={containerH}>
	{#if k > 0}
		<div class="skyline">
			{#each visible as b (b.id)}
				<figure
					class="building"
					class:dimmed={b.group !== active}
					class:hero={b.group === 'hero'}
					transition:fade={{ duration: 400 }}
				>
					{#if b.group === 'hero' && step === 3}
						<div class="schematic" style:height="{(NEIGHBOR_RAW + EXTENSION_RAW) * k}px">
							<div class="ghost" style:height="{EXTENSION_RAW * k}px">+11 floors</div>
							<div class="neighbor" style:height="{NEIGHBOR_RAW * k}px">219 E 42nd<br />(adjoining)</div>
						</div>
					{/if}
					<div class="tower">
						<img src={b.file} alt="Scale drawing of {b.name}" style:height="{b.h * k}px" />
						{#if b.group === 'hero' && step === 3}
							<div class="buckle" style:bottom="{BUCKLE_FRAC * b.h * k}px">
								<span>beam compromised — 21st floor</span>
							</div>
						{/if}
					</div>
					<figcaption>
						<strong>{b.name}</strong>
						<span>{b.year} · {b.height_ft} ft</span>
						{#if b.group === active}<span class="use">{b.uses}</span>{/if}
					</figcaption>
				</figure>
			{/each}
		</div>
		<p class="credit">Scale drawings: SkyscraperPage.com ({credits})</p>
	{/if}
</div>

<style>
	.stage {
		height: 100vh;
		display: flex;
		flex-direction: column;
		justify-content: flex-end;
		background: linear-gradient(#f5f2ec, #ece7dd);
		overflow: hidden;
	}

	.skyline {
		display: flex;
		align-items: flex-end;
		justify-content: center;
		gap: clamp(0.5rem, 2vw, 1.75rem);
		padding: 0 1rem;
		border-bottom: 2px solid #3d3a35;
	}

	.building {
		position: relative;
		margin: 0;
		display: flex;
		align-items: flex-end;
		gap: 0.4rem;
		transition: opacity 400ms ease, filter 400ms ease;
	}

	.building.dimmed {
		opacity: 0.3;
		filter: grayscale(1);
	}

	.tower {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.tower img {
		display: block;
		width: auto;
	}

	.hero .tower img {
		outline: 2px solid #c0392b;
		outline-offset: 2px;
	}

	figcaption {
		position: absolute;
		top: 100%;
		left: 50%;
		transform: translateX(-50%);
		width: max-content;
		max-width: 9rem;
		padding-top: 0.5rem;
		text-align: center;
		font-family: system-ui, sans-serif;
		font-size: 0.65rem;
		line-height: 1.35;
		color: #3d3a35;
	}

	figcaption strong {
		display: block;
		font-size: 0.7rem;
	}

	figcaption .use {
		display: block;
		color: #c0392b;
		font-weight: 600;
	}

	.buckle {
		position: absolute;
		left: -0.5rem;
		right: -0.5rem;
		border-top: 2px dashed #c0392b;
	}

	.buckle span {
		position: absolute;
		bottom: 0.15rem;
		left: 100%;
		width: max-content;
		margin-left: 0.4rem;
		font-family: system-ui, sans-serif;
		font-size: 0.65rem;
		font-weight: 600;
		color: #c0392b;
	}

	.schematic {
		display: flex;
		flex-direction: column;
		justify-content: flex-end;
		width: 3.2rem;
		font-family: system-ui, sans-serif;
		font-size: 0.55rem;
		text-align: center;
		color: #3d3a35;
	}

	.schematic .neighbor {
		border: 1.5px solid #8a857c;
		background: rgb(138 133 124 / 0.15);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.schematic .ghost {
		border: 1.5px dashed #c0392b;
		background: rgb(192 57 43 / 0.12);
		color: #c0392b;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.credit {
		margin: 4.5rem 0 0.5rem;
		text-align: center;
		font-family: system-ui, sans-serif;
		font-size: 0.6rem;
		color: #8a857c;
	}
</style>
```

Note: the skyline sits above a 4.5rem reserved band (`.credit` margin) so the absolute-positioned captions below the baseline never clip.

- [ ] **Step 2: Verify it compiles**

Run: `npm run build`
Expected: build completes with no errors (warnings about unused CSS are acceptable only if unrelated to this file — fix any that reference `ConversionSkyline`).

- [ ] **Step 3: Commit**

```bash
git add src/lib/components/ConversionSkyline.svelte
git commit -m "Add to-scale conversion skyline background component"
```

---

### Task 3: Wire the page — `+page.svelte`

**Files:**
- Modify: `src/routes/+page.svelte` (full rewrite; current content is the placeholder demo from earlier)

**Interfaces:**
- Consumes: `Scroller.svelte` (props `top`, `bottom`, bindables `index`, `count`; snippets `background`, `foreground`), `ConversionSkyline.svelte` (prop `index`).

- [ ] **Step 1: Write the page**

```svelte
<script>
	import Scroller from '$lib/components/Scroller.svelte';
	import ConversionSkyline from '$lib/components/ConversionSkyline.svelte';

	let index = $state(0);
	let count = $state(0);
</script>

<main>
	<header class="masthead">
		<h1>The conversion that reached too high</h1>
		<p class="dek">
			New York has spent two decades turning empty offices into apartments — in ever bigger
			buildings. On July 7, its most ambitious conversion yet began to buckle.
		</p>
		<p class="hint">Scroll ↓</p>
	</header>

	<Scroller top={0} bottom={1} bind:index bind:count>
		{#snippet background()}
			<ConversionSkyline {index} />
		{/snippet}

		{#snippet foreground()}
			<div class="step">
				<div class="card">
					<h2>The buckle</h2>
					<p>
						Just before 8 a.m. on Tuesday, a safety manager at 235 East 42nd Street — the former
						Pfizer headquarters, built in 1961 — reported a compromised steel beam on the 21st
						floor. Two support columns were buckling; upper floors sagged. The tower was
						mid-conversion into some 1,600 apartments, the largest office-to-residential
						conversion in New York City history. A five-block “frozen zone” went up around
						Grand Central.
					</p>
				</div>
			</div>

			<div class="step">
				<div class="card">
					<h2>It began downtown, old and narrow</h2>
					<p>
						Office-to-apartment conversion isn’t new. The first wave, in the 1990s and 2000s,
						took pre-war towers in Lower Manhattan — 90 West Street (1907), the Woolworth
						Building (1913), 20 Pine (1928), 20 Exchange Place (1931), 70 Pine (1932). Old,
						narrow buildings whose slim floor plates put every future bedroom near a window.
						Most now list “residential” among their uses.
					</p>
				</div>
			</div>

			<div class="step">
				<div class="card">
					<h2>The new wave: Midtown, and bigger</h2>
					<p>
						After the pandemic emptied offices, the city rewrote the rules — 2024’s City of Yes
						rezoning, a new 467-m tax break, and an “Office Conversion Accelerator” at City
						Hall. Half of conversions announced since then are in Midtown, and the buildings
						keep getting bigger: 5 Times Square, 135 East 57th, and 750 Third Avenue, a
						34-story office slab set to become 680 apartments.
					</p>
				</div>
			</div>

			<div class="step">
				<div class="card">
					<h2>This one reached too high</h2>
					<p>
						Unlike every downtown precedent, the 42nd Street project didn’t just gut and refit —
						it added weight: an 11-story extension on the adjoining 219 East 42nd Street, part
						of the same complex. Under the new load, a union official said, beams bent “like
						cigarettes.” The developer conceded two columns “could not take the load.” The
						columns of a 64-year-old office tower were asked to carry a building it was never
						designed to be.
					</p>
				</div>
			</div>
		{/snippet}
	</Scroller>

	<footer class="sources">
		<p>
			Sources: New York Times live coverage, July 7, 2026; Wall Street Journal, “Office-to-Residential
			Conversions Are Booming,” Dec. 1, 2025; NYC Office Conversion Accelerator; building data and
			scale drawings from SkyscraperPage.com.
		</p>
	</footer>
</main>

<style>
	main {
		font-family: Georgia, 'Times New Roman', serif;
		color: #26241f;
	}

	.masthead {
		max-width: 42rem;
		margin: 0 auto;
		padding: 5rem 1.5rem 4rem;
		text-align: center;
	}

	h1 {
		margin: 0 0 1rem;
		font-size: clamp(2rem, 5vw, 3rem);
		line-height: 1.1;
	}

	.dek {
		margin: 0 auto;
		max-width: 34rem;
		font-size: 1.15rem;
		line-height: 1.5;
		color: #55524b;
	}

	.hint {
		margin-top: 2.5rem;
		font-family: system-ui, sans-serif;
		font-size: 0.8rem;
		color: #8a857c;
	}

	.step {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: flex-start;
		padding: 0 clamp(1rem, 6vw, 5rem);
	}

	.card {
		max-width: 22rem;
		padding: 1.5rem 1.75rem;
		background: rgb(255 253 248 / 0.96);
		border: 1px solid #d8d2c4;
		border-radius: 0.375rem;
		box-shadow: 0 2px 14px rgb(0 0 0 / 0.08);
	}

	.card h2 {
		margin: 0 0 0.6rem;
		font-size: 1.15rem;
	}

	.card p {
		margin: 0;
		font-size: 0.95rem;
		line-height: 1.6;
	}

	.sources {
		max-width: 42rem;
		margin: 0 auto;
		padding: 3rem 1.5rem 4rem;
	}

	.sources p {
		font-family: system-ui, sans-serif;
		font-size: 0.75rem;
		line-height: 1.5;
		color: #8a857c;
	}
</style>
```

- [ ] **Step 2: Verify it compiles**

Run: `npm run build`
Expected: build completes with no errors.

- [ ] **Step 3: Commit**

```bash
git add src/routes/+page.svelte
git commit -m "Build conversion scrolly page with four steps"
```

---

### Task 4: Visual verification + lint

**Files:** none new — verification only.

- [ ] **Step 1: Run the dev server and walk the piece**

Run: `npm run dev` and open the printed URL. Verify against the spec's slide table:
1. Slide 1: hero alone, red outline, caption shows `1961 · 409 ft` and the office→apartments use line.
2. Slide 2: downtown five fade in to scale (70 Pine visibly ~2.3× hero height); hero dims/grayscales.
3. Slide 3: Midtown trio fades in highlighted; downtown five dim.
4. Slide 4: everything dims except hero; schematic (22-floor neighbor outline + dashed red `+11 floors` ghost) beside hero; dashed buckle line at ~21/37 height.
5. Captions never clip at the bottom; credit line lists SkyscraperPage + illustrator names.

- [ ] **Step 2: Resize check**

Narrow the window to ~375px width: skyline shrinks (shared `k`), no horizontal overflow, cards go full-width.

- [ ] **Step 3: Lint and fix**

Run: `npm run lint` — if Prettier flags the new files, run `npm run format`, re-verify `npm run build`, and include formatting in the commit.

- [ ] **Step 4: Final commit (if formatting changed anything)**

```bash
git add -A src/ && git commit -m "Format scrolly components"
```
