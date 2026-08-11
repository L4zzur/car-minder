import { client } from './api/client.gen';

const csrfCookieName = 'csrf_token';
const csrfHeaderName = 'X-CSRF-Token';
const unsafeMethods = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

function readCookie(name: string) {
	if (typeof document === 'undefined') {
		return null;
	}

	const prefix = `${name}=`;
	return (
		document.cookie
			.split(';')
			.map((cookie) => cookie.trim())
			.find((cookie) => cookie.startsWith(prefix))
			?.slice(prefix.length) ?? null
	);
}

client.setConfig({
	baseUrl: '',
	credentials: 'same-origin'
});

client.interceptors.request.use((request) => {
	if (unsafeMethods.has(request.method.toUpperCase()) && !request.headers.has(csrfHeaderName)) {
		const csrfToken = readCookie(csrfCookieName);
		if (csrfToken) {
			request.headers.set(csrfHeaderName, csrfToken);
		}
	}
	return request;
});

client.interceptors.response.use((response) => {
	if (response.status === 401) {
		console.warn('Unauthorized');
		if (typeof window !== 'undefined' && !['/', '/login', '/register'].includes(window.location.pathname)) {
			window.location.href = '/login';
		}
	}
	return response;
});

export { client };
