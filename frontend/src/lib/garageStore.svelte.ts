import {
	Cars,
	Reminders,
	ServiceItems,
	type CarRead,
	type ReminderRead,
	type ServiceItemSummary
} from "./api";

export type CarWithDetails = CarRead & {
	serviceItems?: ServiceItemSummary[];
	reminders?: ReminderRead[];
};

class GarageStore {
	cars = $state<CarWithDetails[]>([]);
	isLoading = $state(false);
	isInitialized = $state(false);

	async load(forceLoadingSkeleton = false) {
		if (forceLoadingSkeleton || !this.isInitialized) {
			this.isLoading = true;
		}

		try {
			const response = await Cars.listUserCarsApiCarsGet();
			const rawCars = response.data || [];

			this.cars = await Promise.all(
				rawCars.map(async (car) => {
					try {
						const [serviceRes, remindersRes] = await Promise.all([
							ServiceItems.listByCarApiServiceItemsGet({ query: { car_id: car.id } }),
							Reminders.listRemindersApiRemindersGet({ query: { car_id: car.id } })
						]);

						return {
							...car,
							serviceItems: serviceRes.data || [],
							reminders: remindersRes.data || []
						};
					} catch {
						return car;
					}
				})
			);
			this.isInitialized = true;
		} catch (e) {
			console.error("Failed to load cars in garageStore:", e);
		} finally {
			this.isLoading = false;
		}
	}

	invalidate() {
		return this.load(false);
	}
}

export const garageStore = new GarageStore();
