<script lang="ts">
	import Wrench from '@lucide/svelte/icons/wrench';

	import { ServiceItems, type CarRead } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Field from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import * as m from '$lib/paraglide/messages.js';

	let {
		car,
		onServiceAdded,
		child,
		class: className
	} = $props<{
		car: CarRead;
		onServiceAdded: () => void;
		child?: (opts: { props: Record<string, unknown> }) => import('svelte').Snippet;
		class?: string;
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
			error = m.add_service_err_name_required();
			return;
		}

		if (!Number.isFinite(lastOdometerKm) || lastOdometerKm < 0) {
			error = m.add_service_err_odometer_positive();
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
				error = m.add_service_err_failed();
				return;
			}

			name = '';
			lastServiceAt = new Date().toISOString().slice(0, 10);
			lastOdometerKm = car.current_odometer_km;
			open = false;
			onServiceAdded();
		} catch (e) {
			console.error('failed to add service item:', e);
			error = m.add_service_err_failed();
		} finally {
			isLoading = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger class={className}>
		{#if child}
			{@render child({ props: {} })}
		{:else}
			<Button variant="outline" class="w-full">
				<Wrench data-icon="inline-start" />
				{m.add_service_btn()}
			</Button>
		{/if}
	</Dialog.Trigger>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>{m.add_service_title()}</Dialog.Title>
			<Dialog.Description>{m.add_service_desc()}</Dialog.Description>
		</Dialog.Header>
		<form
			class="flex flex-col gap-4"
			onsubmit={(event) => {
				event.preventDefault();
				handleSubmit();
			}}
		>
			<Field.Group class="gap-4">
				<Field.Field>
					<Field.Label for="service-name">{m.add_service_name_label()}</Field.Label>
					<Input id="service-name" bind:value={name} placeholder={m.add_service_name_placeholder()} required />
				</Field.Field>
				<div class="grid grid-cols-2 gap-4">
					<Field.Field>
						<Field.Label for="service-date">{m.add_service_date_label()}</Field.Label>
						<Input id="service-date" type="date" bind:value={lastServiceAt} required />
					</Field.Field>
					<Field.Field>
						<Field.Label for="service-odometer">{m.add_service_odometer_label()}</Field.Label>
						<Input id="service-odometer" type="number" min="0" bind:value={lastOdometerKm} required />
					</Field.Field>
				</div>
				{#if error}
					<p class="text-xs text-destructive">{error}</p>
				{/if}
				<Dialog.Footer>
					<Button type="submit" class="w-full" disabled={isLoading}>
						{isLoading ? m.add_service_btn_submitting() : m.add_service_btn_submit()}
					</Button>
				</Dialog.Footer>
			</Field.Group>
		</form>
	</Dialog.Content>
</Dialog.Root>
