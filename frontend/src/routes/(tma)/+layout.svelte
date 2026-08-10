<script lang="ts">
	import { onMount, type Snippet } from 'svelte';
	import { browser } from '$app/environment';
	import {
		init,
		miniApp,
		swipeBehavior,
		initData,
		retrieveRawInitData,
		retrieveLaunchParams
	} from '@tma.js/sdk-svelte';
	import ShieldAlert from '@lucide/svelte/icons/shield-alert';
	import Bot from '@lucide/svelte/icons/bot';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import Loader2 from '@lucide/svelte/icons/loader-2';
	import CarFront from '@lucide/svelte/icons/car-front';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';

	import { Telegram } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import favicon from '$lib/assets/favicon.svg';
	import * as m from '$lib/paraglide/messages.js';
	import '../(app)/layout.css';

	let { children }: { children: Snippet } = $props();

	let isLoading = $state(true);
	let isTelegramEnv = $state(true);
	let authError = $state<string | null>(null);
	let botUsername = $state<string | null>(null);
	let isBotDisabled = $state(false);

	const botLink = $derived(botUsername ? `https://t.me/${botUsername}` : null);

	async function fetchBotInfo() {
		try {
			const res = await Telegram.getTelegramInfoApiTelegramInfoGet();
			if (res.data) {
				isBotDisabled = !res.data.is_active;
				if (res.data.bot_username) {
					botUsername = res.data.bot_username;
				}
			}
		} catch (e) {
			console.error('Failed to fetch bot info:', e);
		}
	}

	function getInitDataRaw(): string | null {
		if (!browser) return null;

		// 1. @tma.js/sdk retrieveRawInitData()
		try {
			const raw = retrieveRawInitData();
			if (raw) return raw;
		} catch {
			// Ignore if not present in current URL
		}

		// 2. @tma.js/sdk initData.raw signal
		try {
			const raw = initData.raw();
			if (raw) return raw;
		} catch {
			// Ignore
		}

		// 3. @tma.js/sdk retrieveLaunchParams()
		try {
			const lp = retrieveLaunchParams();
			if (lp && lp.initDataRaw) {
				return typeof lp.initDataRaw === 'string' ? lp.initDataRaw : String(lp.initDataRaw);
			}
		} catch {
			// Ignore
		}

		// 4. window.Telegram.WebApp fallback
		const tg = (window as unknown as { Telegram?: { WebApp?: { initData?: string } } }).Telegram;
		if (tg?.WebApp?.initData) {
			return tg.WebApp.initData;
		}

		return null;
	}

	async function findInitDataWithRetry(): Promise<string | null> {
		for (let i = 0; i < 6; i++) {
			const data = getInitDataRaw();
			if (data) return data;
			await new Promise((resolve) => setTimeout(resolve, 100));
		}
		return null;
	}

	function setupTelegramSDK() {
		try {
			init();
		} catch {
			// init may fail if already initialized
		}

		// Restore initData component state
		try {
			initData.restore();
		} catch {
			// Ignore
		}

		// Ready miniApp
		try {
			if (miniApp.ready.isAvailable()) {
				miniApp.ready();
			}
		} catch {
			const tg = (window as unknown as { Telegram?: { WebApp?: { ready?: () => void } } }).Telegram;
			tg?.WebApp?.ready?.();
		}

		// Disable vertical swipe to close
		try {
			if (swipeBehavior.disableVertical.isAvailable()) {
				swipeBehavior.disableVertical();
			}
		} catch {
			const tg = (window as unknown as { Telegram?: { WebApp?: { disableVerticalSwipes?: () => void } } }).Telegram;
			tg?.WebApp?.disableVerticalSwipes?.();
		}
	}

	async function authenticateTelegram(initDataRaw: string) {
		try {
			const res = await Telegram.telegramAuthApiTelegramAuthPost({
				body: { init_data_raw: initDataRaw }
			});

			if (res.error) {
				authError = m.tma_auth_error_failed();
				return;
			}

			auth.init();
			await auth.login();
		} catch (e) {
			console.error('Telegram auth error:', e);
			authError = m.tma_auth_error_unknown();
		}
	}

	onMount(async () => {
		setupTelegramSDK();
		await fetchBotInfo();

		const initDataRaw = await findInitDataWithRetry();

		if (!initDataRaw) {
			isTelegramEnv = false;
			isLoading = false;
			return;
		}

		await authenticateTelegram(initDataRaw);
		isLoading = false;
	});
