<script lang="ts">
	import AlertTriangle from "@lucide/svelte/icons/alert-triangle";
	import CheckCircle2 from "@lucide/svelte/icons/check-circle-2";
	import ExternalLink from "@lucide/svelte/icons/external-link";
	import Loader2 from "@lucide/svelte/icons/loader-2";
	import Send from "@lucide/svelte/icons/send";
	import Unlink from "@lucide/svelte/icons/unlink";

	import { Telegram } from "$lib/api";
	import { auth } from "$lib/auth.svelte";
	import * as Alert from "$lib/components/ui/alert";
	import { Badge } from "$lib/components/ui/badge";
	import { Button } from "$lib/components/ui/button";
	import * as Card from "$lib/components/ui/card";
	import * as m from "$lib/paraglide/messages.js";

	let { isBotDisabled = false }: { isBotDisabled?: boolean } = $props();

	let isLoading = $state(false);
	let isUnlinking = $state(false);
	let errorMsg = $state("");

	async function linkTelegram() {
		errorMsg = "";
		try {
			isLoading = true;
			const res = await Telegram.getLinkTokenApiTelegramLinkTokenPost();

			if (res.error) {
				errorMsg = m.settings_telegram_link_error();
				return;
			}

			const { token, bot_username } = res.data ?? {};
			if (!bot_username) {
				isBotDisabled = true;
				return;
			}
			const url = `https://t.me/${bot_username}?start=${token}`;
			window.open(url, "_blank");

			const checkInterval = setInterval(async () => {
				await auth.fetchUser();
				if (auth.user?.telegram_id) {
					clearInterval(checkInterval);
				}
			}, 2000);

			setTimeout(() => clearInterval(checkInterval), 60000);
		} catch (err: any) {
			console.error("failed to create telegram link token:", err);
			errorMsg = m.settings_telegram_link_error();
		} finally {
			isLoading = false;
		}
	}

	async function unlinkTelegram() {
		errorMsg = "";
		try {
			isUnlinking = true;
			const res = await Telegram.unlinkTelegramApiTelegramLinkDelete();

			if (res.error) {
				errorMsg = m.settings_telegram_unlink_error();
				return;
			}

			await auth.fetchUser();
		} catch (err) {
			console.error("failed to unlink telegram:", err);
			errorMsg = m.settings_telegram_unlink_error();
		} finally {
			isUnlinking = false;
		}
	}
</script>

<div class="flex flex-col gap-6">
	<Card.Root class="w-full">
		<Card.Header>
			<Card.Title class="text-lg font-semibold lowercase"
				>{m.settings_profile_main_info()}</Card.Title
			>
		</Card.Header>
		<Card.Content>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="flex flex-col gap-1">
					<span class="text-xs text-muted-foreground lowercase">{m.settings_profile_name()}</span>
					<p class="font-medium">{auth.user?.name ?? "—"}</p>
				</div>
				<div class="flex flex-col gap-1">
					<span class="text-xs text-muted-foreground lowercase"
						>{m.settings_profile_username()}</span
					>
					<p class="font-medium">{auth.user?.username ?? "—"}</p>
				</div>
			</div>
		</Card.Content>
	</Card.Root>

	<Card.Root class="w-full">
		<Card.Header class="flex flex-row items-start justify-between">
			<div class="flex flex-col gap-1">
				<Card.Title class="flex items-center gap-2 text-lg font-semibold lowercase">
					<Send class="text-info" />
					{m.settings_telegram_title()}
				</Card.Title>
				<Card.Description class="lowercase">
					{m.settings_telegram_desc()}
				</Card.Description>
			</div>

			{#if auth.user?.telegram_id}
				<Badge variant="secondary" class="border-success/20 bg-success/10 text-success lowercase">
					<CheckCircle2 data-icon="inline-start" />
					{m.settings_telegram_linked()}
				</Badge>
			{:else if isBotDisabled}
				<Badge
					variant="outline"
					class="border-destructive/20 bg-destructive/10 text-destructive lowercase"
				>
					{m.settings_telegram_disabled()}
				</Badge>
			{:else}
				<Badge variant="outline" class="border-warning/20 bg-warning/10 text-warning lowercase">
					{m.settings_telegram_unlinked()}
				</Badge>
			{/if}
		</Card.Header>

		<Card.Content class="border-t pt-4">
			{#if errorMsg}
				<Alert.Root
					variant="destructive"
					class="mb-4 flex items-center gap-2 border-destructive/20 bg-destructive/10 text-destructive"
				>
					<AlertTriangle class="size-4 shrink-0" />
					<span class="lowercase">{errorMsg}</span>
				</Alert.Root>
			{/if}

			{#if auth.user?.telegram_id}
				<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
					<div class="text-sm text-muted-foreground lowercase">
						telegram ID: <code
							class="rounded bg-muted px-1.5 py-0.5 font-mono text-xs text-foreground"
							>{auth.user.telegram_id}</code
						>
					</div>

					<Button
						onclick={unlinkTelegram}
						disabled={isUnlinking}
						variant="outline"
						size="sm"
						class="text-destructive lowercase hover:text-destructive"
					>
						{#if isUnlinking}
							<Loader2 data-icon="inline-start" class="animate-spin" />
							{m.settings_telegram_unlinking()}
						{:else}
							<Unlink data-icon="inline-start" />
							{m.settings_telegram_unlink()}
						{/if}
					</Button>
				</div>
			{:else if isBotDisabled}
				<Alert.Root
					class="flex-col gap-2 rounded-lg border-warning/30 bg-warning/10 p-4 text-warning"
				>
					<div class="flex items-center gap-2 font-medium lowercase">
						<AlertTriangle class="size-4 shrink-0" />
						{m.settings_telegram_bot_disabled()}
					</div>
					<p class="text-xs leading-relaxed text-muted-foreground lowercase">
						для привязки аккаунта необходимо сначала задать токен бота в конфигурации приложения (<code
							class="rounded bg-muted px-1 py-0.5 font-mono text-[11px] text-foreground"
							>APP__BOT__TOKEN</code
						>) согласно документации
					</p>
				</Alert.Root>
			{:else}
				<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
					<p class="text-sm text-muted-foreground lowercase">
						{m.settings_telegram_instruction()}
					</p>

					<Button onclick={linkTelegram} disabled={isLoading} size="sm" class="lowercase">
						{#if isLoading}
							<Loader2 data-icon="inline-start" class="animate-spin" />
							{m.settings_telegram_linking()}
						{:else}
							<Send data-icon="inline-start" />
							{m.settings_telegram_link()}
							<ExternalLink data-icon="inline-end" />
						{/if}
					</Button>
				</div>
			{/if}
		</Card.Content>
	</Card.Root>
</div>
