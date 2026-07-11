<script>
	import buildings from '$lib/data/conversions.json';
	import { base } from '$app/paths';
	import { fade } from 'svelte/transition';
	import { flip } from 'svelte/animate';
	import { tick } from 'svelte';

	let { index = 0, offset = 0, masthead } = $props();

	// Slide choreography:
	// 0: headline (hero huge, alone) · 1: annotation (hero huge, swoopy arrow) · 2: buckle (hero to scale)
	// 3: +downtown (active) · 4: +midtown (active) · 5: hero active + schematic
	const step = $derived(Math.max(0, Math.min(index, 5)));
	const landing = $derived(step <= 1);
	const annotate = $derived(step === 1);
	const introduced = $derived(
		step <= 2 ? ['hero'] : step === 3 ? ['hero', 'downtown'] : ['hero', 'downtown', 'midtown']
	);
	const active = $derived(['hero', 'hero', 'hero', 'downtown', 'midtown', 'hero'][step]);
	const visible = $derived(buildings.filter((b) => introduced.includes(b.group)));

	// Shared scale: all drawings ~0.305 px/ft, so raw h values are mutually to scale.
	let containerH = $state(0);
	const TALLEST = Math.max(...buildings.map((b) => b.h)); // 290px (70 Pine)
	const k = $derived(containerH > 0 ? (containerH * 0.58) / TALLEST : 0);

	// The hero never unmounts: huge on the headline screens, shrunk to the shared
	// scale mid-story, then zoomed back up for the final step so we end on it.
	// Shrink (step 2) and regrowth (step 5) are scroll-scrubbed: they interpolate
	// with the section's offset so the size tracks the reader's scroll speed.
	const ease = (t) => t * t * (3 - 2 * t);
	const clamp01 = (t) => Math.max(0, Math.min(1, t));
	const shrinkP = $derived(step < 2 ? 0 : step === 2 ? ease(clamp01(offset / 0.5)) : 1);
	const zoomP = $derived(step === 5 ? ease(clamp01(offset / 0.6)) : 0);
	const displayH = (b) => {
		if (b.group !== 'hero') return b.h * k;
		const landingH = containerH * 0.72;
		const scaleH = b.h * k;
		if (step <= 1) return landingH;
		if (step === 2) return landingH + (scaleH - landingH) * shrinkP;
		if (step === 5) return scaleH + (containerH * 0.66 - scaleH) * zoomP;
		return scaleH;
	};
	// Effective px per raw drawing px, so hero-anchored overlays scale with the zoom.
	const scaleFor = (b) => displayH(b) / b.h;

	// Slide-4 schematic, same raw-px scale as the drawings:
	// 219 E 42nd (adjoining): 22 existing floors ≈ 275 ft ≈ 84px; extension +11 floors ≈ 138 ft ≈ 42px
	const NEIGHBOR_RAW = 84;
	const EXTENSION_RAW = 42;
	// Buckle marker: beam compromised on the 21st of 37 stories (NYT)
	const BUCKLE_FRAC = 21 / 37;

	const credits = [...new Set(buildings.map((b) => b.illustrator))].join(', ');

	// Camera: after each step change, pan the row so the active group's center
	// sits at the viewport center. offsetLeft/offsetWidth read final layout
	// (unaffected by in-flight flip transforms), so the measurement is stable.
	let skylineEl = $state(null);
	let stageW = $state(0);
	let shiftX = $state(0);

	function measure() {
		if (!skylineEl || stageW === 0) return;
		const actives = skylineEl.querySelectorAll('.building:not(.dimmed)');
		if (!actives.length) return;
		let sum = 0;
		for (const el of actives) sum += el.offsetLeft + el.offsetWidth / 2;
		// Final step: bias right so the zoomed hero centers in the space beside the card.
		const targetFrac = step === 5 ? 0.63 : 0.5;
		shiftX = stageW * targetFrac - sum / actives.length;
	}

	$effect(() => {
		void step;
		void stageW;
		void k;
		void shrinkP;
		void zoomP;
		tick().then(measure);
		// Re-measure after entry/exit transitions settle (fades change layout).
		const t = setTimeout(measure, 500);
		return () => clearTimeout(t);
	});
</script>

