<script lang="ts">
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Bell from '@lucide/svelte/icons/bell';
	import CheckCircle2 from '@lucide/svelte/icons/check-circle-2';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import Loader2 from '@lucide/svelte/icons/loader-2';
	import Send from '@lucide/svelte/icons/send';
	import Shield from '@lucide/svelte/icons/shield';
	import Unlink from '@lucide/svelte/icons/unlink';
	import UserIcon from '@lucide/svelte/icons/user';
	import { onMount } from 'svelte';

	import { goto } from '$app/navigation';

	import { Telegram } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import * as Tabs from '$lib/components/ui/tabs';

	let isLoading = $state(false);
	let isUnlinking = $state(false);

	onMount(async () => {
		auth.init();
		await auth.fetchUser();

		if (!auth.isAuthenticated) {
			await goto('/login');
		}
	});

	async function linkTelegram() {
		try {
			isLoading = true;
			const res = await Telegram.getLinkTokenApiTelegramLinkTokenPost();
			if (res.data) {
				const { token, bot_username } = res.data;
				const url = `https://t.me/${bot_username}?start=${token}`;
				window.open(url, '_blank');

				// Начинаем опрашивать профиль, пока telegram_id не появится
				const checkInterval = setInterval(async () => {
					await auth.fetchUser();
					if (auth.user?.telegram_id) {
						clearInterval(checkInterval);
					}
				}, 2000);

				// Ограничиваем время опроса (например, 1 минута)
				setTimeout(() => clearInterval(checkInterval), 60000);
			}
		} catch (err) {
			console.error('ошибка создания токена привязки:', err);
		} finally {
			isLoading = false;
		}
	}

	async function unlinkTelegram() {
		try {
			isUnlinking = true;
			await Telegram.unlinkTelegramApiTelegramLinkDelete();
			await auth.fetchUser();
		} catch (err) {
			console.error('ошибка отвязки telegram:', err);
		} finally {
			isUnlinking = false;
		}
	}
</script>

<svelte:head>
	<title>настройки // car minder</title>
</svelte:head>

<div class="container mx-auto max-w-4xl space-y-6 p-6">
	<!-- Верхняя навигация и заголовок -->
	<div class="space-y-4">
		<div>
			<Button variant="ghost" size="sm" href="/home" class="-ml-2 text-muted-foreground hover:text-foreground">
				<ArrowLeft data-icon="inline-start" />
				назад в гараж
			</Button>
		</div>

		<div class="flex items-center justify-between">
			<h1 class="text-4xl font-bold tracking-tight">настройки</h1>
		</div>
	</div>

	<!-- Вкладки shadcn-svelte -->
	<Tabs.Root value="profile" class="w-full space-y-6">
		<Tabs.List class="grid w-full grid-cols-3 max-w-md">
			<Tabs.Trigger value="profile">
				<UserIcon data-icon="inline-start" />
				профиль
			</Tabs.Trigger>
			<Tabs.Trigger value="notifications">
				<Bell data-icon="inline-start" />
				уведомления
			</Tabs.Trigger>
			<Tabs.Trigger value="security">
				<Shield data-icon="inline-start" />
				безопасность
			</Tabs.Trigger>
		</Tabs.List>

		<!-- Содержимое вкладки Профиль -->
		<Tabs.Content value="profile" class="space-y-6">
			<!-- Карточка основной информации -->
			<Card.Root>
				<Card.Header>
					<Card.Title class="text-lg">основная информация</Card.Title>
				</Card.Header>
				<Card.Content>
					<div class="grid gap-4 sm:grid-cols-2">
						<div class="flex flex-col gap-1">
							<span class="text-xs text-muted-foreground">имя</span>
							<p class="font-medium">{auth.user?.name ?? '—'}</p>
						</div>
						<div class="flex flex-col gap-1">
							<span class="text-xs text-muted-foreground">логин</span>
							<p class="font-medium">{auth.user?.username ?? '—'}</p>
						</div>
					</div>
				</Card.Content>
			</Card.Root>

			<!-- Карточка интеграции с Telegram -->
			<Card.Root>
				<Card.Header class="flex flex-row items-start justify-between space-y-0">
					<div class="flex flex-col gap-1">
						<Card.Title class="flex items-center gap-2 text-lg">
							<Send class="text-sky-500" />
							интеграция с telegram
						</Card.Title>
						<Card.Description>
							привяжи аккаунт для входа через Mini App и получения уведомлений от бота.
						</Card.Description>
					</div>

					{#if auth.user?.telegram_id}
						<Badge variant="secondary" class="border-emerald-500/20 bg-emerald-500/10 text-emerald-500">
							<CheckCircle2 data-icon="inline-start" />
							привязано
						</Badge>
					{:else}
						<Badge variant="outline" class="border-amber-500/20 bg-amber-500/10 text-amber-500">
							не привязано
						</Badge>
					{/if}
				</Card.Header>

				<Card.Content class="flex flex-col gap-4 border-t pt-4 sm:flex-row sm:items-center sm:justify-between">
					{#if auth.user?.telegram_id}
						<div class="text-sm text-muted-foreground">
							telegram ID: <code class="rounded bg-muted px-1.5 py-0.5 font-mono text-xs text-foreground">{auth.user.telegram_id}</code>
						</div>

						<Button onclick={unlinkTelegram} disabled={isUnlinking} variant="outline" size="sm" class="text-destructive hover:text-destructive">
							{#if isUnlinking}
								<Loader2 data-icon="inline-start" class="animate-spin" />
								отвязка...
							{:else}
								<Unlink data-icon="inline-start" />
								отвязать
							{/if}
						</Button>
					{:else}
						<p class="text-sm text-muted-foreground">
							нажми кнопку, чтобы перейти в бота и завершить привязку.
						</p>

						<Button onclick={linkTelegram} disabled={isLoading} size="sm">
							{#if isLoading}
								<Loader2 data-icon="inline-start" class="animate-spin" />
								генерация...
							{:else}
								<Send data-icon="inline-start" />
								привязать telegram
								<ExternalLink data-icon="inline-end" />
							{/if}
						</Button>
					{/if}
				</Card.Content>
			</Card.Root>
		</Tabs.Content>

		<!-- Уведомления -->
		<Tabs.Content value="notifications">
			<Card.Root>
				<Card.Content class="pt-6 text-sm text-muted-foreground">
					раздел уведомлений находится в разработке...
				</Card.Content>
			</Card.Root>
		</Tabs.Content>

		<!-- Безопасность -->
		<Tabs.Content value="security">
			<Card.Root>
				<Card.Content class="pt-6 text-sm text-muted-foreground">
					раздел безопасности находится в разработке...
				</Card.Content>
			</Card.Root>
		</Tabs.Content>
	</Tabs.Root>
</div>


