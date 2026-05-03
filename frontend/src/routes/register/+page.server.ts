import { redirect } from '@sveltejs/kit';

export function load({ cookies }) {
	if (cookies.get('access_token')) {
		throw redirect(303, '/home');
	}
}
