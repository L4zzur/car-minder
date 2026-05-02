<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { ModeWatcher } from 'mode-watcher';

	import { client } from '$lib/api/client.gen';

	client.setConfig({
		baseUrl: ''
	});

	let { children } = $props();
</script>

<ModeWatcher defaultMode="dark" />
<svelte:head><link rel="icon" href={favicon} /></svelte:head>
{@render children()}
