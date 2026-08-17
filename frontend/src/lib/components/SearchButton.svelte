<script lang="ts">
	import Search from "@lucide/svelte/icons/search";
	import { onMount } from "svelte";

	import { commandStore } from "$lib/commandStore.svelte";
	import { Button } from "$lib/components/ui/button";
	import * as Command from "$lib/components/ui/command";
	import * as m from "$lib/paraglide/messages.js";
	import { cn } from "$lib/utils";

	let { class: className }: { class?: string } = $props();

	let isMac = $state(false);

	onMount(() => {
		isMac = /(Mac|iPhone|iPod|iPad)/i.test(navigator.userAgent);
	});
</script>

<Button
	variant="outline"
	class={cn("hidden w-48 justify-between text-muted-foreground sm:inline-flex", className)}
	onclick={() => commandStore.show()}
>
	<span class="flex items-center gap-1.5">
		<Search data-icon="inline-start" />
		<span class="truncate">{m.command_palette_search()}</span>
	</span>
	<Command.Shortcut class="text-[10px]">
		{isMac ? "⌘K" : "Ctrl K"}
	</Command.Shortcut>
</Button>
