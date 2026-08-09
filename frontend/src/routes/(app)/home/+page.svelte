<script lang="ts">
	import CarFront from '@lucide/svelte/icons/car-front';
	import Settings from '@lucide/svelte/icons/settings';
	import { onMount } from 'svelte';

	import { goto } from '$app/navigation';

	import { Auth, Cars, type CarRead } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import CarCard from '$lib/components/CarCard.svelte';
	import AddCarDialog from '$lib/components/ui/AddCarDialog.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import * as Empty from '$lib/components/ui/empty';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import * as m from '$lib/paraglide/messages.js';

	let cars = $state<CarRead[]>([]);
	let isLoading = $state(true);

	async function loadCars() {
		isLoading = true;
		try {
			const response = await Cars.listUserCarsApiCarsGet();
			cars = response.data || [];
		} catch (e) {
			console.error('failed to load cars:', e);
		} finally {
			isLoading = false;
		}
	}

	onMount(async () => {
		auth.init();
		await auth.fetchUser();

		if (!auth.isAuthenticated) {
			await goto('/login');
			return;
		}

		await loadCars();
	});
</script>

<svelte:head>
	<title>{m.garage_head_title()} // car minder</title>
</svelte:head>

<div class="container mx-auto flex flex-col gap-6 p-6">
	<div class="flex items-center justify-between">
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
					await goto('/login');
				}}
			>
				{m.garage_logout()}
			</Button>
		</div>
	</div>
	<div class="flex items-center justify-between">
		<h1 class="text-4xl font-bold tracking-tight">{m.garage_title()}</h1>
		<AddCarDialog onCarAdded={loadCars} />
	</div>

	{#if isLoading}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each Array(3) as _}
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
	{:else if cars.length === 0}
		<Empty.Root class="rounded-lg border-2 border-dashed p-12">
			<Empty.Header>
				<Empty.Media variant="icon">
					<CarFront />
				</Empty.Media>
				<Empty.Title>{m.garage_has_no_car_title()}</Empty.Title>
				<Empty.Description>{m.garage_has_no_car_desc()}</Empty.Description>
			</Empty.Header>
			<Empty.Content>
				<AddCarDialog onCarAdded={loadCars}>
					{#snippet child({ props })}
						<Button {...props}>{m.garage_add_first_car()}</Button>
					{/snippet}
				</AddCarDialog>
			</Empty.Content>
		</Empty.Root>
	{:else}
		<div class="grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
			{#each cars as car}
				<CarCard {car} href={`/cars/${car.id}`} />
			{/each}
		</div>
	{/if}
</div>
