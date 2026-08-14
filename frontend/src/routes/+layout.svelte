<script lang="ts">
	import "./(app)/layout.css";
	import "$lib/api-client";

	import { ModeWatcher } from "mode-watcher";

	import { resolve } from "$app/paths";
	import { page } from "$app/state";
	import type { Pathname } from "$app/types";

	import favicon from "$lib/assets/favicon.svg";
	import * as Tooltip from "$lib/components/ui/tooltip";
	import { locales, localizeHref } from "$lib/paraglide/runtime";

	let { children } = $props();
</script>

<ModeWatcher defaultMode="dark" />
<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div style="display:none">
	{#each locales as locale (locale)}
		<a href={resolve(localizeHref(page.url.pathname, { locale }) as Pathname)}>{locale}</a>
	{/each}
</div>

<Tooltip.Provider>
	{@render children()}
</Tooltip.Provider>
