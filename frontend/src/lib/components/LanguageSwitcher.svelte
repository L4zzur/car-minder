<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { i18n } from '$lib/i18n.svelte';
	import { locales, type Locale } from '$lib/paraglide/runtime';
	import { cn } from '$lib/utils';
	import Check from 'lucide-svelte/icons/check';
	import Languages from 'lucide-svelte/icons/languages';

	const labels: Record<Locale, { name: string; nativeName: string }> = {
		ru: { name: 'Russian', nativeName: 'Русский' },
		en: { name: 'English', nativeName: 'English' }
	};

	function changeLanguage(newLocale: Locale) {
		i18n.lang = newLocale;
	}
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button
				{...props}
				variant="outline"
				size="sm"
				class="gap-2 border-border/60 bg-background/50 hover:bg-accent/80 hover:text-accent-foreground backdrop-blur-sm transition-all"
			>
				<Languages data-icon="inline-start" class="text-muted-foreground" />
				<span class="font-semibold uppercase tracking-wider text-xs">{i18n.lang}</span>
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content align="end" class="w-40">
		<DropdownMenu.Group>
			{#each locales as loc (loc)}
				<DropdownMenu.Item
					class={cn(
						'flex cursor-pointer items-center justify-between rounded-sm px-3 py-2 text-sm transition-colors',
						i18n.lang === loc
							? 'bg-accent/70 font-semibold text-foreground'
							: 'text-muted-foreground hover:text-foreground'
					)}
					onclick={() => changeLanguage(loc)}
				>
					<span>{labels[loc].nativeName}</span>
					{#if i18n.lang === loc}
						<Check class="shrink-0 text-success" />
					{/if}
				</DropdownMenu.Item>
			{/each}
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>
