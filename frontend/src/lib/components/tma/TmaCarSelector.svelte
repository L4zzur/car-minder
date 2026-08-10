<script lang="ts">
	import type { CarRead } from '$lib/api';
	import * as m from '$lib/paraglide/messages.js';
	import * as Select from '$lib/components/ui/select';

	let {
		cars,
		selectedCarId = $bindable()
	}: {
		cars: CarRead[];
		selectedCarId: string | null;
	} = $props();

	const selectedCar = $derived(cars.find((c) => c.id === selectedCarId) ?? cars[0] ?? null);
</script>

{#if cars.length > 1}
	<div class="flex items-center justify-between gap-3 rounded-lg border bg-card p-3">
		<span class="text-xs font-medium text-muted-foreground uppercase">{m.tma_car_selector_label()}</span>
		<div class="w-56">
			<Select.Root type="single" value={selectedCarId ?? cars[0].id} onValueChange={(val) => (selectedCarId = val)}>
				<Select.Trigger class="w-full h-8 text-xs font-medium">
					{selectedCar ? `${selectedCar.brand.toLowerCase()} ${selectedCar.model.toLowerCase()}` : m.tma_car_selector_placeholder()}
				</Select.Trigger>
				<Select.Content>
					<Select.Group>
						{#each cars as car (car.id)}
							<Select.Item value={car.id} label={`${car.brand.toLowerCase()} ${car.model.toLowerCase()}`} class="text-xs">
								{car.brand.toLowerCase()} {car.model.toLowerCase()} ({car.year})
							</Select.Item>
						{/each}
					</Select.Group>
				</Select.Content>
			</Select.Root>
		</div>
	</div>
{/if}
