<script lang="ts">
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import CarFront from '@lucide/svelte/icons/car-front';
	import Home from '@lucide/svelte/icons/home';
	import ServerCrash from '@lucide/svelte/icons/server-crash';
	import ShieldAlert from '@lucide/svelte/icons/shield-alert';
	import { onMount } from 'svelte';

	import { page } from '$app/state';

	import { auth } from '$lib/auth.svelte';
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
		<Empty.Root class="rounded-2xl border bg-card p-8 shadow-sm flex flex-col items-center justify-center text-center">
			<Empty.Header class="flex flex-col items-center gap-3">
				<Empty.Media variant="icon" class="size-16 rounded-2xl border bg-muted/30">
					{#if status === 404}
						<CarFront class="size-8 text-muted-foreground" />
					{:else if status >= 500}
						<ServerCrash class="size-8 text-destructive" />
					{:else}
						<ShieldAlert class="size-8 text-muted-foreground" />
					{/if}
				</Empty.Media>

				<span class="text-xs font-mono font-semibold tracking-wider text-muted-foreground uppercase">
					ERROR // {status}
				</span>

				<Empty.Title class="text-2xl font-bold tracking-tight text-balance">
					{heading}
				</Empty.Title>

				<Empty.Description class="text-sm text-muted-foreground leading-relaxed max-w-xs text-balance">
					{description}
				</Empty.Description>
			</Empty.Header>

			<Empty.Content class="mt-6 flex flex-col sm:flex-row gap-3 w-full justify-center">
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
