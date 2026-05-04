<script lang="ts">
	import { ScrollArea as ScrollAreaPrimitive } from 'bits-ui';
	import { cn } from '$lib/utils';

	let {
		orientation = 'vertical',
		class: className,
		...restProps
	}: ScrollAreaPrimitive.ScrollbarProps = $props();
</script>

<ScrollAreaPrimitive.Scrollbar
	{orientation}
	class={cn(
		'flex touch-none p-px transition-colors select-none',
		orientation === 'vertical'
			? 'h-full w-2.5 border-l border-l-transparent'
			: 'h-2.5 flex-col border-t border-t-transparent',
		className
	)}
	{...restProps}
>
	<ScrollAreaPrimitive.Thumb class="relative flex-1 rounded-full bg-border" />
</ScrollAreaPrimitive.Scrollbar>
