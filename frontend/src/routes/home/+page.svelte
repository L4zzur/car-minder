<script lang="ts">
	import CarFront from '@lucide/svelte/icons/car-front';
	import { onMount } from 'svelte';

	import { goto } from '$app/navigation';

	import { Auth, Cars, type CarRead } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import CarCard from '$lib/components/CarCard.svelte';
	import AddCarDialog from '$lib/components/ui/AddCarDialog.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';

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
	<title>гараж // car minder</title>
</svelte:head>

<div class="container mx-auto space-y-6 p-6">
	<div class="flex items-center gap-3">
		{#if auth.user}
			<span class="primary-foreground text-sm">
				{auth.user.name ?? auth.user.username}
			</span>
		{/if}

		<Button
			variant="secondary"
			onclick={async () => {
				await Auth.logoutApiAuthLogoutPost();
				auth.logout();
				await goto('/login');
			}}
		>
			выйти
		</Button>
	</div>
	<div class="flex items-center justify-between">
		<h1 class="text-4xl font-bold tracking-tight">твой гараж</h1>
		<AddCarDialog onCarAdded={loadCars} />
	</div>

	{#if isLoading}
		<div class="grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
			{#each Array(3) as _}
				<Card.Root class="animate-pulse">
					<Card.Header class="h-32 rounded-t-lg bg-muted"></Card.Header>
					<Card.Content class="space-y-2 p-4">
						<div class="h-4 w-3/4 bg-muted"></div>
						<div class="h-4 w-1/2 bg-muted"></div>
					</Card.Content>
				</Card.Root>
			{/each}
		</div>
	{:else if cars.length === 0}
		<div
			class="flex flex-col items-center justify-center space-y-4 rounded-lg border-2 border-dashed p-12 text-center"
		>
			<div class="rounded-full bg-muted p-4">
				<CarFront class="h-8 w-8 text-muted-foreground" />
			</div>
			<div class="space-y-1">
				<h3 class="text-lg font-semibold">у тебя пока нет машин</h3>
				<p class="text-sm text-muted-foreground">
					добавь свою первую машину, чтобы начать следить за её состоянием.
				</p>
			</div>
			<AddCarDialog onCarAdded={loadCars} />
		</div>
	{:else}
		<div class="grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
			{#each cars as car}
				<CarCard {car} href={`/cars/${car.id}`} />
			{/each}
		</div>
	{/if}
</div>
