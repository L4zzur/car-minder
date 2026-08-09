<script lang="ts">
	import AlertTriangle from '@lucide/svelte/icons/alert-triangle';
	import Bell from '@lucide/svelte/icons/bell';
	import Calendar from '@lucide/svelte/icons/calendar';
	import CheckCircle2 from '@lucide/svelte/icons/check-circle-2';
	import Gauge from '@lucide/svelte/icons/gauge';
	import Loader2 from '@lucide/svelte/icons/loader-2';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Plus from '@lucide/svelte/icons/plus';
	import Save from '@lucide/svelte/icons/save';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import X from '@lucide/svelte/icons/x';

	import { Reminders, type CarRead, type ReminderRead, type ServiceItemSummary } from '$lib/api';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Field from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import * as Select from '$lib/components/ui/select';
	import { Switch } from '$lib/components/ui/switch';
	import * as Tabs from '$lib/components/ui/tabs';
	import * as m from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime';
	import { getReminderMetrics, getReminderStatus } from '$lib/reminderStatus.js';

	let {
		car,
		serviceItems = [],
		targetServiceItemId = null,
		onReminderChanged,
		child,
		class: className = ''
	} = $props<{
		car: CarRead;
		serviceItems?: ServiceItemSummary[];
		targetServiceItemId?: string | null;
		onReminderChanged?: () => void;
		child?: (opts: { props: Record<string, unknown> }) => import('svelte').Snippet;
		class?: string;
	}>();

	let open = $state(false);
	let activeTab = $state('list');

	// Reminders state
	let reminders = $state<ReminderRead[]>([]);
	let isLoading = $state(true);
	let deletingId = $state<string | null>(null);

	// Edit mode state
	let editingReminderId = $state<string | null>(null);
	let editIntervalKm = $state<number | string>('');
	let editIntervalDays = $state<number | string>('');
	let editNotifyBeforeKm = $state<number | string>('');
	let editNotifyBeforeDays = $state<number | string>('');
	let editNote = $state('');
	let editIsActive = $state(true);
	let isSavingEdit = $state(false);
	let editError = $state('');

	// New reminder form state
	let selectedServiceItemId = $state<string>('');
	let intervalKm = $state<number | string>('');
	let intervalDays = $state<number | string>('');
	let notifyBeforeKm = $state<number | string>('');
	let notifyBeforeDays = $state<number | string>('');
	let note = $state('');
	let isSubmitting = $state(false);
	let formError = $state('');
	let formSuccess = $state('');

	const displayReminders = $derived.by(() => {
		if (!targetServiceItemId) return reminders;
		return reminders.filter((r) => r.service_item_id === targetServiceItemId);
	});

	const selectedServiceItemLabel = $derived.by(() => {
		if (!selectedServiceItemId) return m.reminders_dialog_select_placeholder();
		const item = serviceItems.find((s: ServiceItemSummary) => s.id === selectedServiceItemId);
		return item ? item.name.toLowerCase() : m.reminders_dialog_select_placeholder();
	});

	let wasOpen = false;
	$effect(() => {
		if (open && !wasOpen) {
			wasOpen = true;
			editingReminderId = null;
			resetForm();
			activeTab = 'list';
			loadReminders().then(() => {
				if (targetServiceItemId) {
					const existing = reminders.find((r) => r.service_item_id === targetServiceItemId);
					if (!existing) {
						activeTab = 'add';
					}
				}
			});
		} else if (!open) {
			wasOpen = false;
		}
	});

	function resetForm() {
		selectedServiceItemId = targetServiceItemId ?? serviceItems[0]?.id ?? '';
		intervalKm = '';
		intervalDays = '';
		notifyBeforeKm = '';
		notifyBeforeDays = '';
		note = '';
		formError = '';
		formSuccess = '';
	}

	async function loadReminders() {
		isLoading = true;
		try {
			const res = await Reminders.listRemindersApiRemindersGet({
				query: { car_id: car.id }
			});
			reminders = res.data ?? [];
		} catch (err) {
			console.error('failed to load reminders:', err);
		} finally {
			isLoading = false;
		}
	}

	function startEdit(reminder: ReminderRead) {
		editingReminderId = reminder.id;
		editIntervalKm = reminder.interval_km ?? '';
		editIntervalDays = reminder.interval_days ?? '';
		editNotifyBeforeKm = reminder.notify_before_km ?? '';
		editNotifyBeforeDays = reminder.notify_before_days ?? '';
		editNote = reminder.note ?? '';
		editIsActive = reminder.is_active;
		editError = '';
	}

	function cancelEdit() {
		editingReminderId = null;
		editError = '';
	}

	async function handleSaveEdit(reminderId: string) {
		editError = '';

		const intKm = editIntervalKm !== '' ? Number(editIntervalKm) : null;
		const intDays = editIntervalDays !== '' ? Number(editIntervalDays) : null;
		const notKm = editNotifyBeforeKm !== '' ? Number(editNotifyBeforeKm) : null;
		const notDays = editNotifyBeforeDays !== '' ? Number(editNotifyBeforeDays) : null;

		if ((intKm === null || isNaN(intKm)) && (intDays === null || isNaN(intDays))) {
			editError = m.reminders_dialog_err_interval_required();
			return;
		}

		isSavingEdit = true;

		try {
			const res = await Reminders.updateReminderApiRemindersReminderIdPatch({
				path: { reminder_id: reminderId },
				body: {
					is_active: editIsActive,
					interval_km: intKm,
					interval_days: intDays,
					notify_before_km: notKm,
					notify_before_days: notDays,
					note: editNote.trim() || null
				}
			});

			if (res.error) {
				const err = res.error as any;
				editError = (typeof err?.message === 'string' && err.message) || m.reminders_dialog_err_update_failed();
				return;
			}

			editingReminderId = null;
			await loadReminders();
			if (onReminderChanged) onReminderChanged();
		} catch (err) {
			console.error('failed to update reminder:', err);
			editError = m.reminders_dialog_err_update_failed();
		} finally {
			isSavingEdit = false;
		}
	}

	async function handleCreateReminder() {
		formError = '';
		formSuccess = '';

		if (!selectedServiceItemId) {
			formError = m.reminders_dialog_err_service_item_required();
			return;
		}

		const intKm = intervalKm !== '' ? Number(intervalKm) : null;
		const intDays = intervalDays !== '' ? Number(intervalDays) : null;
		const notKm = notifyBeforeKm !== '' ? Number(notifyBeforeKm) : null;
		const notDays = notifyBeforeDays !== '' ? Number(notifyBeforeDays) : null;

		if ((intKm === null || isNaN(intKm)) && (intDays === null || isNaN(intDays))) {
			formError = m.reminders_dialog_err_interval_required();
			return;
		}

		isSubmitting = true;

		try {
			const res = await Reminders.addReminderApiRemindersPost({
				body: {
					service_item_id: selectedServiceItemId,
					is_active: true,
					interval_km: intKm,
					interval_days: intDays,
					notify_before_km: notKm,
					notify_before_days: notDays,
					note: note.trim() || null
				}
			});

			if (res.error) {
				const err = res.error as any;
				formError = (typeof err?.message === 'string' && err.message) || m.reminders_dialog_err_create_failed();
				return;
			}

			formSuccess = m.reminders_dialog_created_success();
			resetForm();
			await loadReminders();
			if (onReminderChanged) onReminderChanged();
			setTimeout(() => {
				activeTab = 'list';
				formSuccess = '';
			}, 1000);
		} catch (err) {
			console.error('failed to create reminder:', err);
			formError = m.reminders_dialog_err_create_failed();
		} finally {
			isSubmitting = false;
		}
	}

	async function handleDeleteReminder(reminderId: string) {
		deletingId = reminderId;
		try {
			const res = await Reminders.deleteReminderApiRemindersReminderIdDelete({
				path: { reminder_id: reminderId }
			});

			if (!res.error) {
				await loadReminders();
				if (onReminderChanged) onReminderChanged();
			}
		} catch (err) {
			console.error('failed to delete reminder:', err);
		} finally {
			deletingId = null;
		}
	}

	function getServiceItem(itemId?: string | null) {
		if (!itemId) return null;
		return serviceItems.find((s: ServiceItemSummary) => s.id === itemId) ?? null;
	}

	const formatOdometer = (val: number) => val.toLocaleString(getLocale());

	const serviceItemName = (item: ServiceItemSummary | null) =>
		item ? item.name.toLowerCase() : m.reminders_dialog_service_item_label();
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger class={className}>
		{#if child}
			{@render child({ props: {} })}
		{:else}
			<Button variant="outline" class="w-full">
				<Bell data-icon="inline-start" /> {m.reminders_dialog_btn()}
			</Button>
		{/if}
	</Dialog.Trigger>
	<Dialog.Content class="sm:max-w-[500px]">
		<Dialog.Header>
			<Dialog.Title class="lowercase font-semibold flex items-center gap-2 text-lg">
				<Bell class="size-5 text-muted-foreground" />
				{m.reminders_dialog_title()}
			</Dialog.Title>
			<Dialog.Description class="lowercase text-sm text-muted-foreground">
				{m.reminders_dialog_desc()}
			</Dialog.Description>
		</Dialog.Header>

		<Tabs.Root bind:value={activeTab} class="flex w-full flex-col gap-4">
			<Tabs.List class="grid w-full grid-cols-2">
				<Tabs.Trigger value="list" class="lowercase">
					{m.reminders_dialog_tab_list({ count: displayReminders.length })}
				</Tabs.Trigger>
				<Tabs.Trigger value="add" class="lowercase">
					<Plus data-icon="inline-start" /> {m.reminders_dialog_tab_add()}
				</Tabs.Trigger>
			</Tabs.List>

			<!-- Tab 1: Reminders List -->
			<Tabs.Content value="list" class="flex flex-col gap-3">
				{#if isLoading}
					<div class="flex items-center justify-center p-8 text-sm text-muted-foreground">
						<Loader2 class="animate-spin" data-icon="inline-start" />
						{m.reminders_dialog_loading()}
					</div>
				{:else if displayReminders.length === 0}
					<div class="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground lowercase">
						<Bell class="size-8 text-muted-foreground/40" />
						<p class="font-medium text-sm">{m.reminders_dialog_empty_title()}</p>
						<p class="text-xs">{m.reminders_dialog_empty_desc()}</p>
					</div>
				{:else}
					<div class="flex max-h-[380px] flex-col gap-3 overflow-y-auto pr-1">
						{#each displayReminders as reminder (reminder.id)}
							{@const item = getServiceItem(reminder.service_item_id)}
							{@const metrics = getReminderMetrics(reminder, item, car.current_odometer_km)}
							{@const status = getReminderStatus(reminder, metrics)}
							<div class="flex flex-col gap-3 rounded-lg border p-4 bg-card hover:bg-accent/30 transition-colors">
								{#if editingReminderId === reminder.id}
									<!-- Inline Edit Form -->
									<div class="flex flex-col gap-3">
										<div class="flex items-center justify-between">
											<span class="text-sm font-semibold lowercase">
												{m.reminders_dialog_edit_title({ name: serviceItemName(item) })}
											</span>
											<label class="flex items-center gap-2 text-xs text-muted-foreground cursor-pointer">
												<span class="lowercase">{m.reminders_dialog_edit_active_label()}</span>
												<Switch bind:checked={editIsActive} />
											</label>
										</div>

										<div class="grid gap-3 sm:grid-cols-2">
											<Field.Field>
												<Field.FieldLabel for={`edit_int_km_${reminder.id}`} class="lowercase text-xs">{m.reminders_dialog_interval_km_label()}</Field.FieldLabel>
												<Input id={`edit_int_km_${reminder.id}`} type="number" bind:value={editIntervalKm} />
											</Field.Field>

											<Field.Field>
												<Field.FieldLabel for={`edit_int_days_${reminder.id}`} class="lowercase text-xs">{m.reminders_dialog_interval_days_label()}</Field.FieldLabel>
												<Input id={`edit_int_days_${reminder.id}`} type="number" bind:value={editIntervalDays} />
											</Field.Field>
										</div>

										<div class="grid gap-3 sm:grid-cols-2">
											<Field.Field>
												<Field.FieldLabel for={`edit_not_km_${reminder.id}`} class="lowercase text-xs">{m.reminders_dialog_alert_km_label()}</Field.FieldLabel>
												<Input id={`edit_not_km_${reminder.id}`} type="number" bind:value={editNotifyBeforeKm} />
											</Field.Field>

											<Field.Field>
												<Field.FieldLabel for={`edit_not_days_${reminder.id}`} class="lowercase text-xs">{m.reminders_dialog_alert_days_label()}</Field.FieldLabel>
												<Input id={`edit_not_days_${reminder.id}`} type="number" bind:value={editNotifyBeforeDays} />
											</Field.Field>
										</div>

										<Field.Field>
											<Field.FieldLabel for={`edit_note_${reminder.id}`} class="lowercase text-xs">{m.reminders_dialog_note_edit_label()}</Field.FieldLabel>
											<Input id={`edit_note_${reminder.id}`} type="text" bind:value={editNote} />
										</Field.Field>

										{#if editError}
											<p class="text-xs text-destructive lowercase">{editError}</p>
										{/if}

										<div class="flex items-center justify-end gap-2 pt-1">
											<Button variant="outline" size="sm" onclick={cancelEdit} class="lowercase">
												<X data-icon="inline-start" /> {m.reminders_dialog_cancel()}
											</Button>
											<Button size="sm" onclick={() => handleSaveEdit(reminder.id)} disabled={isSavingEdit} class="lowercase">
												{#if isSavingEdit}
													<Loader2 class="animate-spin" data-icon="inline-start" /> {m.reminders_dialog_saving()}
												{:else}
													<Save data-icon="inline-start" /> {m.reminders_dialog_save()}
												{/if}
											</Button>
										</div>
									</div>
								{:else}
									<!-- Card Display -->
									<div class="flex items-start justify-between gap-3">
										<div class="flex min-w-0 flex-1 flex-col gap-2">
											<div class="flex items-center gap-2 flex-wrap">
												<span class="text-sm font-semibold text-foreground lowercase truncate">
													{serviceItemName(item)}
												</span>

												{#if reminder.is_active}
													{#if status === 'due'}
														<Badge variant="destructive" class="lowercase text-xs">{m.reminders_dialog_badge_due()}</Badge>
													{:else if status === 'soon'}
														<Badge variant="outline" class="lowercase text-xs border-warning/30 bg-warning/15 text-warning">{m.reminders_dialog_badge_soon()}</Badge>
													{:else}
														<Badge variant="outline" class="lowercase text-xs border-success/30 bg-success/15 text-success">{m.reminders_dialog_active()}</Badge>
													{/if}
												{:else}
													<Badge variant="outline" class="lowercase text-xs text-muted-foreground border-dashed">{m.reminders_dialog_disabled()}</Badge>
												{/if}
											</div>

											<!-- Remaining / Until metrics -->
											<div class="flex flex-col gap-1 text-xs font-medium text-foreground/90">
												{#if metrics?.kmLeft !== null && metrics?.kmLeft !== undefined}
													<div class="flex items-center gap-1.5 flex-wrap">
														<Gauge class="size-4 text-muted-foreground shrink-0" />
														{#if metrics.kmLeft <= 0}
															<span class="text-destructive font-semibold">{m.reminders_dialog_overdue_km({ km: formatOdometer(Math.abs(metrics.kmLeft)) })}</span>
														{:else}
															<span>{m.reminders_dialog_left_km({ km: formatOdometer(metrics.kmLeft) })}</span>
														{/if}
														<span class="text-xs text-muted-foreground font-normal">
															({m.reminders_dialog_interval_km({ km: formatOdometer(reminder.interval_km!) })}{#if reminder.notify_before_km}, {m.reminders_dialog_alert_km({ km: formatOdometer(reminder.notify_before_km) })}{/if})
														</span>
													</div>
												{/if}

												{#if metrics?.daysLeft !== null && metrics?.daysLeft !== undefined}
													<div class="flex items-center gap-1.5 flex-wrap">
														<Calendar class="size-4 text-muted-foreground shrink-0" />
														{#if metrics.daysLeft <= 0}
															<span class="text-destructive font-semibold">{m.reminders_dialog_overdue_days({ days: Math.abs(metrics.daysLeft) })}</span>
														{:else}
															<span>{m.reminders_dialog_left_days({ days: metrics.daysLeft })}</span>
														{/if}
														<span class="text-xs text-muted-foreground font-normal">
															({m.reminders_dialog_interval_days({ days: reminder.interval_days! })}{#if reminder.notify_before_days}, {m.reminders_dialog_alert_days({ days: reminder.notify_before_days })}{/if})
														</span>
													</div>
												{/if}
											</div>

											{#if reminder.note}
												<p class="text-xs text-muted-foreground italic lowercase leading-relaxed pt-0.5">
													"{reminder.note}"
												</p>
											{/if}
										</div>

										<div class="flex items-center gap-1 shrink-0">
											<Button
												variant="ghost"
												size="icon"
												onclick={() => startEdit(reminder)}
												class="text-muted-foreground hover:text-foreground"
											>
												<Pencil />
											</Button>

											<Button
												variant="ghost"
												size="icon"
												onclick={() => handleDeleteReminder(reminder.id)}
												disabled={deletingId === reminder.id}
												class="text-muted-foreground hover:text-destructive hover:bg-destructive/10"
											>
												{#if deletingId === reminder.id}
													<Loader2 class="animate-spin" />
												{:else}
													<Trash2 />
												{/if}
											</Button>
										</div>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			</Tabs.Content>

			<!-- Tab 2: Add Reminder Form -->
			<Tabs.Content value="add">
				<form onsubmit={(e) => { e.preventDefault(); handleCreateReminder(); }} class="flex flex-col gap-4">
					<Field.FieldGroup class="gap-4">
						<Field.Field>
							<Field.FieldLabel for="reminder_service_item" class="lowercase text-xs font-medium">{m.reminders_dialog_service_item_label()}</Field.FieldLabel>
							{#if serviceItems.length > 0}
								<Select.Root type="single" bind:value={selectedServiceItemId}>
									<Select.Trigger id="reminder_service_item" class="w-full lowercase">
										{selectedServiceItemLabel}
									</Select.Trigger>
									<Select.Content>
										{#each serviceItems as item (item.id)}
											<Select.Item value={item.id} label={item.name.toLowerCase()} class="lowercase">
												{item.name.toLowerCase()}
											</Select.Item>
										{/each}
									</Select.Content>
								</Select.Root>
							{:else}
								<p class="text-xs text-warning">{m.reminders_dialog_service_items_missing()}</p>
							{/if}
						</Field.Field>

						<div class="grid gap-4 sm:grid-cols-2">
							<Field.Field>
								<Field.FieldLabel for="interval_km" class="lowercase text-xs font-medium">{m.reminders_dialog_interval_km_label()}</Field.FieldLabel>
								<Input
									id="interval_km"
									type="number"
									placeholder={m.reminders_dialog_interval_km_placeholder()}
									bind:value={intervalKm}
								/>
							</Field.Field>

							<Field.Field>
								<Field.FieldLabel for="interval_days" class="lowercase text-xs font-medium">{m.reminders_dialog_interval_days_label()}</Field.FieldLabel>
								<Input
									id="interval_days"
									type="number"
									placeholder={m.reminders_dialog_interval_days_placeholder()}
									bind:value={intervalDays}
								/>
							</Field.Field>
						</div>

						<div class="grid gap-4 sm:grid-cols-2">
							<Field.Field>
								<Field.FieldLabel for="notify_before_km" class="lowercase text-xs font-medium">{m.reminders_dialog_notify_km_label()}</Field.FieldLabel>
								<Input
									id="notify_before_km"
									type="number"
									placeholder={m.reminders_dialog_notify_km_placeholder()}
									bind:value={notifyBeforeKm}
								/>
							</Field.Field>

							<Field.Field>
								<Field.FieldLabel for="notify_before_days" class="lowercase text-xs font-medium">{m.reminders_dialog_notify_days_label()}</Field.FieldLabel>
								<Input
									id="notify_before_days"
									type="number"
									placeholder={m.reminders_dialog_notify_days_placeholder()}
									bind:value={notifyBeforeDays}
								/>
							</Field.Field>
						</div>

						<Field.Field>
							<Field.FieldLabel for="reminder_note" class="lowercase text-xs font-medium">{m.reminders_dialog_note_label()}</Field.FieldLabel>
							<Input
								id="reminder_note"
								type="text"
								placeholder={m.reminders_dialog_note_placeholder()}
								bind:value={note}
							/>
						</Field.Field>
					</Field.FieldGroup>

					{#if formSuccess}
						<div class="flex items-center gap-2 rounded-md bg-success/10 p-3 text-xs text-success border border-success/20 lowercase">
							<CheckCircle2 class="size-4 shrink-0" />
							{formSuccess}
						</div>
					{/if}

					{#if formError}
						<div class="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-xs text-destructive border border-destructive/20 lowercase">
							<AlertTriangle class="size-4 shrink-0" />
							{formError}
						</div>
					{/if}

					<div class="flex justify-end pt-2">
						<Button type="submit" disabled={isSubmitting || serviceItems.length === 0} size="sm" class="lowercase">
							{#if isSubmitting}
								<Loader2 class="animate-spin" data-icon="inline-start" />
								{m.reminders_dialog_saving()}
							{:else}
								<Plus data-icon="inline-start" />
								{m.reminders_dialog_create_btn()}
							{/if}
						</Button>
					</div>
				</form>
			</Tabs.Content>
		</Tabs.Root>
	</Dialog.Content>
</Dialog.Root>
