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
		logs.map((log, i) => {
			if (i === logs.length - 1) return null;
			return log.odometerKm - logs[i + 1].odometerKm;
		})
	);
</script>

<div class="flex flex-col rounded-lg border bg-card p-4">
	<div class="flex min-w-0 flex-col">
		<div class="flex items-center justify-between gap-3">
			<h3 class="text-sm font-medium">история пробега</h3>
			<span class="shrink-0 text-xs text-muted-foreground">{logs.length} записи</span>
		</div>
		<ScrollArea type="always" class="mt-4 h-[100px] pr-4">
			{#if logs.length}
				<div class="space-y-1">
					{#each logs as log, i (log.id)}
						{@const delta = deltas[i]}
						<div class="grid grid-cols-3 items-center gap-2 py-1.5 text-sm border-b border-border/20 last:border-0">
							<span class="min-w-0 text-xs text-muted-foreground truncate">{formatDate(log.createdAt)}</span>
							<span class="text-xs text-muted-foreground text-center truncate">
								{#if delta !== null}
									+{formatOdometer(Math.abs(delta))} км
								{/if}
							</span>
							<div class="flex items-center justify-end gap-1.5 text-right">
								<span class="font-medium whitespace-nowrap">{formatOdometer(log.odometerKm)} км</span>
								{#if i === 0}
									<Tooltip.Root>
										<Tooltip.Trigger>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label="удалить последнюю запись пробега"
												disabled={deletingId === log.id}
												onclick={() => onDelete(log.id)}
												class="size-6 text-muted-foreground hover:text-destructive"
											>
												<Trash2 class="size-3.5" />
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
