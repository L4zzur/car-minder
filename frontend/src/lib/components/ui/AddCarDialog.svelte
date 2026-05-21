<script lang="ts">
	import Car from '@lucide/svelte/icons/car';
	import Plus from '@lucide/svelte/icons/plus';

	import { Cars } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';

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
			error = 'марка обязательна';
			return;
		}

		if (!model.trim()) {
			error = 'модель обязательна';
			return;
		}

		if (year < 1900 || year > getCurrentYear()) {
			error = 'некорректный год выпуска';
			return;
		}

		if (odometer < 0) {
			error = 'пробег не может быть отрицательным';
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
				error = 'не удалось добавить машину';
				return;
			}

			brand = '';
			model = '';
			year = getCurrentYear();
			odometer = 0;
			open = false;

			onCarAdded();
		} catch (e) {
			console.error('ошибка при добавлении машины:', e);
			error = 'не удалось добавить машину';
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
				<Plus class="mr-2 size-4" /> добавить авто
			</Button>
		{/if}
	</Dialog.Trigger>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>новая машина</Dialog.Title>
			<Dialog.Description>заполни данные о своём железном друге</Dialog.Description>
		</Dialog.Header>
		<form
			class="space-y-4"
			onsubmit={(e) => {
				e.preventDefault();
				handleSubmit();
			}}
		>
			<div class="space-y-2">
				<Label for="brand">марка</Label>
				<Input id="brand" bind:value={brand} placeholder="bmw" required />
			</div>
			<div class="space-y-2">
				<Label for="model">модель</Label>
				<Input id="model" bind:value={model} placeholder="m5" required />
			</div>
			<div class="grid grid-cols-2 gap-4">
				<div class="space-y-2">
					<Label for="year">год выпуска</Label>
					<Input
						id="year"
						type="number"
						bind:value={year}
						min="1900"
						max={getCurrentYear()}
						required
					/>
				</div>
				<div class="space-y-2">
					<Label for="odometer">пробег (км)</Label>
					<Input id="odometer" type="number" bind:value={odometer} min="0" required />
				</div>
			</div>
			{#if error}
				<p class="text-sm text-destructive">{error}</p>
			{/if}
			<Dialog.Footer>
				<Button type="submit" class="w-full" disabled={isLoading}>
					{isLoading ? 'сохраняем...' : 'добавить машину'}
				</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>
