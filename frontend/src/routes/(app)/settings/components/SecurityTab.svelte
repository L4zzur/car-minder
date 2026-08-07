<script lang="ts">
	import AlertTriangle from '@lucide/svelte/icons/alert-triangle';
	import CheckCircle2 from '@lucide/svelte/icons/check-circle-2';
	import Loader2 from '@lucide/svelte/icons/loader-2';
	import Lock from '@lucide/svelte/icons/lock';
	import Mail from '@lucide/svelte/icons/mail';
	import { onMount } from 'svelte';

	import { Auth, Users } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import * as Field from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import * as m from '$lib/paraglide/messages.js';

	// Email state
	let email = $state('');
	let isSavingEmail = $state(false);
	let emailSuccessMsg = $state('');
	let emailErrorMsg = $state('');

	// Password state
	let currentPassword = $state('');
	let newPassword = $state('');
	let confirmPassword = $state('');
	let isChangingPassword = $state(false);
	let passwordSuccessMsg = $state('');
	let passwordErrorMsg = $state('');

	onMount(() => {
		if (auth.user?.email) {
			email = auth.user.email;
		}
	});

	async function updateEmail() {
		if (!auth.user?.id) return;

		const trimmed = email.trim();
		if (trimmed && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
			emailErrorMsg = m.settings_security_email_error_invalid();
			return;
		}

		isSavingEmail = true;
		emailSuccessMsg = '';
		emailErrorMsg = '';

		try {
			const res = await Users.updateUserApiUsersUserIdPatch({
				path: { user_id: auth.user.id },
				body: { email: trimmed || null }
			});

			if (res.error) {
				const error = res.error as any;
				const code = error?.code;
				const detail = error?.detail;
				if (code === 'email_already_taken') {
					emailErrorMsg = m.settings_security_email_error_taken();
				} else if (Array.isArray(detail)) {
					emailErrorMsg = m.settings_security_email_error_invalid();
				} else {
					emailErrorMsg = m.settings_security_email_error();
				}
				return;
			}

			await auth.fetchUser();
			emailSuccessMsg = m.settings_security_email_saved();
			setTimeout(() => (emailSuccessMsg = ''), 3000);
		} catch (err: any) {
			console.error('ошибка обновления email:', err);
			emailErrorMsg = m.settings_security_email_error();
		} finally {
			isSavingEmail = false;
		}
	}

	async function changePassword() {
		if (!currentPassword || !newPassword) return;

		if (newPassword !== confirmPassword) {
			passwordErrorMsg = m.settings_security_password_error_mismatch();
			return;
		}

		if (newPassword.length < 6) {
			passwordErrorMsg = m.settings_security_password_error_too_short();
			return;
		}

		isChangingPassword = true;
		passwordSuccessMsg = '';
		passwordErrorMsg = '';

		try {
			const res = await Auth.changePasswordApiAuthChangePasswordPost({
				body: {
					current_password: currentPassword,
					new_password: newPassword
				}
			});

			if (res.error) {
				const code = (res.error as any)?.code;
				if (code === 'invalid_current_password') {
					passwordErrorMsg = m.settings_security_password_error_wrong();
				} else {
					passwordErrorMsg = m.settings_security_password_error();
				}
				return;
			}

			passwordSuccessMsg = m.settings_security_password_saved();
			currentPassword = '';
			newPassword = '';
			confirmPassword = '';
			setTimeout(() => (passwordSuccessMsg = ''), 3000);
		} catch (err: any) {
			console.error('ошибка смены пароля:', err);
			passwordErrorMsg = m.settings_security_password_error();
		} finally {
			isChangingPassword = false;
		}
	}
</script>

