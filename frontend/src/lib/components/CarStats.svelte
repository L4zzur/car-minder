<script lang="ts">
	import { Bell, CarFront, Gauge, Wrench } from 'lucide-svelte';

	import type { CarRead } from '$lib/api';
	import * as m from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime';

	let {
		car,
		drivenKm,
		dueCount,
		soonCount,
		serviceItemCount
	}: {
		car: CarRead;
		drivenKm: number;
		dueCount: number;
		soonCount: number;
		serviceItemCount: number;
	} = $props();

	const formatOdometer = (value: number) => value.toLocaleString(getLocale());
</script>

<div class="grid grid-cols-2 gap-4 md:grid-cols-2 lg:grid-cols-4">
	<div class="rounded-lg border bg-card p-4">
		<div class="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
			<Gauge class="size-4" />
			<span>{m.car_stats_mileage()}</span>
		</div>
		<div class="text-2xl font-semibold">{formatOdometer(car.current_odometer_km)} {m.car_card_current_odometer_km()}</div>
		<p class="mt-1 text-xs text-muted-foreground">
			{m.car_stats_driven_since_added({ km: formatOdometer(drivenKm) })}
		</p>
	</div>

	<div class="rounded-lg border bg-card p-4">
		<div class="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
			<CarFront class="size-4" />
			<span>{m.car_stats_start_odometer()}</span>
		</div>
		<div class="text-2xl font-semibold">{formatOdometer(car.initial_odometer_km)} {m.car_card_current_odometer_km()}</div>
		<p class="mt-1 text-xs text-muted-foreground">{m.car_stats_at_addition()}</p>
	</div>

	<div class="rounded-lg border bg-card p-4">
		<div class="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
			<Wrench class="size-4" />
			<span>{m.car_stats_service_items()}</span>
		</div>
		<div class="text-2xl font-semibold">{serviceItemCount}</div>
		<p class="mt-1 text-xs text-muted-foreground">{m.car_stats_items_tracked()}</p>
	</div>

	<div class="rounded-lg border bg-card p-4">
		<div class="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
			<Bell class="size-4" />
			<span>{m.car_stats_reminders()}</span>
		</div>
		<div class="text-2xl font-semibold">{dueCount + soonCount}</div>
		<p class="mt-1 text-xs text-muted-foreground">
			{m.car_stats_reminders_summary({ soon: soonCount, due: dueCount })}
		</p>
	</div>
</div>
