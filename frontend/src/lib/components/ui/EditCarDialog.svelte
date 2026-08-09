<script lang="ts">
	import Loader2 from '@lucide/svelte/icons/loader-2';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Save from '@lucide/svelte/icons/save';
	import Trash2 from '@lucide/svelte/icons/trash-2';

	import { Cars, type CarRead } from '$lib/api';
	import * as AlertDialog from '$lib/components/ui/alert-dialog';
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
	let confirmDeleteOpen = $state(false);
	let error = $state('');
	let deleteError = $state('');

	$effect(() => {
		if (open) {
			brand = car.brand;
			model = car.model;
			year = car.year;
			error = '';
			deleteError = '';
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
		deleteError = '';

		try {
			const response = await Cars.deleteCarApiCarsCarIdDelete({
				path: { car_id: car.id }
			});

			if (response.error) {
				deleteError = m.edit_car_err_delete_failed();
				return;
			}

			confirmDeleteOpen = false;
			open = false;
			if (onCarDeleted) {
				onCarDeleted();
			} else {
				onCarUpdated();
			}
		} catch (e) {
			console.error('failed to delete car:', e);
			deleteError = m.edit_car_err_delete_failed();
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
					onclick={() => (confirmDeleteOpen = true)}
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
	</Dialog.Content>
</Dialog.Root>

<AlertDialog.Root bind:open={confirmDeleteOpen}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Media>
				<Trash2 />
			</AlertDialog.Media>
			<AlertDialog.Title class="lowercase">{m.edit_car_delete_confirm_title()}</AlertDialog.Title>
			<AlertDialog.Description class="lowercase leading-relaxed">
				{m.edit_car_delete_confirm_desc()}
			</AlertDialog.Description>
		</AlertDialog.Header>

		{#if deleteError}
			<p class="text-xs text-destructive lowercase">{deleteError}</p>
		{/if}

		<AlertDialog.Footer>
			<AlertDialog.Cancel size="sm" class="lowercase">{m.common_cancel()}</AlertDialog.Cancel>
			<AlertDialog.Action
				variant="destructive"
				size="sm"
				onclick={handleDelete}
				disabled={isDeleting}
				class="lowercase"
			>
				{#if isDeleting}
					<Loader2 class="animate-spin" data-icon="inline-start" />
					{m.edit_car_deleting()}
				{:else}
					<Trash2 data-icon="inline-start" />
					{m.edit_car_delete_confirm_btn()}
				{/if}
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
