<script lang="ts">
	import {
		Bell,
		Check,
		CircleAlert,
		CircleCheck,
		Clock,
		LoaderCircle,
		Trash2
	} from "lucide-svelte";

	import type { CarRead, ServiceItemSummary } from "$lib/api";
	import { Badge } from "$lib/components/ui/badge";
	import { Button } from "$lib/components/ui/button";
	import EditServiceDialog from "$lib/components/ui/EditServiceDialog.svelte";
	import RemindersDialog from "$lib/components/ui/RemindersDialog.svelte";
	import * as Tooltip from "$lib/components/ui/tooltip";
	import * as m from "$lib/paraglide/messages.js";
	import { getLocale } from "$lib/paraglide/runtime";

	let {
		item,
		car,
		serviceItems = [],
		isSaving,
		isDeleting,
		onMarkServiced,
		onItemUpdated,
		onReminderChanged,
		onDelete
	}: {
		item: ServiceItemSummary;
		car?: CarRead;
		serviceItems?: ServiceItemSummary[];
		isSaving: boolean;
		isDeleting: boolean;
		onMarkServiced: () => void;
		onItemUpdated?: () => void;
		onReminderChanged?: () => void;
		onDelete: () => void;
	} = $props();

	const formatOdometer = (val: number) => val.toLocaleString(getLocale());
	const formatDate = (str: string) =>
		new Date(str).toLocaleDateString(getLocale(), {
			day: "numeric",
			month: "short",
			year: "numeric"
		});

	function getNextLabel() {
		if (!item.status || item.status === "ok") {
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
		{#if item.status === "due"}
			<CircleAlert class="mt-0.5 size-5 shrink-0 text-destructive" />
		{:else if item.status === "soon"}
			<Clock class="mt-0.5 size-5 shrink-0 text-warning" />
		{:else}
			<CircleCheck class="mt-0.5 size-5 shrink-0 text-muted-foreground" />
		{/if}
		<div class="flex min-w-0 flex-1 flex-col gap-1">
			<h3 class="truncate text-sm font-medium sm:text-base">{item.name}</h3>
			<div class="flex flex-wrap gap-x-1 text-xs text-muted-foreground">
				<span>{m.service_card_serviced_at({ date: formatDate(item.last_service_at) })}</span>
				<span>//</span>
				<span
					>{formatOdometer(item.last_service_odometer_km)} {m.car_card_current_odometer_km()}</span
				>
			</div>
		</div>
	</div>

	<div class="flex items-center justify-between gap-2 border-t border-border/50 pt-3">
		<div class="min-w-0 flex-1">
			<Badge
				variant={item.status === "due"
					? "destructive"
					: item.status === "soon"
						? "secondary"
						: "outline"}
				class="font-normal"
			>
				{getNextLabel()}
			</Badge>
		</div>

		<div class="flex shrink-0 items-center gap-1">
			<Tooltip.Root>
				<Tooltip.Trigger>
					<Button
						variant="ghost"
						size="sm"
						class="h-8 px-2 text-xs max-sm:size-8 max-sm:p-0"
						disabled={isSaving}
						onclick={onMarkServiced}
					>
						{#if isSaving}
							<LoaderCircle class="size-4 animate-spin sm:hidden" />
							<span class="hidden sm:inline">{m.service_card_btn_servicing()}</span>
						{:else}
							<Check class="size-4 sm:hidden" />
							<span class="hidden sm:inline">{m.service_card_btn_serviced()}</span>
						{/if}
					</Button>
				</Tooltip.Trigger>
				<Tooltip.Content><p>{m.service_card_tooltip_mark()}</p></Tooltip.Content>
			</Tooltip.Root>

			{#if car}
				<Tooltip.Root>
					<Tooltip.Trigger>
						<RemindersDialog {car} {serviceItems} targetServiceItemId={item.id} {onReminderChanged}>
							{#snippet child({ props })}
								<Button
									{...props}
									variant="ghost"
									size="icon"
									class="text-muted-foreground hover:text-foreground"
								>
									<Bell />
								</Button>
							{/snippet}
						</RemindersDialog>
					</Tooltip.Trigger>
					<Tooltip.Content><p>{m.reminders_dialog_tooltip_manage()}</p></Tooltip.Content>
				</Tooltip.Root>
			{/if}

			{#if onItemUpdated}
				<Tooltip.Root>
					<Tooltip.Trigger>
						<EditServiceDialog {item} {onItemUpdated} />
					</Tooltip.Trigger>
					<Tooltip.Content><p>{m.edit_service_edit_btn()}</p></Tooltip.Content>
				</Tooltip.Root>
			{/if}

			<Tooltip.Root>
				<Tooltip.Trigger>
					<Button
						variant="ghost"
						size="icon"
						disabled={isDeleting}
						onclick={onDelete}
						class="text-muted-foreground hover:text-destructive"
					>
						<Trash2 />
					</Button>
				</Tooltip.Trigger>
				<Tooltip.Content><p>{m.service_card_tooltip_delete()}</p></Tooltip.Content>
			</Tooltip.Root>
		</div>
	</div>
</div>
