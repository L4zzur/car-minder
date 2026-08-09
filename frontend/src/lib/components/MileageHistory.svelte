<script lang="ts">
	import { Trash2 } from 'lucide-svelte';

	import { Button } from '$lib/components/ui/button';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import * as m from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime';

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

	const formatOdometer = (val: number) => val.toLocaleString(getLocale());
	const formatDate = (str: string) =>
		new Date(str).toLocaleDateString(getLocale(), {
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

	function getLogCountLabel(count: number) {
		if (count % 10 === 1 && count % 100 !== 11) {
			return m.mileage_history_count_one({ count });
		}
		if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) {
			return m.mileage_history_count_few({ count });
		}
		return m.mileage_history_count_other({ count });
	}
</script>

<div class="flex flex-col rounded-lg border bg-card p-4">
	<div class="flex min-w-0 flex-col">
		<div class="flex items-center justify-between gap-3">
			<h3 class="text-sm font-medium">{m.mileage_history_title()}</h3>
			<span class="shrink-0 text-xs text-muted-foreground">{getLogCountLabel(logs.length)}</span>
		</div>
		<ScrollArea type="always" class="mt-4 h-[100px] pr-4">
			{#if logs.length}
				<div class="flex flex-col gap-1">
					{#each logs as log, i (log.id)}
						{@const delta = deltas[i]}
						<div class="grid grid-cols-3 items-center gap-2 py-1.5 text-sm border-b border-border/20 last:border-0">
							<span class="min-w-0 text-xs text-muted-foreground truncate">{formatDate(log.createdAt)}</span>
							<span class="text-xs text-muted-foreground text-center truncate">
								{#if delta !== null}
									{m.mileage_history_plus_km({ km: formatOdometer(Math.abs(delta)) })}
								{/if}
							</span>
							<div class="flex items-center justify-end gap-1.5 text-right">
								<span class="font-medium whitespace-nowrap">{formatOdometer(log.odometerKm)} {m.car_card_current_odometer_km()}</span>
								{#if i === 0}
									<Tooltip.Root>
										<Tooltip.Trigger>
											<Button
												variant="ghost"
												size="icon-xs"
												aria-label={m.mileage_history_delete_aria()}
												disabled={deletingId === log.id}
												onclick={() => onDelete(log.id)}
												class="text-muted-foreground hover:text-destructive"
											>
												<Trash2 />
											</Button>
										</Tooltip.Trigger>
										<Tooltip.Content>
											<p>{m.mileage_history_delete_btn()}</p>
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
				<p class="text-sm text-muted-foreground">{m.mileage_history_empty()}</p>
			{/if}
		</ScrollArea>
	</div>
</div>
