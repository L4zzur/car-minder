<script lang="ts">
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import * as Empty from '$lib/components/ui/empty';
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
		status?: 'due' | 'soon' | 'ok';
	};

	let {
		car,
		href,
		serviceLines = [],
		actionLabel
	}: {
		car: CarCardData;
		href?: string;
		serviceLines?: ServiceLine[];
		actionLabel?: string;
	} = $props();

	const formatOdometer = (value: number) => value.toLocaleString(getLocale());
	const currentOdometer = $derived(car.current_odometer_km ?? car.initial_odometer_km);
	const hasMileageUpdates = $derived(currentOdometer !== car.initial_odometer_km);
	const finalActionLabel = $derived(actionLabel ?? m.car_card_detailed());
</script>

<Card.Root class="flex h-full flex-col justify-between transition-shadow hover:shadow-md">
	<div>
		<Card.Header>
			<div class="flex items-start justify-between">
				<div>
					<Card.Title class="text-xl capitalize">{car.brand.toLowerCase()} {car.model.toLowerCase()}</Card.Title>
					<Card.Description>{car.year} {m.car_card_year_of_production()}</Card.Description>
				</div>
				<div
					class="flex size-10 items-center justify-center rounded-lg border bg-background text-muted-foreground shadow-2xs"
				>
					<CarFront class="size-5" />
				</div>
			</div>
		</Card.Header>

		<Card.Content class="flex flex-1 flex-col justify-between gap-5">
			<div class="rounded-lg border bg-muted/30 p-3.5">
				<div class="mb-1.5 flex items-center gap-2 text-xs font-medium text-muted-foreground">
					<Gauge class="size-3.5" />
					<span>{m.car_card_current_odometer()}</span>
				</div>
				<div class="text-2xl font-semibold tracking-tight">{formatOdometer(currentOdometer)} {m.car_card_current_odometer_km()}</div>
				<p class="mt-1 text-xs text-muted-foreground">
					{#if hasMileageUpdates}
						{m.car_card_start_odometer({ km: formatOdometer(car.initial_odometer_km) })}
					{:else}
						{m.car_card_initial_odometer()}
					{/if}
				</p>
			</div>

			{#if serviceLines.length}
				<div class="flex flex-col gap-2">
					{#each serviceLines as line}
						<div class="flex items-center justify-between gap-3 rounded-md border border-border/50 bg-card px-3 py-2 text-sm transition-colors">
							<div class="flex items-center gap-2.5 min-w-0">
								<Wrench class="size-3.5 shrink-0 text-muted-foreground" />
								<span class="truncate font-medium text-foreground">{line.label}</span>
							</div>
							<Badge
								variant={line.status === 'due' ? 'destructive' : line.status === 'soon' ? 'secondary' : 'outline'}
								class="shrink-0 font-normal"
							>
								{line.meta}
							</Badge>
						</div>
					{/each}
				</div>
			{:else}
				<Empty.Root class="min-h-[7.5rem] border border-dashed bg-muted/10 p-4">
					<Empty.Description class="text-xs text-muted-foreground">
						{m.car_card_no_service_items()}
					</Empty.Description>
				</Empty.Root>
			{/if}
		</Card.Content>
	</div>

	{#if href}
		<Card.Footer class="pt-4">
			<Button variant="outline" class="w-full" {href}>{finalActionLabel}</Button>
		</Card.Footer>
	{/if}
</Card.Root>
