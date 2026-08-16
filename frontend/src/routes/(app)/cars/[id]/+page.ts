import { error } from "@sveltejs/kit";

import { Cars } from "$lib/api";

import "$lib/api-client";

import * as m from "$lib/paraglide/messages.js";

import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ params }) => {
	const carId = params.id;
	if (!carId) {
		throw error(404, m.car_detail_not_found());
	}

	try {
		const res = await Cars.getCarApiCarsCarIdGet({ path: { car_id: carId } });
		if (res.error || !res.data) {
			throw error(404, m.car_detail_not_found());
		}
		return {
			car: res.data
		};
	} catch (e: unknown) {
		if (
			typeof e === "object" &&
			e !== null &&
			("status" in e || ("body" in e && typeof (e as { body: unknown }).body === "object"))
		) {
			throw e;
		}
		throw error(404, m.car_detail_not_found());
	}
};
