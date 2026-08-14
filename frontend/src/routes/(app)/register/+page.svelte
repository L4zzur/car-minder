<script lang="ts">
	import ShieldAlert from "lucide-svelte/icons/shield-alert";
	import { onMount } from "svelte";

	import { goto } from "$app/navigation";

	import { Auth, Users } from "$lib/api";
	import { auth } from "$lib/auth.svelte";
	import LanguageSwitcher from "$lib/components/LanguageSwitcher.svelte";
	import { Button } from "$lib/components/ui/button";
	import * as Card from "$lib/components/ui/card";
	import * as Empty from "$lib/components/ui/empty";
	import * as Field from "$lib/components/ui/field";
	import { Input } from "$lib/components/ui/input";
	import * as m from "$lib/paraglide/messages.js";

	let username = $state("");
	let name = $state("");
	let password = $state("");
	let confirmPassword = $state("");
	let isLoading = $state(false);
	let isRedirecting = $state(false);
	let isCheckingConfig = $state(true);
	let allowSignup = $state(true);
	let error = $state("");

	let passwordMismatch = $derived(confirmPassword.length > 0 && password !== confirmPassword);
	let usernameInvalid = $state(false);

	async function handleSubmit() {
		if (passwordMismatch) {
			error = m.register_error_password_mismatch();
			return;
		}

		isLoading = true;
		error = "";
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
				await goto("/garage");
				return;
			}

			error = m.register_error_auto_login_failed();
		} catch (e) {
			console.error("registration error:", e);
			error = m.register_error_generic();
		} finally {
			if (!isRedirecting) {
				isLoading = false;
			}
		}
	}

	function getRegisterError(apiError: unknown) {
		if (isApiError(apiError) && apiError.code === "username_already_taken") {
			usernameInvalid = true;
			return m.register_error_username_taken();
		}

		return m.register_error_generic();
	}

	function isApiError(value: unknown): value is { code?: string } {
		return typeof value === "object" && value !== null && "code" in value;
	}

	onMount(async () => {
		await auth.init();
		if (auth.isAuthenticated) {
			await goto("/garage");
			return;
		}

		try {
			const res = await Auth.getAuthConfigApiAuthConfigGet();
			if (res.data) {
				allowSignup = res.data.allow_signup;
			}
		} catch (e) {
			console.error("failed to fetch auth config:", e);
		} finally {
			isCheckingConfig = false;
		}
	});
</script>

<svelte:head>
	<title>{allowSignup ? m.register_title() : m.register_disabled_title()} // car minder</title>
</svelte:head>

<div class="relative flex min-h-screen items-center justify-center p-4 py-8">
	<div class="absolute top-4 right-4">
		<LanguageSwitcher />
	</div>
	<Card.Root class="w-[400px]">
		{#if isCheckingConfig}
			<Card.Header>
				<Card.Title class="text-2xl">{m.register_heading()}</Card.Title>
			</Card.Header>
		{:else if !allowSignup}
			<Card.Content class="pt-6">
				<Empty.Root>
					<Empty.Header>
						<Empty.Media class="text-destructive">
							<ShieldAlert class="size-10" />
						</Empty.Media>
						<Empty.Title>{m.register_disabled_heading()}</Empty.Title>
						<Empty.Description>{m.register_disabled_desc()}</Empty.Description>
					</Empty.Header>
					<Empty.Content>
						<Button href="/login" class="w-full">
							{m.register_link_login()}
						</Button>
					</Empty.Content>
				</Empty.Root>
			</Card.Content>
		{:else}
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
							<Field.Label for="confirm-password">{m.register_confirm_password_label()}</Field.Label
							>
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
		{/if}
	</Card.Root>
</div>
