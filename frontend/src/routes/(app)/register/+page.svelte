<script lang="ts">
	import { onMount } from 'svelte';

	import { goto } from '$app/navigation';

	import { Auth, Users } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import * as Field from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';

	let username = $state('');
	let name = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let isLoading = $state(false);
	let isRedirecting = $state(false);
	let error = $state('');

	let passwordMismatch = $derived(
		confirmPassword.length > 0 && password !== confirmPassword
	);

	async function handleSubmit() {
		if (passwordMismatch) {
			error = 'пароли не совпадают';
			return;
		}

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

<svelte:head>
	<title>регистрация // car minder</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center py-8">
	<Card.Root class="w-[400px]">
		<Card.Header>
			<Card.Title class="text-2xl">регистрация в car minder</Card.Title>
			<Card.Description>заполни данные, чтобы начать следить за авто</Card.Description>
		</Card.Header>
		<Card.Content>
			<form
				onsubmit={(e) => {
					e.preventDefault();
					handleSubmit();
				}}
			>
				<Field.Group>
					<Field.Field data-invalid={error && error.includes('логин') ? true : undefined}>
						<Field.Label for="username">логин</Field.Label>
						<Input
							id="username"
							bind:value={username}
							placeholder="acloudyskye"
							minlength={4}
							aria-invalid={error && error.includes('логин') ? true : undefined}
							required
						/>
						<Field.Description>минимум 4 символа</Field.Description>
					</Field.Field>

					<Field.Field>
						<Field.Label for="name">твоё имя</Field.Label>
						<Input id="name" bind:value={name} placeholder="skye" required />
						<Field.Description>как к тебе обращаться в приложении</Field.Description>
					</Field.Field>

					<Field.Field data-invalid={passwordMismatch || (error && error.includes('пароль')) ? true : undefined}>
						<Field.Label for="password">пароль</Field.Label>
						<Input
							id="password"
							type="password"
							bind:value={password}
							minlength={8}
							aria-invalid={passwordMismatch || (error && error.includes('пароль')) ? true : undefined}
							required
						/>
						<Field.Description>должен быть не менее 8 символов</Field.Description>
					</Field.Field>

					<Field.Field data-invalid={passwordMismatch ? true : undefined}>
						<Field.Label for="confirm-password">повтори пароль</Field.Label>
						<Input
							id="confirm-password"
							type="password"
							bind:value={confirmPassword}
							aria-invalid={passwordMismatch}
							required
						/>
						{#if passwordMismatch}
							<Field.Error>пароли не совпадают</Field.Error>
						{:else}
							<Field.Description>подтверди свой пароль</Field.Description>
						{/if}
					</Field.Field>

					{#if error && !passwordMismatch}
						<Field.Field data-invalid>
							<Field.Error>{error}</Field.Error>
						</Field.Field>
					{/if}

					<Field.Field>
						<Button type="submit" class="w-full" disabled={isLoading || passwordMismatch}>
							{isLoading ? 'создаем...' : 'создать аккаунт'}
						</Button>
						<Field.Description class="text-center">
							уже есть аккаунт?
							<a href="/login" class="text-sidebar-primary hover:underline">войти</a>
						</Field.Description>
					</Field.Field>
				</Field.Group>
			</form>
		</Card.Content>
	</Card.Root>
</div>
