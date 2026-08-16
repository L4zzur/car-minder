# Release & Development Workflow

Краткое руководство по разработке, версионированию и публикации релизов.

---

## 1. Модель веток (Trunk-Based)

Ветки `dev` / `develop` **нет**. 
- **`main`** — единственный источник правды. Всегда содержит стабильный рабочий код.
- **Ветки фич/фиксов** (`feat/...`, `fix/...`) — создаются от `main`, вливаются в `main` через PR (Squash and merge), после чего удаляются.

---

## 2. Правило коммитов (Conventional Commits)

В процессе разработки делай сколько угодно коммитов. 
При слиянии ветки в `main` используй **Squash and merge** с понятным заголовком:

| Префикс | Назначение | Пример |
|---|---|---|
| `feat:` | Новая функциональность | `feat: add pdf export for service records` |
| `fix:` | Исправление бага | `fix: resolve double mileage calculation` |
| `perf:` | Оптимизация производительности | `perf: speed up car list loading` |
| `refactor:` | Рефакторинг без изменения логики | `refactor: extract reminder logic to service` |
| `chore:` | Рутина, обновление зависимостей | `chore: update dependencies` |

> 💡 Из этих заголовков GitHub автоматически формирует **Changelog** при релизе.

---

## 3. Инструкция по шагам

```mermaid
graph LR
    A["Ветка фичи (feat/...)"] -->|Squash & Merge| B["main"]
    B -->|uvx bump-my-version| C["Новая версия + Git Tag"]
    C -->|git push --follow-tags| D["GitHub Release + Docker в GHCR"]
```

### Шаг 1. Разработка фичи
```bash
git checkout main
git pull
git checkout -b feat/my-new-feature

# Работаем, коммитим...
git push -u origin feat/my-new-feature
```
Создай Pull Request в GitHub и влей в `main` через **Squash and merge**.

### Шаг 2. Выпуск релиза
Когда накопились нужные изменения в `main` и пора выкатить обновление:

```bash
git checkout main
git pull

# Для багфикса (0.1.0 -> 0.1.1):
uvx bump-my-version bump patch

# Для новой фичи (0.1.0 -> 0.2.0):
uvx bump-my-version bump minor

# Для мажорного релиза с ломающими изменениями (0.1.0 -> 1.0.0):
uvx bump-my-version bump major
```

### Шаг 3. Публикация
```bash
git push --follow-tags
```

---

## 4. Что происходит автоматически после пуша тега
1. GitHub Actions собирает multi-arch Docker-образ (`linux/amd64`, `linux/arm64`).
2. Пушит в `ghcr.io/L4zzur/car-minder:<version>` и `ghcr.io/L4zzur/car-minder:latest`.
3. Создаёт GitHub Release со структурированным списком изменений (Changelog).

---

## 5. Как обновляется пользователь
```bash
docker compose pull
docker compose up -d
```
