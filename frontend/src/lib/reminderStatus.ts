import type { ReminderRead, ServiceItemSummary } from '$lib/api';

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

export type ReminderStatus = 'due' | 'soon' | 'ok';

export function getReminderStatus(reminder: ReminderRead, metrics: ReminderMetrics | null): ReminderStatus {
	if (
		metrics &&
		((metrics.kmLeft !== null && metrics.kmLeft <= 0) ||
			(metrics.daysLeft !== null && metrics.daysLeft <= 0))
	) {
		return 'due';
	}
	if (
		metrics &&
		((metrics.kmLeft !== null && metrics.kmLeft <= (reminder.notify_before_km || 500)) ||
			(metrics.daysLeft !== null && metrics.daysLeft <= (reminder.notify_before_days || 14)))
	) {
		return 'soon';
	}
	return 'ok';
}
