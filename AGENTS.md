# Project Rules & Guidelines

## 1. Tooling & Commands
- **Backend:** Strictly use `uv` for package management and script execution.
  - Run tests: `uv run pytest`
  - Run linter/formatting: `uv run ruff check .` / `uv run ruff format .`
  - Type checking: `uv run ty check`
  - Database: `uv run alembic ...`
- **Frontend:** Strictly use `pnpm` for package management and scripts.
  - Dev server: `pnpm dev`
  - Type checking: `pnpm check`
  - API Client Generation: `pnpm gen:api`
  - shadcn-svelte preset (nova + zinc + radius 0.625): `bfputO4Jk` — apply with `pnpm dlx shadcn-svelte@latest apply bfputO4Jk -y` (overwrites `src/routes/(app)/layout.css`; re-add Noto Sans import + `--font-sans` after if needed)

## 2. Frontend Conventions (Svelte 5)
- **Reactivity:** Use ONLY Svelte 5 Runes (`$state`, `$derived`, `$effect`, `$props`).
  - NEVER use Svelte 3/4 legacy syntax (`export let`, `$:`, `<slot />`).
- **Component Props:** Destructure props via `$props()`:
  ```ts
  let { carId, onSave }: Props = $props();
  ```
- **Children/Slots:** Use Snippets (`{#snippet ...}`) instead of `<slot />`.

## 3. Backend Conventions (FastAPI & SQLAlchemy 2.0)
- **ORM:** Use ONLY SQLAlchemy 2.0 Async syntax.
  - Define models using `DeclarativeBase` and `mapped_column(...)`.
  - Queries must use `select()` statements with `await session.execute(...)` or `await session.scalars(...)`.
  - NEVER use legacy `session.query()` or sync database sessions.
- **Schemas:** Use Pydantic v2 schemas for request/response validation.
