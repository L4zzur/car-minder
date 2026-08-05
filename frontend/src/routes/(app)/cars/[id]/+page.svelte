<script lang="ts">
	import { ArrowLeft, Bell, CarFront, Plus } from 'lucide-svelte';
	import { onMount } from 'svelte';

	import { goto } from '$app/navigation';
	import { page } from '$app/state';

	import {
		Cars,
		MileageLogs,
		ServiceItems,
		type CarRead,
		type MileageLogRead,
		type ServiceItemSummary
	} from '$lib/api';
	import CarStats from '$lib/components/CarStats.svelte';
	import MileageForm from '$lib/components/MileageForm.svelte';
	import MileageHistory from '$lib/components/MileageHistory.svelte';
	import ServiceItemCard from '$lib/components/ServiceItemCard.svelte';
	import AddServiceDialog from '$lib/components/ui/AddServiceDialog.svelte';
	import { Button } from '$lib/components/ui/button';

	type MileageLogView = {
		id: string;
		odometerKm: number;
		createdAt: string;
	};

	let car = $state<CarRead | null>(null);
	let mileageValue = $state<number | string>('');
	let serviceItems = $state<ServiceItemSummary[]>([]);
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
	const dueCount = $derived(serviceItems.filter((item) => item.status === 'due').length);
	const soonCount = $derived(serviceItems.filter((item) => item.status === 'soon').length);

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
			const [carResponse, mileageResponse, serviceResponse] = await Promise.all([
				Cars.getCarApiCarsCarIdGet({ path: { car_id: carId } }),
				MileageLogs.listByCarApiMileageLogsCarCarIdGet({ path: { car_id: carId } }),
				ServiceItems.listByCarApiServiceItemsCarCarIdGet({ path: { car_id: carId } })
			]);

			if (carResponse.error || !carResponse.data) {
				error = 'машина не найдена';
				return;
			}

			car = carResponse.data;
			mileageValue = car.current_odometer_km;
			mileageLogs = sortMileageLogs(mileageResponse.data ?? []).map((log) => ({
				id: log.id,
				odometerKm: log.odometer_km,
				createdAt: log.created_at
			}));

			serviceItems = serviceResponse.data ?? [];
		} catch (e) {
			console.error('failed to load car page:', e);
			error = 'не удалось загрузить машину';
		} finally {
			isLoading = false;
		}
	}

	async function handleMileageSubmit() {
		if (!car) return;

		const odometer = Number(mileageValue);
		mileageError = '';

		if (!Number.isFinite(odometer)) {
			mileageError = 'введи корректный пробег';
			return;
		}

		if (odometer <= car.current_odometer_km) {
			mileageError = 'пробег должен быть больше текущего';
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
				mileageError = 'не удалось сохранить пробег';
				return;
			}

			await loadCarPage({ showLoading: false });
		} catch (e) {
			console.error('failed to save mileage:', e);
			mileageError = 'не удалось сохранить пробег';
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
				mileageError = 'не удалось удалить запись';
				return;
			}

			await loadCarPage({ showLoading: false });
		} catch (e) {
			console.error('failed to delete mileage log:', e);
			mileageError = 'не удалось удалить запись';
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
				serviceItemError = 'не удалось удалить расходник';
				return;
			}

			await loadCarPage({ showLoading: false });
		} catch (e) {
			console.error('failed to delete service item:', e);
			serviceItemError = 'не удалось удалить расходник';
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
	<title>{car ? `${car.brand} ${car.model}` : 'машина'} // car minder</title>
</svelte:head>

<div class="container mx-auto space-y-6 p-4 sm:p-6">
	<header class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<a
			href="/home"
			class="flex items-center gap-2 self-start text-sm text-muted-foreground transition-colors hover:text-foreground"
		>
			<ArrowLeft class="size-4" />
			<span>назад в гараж</span>
		</a>

		<div class="flex w-full items-center gap-2 sm:w-auto">
			{#if car}
				<AddServiceDialog
					{car}
					onServiceAdded={() => loadCarPage({ showLoading: false })}
					class="flex-1 sm:flex-initial"
				/>
			{/if}
			<Button class="flex-1 sm:flex-none">
				<Bell data-icon="inline-start" />
				напоминание
			</Button>
		</div>
	</header>

	{#if isLoading}
		<div class="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
			загружаем машину...
		</div>
	{:else if error || !car}
		<div class="space-y-4 rounded-lg border bg-card p-6">
			<p class="text-sm text-muted-foreground">{error || 'машина не найдена'}</p>
			<Button onclick={() => goto('/home')}>вернуться в гараж</Button>
		</div>
	{:else}
		<div class="space-y-4">
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
						<span class="rounded-md border px-2 py-1 text-xs text-muted-foreground">{car.year}</span
						>
					</div>
					<p class="text-sm text-muted-foreground">карточка обслуживания и пробега</p>
				</div>
			</div>
		</div>

		<CarStats {car} {drivenKm} {dueCount} {soonCount} {serviceItemCount} />

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

		<div class="space-y-4">
			<div class="flex items-center justify-between">
				<div>
					<h2 class="text-lg font-medium">расходники</h2>
					<p class="text-sm text-muted-foreground">обслуживание по пробегу или времени</p>
				</div>
				{#if car}
					<AddServiceDialog {car} onServiceAdded={loadCarPage}>
						{#snippet child({ props })}
							<Button {...props} variant="outline">
								<Plus data-icon="inline-start" />
								добавить
							</Button>
						{/snippet}
					</AddServiceDialog>
				{/if}
			</div>

			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
				{#if serviceItems.length}
					{#each serviceItems as item}
						<ServiceItemCard
							{item}
							isSaving={savingServiceItemId === item.id}
							isDeleting={deletingServiceItemId === item.id}
							onMarkServiced={() => handleMarkServiced(item.id)}
							onDelete={() => handleDeleteServiceItem(item.id)}
						/>
					{/each}
				{:else}
					<div class="rounded-lg border border-dashed p-6 text-sm text-muted-foreground">
						расходники пока не добавлены
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
