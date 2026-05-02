import { Auth } from './api';
import { client } from './api-client';

class AuthStore {
	user = $state<any>(null);
	token = $state<string | null>(
		typeof localStorage !== 'undefined' ? localStorage.getItem('access_token') : null
	);

	get isAuthenticated() {
		return !!this.token;
	}

	async login(newToken: string) {
		this.token = newToken;
		localStorage.setItem('access_token', newToken);
		await this.fetchUser();
	}

	async fetchUser() {
		if (!this.token) {
			return;
		}

		try {
			const response = await Auth.getMeApiAuthMeGet();
			this.user = response.data;
		} catch (error) {
			console.error('Failed to fetch user data:', error);
			this.logout();
		}
	}

	logout() {
		this.token = null;
		this.user = null;
		if (typeof localStorage !== 'undefined') {
			localStorage.removeItem('access_token');
		}
	}
}

export const auth = new AuthStore();
