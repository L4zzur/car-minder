<script lang="ts">
	import {
		Bell,
		CarFront,
		CodeXml,
		Contact,
		Database,
		DatabaseZap,
		ExternalLink,
		Gauge,
		Layers2,
		LayoutDashboard,
		PaintRoller,
		Server,
		Wrench
	} from 'lucide-svelte';
	import { onMount } from 'svelte';

	import { Cars, Reminders, ServiceItems, type CarRead, type ReminderRead, type ServiceItemSummary } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import CarCard from '$lib/components/CarCard.svelte';
	import GitHubMark from '$lib/components/icons/GitHubMark.svelte';
	import { Button } from '$lib/components/ui/button';
	import CarMinderLogo from '$lib/components/icons/CarMinderLogo.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import * as m from '$lib/paraglide/messages.js';
	import { buildServiceLines, getReminderMetrics, getReminderStatus } from '$lib/reminderStatus.js';

	type ServiceLine = {
		label: string;
		meta: string;
		status?: 'due' | 'soon' | 'ok';
	};

	const demoCar = {
		brand: 'Volkswagen',
		model: 'Golf',
		year: 2019,
		initial_odometer_km: 50221,
		current_odometer_km: 61107
	};

	const demoServiceLines = $derived<ServiceLine[]>([
		{ label: m.landing_demo_engine_oil(), meta: m.landing_status_in_km({ km: '1 580' }), status: 'soon' },
		{ label: m.landing_demo_brake_fluid(), meta: m.landing_status_in_days({ days: '18' }), status: 'ok' },
		{ label: m.landing_demo_air_filter(), meta: m.landing_status_serviced(), status: 'ok' }
	]);

	let displayCar = $state<any>(demoCar);
	let userServiceItems = $state<ServiceItemSummary[]>([]);
	let userReminders = $state<ReminderRead[]>([]);
	let displayHref = $state<string | undefined>(undefined);

	let displayServiceLines = $derived<ServiceLine[]>(
		userReminders.length > 0 || userServiceItems.length > 0
			? buildServiceLines(userReminders, userServiceItems, displayCar.current_odometer_km ?? displayCar.initial_odometer_km, m)
			: demoServiceLines
	);

	const highlights = $derived([
		{ icon: Gauge, label: m.landing_highlight_mileage() },
		{ icon: Wrench, label: m.landing_highlight_service() },
		{ icon: Bell, label: m.landing_highlight_reminders() }
	]);

	const technologies = [
		{ icon: Layers2, label: 'Svelte' },
		{ icon: LayoutDashboard, label: 'shadcn' },
		{ icon: PaintRoller, label: 'Tailwind' },
		{ icon: Server, label: 'FastAPI' },
		{ icon: DatabaseZap, label: 'SQLAlchemy' },
		{ icon: Database, label: 'SQLite' }
	];

	const links = $derived([
		{ icon: Contact, label: m.landing_link_author(), href: 'https://l4zzur.top' },
		{ icon: GitHubMark, label: m.landing_link_repo(), href: 'https://github.com/L4zzur/car-minder' }
	]);

	const currentYear = 2026;

	onMount(async () => {
		await auth.init();
		if (auth.isAuthenticated) {
			try {
				const carsRes = await Cars.listUserCarsApiCarsGet();
				const cars = carsRes.data || [];
				if (cars.length > 0) {
					// Pick first or random car
					const userCar = cars[Math.floor(Math.random() * cars.length)];
					displayCar = userCar;
					displayHref = `/cars/${userCar.id}`;

					const [serviceRes, remindersRes] = await Promise.all([
						ServiceItems.listByCarApiServiceItemsGet({ query: { car_id: userCar.id } }),
						Reminders.listRemindersApiRemindersGet({ query: { car_id: userCar.id } })
					]);

					userServiceItems = serviceRes.data || [];
					userReminders = remindersRes.data || [];
				}
			} catch (e) {
				console.error('Failed to load user car for landing:', e);
			}
		}
	});
</script>

<svelte:head>
	<title>car minder</title>
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
	<section class="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-8">
		<header class="flex items-center justify-between gap-4">
			<a
				class="group flex items-center gap-3 text-sm text-muted-foreground transition-colors hover:text-foreground"
				href="/"
			>
				<span class="flex size-9 items-center justify-center rounded-lg border bg-card transition-colors duration-200 group-hover:border-foreground/20 group-hover:bg-accent">
					<CarMinderLogo class="size-5" />
				</span>
				<span class="font-medium">car minder</span>
			</a>

			<nav class="flex items-center gap-2" aria-label="ссылки проекта">
				{#each links as link}
					{@const Icon = link.icon}
					<a
						class="group inline-flex h-9 items-center gap-2 rounded-lg border bg-card px-2.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
						href={link.href}
						target="_blank"
						rel="noreferrer"
					>
						<Icon class="size-4" />
						<span class="hidden sm:inline">{link.label}</span>
						<ExternalLink class="size-3 opacity-50 transition-opacity group-hover:opacity-100" />
					</a>
				{/each}
				<LanguageSwitcher />
			</nav>
		</header>

		<div class="grid flex-1 items-center gap-12 py-12 lg:grid-cols-[minmax(0,1fr)_24rem]">
			<div class="flex max-w-2xl flex-col gap-8">
				<div class="flex flex-col gap-4">
					<p class="text-sm font-medium text-muted-foreground">{m.landing_badge()}</p>
					<h1 class="text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
						{m.landing_hero_title()}
					</h1>
					<p class="max-w-xl text-base leading-7 text-muted-foreground">
						{m.landing_hero_desc()}
					</p>
				</div>

				<div class="flex flex-col gap-3 sm:flex-row">
					{#if auth.isAuthenticated}
						<Button href="/garage" size="lg">{m.landing_go_to_garage()}</Button>
						<Button href="/settings" variant="outline" size="lg">{m.landing_settings()}</Button>
					{:else}
						<Button href="/login" size="lg">{m.login_btn_submit()}</Button>
						<Button href="/register" variant="outline" size="lg">{m.register_btn_submit()}</Button>
					{/if}
				</div>

				<div class="grid max-w-xl gap-3 sm:grid-cols-3">
					{#each highlights as item}
						{@const Icon = item.icon}
						<div
							class="flex min-h-10 items-center gap-2 rounded-lg border bg-card px-3 py-2 text-sm text-muted-foreground"
						>
							<Icon class="size-4" />
							<span>{item.label}</span>
						</div>
					{/each}
				</div>

				<div class="flex max-w-xl flex-col gap-3">
					<div class="flex items-center gap-2 text-xs font-medium text-muted-foreground uppercase">
						<CodeXml class="size-3.5" />
						<span>{m.landing_stack_label()}</span>
					</div>

					<div class="flex flex-wrap gap-2">
						{#each technologies as technology}
							{@const Icon = technology.icon}
							<span
								class="inline-flex items-center gap-1.5 rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground"
							>
								<Icon class="size-3" />
								{technology.label}
							</span>
						{/each}
					</div>
				</div>
			</div>

			<div class="w-full max-w-md justify-self-start lg:justify-self-end">
				<CarCard car={displayCar} serviceLines={displayServiceLines} href={displayHref} />
			</div>
		</div>

		<footer class="flex items-center justify-between border-t pt-5 text-xs text-muted-foreground">
			<span>car minder // {currentYear}</span>
			<span>by l4zzur</span>
		</footer>
	</section>
</main>
