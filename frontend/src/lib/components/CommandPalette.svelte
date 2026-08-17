<script lang="ts">
	import Car from "@lucide/svelte/icons/car";
	import CarFront from "@lucide/svelte/icons/car-front";
	import Languages from "@lucide/svelte/icons/languages";
	import LogOut from "@lucide/svelte/icons/log-out";
	import Plus from "@lucide/svelte/icons/plus";
	import Settings from "@lucide/svelte/icons/settings";
	import SunMoon from "@lucide/svelte/icons/sun-moon";
	import { mode, resetMode, setMode } from "mode-watcher";
	import { onMount } from "svelte";

	import { goto } from "$app/navigation";
	import { page } from "$app/state";

	import { Auth, UserSettings } from "$lib/api";
	import { auth } from "$lib/auth.svelte";
	import AddCarDialog from "$lib/components/ui/AddCarDialog.svelte";
	import * as Command from "$lib/components/ui/command";
	import { garageStore } from "$lib/garageStore.svelte";
	import { i18n } from "$lib/i18n.svelte";
	import * as m from "$lib/paraglide/messages.js";
	import { locales, type Locale } from "$lib/paraglide/runtime";

	let {
		open = $bindable(false)
	}: {
		open?: boolean;
	} = $props();

	let isAddCarOpen = $state(false);

	$effect(() => {
		if (open && auth.isAuthenticated && !garageStore.isInitialized) {
			garageStore.load();
		}
	});

	function handleKeydown(e: KeyboardEvent) {
		if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) {
			e.preventDefault();
			open = !open;
		}
	}

	onMount(() => {
		window.addEventListener("keydown", handleKeydown);
		return () => {
			window.removeEventListener("keydown", handleKeydown);
		};
	});

	function runCommand(action: () => void | Promise<void>) {
		open = false;
		action();
	}

	async function toggleLanguage() {
		const nextLocale: Locale = i18n.lang === "ru" ? "en" : "ru";
		i18n.lang = nextLocale;
		if (auth.isAuthenticated) {
			try {
				await UserSettings.updateMySettingsApiUsersMeSettingsPatch({
					body: { language: nextLocale }
				});
			} catch (err) {
				console.error("Failed to sync language to backend:", err);
			}
		}
	}

	function toggleTheme() {
		if (mode.current === "dark") {
			setMode("light");
		} else {
			setMode("dark");
		}
	}

	async function handleLogout() {
		try {
			await Auth.logoutApiAuthLogoutPost();
		} catch (err) {
			console.error("Logout failed:", err);
		}
		auth.logout();
		await goto("/login");
	}
</script>

<Command.Dialog bind:open title={m.command_palette_title()} description={m.command_palette_desc()}>
	<Command.Input placeholder={m.command_palette_placeholder()} />
	<Command.List>
		<Command.Empty>{m.command_palette_empty()}</Command.Empty>

		<Command.Group heading={m.command_group_navigation()}>
			<Command.Item onSelect={() => runCommand(() => goto("/garage"))} value="garage гараж">
				<CarFront data-icon="inline-start" />
				<span>{m.command_nav_garage()}</span>
				<Command.Shortcut>G</Command.Shortcut>
			</Command.Item>

			<Command.Item onSelect={() => runCommand(() => goto("/settings"))} value="settings настройки">
				<Settings data-icon="inline-start" />
				<span>{m.command_nav_settings()}</span>
				<Command.Shortcut>S</Command.Shortcut>
			</Command.Item>
		</Command.Group>

		{#if auth.isAuthenticated}
			<Command.Separator />
			<Command.Group heading={m.command_group_actions()}>
				<Command.Item
					onSelect={() =>
						runCommand(() => {
							isAddCarOpen = true;
						})}
					value="add car добавить автомобиль машину"
				>
					<Plus data-icon="inline-start" />
					<span>{m.command_action_add_car()}</span>
				</Command.Item>
			</Command.Group>

			{#if garageStore.cars.length > 0}
				<Command.Separator />
				<Command.Group heading={m.command_group_cars()}>
					{#each garageStore.cars as car (car.id)}
						<Command.Item
							onSelect={() => runCommand(() => goto(`/cars/${car.id}`))}
							value={`${car.brand} ${car.model} ${car.year}`}
						>
							<Car data-icon="inline-start" />
							<span class="capitalize">{car.brand.toLowerCase()} {car.model.toLowerCase()}</span>
							<span class="text-xs text-muted-foreground">({car.year})</span>
						</Command.Item>
					{/each}
				</Command.Group>
			{/if}
		{/if}

		<Command.Separator />
		<Command.Group heading={m.command_group_preferences()}>
			<Command.Item
				onSelect={() => runCommand(toggleTheme)}
				value="theme light dark тема светлая темная"
			>
				<SunMoon data-icon="inline-start" />
				<span>{m.command_pref_theme()}</span>
			</Command.Item>

			<Command.Item
				onSelect={() => runCommand(toggleLanguage)}
				value="language lang язык переключить english русский"
			>
				<Languages data-icon="inline-start" />
				<span>{m.command_pref_lang()}</span>
			</Command.Item>

			{#if auth.isAuthenticated}
				<Command.Item onSelect={() => runCommand(handleLogout)} value="logout signout выйти логаут">
					<LogOut data-icon="inline-start" />
					<span>{m.command_pref_logout()}</span>
				</Command.Item>
			{/if}
		</Command.Group>
	</Command.List>
</Command.Dialog>

{#if auth.isAuthenticated}
	<AddCarDialog
		bind:open={isAddCarOpen}
		showTrigger={false}
		onCarAdded={async () => {
			await garageStore.invalidate();
			if (page.url.pathname !== "/garage") {
				await goto("/garage");
			}
		}}
	/>
{/if}
