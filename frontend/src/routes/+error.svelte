<script lang="ts">
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import CarFront from '@lucide/svelte/icons/car-front';
	import Home from '@lucide/svelte/icons/home';
	import ServerCrash from '@lucide/svelte/icons/server-crash';
	import ShieldAlert from '@lucide/svelte/icons/shield-alert';
	import { onMount } from 'svelte';

	import { page } from '$app/state';

	import { auth } from '$lib/auth.svelte';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import * as Empty from '$lib/components/ui/empty';
	import * as m from '$lib/paraglide/messages.js';

	const status = $derived(page.status ?? 500);

	const heading = $derived(
		status === 404
			? m.error_heading_404()
			: status >= 500
				? m.error_heading_500()
				: m.error_heading_generic()
	);

	const description = $derived(
		status === 404
			? m.error_description_404()
			: status >= 500
				? m.error_description_500()
				: m.error_description_generic()
	);

	onMount(() => {
		auth.init();
	});
</script>

<svelte:head>
	<title>{status} // car minder</title>
</svelte:head>

<main class="flex min-h-screen items-center justify-center p-6 bg-background text-foreground">
	<div class="w-full max-w-md">
		<Empty.Root class="border bg-card p-8 shadow-sm">
			<Empty.Header>
				<Empty.Media variant="icon">
					{#if status === 404}
						<CarFront class="text-muted-foreground" />
					{:else if status >= 500}
						<ServerCrash class="text-destructive" />
					{:else}
						<ShieldAlert class="text-muted-foreground" />
					{/if}
				</Empty.Media>

				<Badge variant="outline" class="font-mono text-xs uppercase">
					ERROR // {status}
				</Badge>

				<Empty.Title class="text-xl">
					{heading}
				</Empty.Title>

				<Empty.Description>
					{description}
				</Empty.Description>
			</Empty.Header>

			<Empty.Content class="flex-row flex-wrap justify-center sm:flex-nowrap">
				{#if auth.isAuthenticated}
					<Button href="/garage" class="w-full sm:w-auto">
						<CarFront data-icon="inline-start" />
						{m.error_btn_garage()}
					</Button>
				{:else}
					<Button href="/" class="w-full sm:w-auto">
						<Home data-icon="inline-start" />
						{m.error_btn_home()}
					</Button>
				{/if}
				<Button variant="outline" onclick={() => history.back()} class="w-full sm:w-auto">
					<ArrowLeft data-icon="inline-start" />
					{m.error_btn_back()}
				</Button>
			</Empty.Content>
		</Empty.Root>
	</div>
</main>
