<script lang="ts">
	import CarFront from "@lucide/svelte/icons/car-front";
	import Settings from "@lucide/svelte/icons/settings";
	import { onMount } from "svelte";

	import { goto } from "$app/navigation";

	import { Auth } from "$lib/api";
	import { auth } from "$lib/auth.svelte";
	import CarCard from "$lib/components/CarCard.svelte";
	import LanguageSwitcher from "$lib/components/LanguageSwitcher.svelte";
	import SearchButton from "$lib/components/SearchButton.svelte";
	import ThemeToggle from "$lib/components/ThemeToggle.svelte";
	import AddCarDialog from "$lib/components/ui/AddCarDialog.svelte";
	import { Button } from "$lib/components/ui/button";
	import * as Card from "$lib/components/ui/card";
	import * as Empty from "$lib/components/ui/empty";
	import { Skeleton } from "$lib/components/ui/skeleton";
	import { garageStore } from "$lib/garageStore.svelte";
	import * as m from "$lib/paraglide/messages.js";
	import { buildServiceLines } from "$lib/reminderStatus.js";

	onMount(async () => {
		auth.init();
		await auth.fetchUser();

		if (!auth.isAuthenticated) {
			await goto("/login");
			return;
		}

		await garageStore.load();
	});
</script>

<svelte:head>
	<title>{m.garage_head_title()} // car minder</title>
</svelte:head>

<div class="container mx-auto flex flex-col gap-6 p-6">
	<div class="flex items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			{#if auth.user}
				<span class="text-sm font-medium">
					{auth.user.name ?? auth.user.username}
				</span>
			{/if}

			<Button variant="outline" href="/settings">
				<Settings data-icon="inline-start" />
				{m.settings_button()}
			</Button>

			<Button
				variant="secondary"
				onclick={async () => {
					await Auth.logoutApiAuthLogoutPost();
					auth.logout();
					await goto("/login");
				}}
			>
				{m.garage_logout()}
			</Button>
		</div>

		<div class="flex items-center gap-2">
			<SearchButton />
			<LanguageSwitcher />
			<ThemeToggle />
		</div>
	</div>
	<div class="flex items-center justify-between">
		<h1 class="text-4xl font-bold tracking-tight">{m.garage_title()}</h1>
		<AddCarDialog onCarAdded={() => garageStore.invalidate()} />
	</div>

	{#if garageStore.isLoading}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each [0, 1, 2] as i (i)}
				<Card.Root>
					<Card.Header class="h-32 rounded-t-lg p-0">
						<Skeleton class="h-full w-full rounded-t-lg" />
					</Card.Header>
					<Card.Content class="flex flex-col gap-2 p-4">
						<Skeleton class="h-4 w-3/4" />
						<Skeleton class="h-4 w-1/2" />
					</Card.Content>
				</Card.Root>
			{/each}
		</div>
	{:else if garageStore.cars.length === 0}
		<Empty.Root class="rounded-lg border-2 border-dashed p-12">
			<Empty.Header>
				<Empty.Media variant="icon">
					<CarFront />
				</Empty.Media>
				<Empty.Title>{m.garage_has_no_car_title()}</Empty.Title>
				<Empty.Description>{m.garage_has_no_car_desc()}</Empty.Description>
			</Empty.Header>
			<Empty.Content>
				<AddCarDialog onCarAdded={() => garageStore.invalidate()}>
					{#snippet child({ props })}
						<Button {...props}>{m.garage_add_first_car()}</Button>
					{/snippet}
				</AddCarDialog>
			</Empty.Content>
		</Empty.Root>
	{:else}
		<div class="grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
			{#each garageStore.cars as car (car.id)}
				<CarCard
					{car}
					serviceLines={buildServiceLines(
						car.reminders || [],
						car.serviceItems || [],
						car.current_odometer_km,
						m
					)}
					href={`/cars/${car.id}`}
					onMileageUpdated={() => garageStore.invalidate()}
				/>
			{/each}
		</div>
	{/if}
</div>
