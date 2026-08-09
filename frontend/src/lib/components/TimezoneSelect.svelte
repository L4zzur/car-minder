<script lang="ts">
	import MapPin from '@lucide/svelte/icons/map-pin';
	import { Button } from '$lib/components/ui/button';
	import * as Select from '$lib/components/ui/select';
	import { Input } from '$lib/components/ui/input';
	import * as m from '$lib/paraglide/messages.js';

	interface Props {
		value: string;
		onchange?: (value: string) => void;
	}

	let { value = $bindable('Europe/Moscow'), onchange }: Props = $props();

	let timezones = $state<Array<{ value: string; label: string; searchStr: string }>>([]);
	let searchQuery = $state('');

	function getTimezoneOffsetString(timeZone: string): string {
		try {
			const now = new Date();
			const formatter = new Intl.DateTimeFormat('en-US', {
				timeZone,
				timeZoneName: 'shortOffset'
			});
			const parts = formatter.formatToParts(now);
			const tzPart = parts.find((p) => p.type === 'timeZoneName');
			return tzPart ? tzPart.value : '';
		} catch {
			return '';
		}
	}

	$effect(() => {
		let rawTzs: string[] = [];
		if (typeof Intl !== 'undefined' && 'supportedValuesOf' in Intl) {
			try {
				// @ts-ignore supportedValuesOf
				rawTzs = Intl.supportedValuesOf('timeZone');
			} catch {
				rawTzs = [];
			}
		}

		if (!rawTzs.length) {
			rawTzs = [
				'UTC',
				'Europe/Moscow',
				'Europe/London',
				'Europe/Paris',
				'Europe/Berlin',
				'Asia/Almaty',
				'Asia/Tashkent',
				'Asia/Tbilisi',
				'Asia/Yerevan',
				'Asia/Baku',
				'Asia/Dubai',
				'Asia/Bangkok',
				'America/New_York',
				'America/Los_Angeles'
			];
		}

		timezones = rawTzs.map((tz) => {
			const offset = getTimezoneOffsetString(tz);
			const label = offset ? `(${offset}) ${tz}` : tz;
			return {
				value: tz,
				label,
				searchStr: `${tz} ${offset}`.toLowerCase()
			};
		});
	});

	let filteredTimezones = $derived(
		searchQuery.trim() === ''
			? timezones
			: timezones.filter((t) => t.searchStr.includes(searchQuery.trim().toLowerCase()))
	);

	function detectLocalTimezone() {
		try {
			const localTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
			if (localTz) {
				value = localTz;
				if (onchange) onchange(localTz);
			}
		} catch (e) {
			console.error('Failed to detect timezone:', e);
		}
	}

	let selectedLabel = $derived(
		timezones.find((t) => t.value === value)?.label || value || m.settings_timezone_placeholder()
	);
</script>

<div class="flex items-center gap-2">
	<div class="flex-1">
		<Select.Root
			type="single"
			bind:value={value}
			onValueChange={(val) => {
				if (val && onchange) onchange(val);
			}}
		>
			<Select.Trigger id="timezone" class="w-full justify-between font-normal">
				<span class="truncate">{selectedLabel}</span>
			</Select.Trigger>
			<Select.Content class="max-h-72 w-[var(--bits-select-anchor-width)] min-w-[280px]">
				<div class="sticky top-0 z-10 bg-popover p-2">
					<Input
						type="search"
						placeholder={m.settings_timezone_search_placeholder()}
						bind:value={searchQuery}
						class="h-8 text-xs"
					/>
				</div>
				<Select.Group>
					{#if filteredTimezones.length === 0}
						<div class="p-3 text-center text-xs text-muted-foreground">{m.settings_timezone_empty()}</div>
					{:else}
						{#each filteredTimezones.slice(0, 100) as tz (tz.value)}
							<Select.Item value={tz.value} label={tz.label} class="text-xs">
								{tz.label}
							</Select.Item>
						{/each}
					{/if}
				</Select.Group>
			</Select.Content>
		</Select.Root>
	</div>

	<Button
		type="button"
		variant="outline"
		size="icon"
		onclick={detectLocalTimezone}
		title={m.settings_timezone_detect_title()}
		aria-label={m.settings_timezone_detect_aria()}
		class="shrink-0"
	>
		<MapPin class="text-muted-foreground" />
	</Button>
</div>
