<script lang="ts">
	import { onMount } from 'svelte';

	import { goto } from '$app/navigation';

	import { Auth, Users } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import * as Field from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import * as m from '$lib/paraglide/messages.js';

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
	let usernameInvalid = $state(false);

	async function handleSubmit() {
		if (passwordMismatch) {
			error = m.register_error_password_mismatch();
			return;
		}

		isLoading = true;
		error = '';
		usernameInvalid = false;

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
				error = m.register_error_auto_login_failed();
				return;
			}

			if (loginResp.data?.access_token) {
				isRedirecting = true;
				await auth.login();
				await goto('/home');
				return;
			}

			error = m.register_error_auto_login_failed();
		} catch (e) {
			console.error('registration error:', e);
			error = m.register_error_generic();
		} finally {
			if (!isRedirecting) {
				isLoading = false;
			}
		}
	}

	function getRegisterError(apiError: unknown) {
		if (isApiError(apiError) && apiError.code === 'username_already_taken') {
			usernameInvalid = true;
			return m.register_error_username_taken();
		}

		return m.register_error_generic();
	}

	function isApiError(value: unknown): value is { code?: string } {
		return typeof value === 'object' && value !== null && 'code' in value;
	}

	onMount(() => auth.init());
</script>

<svelte:head>
	<title>{m.register_title()} // car minder</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center py-8">
	<Card.Root class="w-[400px]">
		<Card.Header>
			<Card.Title class="text-2xl">{m.register_heading()}</Card.Title>
			<Card.Description>{m.register_description()}</Card.Description>
		</Card.Header>
		<Card.Content>
			<form
				onsubmit={(e) => {
					e.preventDefault();
					handleSubmit();
				}}
			>
				<Field.Group class="gap-4">
					<Field.Field data-invalid={usernameInvalid}>
						<Field.Label for="username">{m.auth_username()}</Field.Label>
						<Input
							id="username"
							bind:value={username}
							placeholder="acloudyskye"
							minlength={4}
							aria-invalid={usernameInvalid}
							required
						/>
						<Field.Description>{m.register_username_hint()}</Field.Description>
					</Field.Field>

					<Field.Field>
						<Field.Label for="name">{m.register_name_label()}</Field.Label>
						<Input id="name" bind:value={name} placeholder="skye" required />
						<Field.Description>{m.register_name_hint()}</Field.Description>
					</Field.Field>

					<Field.Field data-invalid={passwordMismatch}>
						<Field.Label for="password">{m.auth_password()}</Field.Label>
						<Input
							id="password"
							type="password"
							bind:value={password}
							minlength={8}
							aria-invalid={passwordMismatch}
							required
						/>
						<Field.Description>{m.register_password_hint()}</Field.Description>
					</Field.Field>

					<Field.Field data-invalid={passwordMismatch ? true : undefined}>
						<Field.Label for="confirm-password">{m.register_confirm_password_label()}</Field.Label>
						<Input
							id="confirm-password"
							type="password"
							bind:value={confirmPassword}
							aria-invalid={passwordMismatch}
							required
						/>
						{#if passwordMismatch}
							<Field.Error>{m.register_error_password_mismatch()}</Field.Error>
						{:else}
							<Field.Description>{m.register_confirm_password_hint()}</Field.Description>
						{/if}
					</Field.Field>

					{#if error && !passwordMismatch}
						<Field.Field data-invalid>
							<Field.Error>{error}</Field.Error>
						</Field.Field>
					{/if}

					<Field.Field>
						<Button type="submit" class="w-full" disabled={isLoading || passwordMismatch}>
							{isLoading ? m.register_btn_submitting() : m.register_btn_submit()}
						</Button>
						<Field.Description class="text-center">
							{m.register_has_account()}
							<a href="/login" class="text-primary hover:underline">{m.register_link_login()}</a>
						</Field.Description>
					</Field.Field>
				</Field.Group>
			</form>
		</Card.Content>
	</Card.Root>
</div>
