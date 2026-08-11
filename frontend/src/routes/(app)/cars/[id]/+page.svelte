<script lang="ts">
	import { ArrowLeft, Bell, CarFront, Plus } from 'lucide-svelte';
	import { onMount } from 'svelte';

	import { goto } from '$app/navigation';
	import { page } from '$app/state';

	import {
		Cars,
		MileageLogs,
		Reminders,
		ServiceItems,
		type CarRead,
		type MileageLogRead,
		type ReminderRead,
		type ServiceItemSummary
	} from '$lib/api';
	import CarStats from '$lib/components/CarStats.svelte';
	import MileageForm from '$lib/components/MileageForm.svelte';
	import MileageHistory from '$lib/components/MileageHistory.svelte';
	import ServiceItemCard from '$lib/components/ServiceItemCard.svelte';
	import AddServiceDialog from '$lib/components/ui/AddServiceDialog.svelte';
	import EditCarDialog from '$lib/components/ui/EditCarDialog.svelte';
	import RemindersDialog from '$lib/components/ui/RemindersDialog.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Empty from '$lib/components/ui/empty';
	import * as m from '$lib/paraglide/messages.js';
	import { getReminderMetrics, getReminderStatus } from '$lib/reminderStatus.js';

	type MileageLogView = {
		id: string;
		odometerKm: number;
		createdAt: string;
	};

	let { data } = $props<{ data: { car?: CarRead } }>();

	let car = $state<CarRead | null>(null);
	let mileageValue = $state<number | string>('');

	$effect(() => {
		car = data?.car ?? null;
		mileageValue = data?.car?.current_odometer_km ?? '';
	});
	let serviceItems = $state<ServiceItemSummary[]>([]);
	let reminders = $state<ReminderRead[]>([]);
	let mileageLogs = $state<MileageLogView[]>([]);
	let isLoading = $state(true);
	let isSavingMileage = $state(false);
	let deletingMileageLogId = $state<string | null>(null);
	let deletingServiceItemId = $state<string | null>(null);
	let savingServiceItemId = $state<string | null>(null);
	let mileageError = $state('');
	let serviceItemError = $state('');
	let error = $state('');

	const drivenKm = $derived(car ? car.current_odometer_km - car.initial_odometer_km : 0);
	const serviceItemCount = $derived(serviceItems.length);
	const reminderCount = $derived(reminders.filter((r) => r.is_active).length);
	const reminderDueCount = $derived(
		reminders.filter((r) => {
			if (!r.is_active || !car) return false;
			const item = serviceItems.find((s) => s.id === r.service_item_id) ?? null;
			return getReminderStatus(r, getReminderMetrics(r, item, car.current_odometer_km)) === 'due';
		}).length
	);
	const reminderSoonCount = $derived(
		reminders.filter((r) => {
			if (!r.is_active || !car) return false;
			const item = serviceItems.find((s) => s.id === r.service_item_id) ?? null;
			return getReminderStatus(r, getReminderMetrics(r, item, car.current_odometer_km)) === 'soon';
		}).length
	);

	function sortMileageLogs(logs: MileageLogRead[]) {
		return [...logs].sort(
			(a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
		);
	}

	async function loadCarPage({ showLoading = true } = {}) {
		const carId = page.params.id;
		if (!carId) return;
		if (showLoading) {
			isLoading = true;
		}
		error = '';

		try {
			const carResponse = await Cars.getCarApiCarsCarIdGet({ path: { car_id: carId } });

			if (carResponse.error || !carResponse.data) {
				error = m.car_detail_not_found();
				car = null;
				return;
			}

			const loadedCar = carResponse.data;
			car = loadedCar;
			mileageValue = loadedCar.current_odometer_km;

			const [mileageResponse, serviceResponse, remindersResponse] = await Promise.all([
				MileageLogs.listByCarApiMileageLogsGet({ query: { car_id: carId } }),
				ServiceItems.listByCarApiServiceItemsGet({ query: { car_id: carId } }),
				Reminders.listRemindersApiRemindersGet({ query: { car_id: carId } })
			]);

			mileageLogs = sortMileageLogs(mileageResponse.data ?? []).map((log) => ({
				id: log.id,
				odometerKm: log.odometer_km,
				createdAt: log.created_at
			}));

			serviceItems = serviceResponse.data ?? [];
			reminders = remindersResponse.data ?? [];
		} catch (e) {
			console.error('failed to load car page:', e);
			error = m.car_detail_not_found();
			car = null;
		} finally {
			isLoading = false;
		}
	}

	async function handleMileageSubmit() {
		if (!car) return;

		const odometer = Number(mileageValue);
		mileageError = '';

		if (!Number.isFinite(odometer)) {
			mileageError = m.mileage_form_err_invalid();
			return;
		}

		if (odometer <= car.current_odometer_km) {
			mileageError = m.mileage_form_err_must_be_greater();
			return;
		}

		isSavingMileage = true;

		try {
			const response = await MileageLogs.addMileageLogApiMileageLogsPost({
				body: {
					car_id: car.id,
					odometer_km: odometer
				}
			});

			if (response.error) {
				mileageError = m.car_detail_err_save_mileage_failed();
				return;
			}

			await loadCarPage({ showLoading: false });
		} catch (e) {
			console.error('failed to save mileage:', e);
			mileageError = m.car_detail_err_save_mileage_failed();
		} finally {
			isSavingMileage = false;
		}
	}

	async function handleDeleteMileageLog(logId: string) {
		deletingMileageLogId = logId;
		mileageError = '';

		try {
			const response = await MileageLogs.deleteMileageLogApiMileageLogsMileageLogIdDelete({
				path: { mileage_log_id: logId }
			});

			if (response.error) {
				mileageError = m.car_detail_err_delete_mileage_failed();
				return;
			}

			await loadCarPage({ showLoading: false });
		} catch (e) {
			console.error('failed to delete mileage log:', e);
			mileageError = m.car_detail_err_delete_mileage_failed();
		} finally {
			deletingMileageLogId = null;
		}
	}

	async function handleDeleteServiceItem(serviceItemId: string) {
		deletingServiceItemId = serviceItemId;
		serviceItemError = '';

		try {
			const response = await ServiceItems.deleteServiceItemApiServiceItemsServiceItemIdDelete({
				path: { service_item_id: serviceItemId }
			});

			if (response.error) {
				serviceItemError = m.car_detail_err_delete_service_failed();
				return;
			}

			await loadCarPage({ showLoading: false });
		} catch (e) {
			console.error('failed to delete service item:', e);
			serviceItemError = m.car_detail_err_delete_service_failed();
		} finally {
			deletingServiceItemId = null;
		}
	}

	async function handleMarkServiced(serviceItemId: string) {
		if (!car) return;

		savingServiceItemId = serviceItemId;

		try {
			const response = await ServiceItems.markServicedApiServiceItemsServiceItemIdMarkServicedPost({
				path: { service_item_id: serviceItemId },
				body: {
					serviced_at: new Date().toISOString(),
					odometer_km: car.current_odometer_km
				}
			});

			if (!response.error) {
				await loadCarPage({ showLoading: false });
			}
		} catch (e) {
			console.error('failed to mark service item serviced:', e);
		} finally {
			savingServiceItemId = null;
		}
	}

	onMount(() => {
		loadCarPage();
	});
</script>

<svelte:head>
	<title>{car ? `${car.brand} ${car.model}` : m.add_car_dialog_title()} // car minder</title>
</svelte:head>

<div class="container mx-auto flex flex-col gap-6 p-4 sm:p-6">
	<header class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<a
			href="/garage"
			class="flex items-center gap-2 self-start text-sm text-muted-foreground transition-colors hover:text-foreground"
		>
			<ArrowLeft class="size-4" />
			<span>{m.car_detail_back()}</span>
		</a>

		<div class="flex w-full items-center gap-2 sm:w-auto">
			{#if car}
				<AddServiceDialog
					{car}
					onServiceAdded={() => loadCarPage({ showLoading: false })}
					class="flex-1 sm:flex-initial"
				/>
				<RemindersDialog
					{car}
					{serviceItems}
					onReminderChanged={() => loadCarPage({ showLoading: false })}
					class="flex-1 sm:flex-initial"
				/>
			{/if}
		</div>
	</header>

	{#if isLoading}
		<div class="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
			{m.car_detail_loading()}
		</div>
	{:else if car}
		<div class="flex flex-col gap-4">
			<div class="flex items-center gap-3">
				<div class="flex size-10 items-center justify-center rounded-lg border bg-card">
					<CarFront class="size-5" />
				</div>
				<div>
					<div class="flex items-center gap-2">
						<h1 class="text-2xl font-semibold tracking-tight sm:text-3xl">
							{car.brand.toLowerCase()}
							{car.model.toLowerCase()}
						</h1>
						<span class="rounded-md border px-2 py-1 text-xs text-muted-foreground">{car.year}</span>
						<EditCarDialog
							{car}
							onCarUpdated={() => loadCarPage({ showLoading: false })}
							onCarDeleted={() => goto('/garage')}
						/>
					</div>
					<p class="text-sm text-muted-foreground">{m.car_detail_subtitle()}</p>
				</div>
			</div>
		</div>

		<CarStats {car} {drivenKm} {serviceItemCount} {reminderCount} {reminderDueCount} {reminderSoonCount} />

		<div class="grid max-w-4xl grid-cols-1 gap-4 md:grid-cols-2">
			<MileageForm
				{car}
				bind:mileageValue
				isSaving={isSavingMileage}
				error={mileageError}
				onSubmit={handleMileageSubmit}
			/>

			<MileageHistory
				logs={mileageLogs}
				deletingId={deletingMileageLogId}
				onDelete={handleDeleteMileageLog}
			/>
		</div>

		<div class="flex flex-col gap-4">
			<div class="flex items-center justify-between">
				<div>
					<h2 class="text-lg font-medium">{m.car_detail_service_items_heading()}</h2>
					<p class="text-sm text-muted-foreground">{m.car_detail_service_items_sub()}</p>
				</div>
				{#if car}
					<AddServiceDialog {car} onServiceAdded={loadCarPage}>
						{#snippet child({ props })}
							<Button {...props} variant="outline">
								<Plus data-icon="inline-start" />
								{m.car_detail_add_btn()}
							</Button>
						{/snippet}
					</AddServiceDialog>
				{/if}
			</div>

			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#if serviceItems.length}
					{#each serviceItems as item}
						<ServiceItemCard
							{item}
							{car}
							{serviceItems}
							isSaving={savingServiceItemId === item.id}
							isDeleting={deletingServiceItemId === item.id}
							onMarkServiced={() => handleMarkServiced(item.id)}
							onItemUpdated={() => loadCarPage({ showLoading: false })}
							onReminderChanged={() => loadCarPage({ showLoading: false })}
							onDelete={() => handleDeleteServiceItem(item.id)}
						/>
					{/each}
				{:else}
					<Empty.Root class="rounded-lg border border-dashed">
						<Empty.Header>
							<Empty.Description>{m.car_detail_empty_service_items()}</Empty.Description>
						</Empty.Header>
					</Empty.Root>
				{/if}
			</div>
		</div>
	{/if}
</div>
