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
							New York has spent two decades turning empty offices into apartments, in ever bigger
							buildings. On July 7, its most ambitious conversion yet began to buckle.
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
						No bricks had actually fallen, the buildings commissioner later said. But inside 235
						East 42nd Street, two columns were buckling and the floors above the 21st story had
						begun to sag. Workers fled, and the city emptied nine neighboring buildings and a school
						of 400 children.
					</p>
				</div>
			</div>

			<div class="step">
				<div class="card">
					<h2>Conversions started downtown.</h2>
					<p>
						The first wave in the 1990s and 2000s took the old towers of Lower Manhattan: 90 West
						Street, the Woolworth Building, 20 Pine, 20 Exchange Place, 70 Pine. All built between
						1907 and 1932, and narrow enough that every future bedroom sat near a window.
					</p>
				</div>
			</div>

			<div class="step">
				<div class="card">
					<h2>The new wave moved to Midtown.</h2>
					<p>
						Then the pandemic emptied Midtown, and the city rewrote its rules to fill it: looser
						zoning, a tax break, an office at City Hall to hurry conversions along. Half the
						projects announced since are in Midtown, according to a Wall Street Journal analysis of
						Cushman & Wakefield data, and they keep getting bigger.
					</p>
				</div>
			</div>

			<div class="step">
				<div class="card">
					<h2>Then this one buckled.</h2>
					<p>
						The 42nd Street project went further than the earlier conversions. The plan added an
						11-story extension on the adjoining 219 East 42nd, part of the same complex, and on
						Tuesday the added weight proved too much. A union official had told The New York Times
						that beams bent "like cigarettes", and the developer admitted two columns "could not
						take the load".
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
