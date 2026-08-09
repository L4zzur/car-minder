<script lang="ts">
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Bell from '@lucide/svelte/icons/bell';
	import Shield from '@lucide/svelte/icons/shield';
	import UserIcon from '@lucide/svelte/icons/user';
	import { onMount } from 'svelte';

	import { goto } from '$app/navigation';

	import { Telegram } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Tabs from '$lib/components/ui/tabs';
	import * as m from '$lib/paraglide/messages.js';

	import NotificationsTab from './components/NotificationsTab.svelte';
	import ProfileTab from './components/ProfileTab.svelte';
	import SecurityTab from './components/SecurityTab.svelte';

	let isBotDisabled = $state(false);

	onMount(async () => {
		auth.init();
		await auth.fetchUser();

		if (!auth.isAuthenticated) {
			await goto('/login');
			return;
		}

		try {
			const webhookRes = await Telegram.getBotWebhookApiTelegramWebhookGet();
			if (webhookRes.data?.status === 'Telegram bot is disabled') {
				isBotDisabled = true;
			}
		} catch {
			// ignore check failure
		}
	});
</script>

<svelte:head>
	<title>{m.settings_title()} // car minder</title>
</svelte:head>

<div class="container mx-auto flex max-w-3xl flex-col gap-6 p-4 sm:p-6">
	<div class="flex flex-col gap-4">
		<div>
			<Button variant="ghost" size="sm" href="/home" class="-ml-2 text-muted-foreground hover:text-foreground lowercase">
				<ArrowLeft data-icon="inline-start" />
				{m.settings_back()}
			</Button>
		</div>

		<div class="flex items-center justify-between">
			<h1 class="text-3xl font-bold tracking-tight lowercase">{m.settings_title()}</h1>
			<LanguageSwitcher />
		</div>
	</div>

	<Tabs.Root value="profile" class="flex w-full flex-col gap-6">
		<Tabs.List class="grid w-full grid-cols-3 max-w-md">
			<Tabs.Trigger value="profile" class="lowercase">
				<UserIcon data-icon="inline-start" />
				{m.settings_tabs_profile()}
			</Tabs.Trigger>
			<Tabs.Trigger value="notifications" class="lowercase">
				<Bell data-icon="inline-start" />
				{m.settings_tabs_notifications()}
			</Tabs.Trigger>
			<Tabs.Trigger value="security" class="lowercase">
				<Shield data-icon="inline-start" />
				{m.settings_tabs_security()}
			</Tabs.Trigger>
		</Tabs.List>

		<Tabs.Content value="profile">
			<ProfileTab {isBotDisabled} />
		</Tabs.Content>

		<Tabs.Content value="notifications">
			<NotificationsTab />
		</Tabs.Content>

		<Tabs.Content value="security">
			<SecurityTab />
		</Tabs.Content>
	</Tabs.Root>
</div>
