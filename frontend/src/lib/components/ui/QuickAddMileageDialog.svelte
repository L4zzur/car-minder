<script lang="ts">
	import Plus from "@lucide/svelte/icons/plus";

	import { MileageLogs } from "$lib/api";
	import { Button } from "$lib/components/ui/button";
	import * as Dialog from "$lib/components/ui/dialog";
	import * as Field from "$lib/components/ui/field";
	import { Input } from "$lib/components/ui/input";
	import * as Tooltip from "$lib/components/ui/tooltip";
	import * as m from "$lib/paraglide/messages.js";
	import { getLocale } from "$lib/paraglide/runtime";

	let {
		carId,
		carTitle,
		currentOdometerKm,
		onMileageUpdated
	}: {
		carId: string;
		carTitle: string;
		currentOdometerKm: number;
		onMileageUpdated?: () => void;
	} = $props();

	let open = $state(false);
	let newMileage = $state<number | string>("");
	let isLoading = $state(false);
	let error = $state("");

	function handleOpen() {
		newMileage = "";
		error = "";
		open = true;
	}

	async function handleSubmit() {
		error = "";
		const numericMileage = typeof newMileage === "string" ? parseInt(newMileage, 10) : newMileage;

		if (!Number.isFinite(numericMileage) || isNaN(numericMileage)) {
			error = m.mileage_form_err_invalid();
			return;
		}

		if (numericMileage < currentOdometerKm) {
			error = m.tma_mileage_error_too_low({ km: currentOdometerKm.toLocaleString(getLocale()) });
			return;
		}

		isLoading = true;
		try {
			const res = await MileageLogs.addMileageLogApiMileageLogsPost({
				body: {
					car_id: carId,
					odometer_km: numericMileage
				}
			});

			if (res.error) {
				error = m.tma_mileage_error_save();
				return;
			}

			open = false;
			onMileageUpdated?.();
		} catch (e) {
			console.error("Failed to add mileage log:", e);
			error = m.tma_mileage_error_save();
		} finally {
			isLoading = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Tooltip.Root>
		<Tooltip.Trigger>
			<Button
				variant="outline"
				size="icon-xs"
				class="text-muted-foreground hover:bg-background hover:text-foreground"
				onclick={handleOpen}
				aria-label={m.car_card_quick_mileage_tooltip()}
			>
				<Plus />
			</Button>
		</Tooltip.Trigger>
		<Tooltip.Content side="top">
			<p>{m.car_card_quick_mileage_tooltip()}</p>
		</Tooltip.Content>
	</Tooltip.Root>

	<Dialog.Content class="sm:max-w-sm">
		<Dialog.Header>
			<Dialog.Title>{m.tma_mileage_dialog_title()}</Dialog.Title>
			<Dialog.Description class="capitalize">{carTitle.toLowerCase()}</Dialog.Description>
		</Dialog.Header>

		<form
			class="flex flex-col gap-4"
			onsubmit={(e) => {
				e.preventDefault();
				handleSubmit();
			}}
		>
			<Field.Group class="gap-3">
				<p class="text-xs text-muted-foreground">
					{m.tma_mileage_current({ km: currentOdometerKm.toLocaleString(getLocale()) })}
				</p>

				<Field.Field>
					<Field.Label for="quick-mileage-input">{m.tma_mileage_new_label()}</Field.Label>
					<Input
						id="quick-mileage-input"
						type="number"
						bind:value={newMileage}
						min={currentOdometerKm}
						placeholder={currentOdometerKm.toString()}
						required
						autofocus
					/>
				</Field.Field>

				{#if error}
					<p class="text-xs font-medium text-destructive">{error}</p>
				{/if}
			</Field.Group>

			<Dialog.Footer class="mt-2">
				<Button
					type="button"
					variant="outline"
					disabled={isLoading}
					onclick={() => (open = false)}
				>
					{m.common_cancel()}
				</Button>
				<Button type="submit" disabled={isLoading}>
					{isLoading ? m.mileage_form_btn_submitting() : m.mileage_form_btn_submit()}
				</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>
