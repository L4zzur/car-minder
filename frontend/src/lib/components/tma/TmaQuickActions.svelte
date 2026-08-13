<script lang="ts">
	import Gauge from '@lucide/svelte/icons/gauge';
	import Wrench from '@lucide/svelte/icons/wrench';
	import Bell from '@lucide/svelte/icons/bell';
	import Plus from '@lucide/svelte/icons/plus';

	import type { CarRead, ServiceItemSummary } from '$lib/api';
	import AddCarDialog from '$lib/components/ui/AddCarDialog.svelte';
	import AddServiceDialog from '$lib/components/ui/AddServiceDialog.svelte';
	import RemindersDialog from '$lib/components/ui/RemindersDialog.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Field from '$lib/components/ui/field';
	import * as m from '$lib/paraglide/messages.js';

	let {
		selectedCar,
		serviceItems,
		onCarAdded,
		onServiceAdded,
		onReminderChanged,
		onMileageAdded
	}: {
		selectedCar: CarRead;
		serviceItems: ServiceItemSummary[];
		onCarAdded: () => void;
		onServiceAdded: () => void;
		onReminderChanged: () => void;
		onMileageAdded: (newMileage: number) => Promise<boolean>;
	} = $props();

	let mileageDialogOpen = $state(false);
	let newMileage = $state<number | ''>('');
	let isSavingMileage = $state(false);
	let mileageError = $state('');

	$effect(() => {
		if (mileageDialogOpen && selectedCar) {
			newMileage = selectedCar.current_odometer_km ?? selectedCar.initial_odometer_km;
			mileageError = '';
		}
	});

	async function handleAddMileage() {
		if (typeof newMileage !== 'number' || newMileage <= 0) {
			mileageError = m.mileage_form_err_invalid();
			return;
		}

		const currentOdo = selectedCar.current_odometer_km ?? selectedCar.initial_odometer_km;
		if (newMileage <= currentOdo) {
			mileageError = m.mileage_form_err_must_be_greater();
			return;
		}

		isSavingMileage = true;
		mileageError = '';
		try {
			const success = await onMileageAdded(newMileage);
			if (success) {
				mileageDialogOpen = false;
				newMileage = '';
			} else {
				mileageError = m.car_detail_err_save_mileage_failed();
			}
		} catch (e) {
			console.error('failed to save mileage:', e);
			mileageError = m.tma_mileage_error_save();
		} finally {
			isSavingMileage = false;
		}
	}
</script>

<div class="grid grid-cols-2 gap-3">
	<!-- Quick Mileage Button -->
	<Dialog.Root bind:open={mileageDialogOpen}>
		<Dialog.Trigger class="w-full">
			{#snippet child({ props })}
				<Button {...props} variant="outline" class="w-full h-auto flex-col gap-1.5 p-3 text-left items-start justify-center">
					<div class="flex items-center gap-1.5 text-xs text-muted-foreground">
						<Gauge data-icon="inline-start" />
						<span>{m.tma_quick_mileage()}</span>
					</div>
					<span class="text-sm font-semibold">{m.tma_quick_mileage_action()}</span>
				</Button>
			{/snippet}
		</Dialog.Trigger>
		<Dialog.Content class="max-w-xs sm:max-w-sm">
			<Dialog.Header>
				<Dialog.Title>{m.tma_mileage_dialog_title()}</Dialog.Title>
				<Dialog.Description>
					{m.tma_mileage_current({ km: selectedCar.current_odometer_km ?? selectedCar.initial_odometer_km })}
				</Dialog.Description>
			</Dialog.Header>
			<form
				class="flex flex-col gap-4"
				onsubmit={(e) => {
					e.preventDefault();
					handleAddMileage();
				}}
			>
				<Field.Group>
					<Field.Field>
						<Field.Label for="odometer">{m.tma_mileage_new_label()}</Field.Label>
						<Input
							id="odometer"
							type="number"
							bind:value={newMileage}
							placeholder={(selectedCar.current_odometer_km ?? selectedCar.initial_odometer_km).toString()}
							required
						/>
					</Field.Field>
					{#if mileageError}
						<p class="text-xs text-destructive">{mileageError}</p>
					{/if}
				</Field.Group>
				<Dialog.Footer>
					<Button type="submit" class="w-full" disabled={isSavingMileage}>
						{isSavingMileage ? m.mileage_form_btn_submitting() : m.common_save()}
					</Button>
				</Dialog.Footer>
			</form>
		</Dialog.Content>
	</Dialog.Root>

	<!-- Add Service Item Dialog -->
	<AddServiceDialog car={selectedCar} {onServiceAdded}>
		{#snippet child({ props })}
			<Button {...props} variant="outline" class="w-full h-auto flex-col gap-1.5 p-3 text-left items-start justify-center">
				<div class="flex items-center gap-1.5 text-xs text-muted-foreground">
					<Wrench data-icon="inline-start" />
					<span>{m.tma_quick_service()}</span>
				</div>
				<span class="text-sm font-semibold">{m.tma_quick_service_action()}</span>
			</Button>
		{/snippet}
	</AddServiceDialog>

	<!-- Reminders Dialog -->
	<RemindersDialog car={selectedCar} {serviceItems} {onReminderChanged}>
		{#snippet child({ props })}
			<Button {...props} variant="outline" class="w-full h-auto flex-col gap-1.5 p-3 text-left items-start justify-center">
				<div class="flex items-center gap-1.5 text-xs text-muted-foreground">
					<Bell data-icon="inline-start" />
					<span>{m.reminders_dialog_btn()}</span>
				</div>
				<span class="text-sm font-semibold">{m.tma_quick_reminders_action()}</span>
			</Button>
		{/snippet}
	</RemindersDialog>

	<!-- Add New Car Dialog -->
	<AddCarDialog {onCarAdded}>
		{#snippet child({ props })}
			<Button {...props} variant="outline" class="w-full h-auto flex-col gap-1.5 p-3 text-left items-start justify-center">
				<div class="flex items-center gap-1.5 text-xs text-muted-foreground">
					<Plus data-icon="inline-start" />
					<span>{m.garage_head_title()}</span>
				</div>
				<span class="text-sm font-semibold">{m.tma_quick_car_action()}</span>
			</Button>
		{/snippet}
	</AddCarDialog>
</div>
