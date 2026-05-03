<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Auth } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let username = $state('');
	let password = $state('');
	let isLoading = $state(false);
	let isRedirecting = $state(false);
	let error = $state('');

	async function handleSubmit() {
		isLoading = true;
		error = '';

		try {
			const response = await Auth.loginApiAuthLoginPost({
				body: {
					username,
					password
				}
			});

			if (response.error) {
				error = 'неверный логин или пароль';
				return;
			}

			if (response.data?.access_token) {
				isRedirecting = true;
				await auth.login();
				await goto('/home');
				return;
			}

			error = 'неверный логин или пароль';
		} catch (e) {
			console.error('login error:', e);
			error = 'не удалось войти. попробуй ещё раз';
		} finally {
			if (!isRedirecting) {
				isLoading = false;
			}
		}
	}

	onMount(() => auth.init());
</script>

<div class="flex h-screen items-center justify-center">
	<Card.Root class="w-[350px]">
		<Card.Header>
			<Card.Title>вход в car minder</Card.Title>
			<Card.Description>введи свои данные для доступа к гаражу</Card.Description>
		</Card.Header>
		<Card.Content>
			<form
				onsubmit={(e) => {
					e.preventDefault();
					handleSubmit();
				}}
				class="space-y-4"
			>
				<div class="space-y-2">
					<Label for="username">логин</Label>
					<Input id="username" bind:value={username} placeholder="acloudyskye" required />
				</div>
				<div class="space-y-2">
					<Label for="password">пароль</Label>
					<Input id="password" type="password" bind:value={password} required />
				</div>
				{#if error}
					<p class="text-sm text-destructive">{error}</p>
				{/if}
				<Button type="submit" class="w-full" disabled={isLoading}>
					{isLoading ? 'входим...' : 'войти'}
				</Button>
			</form>
			<div class="mt-4 text-center text-sm">
				ещё нет аккаунта?
				<a href="/register" class="text-sidebar-primary hover:underline">создать</a>
			</div>
		</Card.Content>
	</Card.Root>
</div>
