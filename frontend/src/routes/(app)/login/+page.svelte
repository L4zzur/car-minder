<script lang="ts">
	import { onMount } from 'svelte';

	import { goto } from '$app/navigation';

	import { Auth } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import * as Field from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import * as m from '$lib/paraglide/messages.js';

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
				error = m.auth_error_invalid_credentials();
				return;
			}

			if (response.data?.access_token) {
				isRedirecting = true;
				await auth.login();
				await goto('/home');
				return;
			}

			error = m.auth_error_invalid_credentials();
		} catch (e) {
			console.error('login error:', e);
			error = m.auth_error_login_failed();
		} finally {
			if (!isRedirecting) {
				isLoading = false;
			}
		}
	}

	onMount(() => auth.init());
</script>

<svelte:head>
	<title>{m.login_title()} // car minder</title>
</svelte:head>

<div class="flex h-screen items-center justify-center">
	<Card.Root class="w-[350px]">
		<Card.Header>
			<Card.Title class="text-2xl">{m.login_heading()}</Card.Title>
			<Card.Description>{m.login_description()}</Card.Description>
		</Card.Header>
		<Card.Content>
			<form
				onsubmit={(e) => {
					e.preventDefault();
					handleSubmit();
				}}
			>
				<Field.Group>
					<Field.Field data-invalid={error ? true : undefined}>
						<Field.Label for="username">{m.auth_username()}</Field.Label>
						<Input
							id="username"
							bind:value={username}
							placeholder="acloudyskye"
							aria-invalid={!!error}
							required
						/>
					</Field.Field>

					<Field.Field data-invalid={error ? true : undefined}>
						<Field.Label for="password">{m.auth_password()}</Field.Label>
						<Input
							id="password"
							type="password"
							bind:value={password}
							aria-invalid={!!error}
							required
						/>
						{#if error}
							<Field.Error>{error}</Field.Error>
						{/if}
					</Field.Field>

					<Field.Field>
						<Button type="submit" class="w-full" disabled={isLoading}>
							{isLoading ? m.login_btn_submitting() : m.login_btn_submit()}
						</Button>
						<Field.Description class="text-center">
							{m.login_no_account()}
							<a href="/register" class="text-sidebar-primary hover:underline">{m.login_link_register()}</a>
						</Field.Description>
					</Field.Field>
				</Field.Group>
			</form>
		</Card.Content>
	</Card.Root>
</div>
