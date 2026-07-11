<script>
	import Scroller from '$lib/components/Scroller.svelte';
	import ConversionSkyline from '$lib/components/ConversionSkyline.svelte';

	let index = $state(0);
	let count = $state(0);
	let offset = $state(0);
</script>

<main>
	<Scroller top={0} bottom={1} bind:index bind:count bind:offset>
		{#snippet background()}
			<ConversionSkyline {index} {offset}>
				{#snippet masthead()}
					<header class="masthead">
						<h1>The tower that couldn’t take the weight</h1>
						<p class="dek">
							For two decades, New York has been turning its empty offices into apartments, and
							each wave of conversions has been more ambitious than the last. On July 7, the
							boldest of them began to buckle.
						</p>
						<p class="hint">Scroll ↓</p>
					</header>
				{/snippet}
			</ConversionSkyline>
		{/snippet}

		{#snippet foreground()}
			<!-- headline beat: masthead lives in the background so it stays put -->
			<div class="step" aria-hidden="true"></div>

			<!-- annotation beat: background draws the swoopy arrow; this step is a spacer -->
			<div class="step" aria-hidden="true"></div>

			<div class="step">
				<div class="card">
					<h2>The first call, just before 8 a.m. Tuesday, was about falling bricks.</h2>
					<p>
						No bricks had fallen, the buildings commissioner said later. The truth was worse.
						Inside 235 East 42nd Street, two columns were buckling, and the floors above the 21st
						story had begun to sag. Workers fled. By midmorning, the city had emptied nine
						neighboring buildings and a school of 400 children.
					</p>
				</div>
			</div>

			<div class="step">
				<div class="card">
					<h2>New York had done this before — and it had worked.</h2>
					<p>
						The first wave of conversions, in the 1990s and 2000s, took the old towers of Lower
						Manhattan: 90 West Street, the Woolworth Building, 20 Pine, 20 Exchange Place, 70
						Pine. All were built between 1907 and 1932, and all were slender by modern standards —
						so slender that every future bedroom sat near a window. The old towers made natural
						apartments.
					</p>
				</div>
			</div>

			<div class="step">
				<div class="card">
					<h2>Then the pandemic emptied Midtown, and the city rewrote its rules.</h2>
					<p>
						Looser zoning, a new tax break, an office at City Hall to hurry projects along — all
						of it designed to refill a hollowed-out office district with residents. It worked.
						Half the conversions announced since have been in Midtown, according to a Wall Street
						Journal analysis of Cushman & Wakefield data. And the projects kept getting bigger.
					</p>
				</div>
			</div>

			<div class="step">
				<div class="card">
					<h2>The Pfizer Building went further than conversion.</h2>
					<p>
						The plan for the drugmaker’s former headquarters called for about 1,600 apartments —
						and an 11-story extension stacked atop 219 East 42nd Street, the adjoining building in
						the complex. On Tuesday, the added weight proved too much. Beams bent “like
						cigarettes,” a union official told The New York Times. Two columns, the developer
						conceded, simply “could not take the load.”
					</p>
				</div>
			</div>
		{/snippet}
	</Scroller>

	<footer class="sources">
		<p>
			Sources: New York Times live coverage, July 7, 2026; Wall Street Journal,
			"Office-to-Residential Conversions Are Booming," Dec. 1, 2025; NYC Office Conversion
			Accelerator; building data and scale drawings from SkyscraperPage.com.
		</p>
	</footer>
</main>

<style>
	main {
		font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif;
		color: #26241f;
	}

	.step {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: flex-start;
		padding: 0 clamp(1rem, 6vw, 5rem);
	}

	.masthead {
		max-width: 24rem;
		text-align: left;
	}

	h1 {
		margin: 0 0 1rem;
		font-family: 'Fraunces', Georgia, serif;
		font-size: clamp(2.2rem, 4.5vw, 3.2rem);
		font-weight: 800;
		line-height: 1.05;
		letter-spacing: -0.015em;
	}

	.dek {
		margin: 0;
		max-width: 22rem;
		font-size: 1.1rem;
		line-height: 1.55;
		color: #55524b;
	}

	.hint {
		margin: 2rem 0 0;
		font-family: 'Libre Franklin', system-ui, sans-serif;
		font-size: 0.8rem;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #8a857c;
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
		font-family: 'Libre Franklin', system-ui, sans-serif;
		font-size: 1.05rem;
		font-weight: 700;
		letter-spacing: 0.01em;
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
		font-family: 'Libre Franklin', system-ui, sans-serif;
		font-size: 0.75rem;
		line-height: 1.5;
		color: #8a857c;
	}
</style>
