<script lang="ts">
	import { CircleAlert, CircleCheck, Clock, Trash2 } from 'lucide-svelte';

	import type { ServiceItemSummary } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import * as Tooltip from '$lib/components/ui/tooltip';

	let {
		item,
		isSaving,
		isDeleting,
		onMarkServiced,
		onDelete
	}: {
		item: ServiceItemSummary;
		isSaving: boolean;
		isDeleting: boolean;
		onMarkServiced: () => void;
		onDelete: () => void;
	} = $props();

	const formatOdometer = (val: number) => val.toLocaleString('ru-RU');
	const formatDate = (str: string) =>
		new Date(str).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' });

	function getNextLabel() {
		if (!item.status || item.status === 'ok') {
			return 'без напоминания';
		}

		const parts: string[] = [];
		if (item.km_until_due != null) {
			if (item.km_until_due <= 0) {
				parts.push(`просрочено на ${formatOdometer(Math.abs(item.km_until_due))} км`);
			} else {
				parts.push(`через ${formatOdometer(item.km_until_due)} км`);
			}
		}
		if (item.days_until_due != null) {
			if (item.days_until_due <= 0) {
				parts.push(`просрочено на ${Math.abs(item.days_until_due)} дн.`);
			} else {
				parts.push(`через ${item.days_until_due} дн.`);
			}
		}
		return parts.length > 0 ? parts[0] : 'в норме';
	}
</script>

<div class="flex items-center justify-between gap-4 rounded-lg border bg-card p-4">
	<div class="flex items-start gap-3">
		{#if item.status === 'due'}
			<CircleAlert class="mt-0.5 size-5 text-destructive" />
		{:else if item.status === 'soon'}
			<Clock class="mt-0.5 size-5 text-primary" />
		{:else}
			<CircleCheck class="mt-0.5 size-5 text-muted-foreground" />
		{/if}
		<div class="space-y-1">
			<h3 class="font-medium">{item.name}</h3>
			<div class="flex flex-wrap gap-x-1 text-xs text-muted-foreground">
				<span>обслужено: {formatDate(item.last_service_at)}</span>
				<span>//</span>
				<span>{formatOdometer(item.last_service_odometer_km)} км</span>
			</div>
		</div>
	</div>

	<div class="flex shrink-0 items-center gap-2">
		<span class="rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground">
			{getNextLabel()}
		</span>

		<Tooltip.Root>
			<Tooltip.Trigger>
				<Button variant="ghost" size="sm" disabled={isSaving} onclick={onMarkServiced}>
					{isSaving ? 'сохраняем...' : 'обслужено'}
				</Button>
			</Tooltip.Trigger>
			<Tooltip.Content><p>отметить обслуживание</p></Tooltip.Content>
		</Tooltip.Root>

		<Tooltip.Root>
			<Tooltip.Trigger>
				<Button variant="ghost" size="icon" disabled={isDeleting} onclick={onDelete}>
					<Trash2 class="size-4" />
				</Button>
			</Tooltip.Trigger>
			<Tooltip.Content><p>удалить расходник</p></Tooltip.Content>
		</Tooltip.Root>
	</div>
</div>
