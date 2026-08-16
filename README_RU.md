<p align="center">
  <img src="docs/assets/banner.png" alt="car minder banner" width="100%" />
</p>

# car minder

<img height="100px" src="docs/assets/logo.svg" alt="car minder logo" align="right" />

**Гараж, пробег и сервисное обслуживание.**  
Open-source, self-hosted и создан, чтобы ваши автомобили всегда были в порядке.

[English](README.md) • **Русский**

[Скриншоты](docs/SCREENSHOTS.md) •
[Возможности](#возможности) •
[Быстрый старт](#быстрый-старт) •
[Конфигурация](#конфигурация) •
[Стек технологий](#стек-технологий) •
[Разработка](#разработка) •
[Участие в проекте](#участие-в-проекте) •
[Лицензия](#лицензия)

---

**сar minder** — это открытое self-hosted веб-приложение и Telegram-компаньон для вашего гаража. Помогает вести цифровую сервисную книжку, фиксировать показания одометра и получать своевременные напоминания, когда автомобилю требуется замена масла, расходников или плановое ТО.

## Возможности

- **Гараж**: добавление автомобилей (марка, модель, год) и учет их текущего пробега.
- **Сервисная книжка**: настройка интервалов замены расходников по километрам, дням или обоим параметрам.
- **Статусы обслуживания**: наглядные бейджи `OK`, `SOON` и `DUE`, показывающие, когда пора на обслуживание.
- **Журнал пробега**: запись показаний одометра в любой момент.
- **Уведомления в Telegram**: напоминания об обслуживание с кнопкой для быстрой отметки выполнения прямо в чате.
- **Запросы пробега**: бот сам спросит актуальный одометр, если пробег давно не обновлялся.
- **Telegram Mini App**: мобильный интерфейс внутри Telegram для быстрого просмотра статусов и ввода пробега.
- **Self-hosted**: работает в одном Docker-контейнере со встроенной SQLite — без лишних сервисов и баз данных.

## Быстрый старт

Готовый файл `docker-compose.yml` уже находится в корне репозитория.

### 1. Клонирование и настройка

```bash
git clone https://github.com/L4zzur/car-minder.git
cd car-minder
cp .env.template .env
```

Сгенерируйте секретный ключ и укажите его в параметре `APP__AUTH__SECRET_KEY` в файле `.env`:

**Вариант A (OpenSSL):**

```bash
openssl rand -hex 32
```

**Вариант B (Python):**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Запуск через Docker Compose

Запустите приложение командой:

```bash
docker compose up -d --build
```

Веб-интерфейс будет доступен по адресу [http://localhost:8000](http://localhost:8000).

## Конфигурация

Параметры car minder задаются через переменные окружения с префиксом `APP__`:

| Переменная                               | Описание                                                                 | По умолчанию                     |
| :--------------------------------------- | :----------------------------------------------------------------------- | :------------------------------- |
| `APP__MODE`                              | Режим работы приложения (`prod` или `dev`)                               | `prod`                           |
| `APP__DOMAIN`                            | Публичный домен для Telegram Webhook (например, `carminder.example.com`) | _None_                           |
| `APP__RUN__HOST`                         | Сетевой интерфейс сервера                                                | `0.0.0.0`                        |
| `APP__RUN__PORT`                         | Порт HTTP-сервера                                                        | `8000`                           |
| `APP__API__PREFIX`                       | Базовый префикс API маршрутов                                            | `/api`                           |
| `APP__CORS__ORIGINS`                     | Список разрешенных CORS-источников (JSON-массив)                         | `["http://localhost:8000", ...]` |
| `APP__DB__FILE_PATH`                     | Путь к файлу базы данных SQLite                                          | `/app/backend/data/db.sqlite`    |
| `APP__AUTH__SECRET_KEY`                  | Секретный ключ для подписи JWT и шифрования сессий                       | _Обязательно_                    |
| `APP__AUTH__ALGORITHM`                   | Алгоритм подписи JWT токенов                                             | `HS256`                          |
| `APP__AUTH__ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена доступа в минутах                                     | `10080` (7 дней)                 |
| `APP__AUTH__ALLOW_SIGNUP`                | Разрешить публичную регистрацию новых пользователей (`true` / `false`)   | `true`                           |
| `APP__BOT__TOKEN`                        | Токен Telegram-бота от [@BotFather](https://t.me/BotFather)              | _Опционально_                    |
| `APP__BOT__WEBHOOK_SECRET`               | Секретный токен для валидации входящих вебхуков Telegram                 | _Опционально_                    |

## Стек технологий

- **Бэкенд**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.13), [SQLAlchemy 2.0](https://www.sqlalchemy.org/) Async, [SQLite](https://www.sqlite.org/) (`aiosqlite`), [APScheduler](https://apscheduler.readthedocs.io/)
  - _Инструменты_: [uv](https://docs.astral.sh/uv/), [Ruff](https://docs.astral.sh/ruff/), [ty](https://github.com/bndr/ty), [Alembic](https://alembic.sqlalchemy.org/), [Pytest](https://pytest.org/)
- **Фронтенд**: [Svelte 5](https://svelte.dev/) (Runes), [SvelteKit](https://kit.svelte.dev/), [Tailwind CSS v4](https://tailwindcss.com/), [shadcn-svelte](https://shadcn-svelte.com/)
  - _Инструменты_: [pnpm](https://pnpm.io/), [Vite](https://vite.dev/), [ESLint](https://eslint.org/), [Prettier](https://prettier.io/)
- **Telegram**: [aiogram 3](https://aiogram.dev/) (Webhook-бот), [@tma.js/sdk-svelte](https://github.com/Telegram-Mini-Apps/tma.js) (Telegram Mini App)
- **Деплой**: [Docker](https://www.docker.com/), Docker Compose

## Разработка

### Предварительные требования

- [uv](https://docs.astral.sh/uv/) (менеджер пакетов Python)
- [pnpm](https://pnpm.io/) (менеджер пакетов Node.js)
- Node.js 20+

### Бэкенд

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn main:app --reload --port 8000
```

Запуск тестов:

```bash
uv run pytest
```

### Фронтенд

```bash
cd frontend
pnpm install
pnpm dev
```

Проверка типов:

```bash
pnpm check
```

## Участие в проекте

Мы рады любым предложениям, сообщениям об ошибках и пулл-реквестам!

### Добавление переводов

car minder поддерживает мультиязычность из коробки:

- **Веб-интерфейс**: локализуется через Paraglide JS в каталоге `frontend/messages/`.
- **Telegram-бот**: локализуется через Fluent-файлы в `backend/app/bot/locales/`.

Если вы хотите помочь с переводом car minder на свой язык или дополнить текущие переводы — создавайте Pull Request!

## Лицензия

car minder распространяется под лицензией [MIT](LICENSE). Вы можете свободно использовать, модифицировать и распространять этот проект в личных или коммерческих целях. Если вы разработали полезное улучшение — отправьте Pull Request, чтобы поделиться им с сообществом.
