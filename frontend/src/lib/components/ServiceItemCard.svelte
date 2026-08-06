<script lang="ts">
	import { CircleAlert, CircleCheck, Clock, Trash2 } from 'lucide-svelte';

	import type { ServiceItemSummary } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import * as m from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime';

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

	const formatOdometer = (val: number) => val.toLocaleString(getLocale());
	const formatDate = (str: string) =>
		new Date(str).toLocaleDateString(getLocale(), { day: 'numeric', month: 'short', year: 'numeric' });

	function getNextLabel() {
		if (!item.status || item.status === 'ok') {
			return m.service_card_no_reminder();
		}

		const parts: string[] = [];
		if (item.km_until_due != null) {
			if (item.km_until_due <= 0) {
				parts.push(m.service_card_due_km({ km: formatOdometer(Math.abs(item.km_until_due)) }));
			} else {
				parts.push(m.service_card_until_km({ km: formatOdometer(item.km_until_due) }));
			}
		}
		if (item.days_until_due != null) {
			if (item.days_until_due <= 0) {
				parts.push(m.service_card_due_days({ days: Math.abs(item.days_until_due) }));
			} else {
				parts.push(m.service_card_until_days({ days: item.days_until_due }));
			}
		}
		return parts.length > 0 ? parts[0] : m.service_card_ok();
	}
</script>

<div class="flex flex-col gap-3 rounded-lg border bg-card p-4">
	<div class="flex items-start gap-3">
		{#if item.status === 'due'}
			<CircleAlert class="mt-0.5 size-5 text-destructive shrink-0" />
		{:else if item.status === 'soon'}
			<Clock class="mt-0.5 size-5 text-primary shrink-0" />
		{:else}
			<CircleCheck class="mt-0.5 size-5 text-muted-foreground shrink-0" />
		{/if}
		<div class="space-y-1">
			<h3 class="font-medium text-sm sm:text-base">{item.name}</h3>
			<div class="flex flex-wrap gap-x-1 text-xs text-muted-foreground">
				<span>{m.service_card_serviced_at({ date: formatDate(item.last_service_at) })}</span>
				<span>//</span>
				<span>{formatOdometer(item.last_service_odometer_km)} {m.car_card_current_odometer_km()}</span>
			</div>
		</div>
	</div>

	<div class="flex items-center justify-between gap-2 border-t border-border/50 pt-3">
		<span class="rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground">
			{getNextLabel()}
		</span>

		<div class="flex items-center gap-1">
			<Tooltip.Root>
				<Tooltip.Trigger>
					<Button variant="ghost" size="sm" disabled={isSaving} onclick={onMarkServiced}>
						{isSaving ? m.service_card_btn_servicing() : m.service_card_btn_serviced()}
					</Button>
				</Tooltip.Trigger>
				<Tooltip.Content><p>{m.service_card_tooltip_mark()}</p></Tooltip.Content>
			</Tooltip.Root>

			<Tooltip.Root>
				<Tooltip.Trigger>
					<Button variant="ghost" size="icon" disabled={isDeleting} onclick={onDelete} class="text-muted-foreground hover:text-destructive">
						<Trash2 class="size-4" />
					</Button>
				</Tooltip.Trigger>
				<Tooltip.Content><p>{m.service_card_tooltip_delete()}</p></Tooltip.Content>
			</Tooltip.Root>
		</div>
	</div>
</div>
