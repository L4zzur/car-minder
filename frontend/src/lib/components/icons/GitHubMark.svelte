<script lang="ts">
	import type { HTMLAttributes } from "svelte/elements";

	let { class: className, ...restProps }: HTMLAttributes<HTMLSpanElement> = $props();

	const iconUrl = "https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@latest/icons/github.svg";
</script>

<span
	class={className}
	style={`display:inline-block;background-color:currentColor;mask:url('${iconUrl}') center / contain no-repeat;-webkit-mask:url('${iconUrl}') center / contain no-repeat;`}
	aria-hidden="true"
	{...restProps}
></span>
