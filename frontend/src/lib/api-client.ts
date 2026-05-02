import { client } from './api/client.gen';

client.setConfig({
	baseUrl: 'http://127.0.0.1:4267'
});

client.interceptors.request.use((request) => {
	const token = localStorage.getItem('access_token');
	if (token) {
		request.headers.set('Authorization', `Bearer ${token}`);
	}
	return request;
});

client.interceptors.response.use((response) => {
	if (response.status === 401) {
		console.warn('Unauthorized');
		localStorage.removeItem('access_token');
		if (typeof window !== 'undefined') {
			window.location.href = '/login';
		}
	}
	return response;
});

export { client };
