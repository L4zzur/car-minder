<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Users, Auth } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let username = $state('');
	let name = $state('');
	let password = $state('');
	let isLoading = $state(false);
	let isRedirecting = $state(false);
	let error = $state('');

	async function handleSubmit() {
		isLoading = true;
		error = '';

		try {
			const registerResp = await Users.registerUserApiUsersPost({
				body: {
					username,
					name,
					password
				}
			});

			if (registerResp.error) {
				error = getRegisterError(registerResp.error);
				return;
			}

			const loginResp = await Auth.loginApiAuthLoginPost({
				body: {
					username,
					password
				}
			});

			if (loginResp.error) {
				error = 'аккаунт создан, но не удалось войти автоматически';
				return;
			}

			if (loginResp.data?.access_token) {
				isRedirecting = true;
				await auth.login();
				await goto('/home');
				return;
			}

			error = 'аккаунт создан, но не удалось войти автоматически';
		} catch (e) {
			console.error('registration error:', e);
			error = 'не удалось создать аккаунт. попробуй ещё раз';
		} finally {
			if (!isRedirecting) {
				isLoading = false;
			}
		}
	}

	function getRegisterError(apiError: unknown) {
		if (isApiError(apiError) && apiError.code === 'username_already_taken') {
			return 'логин уже занят';
		}

		return 'не удалось создать аккаунт. проверь данные и попробуй ещё раз';
	}

	function isApiError(value: unknown): value is { code?: string } {
		return typeof value === 'object' && value !== null && 'code' in value;
	}

	onMount(() => auth.init());
</script>

<div class="flex h-screen items-center justify-center">
	<Card.Root class="w-[400px]">
		<Card.Header>
			<Card.Title>регистрация в car minder</Card.Title>
			<Card.Description>создай аккаунт, чтобы начать следить за авто</Card.Description>
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
					<Label for="username">логин (хотя бы 4 символа)</Label>
					<Input
						id="username"
						bind:value={username}
						placeholder="acloudyskye"
						minlength={4}
						required
					/>
				</div>
				<div class="space-y-2">
					<Label for="name">твоё имя</Label>
					<Input id="name" bind:value={name} placeholder="skye" required />
				</div>
				<div class="space-y-2">
					<Label for="password">пароль (минимум 8 символов)</Label>
					<Input id="password" type="password" bind:value={password} minlength={8} required />
				</div>

				{#if error}
					<p class="text-sm text-destructive">{error}</p>
				{/if}

				<Button type="submit" class="w-full" disabled={isLoading}>
					{isLoading ? 'создаем...' : 'создать аккаунт'}
				</Button>
			</form>
			<div class="mt-4 text-center text-sm">
				уже есть аккаунт?
				<a href="/login" class="text-sidebar-primary hover:underline">войти</a>
			</div>
		</Card.Content>
	</Card.Root>
</div>
