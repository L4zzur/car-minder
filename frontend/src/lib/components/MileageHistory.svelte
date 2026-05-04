<script lang="ts">
	import { Trash2 } from 'lucide-svelte';

	import { Button } from '$lib/components/ui/button';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import * as Tooltip from '$lib/components/ui/tooltip';

	type Log = {
		id: string;
		odometerKm: number;
		createdAt: string;
	};
	let {
		logs,
		deletingId,
		onDelete
	}: {
		logs: Log[];
		deletingId: string | null;
		onDelete: (id: string) => void;
	} = $props();

	const formatOdometer = (val: number) => val.toLocaleString('ru-RU');
	const formatDate = (str: string) =>
		new Date(str).toLocaleDateString('ru-RU', {
			day: 'numeric',
			month: 'short',
			year: 'numeric'
		});
	const deltas = $derived(
		logs.map((log, i) => (i === 0 ? null : log.odometerKm - logs[i - 1].odometerKm))
	);
</script>

<div class="flex flex-col rounded-lg border bg-card p-4">
	<div class="flex min-w-0 flex-col">
		<div class="flex items-center justify-between gap-3">
			<h3 class="text-sm font-medium">история пробега</h3>
			<span class="shrink-0 text-xs text-muted-foreground">{logs.length} записи</span>
		</div>
		<ScrollArea type="always" class="mt-4 max-h-24 min-h-0 pr-6">
			{#if logs.length}
				<div>
					{#each logs as log, i (log.id)}
						{@const delta = deltas[i]}
						<div class="flex min-h-6 items-center justify-between gap-4 rounded-md text-sm">
							<span class="min-w-0 text-xs text-muted-foreground">{formatDate(log.createdAt)}</span>
							<div class="flex shrink-0 items-center gap-3 text-right">
								{#if delta !== null}
									<span class="text-xs text-muted-foreground">
										+{formatOdometer(Math.abs(delta))} км
									</span>
								{/if}
								<span class="min-w-20 font-medium">{formatOdometer(log.odometerKm)} км</span>
								{#if i === 0}
									<Tooltip.Root>
										<Tooltip.Trigger>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label="удалить последнюю запись пробега"
												disabled={deletingId === log.id}
												onclick={() => onDelete(log.id)}
											>
												<Trash2 class="size-3" />
											</Button>
										</Tooltip.Trigger>
										<Tooltip.Content>
											<p>удалить запись</p>
										</Tooltip.Content>
									</Tooltip.Root>
								{:else}
									<span class="size-6 shrink-0" aria-hidden="true"></span>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<p class="text-sm text-muted-foreground">записей пробега пока нет</p>
			{/if}
		</ScrollArea>
	</div>
</div>