<div class="space-y-6 w-full">
	<!-- Email Card -->
	<Card.Root class="w-full">
		<Card.Header>
			<Card.Title class="text-lg font-semibold lowercase">
				{m.settings_security_email_title()}
			</Card.Title>
			<Card.Description class="lowercase">{m.settings_security_email_desc()}</Card.Description>
		</Card.Header>
		<Card.Content>
			<form onsubmit={(e) => { e.preventDefault(); updateEmail(); }} class="space-y-4">
				<Field.FieldGroup class="max-w-md gap-4">
					<Field.Field>
						<Field.FieldLabel for="user_email" class="lowercase">{m.settings_security_email_label()}</Field.FieldLabel>
						<Input
							id="user_email"
							type="email"
							placeholder="example@domain.com"
							bind:value={email}
						/>
					</Field.Field>
				</Field.FieldGroup>

				{#if emailSuccessMsg}
					<div class="flex items-center gap-2 rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-500 border border-emerald-500/20 lowercase">
						<CheckCircle2 class="size-4 shrink-0" />
						{emailSuccessMsg}
					</div>
				{/if}

				{#if emailErrorMsg}
					<div class="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive border border-destructive/20 lowercase">
						<AlertTriangle class="size-4 shrink-0" />
						{emailErrorMsg}
					</div>
				{/if}

				<div class="flex justify-end">
					<Button type="submit" disabled={isSavingEmail} variant="outline" size="sm" class="lowercase">
						{#if isSavingEmail}
							<Loader2 class="animate-spin" data-icon="inline-start" />
							{m.settings_security_email_saving()}
						{:else}
							<Mail data-icon="inline-start" />
							{m.settings_security_email_save()}
						{/if}
					</Button>
				</div>
			</form>
		</Card.Content>
	</Card.Root>

	<!-- Change Password Card -->
	<Card.Root class="w-full">
		<Card.Header>
			<Card.Title class="text-lg font-semibold lowercase">
				{m.settings_security_password_title()}
			</Card.Title>
			<Card.Description class="lowercase">{m.settings_security_password_desc()}</Card.Description>
		</Card.Header>
		<Card.Content>
			<form onsubmit={(e) => { e.preventDefault(); changePassword(); }} class="space-y-4">
				<Field.FieldGroup class="gap-4">
					<Field.Field class="max-w-md">
						<Field.FieldLabel for="current_password" class="lowercase">{m.settings_security_password_current()}</Field.FieldLabel>
						<Input
							id="current_password"
							type="password"
							placeholder="••••••••"
							bind:value={currentPassword}
							required
						/>
					</Field.Field>

					<div class="grid gap-4 sm:grid-cols-2">
						<Field.Field>
							<Field.FieldLabel for="new_password" class="lowercase">{m.settings_security_password_new()}</Field.FieldLabel>
							<Input
								id="new_password"
								type="password"
								placeholder="••••••••"
								bind:value={newPassword}
								required
							/>
						</Field.Field>

						<Field.Field>
							<Field.FieldLabel for="confirm_password" class="lowercase">{m.settings_security_password_confirm()}</Field.FieldLabel>
							<Input
								id="confirm_password"
								type="password"
								placeholder="••••••••"
								bind:value={confirmPassword}
								required
							/>
						</Field.Field>
					</div>
				</Field.FieldGroup>

				{#if passwordSuccessMsg}
					<div class="flex items-center gap-2 rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-500 border border-emerald-500/20 lowercase">
						<CheckCircle2 class="size-4 shrink-0" />
						{passwordSuccessMsg}
					</div>
				{/if}

				{#if passwordErrorMsg}
					<div class="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive border border-destructive/20 lowercase">
						<AlertTriangle class="size-4 shrink-0" />
						{passwordErrorMsg}
					</div>
				{/if}

				<div class="flex justify-end">
					<Button type="submit" disabled={isChangingPassword} size="sm" class="lowercase">
						{#if isChangingPassword}
							<Loader2 class="animate-spin" data-icon="inline-start" />
							{m.settings_security_password_saving()}
						{:else}
							<Lock data-icon="inline-start" />
							{m.settings_security_password_save()}
						{/if}
					</Button>
				</div>
			</form>
		</Card.Content>
	</Card.Root>
</div>
