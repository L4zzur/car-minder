import { client } from './api/client.gen';

client.setConfig({
	baseUrl: '',
	credentials: 'same-origin'
});

client.interceptors.response.use((response) => {
	if (response.status === 401) {
		console.warn('Unauthorized');
		if (typeof window !== 'undefined' && !['/login', '/register'].includes(window.location.pathname)) {
			window.location.href = '/login';
		}
	}
	return response;
});

export { client };
