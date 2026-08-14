<script lang="ts">
	import CarFront from "@lucide/svelte/icons/car-front";
	import Plus from "@lucide/svelte/icons/plus";
	import RefreshCw from "@lucide/svelte/icons/refresh-cw";
	import Wrench from "@lucide/svelte/icons/wrench";
	import { onMount } from "svelte";

	import {
		Cars,
		MileageLogs,
		Reminders,
		ServiceItems,
		type CarRead,
		type ReminderRead,
		type ServiceItemSummary
	} from "$lib/api";
	import CarCard from "$lib/components/CarCard.svelte";
	import ServiceItemCard from "$lib/components/ServiceItemCard.svelte";
	import TmaCarSelector from "$lib/components/tma/TmaCarSelector.svelte";
	import TmaHeader from "$lib/components/tma/TmaHeader.svelte";
	import TmaQuickActions from "$lib/components/tma/TmaQuickActions.svelte";
	import AddCarDialog from "$lib/components/ui/AddCarDialog.svelte";
	import AddServiceDialog from "$lib/components/ui/AddServiceDialog.svelte";
	import { Button } from "$lib/components/ui/button";
	import * as Card from "$lib/components/ui/card";
	import * as Empty from "$lib/components/ui/empty";
	import { Separator } from "$lib/components/ui/separator";
	import { Skeleton } from "$lib/components/ui/skeleton";
	import * as m from "$lib/paraglide/messages.js";
	import { buildServiceLines } from "$lib/reminderStatus.js";

	let cars = $state<CarRead[]>([]);
	let selectedCarId = $state<string | null>(null);
	let serviceItems = $state<ServiceItemSummary[]>([]);
	let reminders = $state<ReminderRead[]>([]);
	let isLoadingCars = $state(true);
	let isLoadingServices = $state(false);

	let savingItemId = $state<string | null>(null);
	let deletingItemId = $state<string | null>(null);

	const selectedCar = $derived(cars.find((c) => c.id === selectedCarId) ?? cars[0] ?? null);

	const serviceLines = $derived(
		selectedCar && (reminders.length > 0 || serviceItems.length > 0)
			? buildServiceLines(
					reminders,
					serviceItems,
					selectedCar.current_odometer_km ?? selectedCar.initial_odometer_km,
					m
				)
			: []
	);

	const dueItemsCount = $derived(
		serviceItems.filter((i) => i.status === "due" || i.status === "soon").length
	);

	async function loadCars() {
		isLoadingCars = true;
		try {
			const res = await Cars.listUserCarsApiCarsGet();
			cars = res.data ?? [];
			if (cars.length > 0 && !selectedCarId) {
				selectedCarId = cars[0].id;
			}
		} catch (e) {
			console.error("failed to load cars:", e);
		} finally {
			isLoadingCars = false;
		}
	}

	async function loadCarDetails(carId: string) {
		isLoadingServices = true;
		try {
			const [serviceRes, remindersRes] = await Promise.all([
				ServiceItems.listByCarApiServiceItemsGet({
					query: { car_id: carId }
				}),
				Reminders.listRemindersApiRemindersGet({
					query: { car_id: carId }
				})
			]);
			serviceItems = serviceRes.data ?? [];
			reminders = remindersRes.data ?? [];
		} catch (e) {
			console.error("failed to load car details:", e);
		} finally {
			isLoadingServices = false;
		}
	}

	$effect(() => {
		if (selectedCarId) {
			loadCarDetails(selectedCarId);
		} else {
			serviceItems = [];
			reminders = [];
		}
	});

	async function handleAddMileage(newMileage: number): Promise<boolean> {
		if (!selectedCar) return false;
		try {
			const res = await MileageLogs.addMileageLogApiMileageLogsPost({
				body: {
					car_id: selectedCar.id,
					odometer_km: newMileage
				}
			});

			if (res.error) return false;

			await loadCars();
			if (selectedCarId) {
				await loadCarDetails(selectedCarId);
			}
			return true;
		} catch (e) {
			console.error("failed to save mileage:", e);
			return false;
		}
	}

	async function handleMarkServiced(itemId: string) {
		if (!selectedCar) return;
		savingItemId = itemId;
		try {
			await ServiceItems.markServicedApiServiceItemsServiceItemIdMarkServicedPost({
				path: { service_item_id: itemId },
				body: {
					serviced_at: new Date().toISOString(),
					odometer_km: selectedCar.current_odometer_km ?? selectedCar.initial_odometer_km
				}
			});
			if (selectedCarId) {
				await loadCarDetails(selectedCarId);
			}
		} catch (e) {
			console.error("failed to mark serviced:", e);
		} finally {
			savingItemId = null;
		}
	}

	async function handleDeleteServiceItem(itemId: string) {
		deletingItemId = itemId;
		try {
			await ServiceItems.deleteServiceItemApiServiceItemsServiceItemIdDelete({
				path: { service_item_id: itemId }
			});
			if (selectedCarId) {
				await loadCarDetails(selectedCarId);
			}
		} catch (e) {
			console.error("failed to delete service item:", e);
		} finally {
			deletingItemId = null;
		}
	}

	onMount(async () => {
		await loadCars();
	});
