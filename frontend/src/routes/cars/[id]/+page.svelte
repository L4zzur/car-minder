<script lang="ts">
	import {
		ArrowLeft,
		Bell,
		CarFront,
		CircleAlert,
		CircleCheck,
		Clock,
		Gauge,
		Plus,
		Trash2
	} from 'lucide-svelte';
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
		type ServiceItemRead
	} from '$lib/api';
	import CarStats from '$lib/components/CarStats.svelte';
	import MileageForm from '$lib/components/MileageForm.svelte';
	import MileageHistory from '$lib/components/MileageHistory.svelte';
	import AddServiceDialog from '$lib/components/ui/AddServiceDialog.svelte';
	import { Button } from '$lib/components/ui/button';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import * as Tooltip from '$lib/components/ui/tooltip';

	type ServiceItemView = {
		id: string;
		name: string;
		lastServiceAt: string;
		lastServiceOdometerKm: number;
		nextLabel: string;
		status: 'ok' | 'soon' | 'due';
	};

	type MileageLogView = {
		id: string;
		odometerKm: number;
		createdAt: string;
	};

	let car = $state<CarRead | null>(null);
	let mileageValue = $state<number | string>('');
	let serviceItems = $state<ServiceItemView[]>([]);
	let mileageLogs = $state<MileageLogView[]>([]);
	let isLoading = $state(true);
	let isSavingMileage = $state(false);
	let deletingMileageLogId = $state<string | null>(null);
	let deletingServiceItemId = $state<string | null>(null);
	let savingServiceItemId = $state<string | null>(null);
	let mileageError = $state('');
	let serviceItemError = $state('');
	let error = $state('');

	const formatOdometer = (value: number) => value.toLocaleString('ru-RU');
	const drivenKm = $derived(car ? car.current_odometer_km - car.initial_odometer_km : 0);
	const serviceItemCount = $derived(serviceItems.length);
	const dueCount = $derived(serviceItems.filter((item) => item.status === 'due').length);
	const soonCount = $derived(serviceItems.filter((item) => item.status === 'soon').length);

	const deltas = $derived(
		mileageLogs.map((log, i) => {
			const prev = mileageLogs[i - 1];
			return i === 0 ? null : log.odometerKm - prev.odometerKm;
		})
	);

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('ru-RU', {
			day: 'numeric',
			month: 'short',
			year: 'numeric'
		});
	}

	function statusIcon(status: ServiceItemView['status']) {
		if (status === 'due') return { icon: CircleAlert, color: 'text-destructive' };
		if (status === 'soon') return { icon: Clock, color: 'text-primary' };
		return { icon: CircleCheck, color: 'text-muted-foreground' };
	}

	function sortMileageLogs(logs: MileageLogRead[]) {
		return [...logs].sort(
			(a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
		);
	}

	function daysUntilReminder(
		lastServiceAt: string,
		intervalDays: number,
		notifyBeforeDays: number
	) {
		const lastService = new Date(lastServiceAt);
		const notifyAt = new Date(lastService);
		notifyAt.setDate(lastService.getDate() + intervalDays - notifyBeforeDays);

		return Math.ceil((notifyAt.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
	}

	function getReminderState(item: ServiceItemRead, reminder: ReminderRead | null) {
		if (!car || !reminder) {
			return { status: 'ok' as const, nextLabel: 'без напоминания' };
		}

		const labels: string[] = [];
		let status: ServiceItemView['status'] = 'ok';

		if (reminder.interval_km) {
			const notifyBeforeKm = reminder.notify_before_km ?? 0;
			const dueAtKm = item.last_service_odometer_km + reminder.interval_km;
			const notifyAtKm = dueAtKm - notifyBeforeKm;
			const kmUntilDue = dueAtKm - car.current_odometer_km;
			const kmUntilNotify = notifyAtKm - car.current_odometer_km;

			if (kmUntilDue <= 0) {
				status = 'due';
				labels.push(`просрочено на ${formatOdometer(Math.abs(kmUntilDue))} км`);
			} else if (kmUntilNotify <= 0) {
				status = 'soon';
				labels.push(`через ${formatOdometer(kmUntilDue)} км`);
			} else {
				labels.push(`через ${formatOdometer(kmUntilDue)} км`);
			}
		}

		if (reminder.interval_days) {
			const notifyBeforeDays = reminder.notify_before_days ?? 0;
			const days = daysUntilReminder(
				item.last_service_at,
				reminder.interval_days,
				notifyBeforeDays
			);

			if (days <= 0 && status !== 'due') {
				status = 'soon';
				labels.push('скоро по времени');
			} else if (days > 0) {
				labels.push(`через ${days} дн.`);
			}
		}

		return { status, nextLabel: labels[0] ?? 'в норме' };
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

			const services = serviceResponse.data ?? [];
			const reminders = await Promise.all(
				services.map(async (item) => {
					const response =
						await Reminders.listActiveByServiceItemApiRemindersServiceItemServiceItemIdActiveGet({
							path: { service_item_id: item.id }
						});

					return response.data?.[0] ?? null;
				})
			);

			serviceItems = services.map((item, index) => {
				const reminderState = getReminderState(item, reminders[index]);

				return {
					id: item.id,
					name: item.name,
					lastServiceAt: item.last_service_at,
					lastServiceOdometerKm: item.last_service_odometer_km,
					nextLabel: reminderState.nextLabel,
					status: reminderState.status
				};
			});
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
				await loadCarPage();
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

<div class="container mx-auto space-y-6 p-6">
	<header class="flex items-center justify-between">
		<a
			href="/home"
			class="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
		>
			<ArrowLeft class="size-4" />
			<span>назад в гараж</span>
		</a>

		<div class="flex items-center gap-2">
			{#if car}
				<AddServiceDialog {car} onServiceAdded={() => loadCarPage({ showLoading: false })} />
			{/if}
			<Button size="sm">
				<Bell class="size-3.5" />
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

		<div class="grid gap-4 sm:grid-cols-2">
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
							<Button {...props} variant="outline" size="sm">
								<Plus class="size-4" />
								добавить
							</Button>
						{/snippet}
					</AddServiceDialog>
				{/if}
			</div>

			<div class="grid gap-4 sm:grid-cols-2">
				{#if serviceItems.length}
					{#each serviceItems as item}
						{@const { icon: StatusIcon, color } = statusIcon(item.status)}
						<div class="flex items-center justify-between gap-4 rounded-lg border bg-card p-4">
							<div class="flex items-start gap-3">
								<StatusIcon class={`mt-0.5 size-5 ${color}`} />
								<div class="space-y-1">
									<h3 class="font-medium">{item.name}</h3>
									<div class="flex flex-wrap gap-x-4 text-xs text-muted-foreground">
										<span>замена: {formatDate(item.lastServiceAt)}</span>
										<span>{formatOdometer(item.lastServiceOdometerKm)} км</span>
									</div>
								</div>
							</div>

							<div class="flex shrink-0 items-center gap-2">
								<span class="rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground">
									{item.nextLabel}
								</span>

								<Tooltip.Root>
									<Tooltip.Trigger>
										<Button
											variant="ghost"
											size="sm"
											disabled={savingServiceItemId === item.id}
											onclick={() => handleMarkServiced(item.id)}
										>
											{savingServiceItemId === item.id ? 'сохраняем...' : 'обслужено'}
										</Button>
									</Tooltip.Trigger>
									<Tooltip.Content>
										<p>отметить обслуживание</p>
									</Tooltip.Content>
								</Tooltip.Root>

								<Tooltip.Root>
									<Tooltip.Trigger>
										<Button
											variant="ghost"
											size="icon"
											disabled={deletingServiceItemId === item.id}
											onclick={() => handleDeleteServiceItem(item.id)}
										>
											<Trash2 class="size-4" />
										</Button>
									</Tooltip.Trigger>
									<Tooltip.Content>
										<p>удалить расходник</p>
									</Tooltip.Content>
								</Tooltip.Root>
							</div>
						</div>
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
