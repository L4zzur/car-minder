class CommandStore {
	open = $state(false);

	toggle() {
		this.open = !this.open;
	}

	show() {
		this.open = true;
	}

	hide() {
		this.open = false;
	}
}

export const commandStore = new CommandStore();
