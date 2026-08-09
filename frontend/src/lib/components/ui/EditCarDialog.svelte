<script lang="ts">
	import AlertTriangle from '@lucide/svelte/icons/alert-triangle';
	import Loader2 from '@lucide/svelte/icons/loader-2';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Save from '@lucide/svelte/icons/save';
	import Trash2 from '@lucide/svelte/icons/trash-2';

	import { Cars, type CarRead } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Field from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import * as m from '$lib/paraglide/messages.js';

	let {
		car,
		onCarUpdated,
		onCarDeleted,
		child
	} = $props<{
		car: CarRead;
		onCarUpdated: () => void;
		onCarDeleted?: () => void;
		child?: (opts: { props: Record<string, unknown> }) => import('svelte').Snippet;
	}>();

	let open = $state(false);
	let brand = $state('');
	let model = $state('');
	let year = $state<number>(1900);

	let isLoading = $state(false);
	let isDeleting = $state(false);
	let isConfirmingDelete = $state(false);
	let error = $state('');

	$effect(() => {
		if (open) {
			brand = car.brand;
			model = car.model;
			year = car.year;
			error = '';
			isConfirmingDelete = false;
		}
	});

	function getCurrentYear() {
		return new Date().getFullYear();
	}

	async function handleSubmit() {
		error = '';

		if (!brand.trim()) {
			error = m.add_car_err_brand_required();
			return;
		}

		if (!model.trim()) {
			error = m.add_car_err_model_required();
			return;
		}

		if (year < 1900 || year > getCurrentYear()) {
			error = m.add_car_err_year_invalid();
			return;
		}

		isLoading = true;

		try {
			const response = await Cars.updateCarApiCarsCarIdPatch({
				path: { car_id: car.id },
				body: {
					brand: brand.trim(),
					model: model.trim(),
					year
				}
			});

			if (response.error) {
				const err = response.error as any;
				error = (typeof err?.message === 'string' && err.message) || m.edit_car_err_update_failed();
				return;
			}

			open = false;
			onCarUpdated();
		} catch (e) {
			console.error('failed to update car:', e);
			error = m.edit_car_err_update_failed();
		} finally {
			isLoading = false;
		}
	}

	async function handleDelete() {
		isDeleting = true;
		error = '';

		try {
			const response = await Cars.deleteCarApiCarsCarIdDelete({
				path: { car_id: car.id }
			});

			if (response.error) {
				error = m.edit_car_err_delete_failed();
				return;
			}

			open = false;
			if (onCarDeleted) {
				onCarDeleted();
			} else {
				onCarUpdated();
			}
		} catch (e) {
			console.error('failed to delete car:', e);
			error = m.edit_car_err_delete_failed();
		} finally {
			isDeleting = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger>
		{#if child}
			{@render child({ props: {} })}
		{:else}
			<Button variant="outline" size="sm" class="lowercase">
				<Pencil data-icon="inline-start" /> {m.edit_car_edit_btn()}
			</Button>
		{/if}
	</Dialog.Trigger>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title class="lowercase font-semibold">{m.edit_car_title()}</Dialog.Title>
			<Dialog.Description class="lowercase">{m.edit_car_desc()}</Dialog.Description>
		</Dialog.Header>

		{#if isConfirmingDelete}
			<div class="flex flex-col gap-4 py-2">
				<div class="flex items-center gap-3 rounded-lg border border-destructive/20 bg-destructive/10 p-4 text-destructive">
					<AlertTriangle class="size-5 shrink-0" />
					<div class="flex flex-col gap-1">
						<p class="text-sm font-medium lowercase">{m.edit_car_delete_confirm_title()}</p>
						<p class="text-xs text-muted-foreground lowercase leading-relaxed">
							{m.edit_car_delete_confirm_desc()}
						</p>
					</div>
				</div>

				{#if error}
					<p class="text-xs text-destructive lowercase">{error}</p>
				{/if}

				<div class="flex items-center justify-end gap-2 pt-2">
					<Button variant="outline" size="sm" onclick={() => (isConfirmingDelete = false)} class="lowercase">
						{m.common_cancel()}
					</Button>
					<Button variant="destructive" size="sm" onclick={handleDelete} disabled={isDeleting} class="lowercase">
						{#if isDeleting}
							<Loader2 class="animate-spin" data-icon="inline-start" />
							{m.edit_car_deleting()}
						{:else}
							<Trash2 data-icon="inline-start" />
							{m.edit_car_delete_confirm_btn()}
						{/if}
					</Button>
				</div>
			</div>
		{:else}
			<form
				class="flex flex-col gap-4"
				onsubmit={(e) => {
					e.preventDefault();
					handleSubmit();
				}}
			>
				<Field.FieldGroup class="gap-4">
					<Field.Field>
						<Field.FieldLabel for="edit_brand" class="lowercase">{m.add_car_brand_label()}</Field.FieldLabel>
						<Input id="edit_brand" bind:value={brand} placeholder="BMW, Toyota..." required />
					</Field.Field>

					<Field.Field>
						<Field.FieldLabel for="edit_model" class="lowercase">{m.add_car_model_label()}</Field.FieldLabel>
						<Input id="edit_model" bind:value={model} placeholder="3 series, Camry..." required />
					</Field.Field>

					<Field.Field>
						<Field.FieldLabel for="edit_year" class="lowercase">{m.add_car_year_label()}</Field.FieldLabel>
						<Input
							id="edit_year"
							type="number"
							bind:value={year}
							min="1900"
							max={getCurrentYear()}
							required
						/>
					</Field.Field>
				</Field.FieldGroup>

				{#if error}
					<p class="text-xs text-destructive lowercase">{error}</p>
				{/if}

				<Dialog.Footer class="flex flex-col-reverse items-stretch gap-2 pt-2 sm:flex-row sm:items-center sm:justify-between">
					<Button
						type="button"
						variant="destructive"
						size="sm"
						onclick={() => (isConfirmingDelete = true)}
						class="lowercase"
					>
						<Trash2 data-icon="inline-start" />
						{m.edit_car_delete_btn()}
					</Button>

					<Button type="submit" size="sm" disabled={isLoading} class="lowercase">
						{#if isLoading}
							<Loader2 class="animate-spin" data-icon="inline-start" />
							{m.edit_car_saving()}
						{:else}
							<Save data-icon="inline-start" />
							{m.common_save()}
						{/if}
					</Button>
				</Dialog.Footer>
			</form>
		{/if}
	</Dialog.Content>
</Dialog.Root>
