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

	import CarCard from '$lib/components/CarCard.svelte';
	import GitHubMark from '$lib/components/icons/GitHubMark.svelte';
	import { Button } from '$lib/components/ui/button';

	const demoCar = {
		brand: 'Volkswagen',
		model: 'Golf',
		year: 2019,
		initial_odometer_km: 50221,
		current_odometer_km: 61107
	};

	const serviceLines = [
		{ label: 'масло двигателя', meta: 'через 1 580 км' },
		{ label: 'тормозная жидкость', meta: 'через 18 дней' },
		{ label: 'воздушный фильтр', meta: 'готово' }
	];

	const highlights = [
		{ icon: Gauge, label: 'пробег' },
		{ icon: Wrench, label: 'обслуживание' },
		{ icon: Bell, label: 'напоминания' }
	];

	const technologies = [
		{ icon: Layers2, label: 'Svelte' },
		{ icon: LayoutDashboard, label: 'shadcn' },
		{ icon: PaintRoller, label: 'Tailwind' },
		{ icon: Server, label: 'FastAPI' },
		{ icon: DatabaseZap, label: 'SQLAlchemy' },
		{ icon: Database, label: 'SQLite' }
	];

	const links = [
		{ icon: Contact, label: 'автор', href: 'https://l4zzur.top' },
		{ icon: GitHubMark, label: 'репо', href: 'https://github.com/L4zzur/car-minder' }
	];

	const currentYear = 2026;
</script>

<svelte:head>
	<title>car minder</title>
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
	<section class="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-8">
		<header class="flex items-center justify-between gap-4">
			<a
				class="flex items-center gap-3 text-sm text-muted-foreground transition-colors hover:text-foreground"
				href="/"
			>
				<span class="flex size-9 items-center justify-center rounded-lg border bg-card">
					<CarFront class="size-4" />
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
			</nav>
		</header>

		<div class="grid flex-1 items-center gap-12 py-12 lg:grid-cols-[minmax(0,1fr)_24rem]">
			<div class="max-w-2xl space-y-8">
				<div class="space-y-4">
					<p class="text-sm font-medium text-muted-foreground">личный журнал обслуживания</p>
					<h1 class="text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
						гараж, пробег и обслуживание в одном месте
					</h1>
					<p class="max-w-xl text-base leading-7 text-muted-foreground">
						добавляй машины, фиксируй пробег и держи рядом список работ, которые скоро потребуют
						внимания.
					</p>
				</div>

				<div class="flex flex-col gap-3 sm:flex-row">
					<Button href="/login" size="lg">войти</Button>
					<Button href="/register" variant="outline" size="lg">создать аккаунт</Button>
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

				<div class="max-w-xl space-y-3">
					<div class="flex items-center gap-2 text-xs font-medium text-muted-foreground uppercase">
						<CodeXml class="size-3.5" />
						<span>стек</span>
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
				<CarCard car={demoCar} {serviceLines} />
			</div>
		</div>

		<footer class="flex items-center justify-between border-t pt-5 text-xs text-muted-foreground">
			<span>car minder // {currentYear}</span>
			<span>by l4zzur</span>
		</footer>
	</section>
</main>
