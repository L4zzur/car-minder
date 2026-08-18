<script lang="ts">
	import Loader2 from '@lucide/svelte/icons/loader-2';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Save from '@lucide/svelte/icons/save';

	import { ServiceItems, type ServiceItemSummary } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Field from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import * as m from '$lib/paraglide/messages.js';

	let {
		item,
		onItemUpdated,
		child
	} = $props<{
		item: ServiceItemSummary;
		onItemUpdated: () => void;
		child?: (opts: { props: Record<string, unknown> }) => import('svelte').Snippet;
	}>();

	let open = $state(false);
	let name = $state('');
	let lastServiceAt = $state('');
	let lastOdometerKm = $state<number>(0);
	let isLoading = $state(false);
	let error = $state('');

	$effect(() => {
		if (open) {
			name = item.name;
			lastServiceAt = item.last_service_at ? item.last_service_at.slice(0, 10) : new Date().toISOString().slice(0, 10);
			lastOdometerKm = item.last_service_odometer_km;
			error = '';
		}
	});

	async function handleSubmit() {
		error = '';

		if (!name.trim()) {
			error = m.add_service_err_name_required();
			return;
		}

		if (!Number.isFinite(lastOdometerKm) || lastOdometerKm < 0) {
			error = m.add_service_err_odometer_positive();
			return;
		}

		isLoading = true;

		try {
			const response = await ServiceItems.updateServiceItemApiServiceItemsServiceItemIdPatch({
				path: { service_item_id: item.id },
				body: {
					name: name.trim(),
					last_service_at: new Date(lastServiceAt).toISOString(),
					last_service_odometer_km: lastOdometerKm
				}
			});

			if (response.error) {
				const err = response.error as any;
				error = (typeof err?.message === 'string' && err.message) || m.edit_service_err_failed();
				return;
			}

			open = false;
			onItemUpdated();
		} catch (e) {
			console.error('failed to update service item:', e);
			error = m.edit_service_err_failed();
		} finally {
			isLoading = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger>
		{#if child}
			{@render child({ props: {} })}
		{:else}
			<Button
				variant="ghost"
				size="icon"
				class="text-muted-foreground hover:text-foreground"
				aria-label={m.edit_service_edit_btn()}
			>
				<Pencil />
			</Button>
		{/if}
	</Dialog.Trigger>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title class="lowercase font-semibold">{m.edit_service_title()}</Dialog.Title>
			<Dialog.Description class="lowercase text-sm text-muted-foreground">{m.edit_service_desc()}</Dialog.Description>
		</Dialog.Header>
		<form
			class="flex flex-col gap-4"
			onsubmit={(event) => {
				event.preventDefault();
				handleSubmit();
			}}
		>
			<Field.FieldGroup class="gap-4">
				<Field.Field>
					<Field.FieldLabel for="edit-service-name" class="lowercase text-xs">{m.add_service_name_label()}</Field.FieldLabel>
					<Input id="edit-service-name" bind:value={name} placeholder={m.add_service_name_placeholder()} required />
				</Field.Field>
				<div class="grid grid-cols-2 gap-4">
					<Field.Field>
						<Field.FieldLabel for="edit-service-date" class="lowercase text-xs">{m.add_service_date_label()}</Field.FieldLabel>
						<Input id="edit-service-date" type="date" bind:value={lastServiceAt} required />
					</Field.Field>
					<Field.Field>
						<Field.FieldLabel for="edit-service-odometer" class="lowercase text-xs">{m.add_service_odometer_label()}</Field.FieldLabel>
						<Input id="edit-service-odometer" type="number" min="0" bind:value={lastOdometerKm} required />
					</Field.Field>
				</div>
			</Field.FieldGroup>

			{#if error}
				<p class="text-xs text-destructive lowercase">{error}</p>
			{/if}

			<Dialog.Footer class="pt-2">
				<Button type="submit" size="sm" class="w-full lowercase" disabled={isLoading}>
					{#if isLoading}
						<Loader2 class="animate-spin" data-icon="inline-start" />
						{m.edit_service_saving()}
					{:else}
						<Save data-icon="inline-start" />
						{m.common_save()}
					{/if}
				</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>
