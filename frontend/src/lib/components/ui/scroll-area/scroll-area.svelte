<script lang="ts">
	import { ScrollArea as ScrollAreaPrimitive } from 'bits-ui';
	import { cn } from '$lib/utils';
	import ScrollAreaScrollbar from './scroll-area-scrollbar.svelte';

	type Props = ScrollAreaPrimitive.RootProps & {
		class?: string;
		viewportClass?: string;
		orientation?: 'vertical' | 'horizontal' | 'both';
	};

	let {
		ref = $bindable(null),
		class: className,
		viewportClass,
		orientation = 'vertical',
		children,
		...restProps
	}: Props = $props();
</script>

<ScrollAreaPrimitive.Root
	bind:ref
	class={cn('relative overflow-hidden', className)}
	{...restProps}
>
	<ScrollAreaPrimitive.Viewport class={cn('h-full w-full rounded-[inherit]', viewportClass)}>
		{@render children?.()}
	</ScrollAreaPrimitive.Viewport>
	{#if orientation === 'vertical' || orientation === 'both'}
		<ScrollAreaScrollbar />
	{/if}
	{#if orientation === 'horizontal' || orientation === 'both'}
		<ScrollAreaScrollbar orientation="horizontal" />
	{/if}
	<ScrollAreaPrimitive.Corner />
</ScrollAreaPrimitive.Root>
