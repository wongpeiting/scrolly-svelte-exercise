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
