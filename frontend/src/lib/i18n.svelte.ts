import { getLocale, overwriteGetLocale, setLocale as setParaglideLocale, type Locale } from '$lib/paraglide/runtime';

class I18nState {
	#locale = $state<Locale>(getLocale());

	constructor() {
		// Hook into Paraglide's internal getLocale so Svelte 5 tracks the $state rune dependency
		overwriteGetLocale(() => this.#locale);
	}

	get lang(): Locale {
		return this.#locale;
	}

	set lang(newLocale: Locale) {
		if (this.#locale !== newLocale) {
			this.#locale = newLocale;
			setParaglideLocale(newLocale, { reload: false });
		}
	}
}

export const i18n = new I18nState();
