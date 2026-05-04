<script lang="ts">
	import { onMount } from 'svelte';
	import { auth } from '$lib/auth.svelte';

	onMount(() => {
		auth.init();
	});

	let { children } = $props();
</script>

{@render children()}
