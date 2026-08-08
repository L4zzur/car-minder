<script lang="ts">
	import AlertTriangle from '@lucide/svelte/icons/alert-triangle';
	import CheckCircle2 from '@lucide/svelte/icons/check-circle-2';
	import Loader2 from '@lucide/svelte/icons/loader-2';
	import Save from '@lucide/svelte/icons/save';
	import { onMount } from 'svelte';

	import { UserSettings, type UserSettingsRead } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import * as Field from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import TimezoneSelect from '$lib/components/TimezoneSelect.svelte';
	import * as m from '$lib/paraglide/messages.js';

	let settings = $state<UserSettingsRead | null>(null);
	let isLoading = $state(true);
	let isSaving = $state(false);
	let successMsg = $state('');
	let errorMsg = $state('');

	async function loadSettings() {
		isLoading = true;
		errorMsg = '';
		try {
			const res = await UserSettings.getMySettingsApiUsersMeSettingsGet();
			if (res.data) {
				settings = res.data;
			} else if (res.error) {
				errorMsg = m.settings_notifications_load_error();
			}
		} catch (err: any) {
			console.error('failed to load settings:', err);
			errorMsg = m.settings_notifications_load_error();
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadSettings();
	});

	async function saveSettings() {
		if (!settings) return;

		isSaving = true;
		successMsg = '';
		errorMsg = '';

		try {
			const res = await UserSettings.updateMySettingsApiUsersMeSettingsPatch({
				body: {
					service_reminder_time: settings.service_reminder_time,
					mileage_reminder_time: settings.mileage_reminder_time,
					mileage_prompt_interval_days: settings.mileage_prompt_interval_days,
					timezone: settings.timezone,
					notify_via_telegram: settings.notify_via_telegram,
					notify_via_email: settings.notify_via_email,
					language: settings.language
				}
			});
			if (res.data) {
				settings = res.data;
				successMsg = m.settings_notifications_saved();
				setTimeout(() => (successMsg = ''), 3000);
			} else {
				errorMsg = m.settings_notifications_save_error();
			}
		} catch (err: any) {
			console.error('failed to save settings:', err);
			errorMsg = err?.body?.detail || m.settings_notifications_save_error();
		} finally {
			isSaving = false;
		}
	}
</script>

