<script lang="ts">
	import "./layout.css";
	import "$lib/api-client";

	import { ModeWatcher } from "mode-watcher";

	import favicon from "$lib/assets/favicon.svg";
	import CommandPalette from "$lib/components/CommandPalette.svelte";
	import * as Tooltip from "$lib/components/ui/tooltip";

	let { children } = $props();
</script>

<ModeWatcher defaultMode="dark" />
<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<Tooltip.Provider>
	{@render children()}
	<CommandPalette />
</Tooltip.Provider>
