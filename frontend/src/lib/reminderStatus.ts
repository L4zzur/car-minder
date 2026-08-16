import type { ReminderRead, ServiceItemSummary } from "$lib/api";

export type ReminderMetrics = {
	kmLeft: number | null;
	daysLeft: number | null;
};

export function getReminderMetrics(
	reminder: ReminderRead,
	item: ServiceItemSummary | null,
	currentOdometerKm: number
): ReminderMetrics | null {
	if (!item) return null;

	let kmLeft: number | null = null;
	let daysLeft: number | null = null;

	if (reminder.interval_km && item.last_service_odometer_km !== undefined) {
		const dueKm = item.last_service_odometer_km + reminder.interval_km;
		kmLeft = dueKm - currentOdometerKm;
	}

	if (reminder.interval_days && item.last_service_at) {
		const lastDate = new Date(item.last_service_at).getTime();
		const dueDate = lastDate + reminder.interval_days * 86400 * 1000;
		daysLeft = Math.ceil((dueDate - Date.now()) / (86400 * 1000));
	}

	return { kmLeft, daysLeft };
}

export type ReminderStatus = "due" | "soon" | "ok";

export function getReminderStatus(
	reminder: ReminderRead,
	metrics: ReminderMetrics | null
): ReminderStatus {
	if (
		metrics &&
		((metrics.kmLeft !== null && metrics.kmLeft <= 0) ||
			(metrics.daysLeft !== null && metrics.daysLeft <= 0))
	) {
		return "due";
	}
	if (
		metrics &&
		((metrics.kmLeft !== null && metrics.kmLeft <= (reminder.notify_before_km || 500)) ||
			(metrics.daysLeft !== null && metrics.daysLeft <= (reminder.notify_before_days || 14)))
	) {
		return "soon";
	}
	return "ok";
}

export type ServiceLine = {
	label: string;
	meta: string;
	status: "due" | "soon" | "ok";
	urgencyRank: number; // Smaller means more urgent
};

export function buildServiceLines(
	reminders: ReminderRead[],
	serviceItems: ServiceItemSummary[],
	currentOdometerKm: number,
	m: Record<string, ((...args: never[]) => string) | undefined>
): ServiceLine[] {
	const lines: ServiceLine[] = [];

	for (const r of reminders) {
		if (!r.is_active) continue;
		const item = serviceItems.find((s) => s.id === r.service_item_id) || null;
		if (!item) continue;
		const metrics = getReminderMetrics(r, item, currentOdometerKm);
		const status = getReminderStatus(r, metrics);

		let meta = m.landing_status_active?.() ?? "активно";
		let urgencyRank = 999999;

		if (metrics?.kmLeft !== null && metrics?.kmLeft !== undefined) {
			urgencyRank = metrics.kmLeft;
			meta =
				metrics.kmLeft <= 0
					? (m.landing_status_due?.() ?? "просрочено")
					: (m.landing_status_in_km?.({ km: metrics.kmLeft.toLocaleString() }) ??
						`через ${metrics.kmLeft} км`);
		} else if (metrics?.daysLeft !== null && metrics?.daysLeft !== undefined) {
			urgencyRank = metrics.daysLeft * 100; // approximate weighting
			meta =
				metrics.daysLeft <= 0
					? (m.landing_status_due?.() ?? "просрочено")
					: (m.landing_status_in_days?.({ days: metrics.daysLeft.toString() }) ??
						`через ${metrics.daysLeft} дн.`);
		}

		lines.push({
			label: item.name,
			meta,
			status,
			urgencyRank
		});
	}

	// Priority sorting:
	// 1. 'due' status first
	// 2. 'soon' status second
	// 3. 'ok' status last
	// Within same status, sort by urgencyRank ascending (most urgent top)
	const statusWeight: Record<ReminderStatus, number> = {
		due: 1,
		soon: 2,
		ok: 3
	};

	lines.sort((a, b) => {
		if (statusWeight[a.status] !== statusWeight[b.status]) {
			return statusWeight[a.status] - statusWeight[b.status];
		}
		return a.urgencyRank - b.urgencyRank;
	});

	if (lines.length > 0) {
		return lines.slice(0, 3);
	}

	// Fallback if no active reminders: show up to 3 service items
	return serviceItems.slice(0, 3).map((item) => ({
		label: item.name,
		meta: m.landing_status_serviced?.() ?? "обслужено",
		status: "ok",
		urgencyRank: 999999
	}));
}
