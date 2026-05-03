<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
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
		actionLabel = 'подробнее'
	}: {
		car: CarCardData;
		href?: string;
		serviceLines?: ServiceLine[];
		actionLabel?: string;
	} = $props();

	const formatOdometer = (value: number) => value.toLocaleString('ru-RU');
	const currentOdometer = $derived(car.current_odometer_km ?? car.initial_odometer_km);
	const hasMileageUpdates = $derived(currentOdometer !== car.initial_odometer_km);
</script>

<Card.Root>
	<Card.Header>
		<div class="flex items-start justify-between gap-4">
			<div>
				<Card.Title>{car.brand.toLowerCase()} {car.model.toLowerCase()}</Card.Title>
				<Card.Description>{car.year} год выпуска</Card.Description>
			</div>
			<div class="flex size-9 items-center justify-center rounded-lg border bg-background text-muted-foreground">
				<CarFront class="size-4" />
			</div>
		</div>
	</Card.Header>

	<Card.Content class="space-y-4">
		<div class="rounded-lg border bg-background p-3">
			<div class="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
				<Gauge class="size-3.5" />
				<span>текущий пробег</span>
			</div>
			<div class="text-2xl font-semibold tracking-tight">{formatOdometer(currentOdometer)} км</div>
			<p class="mt-1 text-xs text-muted-foreground">
				{#if hasMileageUpdates}
					старт: {formatOdometer(car.initial_odometer_km)} км
				{:else}
					пока равен начальному
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
			<Button variant="ghost" class="w-full" {href}>{actionLabel}</Button>
		</Card.Footer>
	{/if}
</Card.Root>
