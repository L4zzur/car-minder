<script lang="ts">
	import { Gauge } from "lucide-svelte";

	import { type CarRead } from "$lib/api";
	import { Button } from "$lib/components/ui/button";
	import * as Field from "$lib/components/ui/field";
	import { Input } from "$lib/components/ui/input";
	import * as m from "$lib/paraglide/messages.js";

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
		localError = "";

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
	<form class="flex flex-col gap-3" onsubmit={handleSubmit} novalidate>
		<Field.Field data-invalid={localError ? true : undefined}>
			<Field.Label for="odometer">{m.mileage_form_label()}</Field.Label>
			<Input
				id="odometer"
				type="number"
				bind:value={mileageValue}
				aria-invalid={localError ? true : undefined}
			/>
		</Field.Field>
		<Button type="submit" class="w-full" disabled={isSaving}>
			<Gauge data-icon="inline-start" />
			{isSaving ? m.mileage_form_btn_submitting() : m.mileage_form_btn_submit()}
		</Button>
	</form>
</div>
