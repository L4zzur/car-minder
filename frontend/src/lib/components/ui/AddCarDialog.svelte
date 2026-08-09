<script lang="ts">
	import Car from '@lucide/svelte/icons/car';
	import Plus from '@lucide/svelte/icons/plus';

	import { Cars } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Field from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import * as m from '$lib/paraglide/messages.js';

	let { onCarAdded, child } = $props<{
		onCarAdded: () => void;
		child?: (opts: { props: Record<string, unknown> }) => import('svelte').Snippet;
	}>();

	let open = $state(false);
	let brand = $state('');
	let model = $state('');
	let year = $state<number>(getCurrentYear());
	let odometer = $state<number>(0);
	let isLoading = $state(false);
	let error = $state('');

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

		if (odometer < 0) {
			error = m.add_car_err_odometer_negative();
			return;
		}

		isLoading = true;

		try {
			const response = await Cars.addCarApiCarsPost({
				body: {
					brand: brand.trim(),
					model: model.trim(),
					year,
					initial_odometer_km: odometer
				}
			});

			if (response.error) {
				error = m.add_car_err_failed();
				return;
			}

			brand = '';
			model = '';
			year = getCurrentYear();
			odometer = 0;
			open = false;

			onCarAdded();
		} catch (e) {
			console.error('failed to add car:', e);
			error = m.add_car_err_failed();
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
			<Button variant="outline">
				<Plus data-icon="inline-start" /> {m.add_car_btn()}
			</Button>
		{/if}
	</Dialog.Trigger>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>{m.add_car_dialog_title()}</Dialog.Title>
			<Dialog.Description>{m.add_car_dialog_desc()}</Dialog.Description>
		</Dialog.Header>
		<form
			class="flex flex-col gap-4"
			onsubmit={(e) => {
				e.preventDefault();
				handleSubmit();
			}}
		>
			<Field.Group class="gap-4">
				<Field.Field>
					<Field.Label for="brand">{m.add_car_brand_label()}</Field.Label>
					<Input id="brand" bind:value={brand} placeholder={m.add_car_brand_placeholder()} required />
				</Field.Field>
				<Field.Field>
					<Field.Label for="model">{m.add_car_model_label()}</Field.Label>
					<Input id="model" bind:value={model} placeholder={m.add_car_model_placeholder()} required />
				</Field.Field>
				<div class="grid grid-cols-2 gap-4">
					<Field.Field>
						<Field.Label for="year">{m.add_car_year_label()}</Field.Label>
						<Input
							id="year"
							type="number"
							bind:value={year}
							min="1900"
							max={getCurrentYear()}
							required
						/>
					</Field.Field>
					<Field.Field>
						<Field.Label for="odometer">{m.add_car_odometer_label()}</Field.Label>
						<Input id="odometer" type="number" bind:value={odometer} min="0" required />
					</Field.Field>
				</div>
				{#if error}
					<p class="text-sm text-destructive">{error}</p>
				{/if}
				<Dialog.Footer>
					<Button type="submit" class="w-full" disabled={isLoading}>
						{isLoading ? m.add_car_btn_submitting() : m.add_car_btn_submit()}
					</Button>
				</Dialog.Footer>
			</Field.Group>
		</form>
	</Dialog.Content>
</Dialog.Root>
