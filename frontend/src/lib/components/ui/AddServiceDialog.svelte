<script lang="ts">
	import Wrench from '@lucide/svelte/icons/wrench';

	import { ServiceItems, type CarRead } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';

	let { car, onServiceAdded, child } = $props<{
		car: CarRead;
		onServiceAdded: () => void;
		child?: (opts: { props: Record<string, unknown> }) => import('svelte').Snippet;
	}>();

	let open = $state(false);
	let name = $state('');
	let lastServiceAt = $state(new Date().toISOString().slice(0, 10));
	let lastOdometerKm = $state<number>(getInitialOdometer());
	let isLoading = $state(false);
	let error = $state('');

	function getInitialOdometer() {
		return car.current_odometer_km;
	}

	async function handleSubmit() {
		error = '';

		if (!name.trim()) {
			error = 'название обязательно';
			return;
		}

		if (!Number.isFinite(lastOdometerKm) || lastOdometerKm < 0) {
			error = 'пробег должен быть положительным числом';
			return;
		}

		isLoading = true;

		try {
			const response = await ServiceItems.addServiceItemApiServiceItemsPost({
				body: {
					car_id: car.id,
					name: name.trim(),
					last_service_at: new Date(lastServiceAt).toISOString(),
					last_service_odometer_km: lastOdometerKm
				}
			});

			if (response.error) {
				error = 'не удалось добавить расходник';
				return;
			}

			name = '';
			lastServiceAt = new Date().toISOString().slice(0, 10);
			lastOdometerKm = car.current_odometer_km;
			open = false;
			onServiceAdded();
		} catch (e) {
			console.error('failed to add service item:', e);
			error = 'не удалось добавить расходник';
		} finally {
			isLoading = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger>
		{#if child}
			{@render child({ props: {} })}
		{:else}
			<Button variant="outline" size="sm">
				<Wrench class="size-3.5" />
				расходник
			</Button>
		{/if}
	</Dialog.Trigger>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>новый расходник</Dialog.Title>
			<Dialog.Description>добавь элемент обслуживания для этой машины</Dialog.Description>
		</Dialog.Header>
		<form
			class="space-y-4"
			onsubmit={(event) => {
				event.preventDefault();
				handleSubmit();
			}}
		>
			<div class="space-y-2">
				<Label for="service-name">название</Label>
				<Input id="service-name" bind:value={name} placeholder="масло двигателя" required />
			</div>
			<div class="grid grid-cols-2 gap-4">
				<div class="space-y-2">
					<Label for="service-date">дата замены</Label>
					<Input id="service-date" type="date" bind:value={lastServiceAt} required />
				</div>
				<div class="space-y-2">
					<Label for="service-odometer">пробег, км</Label>
					<Input id="service-odometer" type="number" min="0" bind:value={lastOdometerKm} required />
				</div>
			</div>
			{#if error}
				<p class="text-xs text-destructive">{error}</p>
			{/if}
			<Dialog.Footer>
				<Button type="submit" class="w-full" disabled={isLoading}>
					{isLoading ? 'добавляем...' : 'добавить расходник'}
				</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>