<div class="w-full">
	<Card.Root class="w-full">
		<Card.Header>
			<Card.Title class="text-lg font-semibold lowercase">{m.settings_notifications_title()}</Card.Title>
			<Card.Description class="lowercase">{m.settings_notifications_desc()}</Card.Description>
		</Card.Header>
		<Card.Content>
			{#if isLoading}
				<div class="flex items-center justify-center p-8 text-sm text-muted-foreground">
					<Loader2 class="animate-spin" data-icon="inline-start" />
					{m.settings_notifications_loading()}
				</div>
			{:else if settings}
				<form onsubmit={(e) => { e.preventDefault(); saveSettings(); }} class="space-y-4">
					<Field.FieldGroup class="gap-4">
						<!-- Tab 1: Time inputs -->
						<div class="grid gap-4 sm:grid-cols-2">
							<Field.Field>
								<Field.FieldLabel for="service_reminder_time" class="lowercase">{m.settings_notifications_service_time_label()}</Field.FieldLabel>
								<Input
									id="service_reminder_time"
									type="time"
									step="60"
									bind:value={settings.service_reminder_time}
									class="appearance-none bg-background [&::-webkit-calendar-picker-indicator]:hidden [&::-webkit-calendar-picker-indicator]:appearance-none"
								/>
								<Field.FieldDescription class="lowercase">{m.settings_notifications_service_time_desc()}</Field.FieldDescription>
							</Field.Field>

							<Field.Field>
								<Field.FieldLabel for="mileage_reminder_time" class="lowercase">{m.settings_notifications_mileage_time_label()}</Field.FieldLabel>
								<Input
									id="mileage_reminder_time"
									type="time"
									step="60"
									bind:value={settings.mileage_reminder_time}
									class="appearance-none bg-background [&::-webkit-calendar-picker-indicator]:hidden [&::-webkit-calendar-picker-indicator]:appearance-none"
								/>
								<Field.FieldDescription class="lowercase">{m.settings_notifications_mileage_time_desc()}</Field.FieldDescription>
							</Field.Field>
						</div>

						<!-- Tab 2: Intervals and Timezone -->
						<div class="grid gap-4 sm:grid-cols-2">
							<Field.Field>
								<Field.FieldLabel for="mileage_prompt_interval_days" class="lowercase">{m.settings_notifications_interval_label()}</Field.FieldLabel>
								<Input
									id="mileage_prompt_interval_days"
									type="number"
									min="1"
									max="365"
									bind:value={settings.mileage_prompt_interval_days}
								/>
								<Field.FieldDescription class="lowercase">{m.settings_notifications_interval_desc()}</Field.FieldDescription>
							</Field.Field>

							<Field.Field>
								<Field.FieldLabel for="timezone" class="lowercase">{m.settings_notifications_timezone_label()}</Field.FieldLabel>
								<TimezoneSelect bind:value={settings.timezone} />
								<Field.FieldDescription class="lowercase">{m.settings_notifications_timezone_desc()}</Field.FieldDescription>
							</Field.Field>
						</div>

						<!-- Tab 3: Notification Channels -->
						<div class="flex flex-col gap-3">
							<span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{m.settings_notifications_channels_heading()}</span>

							<div class="grid gap-3 sm:grid-cols-2">
								<Label
									class="flex items-start gap-3 rounded-lg border p-3.5 hover:bg-accent/50 cursor-pointer has-[[aria-checked=true]]:border-primary has-[[aria-checked=true]]:bg-primary/5 transition-colors"
								>
									<Checkbox
										id="notify_telegram"
										bind:checked={settings.notify_via_telegram}
										class="mt-0.5"
									/>
									<div class="grid gap-1 font-normal">
										<p class="text-sm font-medium leading-none lowercase">{m.settings_notifications_telegram_title()}</p>
										<p class="text-xs text-muted-foreground lowercase">
											{m.settings_notifications_telegram_desc()}
										</p>
									</div>
								</Label>

								<Label
									class="flex items-start gap-3 rounded-lg border p-3.5 hover:bg-accent/50 cursor-pointer has-[[aria-checked=true]]:border-primary has-[[aria-checked=true]]:bg-primary/5 transition-colors"
								>
									<Checkbox
										id="notify_email"
										bind:checked={settings.notify_via_email}
										class="mt-0.5"
									/>
									<div class="grid gap-1 font-normal">
										<p class="text-sm font-medium leading-none lowercase">{m.settings_notifications_email_title()}</p>
										<p class="text-xs text-muted-foreground lowercase">
											{m.settings_notifications_email_desc()}
										</p>
									</div>
								</Label>
							</div>
						</div>
					</Field.FieldGroup>

					{#if successMsg}
						<div class="flex items-center gap-2 rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-500 border border-emerald-500/20 lowercase">
							<CheckCircle2 class="size-4 shrink-0" />
							{successMsg}
						</div>
					{/if}

					{#if errorMsg}
						<div class="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive border border-destructive/20 lowercase">
							<AlertTriangle class="size-4 shrink-0" />
							{errorMsg}
						</div>
					{/if}

					<div class="flex justify-end">
						<Button type="submit" disabled={isSaving} size="sm" class="lowercase">
							{#if isSaving}
								<Loader2 class="animate-spin" data-icon="inline-start" />
								{m.settings_notifications_saving()}
							{:else}
								<Save data-icon="inline-start" />
								{m.settings_notifications_save()}
							{/if}
						</Button>
					</div>
				</form>
			{:else}
				<div class="flex flex-col items-center justify-center gap-4 p-8 text-center text-sm text-muted-foreground lowercase">
					<p>{errorMsg || m.settings_notifications_load_error()}</p>
					<Button variant="outline" size="sm" onclick={loadSettings} class="lowercase">
						{m.settings_notifications_retry()}
					</Button>
				</div>
			{/if}
		</Card.Content>
	</Card.Root>
</div>
