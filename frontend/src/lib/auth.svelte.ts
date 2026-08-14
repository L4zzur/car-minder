import { Auth } from "./api";

import "./api-client";

class AuthStore {
	user = $state<any>(null);
	isReady = $state(false);

	get isAuthenticated() {
		return !!this.user;
	}

	async init() {
		if (!this.isReady) {
			this.isReady = true;
			if (!this.user) {
				await this.fetchUser();
			}
		}
	}

	async login() {
		await this.fetchUser();
	}

	async fetchUser() {
		try {
			const response = await Auth.getMeApiAuthMeGet();
			this.user = response.data;
		} catch (error) {
			console.error("Failed to fetch user data:", error);
			this.logout();
		}
	}

	logout() {
		this.user = null;
	}
}

export const auth = new AuthStore();
