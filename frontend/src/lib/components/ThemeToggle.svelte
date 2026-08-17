<script lang="ts">
	import Moon from "@lucide/svelte/icons/moon";
	import Sun from "@lucide/svelte/icons/sun";
	import { mode, setMode } from "mode-watcher";

	import { Button } from "$lib/components/ui/button";
	import * as Tooltip from "$lib/components/ui/tooltip";
	import * as m from "$lib/paraglide/messages.js";
	import { cn } from "$lib/utils";

	let { class: className }: { class?: string } = $props();

	function toggleTheme() {
		if (mode.current === "dark") {
			setMode("light");
		} else {
			setMode("dark");
		}
	}
</script>

<Tooltip.Root>
	<Tooltip.Trigger>
		{#snippet child({ props })}
			<Button
				{...props}
				variant="outline"
				size="icon"
				class={cn("relative shrink-0", className)}
				onclick={toggleTheme}
				aria-label={m.theme_toggle()}
			>
				<Sun class="scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
				<Moon class="absolute scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
				<span class="sr-only">{m.theme_toggle()}</span>
			</Button>
		{/snippet}
	</Tooltip.Trigger>
	<Tooltip.Content side="bottom">
		<p>{m.theme_toggle()}</p>
	</Tooltip.Content>
</Tooltip.Root>