</script>

<svelte:head>
	<title>car minder</title>
</svelte:head>

<div class="mx-auto flex w-full max-w-lg flex-col gap-5 p-4 pb-12">
	<!-- Header -->
	<TmaHeader {dueItemsCount} />

	{#if isLoadingCars}
		<div class="flex flex-col gap-4">
			<Skeleton class="h-10 w-full rounded-lg" />
			<Skeleton class="h-48 w-full rounded-lg" />
			<Skeleton class="h-32 w-full rounded-lg" />
		</div>
	{:else if cars.length === 0}
		<Card.Root class="border-dashed">
			<Card.Content class="p-6">
				<Empty.Root class="border-none p-4">
					<Empty.Header>
						<Empty.Media variant="icon" class="size-12 rounded-xl">
							<CarFront class="size-6 text-muted-foreground" />
						</Empty.Media>
						<Empty.Title>{m.garage_has_no_car_title()}</Empty.Title>
						<Empty.Description>{m.garage_has_no_car_desc()}</Empty.Description>
					</Empty.Header>
					<Empty.Content class="pt-4">
						<AddCarDialog onCarAdded={loadCars}>
							{#snippet child({ props })}
								<Button {...props} class="w-full">
									<Plus data-icon="inline-start" />
									{m.garage_add_first_car()}
								</Button>
							{/snippet}
						</AddCarDialog>
					</Empty.Content>
				</Empty.Root>
			</Card.Content>
		</Card.Root>
	{:else}
		<!-- Car Switcher -->
		<TmaCarSelector {cars} bind:selectedCarId />

		<!-- Active Car Overview -->
		{#if selectedCar}
			<CarCard car={selectedCar} {serviceLines} />

			<!-- Quick Actions Grid -->
			<TmaQuickActions
				{selectedCar}
				{serviceItems}
				onCarAdded={loadCars}
				onServiceAdded={() => loadCarDetails(selectedCar.id)}
				onReminderChanged={() => loadCarDetails(selectedCar.id)}
				onMileageAdded={handleAddMileage}
			/>

			<Separator class="my-1" />

			<!-- Maintenance & Consumables Header -->
			<div class="flex items-center justify-between">
				<h2 class="text-base font-semibold tracking-tight">{m.tma_service_items_heading()}</h2>
				<Button
					variant="ghost"
					size="icon"
					class="size-8 text-muted-foreground"
					onclick={() => loadCarDetails(selectedCar.id)}
					disabled={isLoadingServices}
				>
					<RefreshCw class="size-3.5 {isLoadingServices ? 'animate-spin' : ''}" />
				</Button>
			</div>

			<!-- Service Items List -->
			{#if isLoadingServices}
				<div class="flex flex-col gap-3">
					<Skeleton class="h-24 w-full rounded-lg" />
					<Skeleton class="h-24 w-full rounded-lg" />
				</div>
			{:else if serviceItems.length === 0}
				<Card.Root>
					<Card.Content class="p-6">
						<Empty.Root class="border-none p-2">
							<Empty.Header>
								<Empty.Media variant="icon" class="size-12 rounded-xl">
									<Wrench class="size-6 text-muted-foreground" />
								</Empty.Media>
								<Empty.Title class="text-base">{m.tma_service_items_empty_title()}</Empty.Title>
								<Empty.Description class="text-xs">
									{m.tma_service_items_empty_desc()}
								</Empty.Description>
							</Empty.Header>
							<Empty.Content class="pt-3">
								<AddServiceDialog
									car={selectedCar}
									onServiceAdded={() => loadCarDetails(selectedCar.id)}
								>
									{#snippet child({ props })}
										<Button {...props} variant="secondary" size="sm">
											<Plus data-icon="inline-start" />
											{m.tma_service_items_add_first()}
										</Button>
									{/snippet}
								</AddServiceDialog>
							</Empty.Content>
						</Empty.Root>
					</Card.Content>
				</Card.Root>
			{:else}
				<div class="flex flex-col gap-3">
					{#each serviceItems as item (item.id)}
						<ServiceItemCard
							{item}
							car={selectedCar}
							{serviceItems}
							isSaving={savingItemId === item.id}
							isDeleting={deletingItemId === item.id}
							onMarkServiced={() => handleMarkServiced(item.id)}
							onItemUpdated={() => loadCarDetails(selectedCar.id)}
							onReminderChanged={() => loadCarDetails(selectedCar.id)}
							onDelete={() => handleDeleteServiceItem(item.id)}
						/>
					{/each}
				</div>
			{/if}
		{/if}
	{/if}
</div>
