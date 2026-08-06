<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import * as m from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime';
	import CarFront from '@lucide/svelte/icons/car-front';
	import Gauge from '@lucide/svelte/icons/gauge';
	import Wrench from '@lucide/svelte/icons/wrench';

	type CarCardData = {
		id?: string;
		brand: string;
		model: string;
		year: number;
		initial_odometer_km: number;
		current_odometer_km?: number;
	};

	type ServiceLine = {
		label: string;
		meta: string;
	};

	let {
		car,
		href,
		serviceLines = [],
		actionLabel = m.car_card_detailed()
	}: {
		car: CarCardData;
		href?: string;
		serviceLines?: ServiceLine[];
		actionLabel?: string;
	} = $props();

	const formatOdometer = (value: number) => value.toLocaleString(getLocale());
	const currentOdometer = $derived(car.current_odometer_km ?? car.initial_odometer_km);
	const hasMileageUpdates = $derived(currentOdometer !== car.initial_odometer_km);
</script>

<Card.Root>
	<Card.Header>
		<div class="flex items-start justify-between">
			<div>
				<Card.Title class="text-xl">{car.brand.toLowerCase()} {car.model.toLowerCase()}</Card.Title>
				<Card.Description>{car.year} {m.car_card_year_of_production()}</Card.Description>
			</div>
			<div
				class="flex size-10 items-center justify-center rounded-lg border bg-background text-muted-foreground"
			>
				<CarFront class="size-5" />
			</div>
		</div>
	</Card.Header>

	<Card.Content class="space-y-5">
		<div class="rounded-lg border bg-background p-3">
			<div class="text-xm mb-2 flex items-center gap-2 text-muted-foreground">
				<Gauge class="size-3.5" />
				<span>{m.car_card_current_odometer()}</span>
			</div>
			<div class="text-2xl font-semibold tracking-tight">{formatOdometer(currentOdometer)} {m.car_card_current_odometer_km()}</div>
			<p class="text-xm mt-1 text-muted-foreground">
				{#if hasMileageUpdates}
					{m.car_card_start_odometer({ km: formatOdometer(car.initial_odometer_km) })}
				{:else}
					{m.car_card_initial_odometer()}
				{/if}
			</p>
		</div>

		{#if serviceLines.length}
			<div class="space-y-2">
				{#each serviceLines as line}
					<div class="flex items-center justify-between gap-3 rounded-lg bg-muted/50 px-3 py-2">
						<div class="flex items-center gap-2">
							<Wrench class="size-3.5 text-muted-foreground" />
							<span class="text-sm">{line.label}</span>
						</div>
						<span class="text-xs text-muted-foreground">{line.meta}</span>
					</div>
				{/each}
			</div>
		{/if}
	</Card.Content>

	{#if href}
		<Card.Footer>
			<Button variant="outline" class="w-full" {href}>{actionLabel}</Button>
		</Card.Footer>
	{/if}
</Card.Root>