<div class="stage" bind:clientHeight={containerH} bind:clientWidth={stageW}>
	{#if landing && masthead}
		<div class="masthead-slot" transition:fade={{ duration: 400 }}>
			{@render masthead()}
		</div>
	{/if}
	{#if k > 0}
		<div
			class="skyline"
			class:landing
			bind:this={skylineEl}
			style:transform="translateX({shiftX}px)"
		>
			{#each visible as b (b.id)}
				<figure
					class="building"
					class:dimmed={b.group !== active}
					class:hero={b.group === 'hero'}
					animate:flip={{ duration: 600 }}
					transition:fade={{ duration: 400 }}
				>
					{#if b.group === 'hero' && step === 5}
						<div class="schematic" style:height="{(NEIGHBOR_RAW + EXTENSION_RAW) * scaleFor(b)}px">
							<div class="ghost" style:height="{EXTENSION_RAW * scaleFor(b)}px">+11 floors</div>
							<div class="neighbor" style:height="{NEIGHBOR_RAW * scaleFor(b)}px">
								219 E 42nd<br />(adjoining)
							</div>
						</div>
					{/if}
					<div class="tower">
						<img src="{base}{b.file}" alt="Scale drawing of {b.name}" style:height="{displayH(b)}px" />
						{#if b.group === 'hero' && annotate}
							<div class="annotation" transition:fade={{ duration: 300 }}>
								<p>
									as of this morning, this <strong>former Pfizer HQ</strong> became the
									<strong>‘building that might collapse’</strong>
								</p>
								<svg viewBox="0 0 130 90" aria-hidden="true">
									<path class="swoop" d="M124,8 C 116,58 72,84 18,56" />
									<path class="head" d="M30,50 L16,55 L26,66" />
								</svg>
							</div>
						{/if}
						{#if b.group === 'hero' && step === 5}
							<div class="buckle" style:bottom="{BUCKLE_FRAC * displayH(b)}px">
								<span>21st floor: compromised beam</span>
							</div>
						{/if}
					</div>
					{#if !landing}
						<figcaption transition:fade={{ duration: 300 }}>
							<strong>{b.name}</strong>
							<span>{b.year} · {b.height_ft} ft</span>
							{#if b.group === active}<span class="use">{b.uses}</span>{/if}
						</figcaption>
					{/if}
				</figure>
			{/each}
		</div>
		<p class="credit">Scale drawings: SkyscraperPage.com ({credits})</p>
	{/if}
</div>

<style>
	.stage {
		position: relative;
		height: 100vh;
		display: flex;
		flex-direction: column;
		justify-content: flex-end;
		background: linear-gradient(#f5f2ec, #ece7dd);
		overflow: hidden;
	}

	.masthead-slot {
		position: absolute;
		left: clamp(1rem, 6vw, 5rem);
		top: 50%;
		transform: translateY(-50%);
		z-index: 1;
	}

	.skyline {
		position: relative;
		display: flex;
		align-items: flex-end;
		justify-content: center;
		gap: clamp(0.5rem, 2vw, 1.75rem);
		padding: 0 1rem;
		border-bottom: 2px solid #3d3a35;
		transition: transform 700ms cubic-bezier(0.4, 0, 0.2, 1);
		will-change: transform;
	}

	.building {
		position: relative;
		margin: 0;
		display: flex;
		align-items: flex-end;
		gap: 0.4rem;
		transition:
			opacity 400ms ease,
			filter 400ms ease;
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
		image-rendering: pixelated;
		transition: height 150ms ease-out;
	}

	.hero .tower img {
		outline: 2px solid #c0392b;
		outline-offset: 2px;
	}

	.skyline.landing .hero .tower img {
		outline-color: transparent;
	}

	figcaption {
		position: absolute;
		top: 100%;
		left: 50%;
		transform: translateX(-50%);
		width: max-content;
		max-width: 11rem;
		padding-top: 0.5rem;
		text-align: center;
		font-family: 'Libre Franklin', system-ui, sans-serif;
		font-size: 0.8rem;
		line-height: 1.35;
		color: #3d3a35;
	}

	figcaption strong {
		display: block;
		font-size: 0.85rem;
	}

	figcaption .use {
		display: block;
		width: max-content;
		white-space: nowrap;
		position: relative;
		left: 50%;
		transform: translateX(-50%);
		color: #c0392b;
		font-weight: 600;
	}

	.annotation {
		position: absolute;
		left: calc(100% + 0.1rem);
		top: 18%;
		width: 15rem;
		text-align: left;
		font-family: 'Caveat', cursive;
		font-size: 1.5rem;
		font-weight: 600;
		line-height: 1.15;
		color: #b03427;
		transform: rotate(2.5deg);
	}

	.annotation p {
		margin: 0 0 0.25rem;
	}

	.annotation svg {
		width: 7.5rem;
		height: auto;
		margin-left: 0;
		overflow: visible;
	}

	.annotation .swoop {
		fill: none;
		stroke: #b03427;
		stroke-width: 3;
		stroke-linecap: round;
		stroke-dasharray: 220;
		stroke-dashoffset: 220;
		animation: draw 800ms ease-out 250ms forwards;
	}

	.annotation .head {
		fill: none;
		stroke: #b03427;
		stroke-width: 3;
		stroke-linecap: round;
		stroke-linejoin: round;
		opacity: 0;
		animation: pop 200ms ease-out 950ms forwards;
	}

	@keyframes draw {
		to {
			stroke-dashoffset: 0;
		}
	}

	@keyframes pop {
		to {
			opacity: 1;
		}
	}

	.buckle {
		position: absolute;
		left: -0.5rem;
		right: -0.5rem;
		border-top: 2px dashed #c0392b;
		transition: bottom 150ms ease-out;
	}

	.buckle span {
		position: absolute;
		bottom: 0.15rem;
		left: 100%;
		width: max-content;
		margin-left: 0.4rem;
		font-family: 'Libre Franklin', system-ui, sans-serif;
		font-size: 0.8rem;
		font-weight: 600;
		color: #c0392b;
	}

	.schematic {
		display: flex;
		flex-direction: column;
		justify-content: flex-end;
		width: 3.6rem;
		font-family: 'Libre Franklin', system-ui, sans-serif;
		font-size: 0.65rem;
		text-align: center;
		color: #3d3a35;
	}

	/* Match .tower img so the schematic tracks the hero's height easing. */
	.schematic,
	.schematic .neighbor,
	.schematic .ghost {
		transition: height 150ms ease-out;
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
		font-family: 'Libre Franklin', system-ui, sans-serif;
		font-size: 0.7rem;
		color: #8a857c;
	}
</style>
