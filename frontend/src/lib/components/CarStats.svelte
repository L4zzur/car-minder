<script lang="ts">
	import { Bell, CarFront, Gauge } from 'lucide-svelte';

	import type { CarRead } from '$lib/api';

	let {
		car,
		drivenKm,
		dueCount,
		soonCount
	}: {
		car: CarRead;
		drivenKm: number;
		dueCount: number;
		soonCount: number;
	} = $props();

	const formatOdometer = (value: number) => value.toLocaleString('ru-RU');
</script>

<div class="grid gap-4 sm:grid-cols-3">
	<div class="rounded-lg border bg-card p-4">
		<div class="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
			<Gauge class="size-4" />
			<span>пробег</span>
		</div>
		<div class="text-2xl font-semibold">{formatOdometer(car.current_odometer_km)} км</div>
		<p class="mt-1 text-xs text-muted-foreground">
			+{formatOdometer(drivenKm)} км с добавления
		</p>
	</div>

	<div class="rounded-lg border bg-card p-4">
		<div class="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
			<Bell class="size-4" />
			<span>напоминания</span>
		</div>
		<div class="text-2xl font-semibold">{dueCount + soonCount}</div>
		<p class="mt-1 text-xs text-muted-foreground">
			{soonCount} скоро, {dueCount} просрочено
		</p>
	</div>

	<div class="rounded-lg border bg-card p-4">
		<div class="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
			<CarFront class="size-4" />
			<span>стартовый пробег</span>
		</div>
		<div class="text-2xl font-semibold">{formatOdometer(car.initial_odometer_km)} км</div>
		<p class="mt-1 text-xs text-muted-foreground">на момент добавления</p>
	</div>
</div>
