<script lang="ts">
	import { Gauge } from 'lucide-svelte';

	import { type CarRead } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import * as m from '$lib/paraglide/messages.js';

	import Input from './ui/input/input.svelte';

	let {
		car,
		mileageValue = $bindable(),
		isSaving,
		error,
		onSubmit
	}: {
		car: CarRead;
		mileageValue: number | string;
		isSaving: boolean;
		error: string;
		onSubmit: () => void;
	} = $props();

	let localError = $state();

	$effect(() => {
		if (error) localError = error;
	});

	function handleSubmit(event: Event) {
		event.preventDefault();
		localError = '';

		const val = Number(mileageValue);
		if (!Number.isFinite(val)) {
			localError = m.mileage_form_err_invalid();
			return;
		}
		if (val <= car.current_odometer_km) {
			localError = m.mileage_form_err_must_be_greater();
			return;
		}
		onSubmit();
	}
</script>

<div class="flex flex-col gap-3 rounded-lg border bg-card p-4">
	<div class="flex min-h-5 items-center justify-between gap-3">
		<h3 class="text-sm font-medium">{m.mileage_form_title()}</h3>
		{#if localError}
			<span class="text-right text-xs text-destructive">{localError}</span>
		{/if}
	</div>
	<form class="space-y-3" onsubmit={handleSubmit} novalidate>
		<div>
			<label for="odometer" class="mb-1.5 block text-xs text-muted-foreground"> {m.mileage_form_label()} </label>

			<Input type="number" bind:value={mileageValue} />
		</div>
		<Button type="submit" class="w-full" disabled={isSaving}>
			<Gauge data-icon="inline-start" />
			{isSaving ? m.mileage_form_btn_submitting() : m.mileage_form_btn_submit()}
		</Button>
	</form>
</div>