</script>

<svelte:head>
	<title>car minder</title>
	<link rel="icon" href={favicon} />
	<script src="https://telegram.org/js/telegram-web-app.js"></script>
</svelte:head>

<div class="min-h-screen bg-background text-foreground antialiased font-sans">
	{#if isLoading}
		<div class="flex min-h-screen flex-col items-center justify-center p-6 text-center">
			<Loader2 class="size-8 animate-spin text-muted-foreground mb-4" />
			<p class="text-sm font-medium text-muted-foreground">{m.tma_loading_init()}</p>
		</div>
	{:else if !isTelegramEnv}
		<div class="flex min-h-screen items-center justify-center p-6">
			<Card.Root class="w-full max-w-md">
				<Card.Header class="flex flex-col items-center gap-4 text-center">
					<div class="flex size-12 items-center justify-center rounded-xl border bg-card text-foreground">
						<CarFront class="size-6" />
					</div>
					<div class="flex flex-col gap-1.5">
						<Card.Title class="text-xl font-semibold tracking-tight">car minder</Card.Title>
						<Card.Description class="text-sm leading-relaxed text-muted-foreground text-balance">
							{m.tma_env_required_desc()}
						</Card.Description>
					</div>
				</Card.Header>
				<Card.Content class="flex flex-col gap-4 pt-2">
					{#if isBotDisabled}
						<div class="flex items-center gap-2.5 rounded-lg border border-warning/30 bg-warning/10 p-3.5 text-xs text-warning leading-relaxed">
							<CircleAlert class="size-4 shrink-0" />
							<span>{m.tma_bot_disabled()}</span>
						</div>
					{:else if botLink}
						<Button href={botLink} target="_blank" rel="noreferrer" size="lg" class="w-full">
							<Bot data-icon="inline-start" />
							{m.tma_open_bot({ username: botUsername ? `@${botUsername}` : '' })}
							<ExternalLink data-icon="inline-end" />
						</Button>
					{:else}
						<div class="rounded-lg border bg-muted/50 p-3 text-center text-xs text-muted-foreground">
							{m.tma_open_bot_placeholder()}
						</div>
					{/if}
				</Card.Content>
				<Card.Footer class="justify-center border-t border-border/50 pt-4 text-xs text-muted-foreground">
					<span>car minder {botUsername ? `// @${botUsername}` : ''}</span>
				</Card.Footer>
			</Card.Root>
		</div>
	{:else if authError}
		<div class="flex min-h-screen items-center justify-center p-6">
			<Card.Root class="w-full max-w-md">
				<Card.Header class="flex flex-col items-center gap-4 text-center">
					<div class="flex size-12 items-center justify-center rounded-xl border bg-card text-destructive">
						<ShieldAlert class="size-6" />
					</div>
					<div class="flex flex-col gap-1.5">
						<Card.Title class="text-xl font-semibold tracking-tight">{m.tma_auth_error_title()}</Card.Title>
						<Card.Description class="text-sm leading-relaxed text-muted-foreground text-balance">
							{authError}
						</Card.Description>
					</div>
				</Card.Header>
				<Card.Content class="flex flex-col gap-4 pt-2">
					<Button onclick={() => window.location.reload()} variant="outline" size="lg" class="w-full">
						{m.tma_auth_retry()}
					</Button>
				</Card.Content>
				<Card.Footer class="justify-center border-t border-border/50 pt-4 text-xs text-muted-foreground">
					<span>car minder {botUsername ? `// @${botUsername}` : ''}</span>
				</Card.Footer>
			</Card.Root>
		</div>
	{:else}
		<Tooltip.Provider>
			{@render children()}
		</Tooltip.Provider>
	{/if}
</div>
