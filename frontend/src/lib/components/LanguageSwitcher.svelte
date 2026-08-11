<script lang="ts">
	import Check from '@lucide/svelte/icons/check';
	import Languages from '@lucide/svelte/icons/languages';

	import { UserSettings } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { i18n } from '$lib/i18n.svelte';
	import { locales, type Locale } from '$lib/paraglide/runtime';
	import { cn } from '$lib/utils';

	const labels: Record<Locale, { name: string; nativeName: string }> = {
		ru: { name: 'Russian', nativeName: 'Русский' },
		en: { name: 'English', nativeName: 'English' }
	};

	async function changeLanguage(newLocale: Locale) {
		i18n.lang = newLocale;
		if (auth.isAuthenticated) {
			try {
				await UserSettings.updateMySettingsApiUsersMeSettingsPatch({
					body: { language: newLocale }
				});
			} catch (e) {
				console.error('Failed to sync language to backend:', e);
			}
		}
	}
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button
				{...props}
				variant="outline"
				size="sm"
				class="gap-1.5"
			>
				<Languages data-icon="inline-start" class="text-muted-foreground" />
				<span class="text-xs font-medium uppercase tracking-normal">{i18n.lang}</span>
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content align="end" class="w-36">
		<DropdownMenu.Group>
			{#each locales as loc (loc)}
				<DropdownMenu.Item
					class={cn(
						'flex cursor-pointer items-center justify-between rounded-sm px-2.5 py-1.5 text-xs transition-colors',
						i18n.lang === loc
							? 'bg-accent/70 font-medium text-foreground'
							: 'text-muted-foreground hover:text-foreground'
					)}
					onclick={() => changeLanguage(loc)}
				>
					<span>{labels[loc].nativeName}</span>
					{#if i18n.lang === loc}
						<Check class="shrink-0 text-primary" />
					{/if}
				</DropdownMenu.Item>
			{/each}
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>
