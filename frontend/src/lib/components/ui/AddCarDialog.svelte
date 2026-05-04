<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Cars } from '$lib/api';
	import Plus from '@lucide/svelte/icons/plus';

	let { onCarAdded } = $props<{ onCarAdded: () => void }>();

	let open = $state(false);
	let brand = $state('');
	let model = $state('');
	let year = $state(new Date().getFullYear());
	let odometer = $state(0);
	let isLoading = $state(false);

	async function handleSubmit() {
		isLoading = true;
		try {
			await Cars.addCarApiCarsPost({
				body: {
					brand,
					model,
					year,
					initial_odometer_km: odometer
				}
			});

			brand = '';
			model = '';
			open = false;

			onCarAdded();
		} catch (e) {
			console.error('ошибка при добавлении машины:', e);
		} finally {
			isLoading = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger>
		{#snippet child({ props })}
			<Button {...props}>
				<Plus class="mr-2 h-4 w-4" /> добавить авто
			</Button>
		{/snippet}
	</Dialog.Trigger>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>новая машина</Dialog.Title>
			<Dialog.Description>заполни данные о своём железном друге</Dialog.Description>
		</Dialog.Header>
		<form
			onsubmit={(e) => {
				e.preventDefault();
				handleSubmit();
			}}
			class="space-y-4 py-4"
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
						max={new Date().getFullYear()}
						required
					/>
				</div>
				<div class="space-y-2">
					<Label for="odometer">текущий пробег (км)</Label>
					<Input id="odometer" type="number" bind:value={odometer} min="0" required />
				</div>
			</div>
			<Dialog.Footer>
				<Button type="submit" class="w-full" disabled={isLoading}>
					{isLoading ? 'сохраняем...' : 'добавить машину'}
				</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>
