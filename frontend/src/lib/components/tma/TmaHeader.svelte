<script lang="ts">
	import CarFront from '@lucide/svelte/icons/car-front';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import CircleCheck from '@lucide/svelte/icons/circle-check';

	import { auth } from '$lib/auth.svelte';
	import { Badge } from '$lib/components/ui/badge';
	import * as m from '$lib/paraglide/messages.js';

	let { dueItemsCount }: { dueItemsCount: number } = $props();
</script>

<header class="flex items-center justify-between border-b pb-3">
	<div class="flex items-center gap-2.5">
		<span class="flex size-9 items-center justify-center rounded-lg border bg-card text-foreground">
			<CarFront class="size-4" />
		</span>
		<div class="flex flex-col">
			<span class="text-sm font-semibold tracking-tight">car minder</span>
			{#if auth.user}
				<span class="text-xs text-muted-foreground">
					{auth.user.name ?? auth.user.username}
				</span>
			{/if}
		</div>
	</div>

	{#if dueItemsCount > 0}
		<Badge variant="destructive" class="flex items-center gap-1.5 px-2.5 py-1 text-xs">
			<CircleAlert class="size-3.5" />
			<span>{m.tma_header_attention({ count: dueItemsCount })}</span>
		</Badge>
	{:else}
		<Badge variant="secondary" class="flex items-center gap-1.5 px-2.5 py-1 text-xs">
			<CircleCheck class="size-3.5 text-success" />
			<span>{m.tma_header_all_good()}</span>
		</Badge>
	{/if}
</header>
