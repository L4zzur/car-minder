# Дизайн-система и темы оформления (Theming & Palettes)

## 1. Концепция и границы кастомизации

Приложение **Car Minder** использует дизайн-систему на базе **Tailwind CSS v4** и **shadcn-svelte**.

Для обеспечения максимальной стабильности, производительности и консистентности UI разделен на два слоя: **статический каркас** (запекается на этапе сборки Vite) и **рантайм-кастомизацию** (переключается на лету без пересборки).

### Что зафиксировано при компиляции (Build-time):
* **Стиль компонентов:** Пресет `nova` (структура DOM, геометрия, тени и паддинги компонентов).
* **Типографика:** Шрифт `Noto Sans Variable` (локальный бандл `@fontsource-variable/noto-sans` без внешних HTTP-запросов).
* **Иконки:** Библиотека `lucide-svelte`.

### Что управляется в рантайме (Runtime):
* **Цветовые палитры:** `zinc` (дефолт), `slate`, `violet`, `blue`, `emerald`, `rose`, `amber`.
* **Режим освещения:** `dark` (по умолчанию) / `light` / `system` (управляется `mode-watcher`).
* **Скругления (Border Radius):** `0.375rem` (sharp), `0.625rem` (default), `0.875rem` (rounded).

---

## 2. Архитектура управления темами

```
                        ┌──────────────────────────────────────────────┐
                        │   Настройки пользователя (UI / Settings)     │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │     Svelte 5 State ($state / Rune Store)     │
                        │        + синхронизация с localStorage        │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ HTML Document Root:                                                                         │
│ <html class="dark" data-theme="violet" data-radius="0.625">                                 │
└──────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ CSS Cascade (Tailwind v4 @theme inline):                                                    │
│ [data-theme="violet"] { --primary: ...; --accent: ...; }                                    │
│ [data-theme="violet"].dark { --primary: ...; }                                              │
│ [data-radius="0.625"] { --radius: 0.625rem; }                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Преимущества клиентского подхода через Data-атрибуты:
1. **Live Preview:** Мгновенное переключение тем и радиусов в реальном времени прямо в интерфейсе настроек без перезагрузки страницы или контейнера.
2. **Изоляция слоев (Clean Architecture):** Бэкенд остается чистым REST API, а статический SPA не зависит от рантайм-генерации CSS.
3. **Поддержка Telegram Mini App (TMA):** Автоматическая адаптация под тему Telegram или выбор индивидуальной темы пользователем.
4. **Кэширование:** Все стили палитр скомпилированы в единый чанк CSS с content-hash, отдаются с `Cache-Control: max-age=31536000, immutable`.

---

## 3. Реализация CSS (`layout.css`)

Все палитры объявляются через атрибут `[data-theme="..."]`, переопределяя базовые токены `--primary`, `--accent`, `--ring`, `--sidebar-*` и `--chart-*`.

```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn-svelte/tailwind.css";
@import "@fontsource-variable/noto-sans";

@custom-variant dark (&:is(.dark *));

/* === Базовая палитра (Zinc / Default) === */
:root {
  --radius: 0.625rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.141 0.005 285.823);
  --primary: oklch(0.457 0.24 277.023);
  --primary-foreground: oklch(0.962 0.018 272.314);
  /* ... */
}

.dark {
  --background: oklch(0.141 0.005 285.823);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.398 0.195 277.366);
  --primary-foreground: oklch(0.962 0.018 272.314);
  /* ... */
}

/* === Палитра Violet === */
[data-theme="violet"] {
  --primary: oklch(0.541 0.281 293.009);
  --primary-foreground: oklch(0.985 0 0);
}
[data-theme="violet"].dark {
  --primary: oklch(0.627 0.265 293.009);
  --primary-foreground: oklch(0.985 0 0);
}

/* === Палитра Emerald === */
[data-theme="emerald"] {
  --primary: oklch(0.596 0.145 163.225);
  --primary-foreground: oklch(0.985 0 0);
}
[data-theme="emerald"].dark {
  --primary: oklch(0.696 0.17 162.48);
  --primary-foreground: oklch(0.141 0.005 285.823);
}

/* === Радиусы скругления === */
[data-radius="0.375"] { --radius: 0.375rem; }
[data-radius="0.625"] { --radius: 0.625rem; }
[data-radius="0.875"] { --radius: 0.875rem; }

@theme inline {
  --font-sans: "Noto Sans Variable", sans-serif;
  --font-heading: "Noto Sans Variable", sans-serif;
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  /* ... */
  --radius-sm: calc(var(--radius) * 0.6);
  --radius-md: calc(var(--radius) * 0.8);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) * 1.4);
}
```

---

## 4. Клиентский модуль управления (`$lib/state/theme.svelte.ts`)

Управление палитрой и радиусом реализуется на Svelte 5 Runes:

```ts
import { browser } from '$app/environment';

export type ThemePalette = 'zinc' | 'slate' | 'violet' | 'blue' | 'emerald' | 'rose' | 'amber';
export type ThemeRadius = '0.375' | '0.625' | '0.875';

class ThemeStore {
  palette = $state<ThemePalette>('zinc');
  radius = $state<ThemeRadius>('0.625');

  constructor() {
    if (browser) {
      const savedPalette = localStorage.getItem('app__theme_palette') as ThemePalette | null;
      const savedRadius = localStorage.getItem('app__theme_radius') as ThemeRadius | null;

      if (savedPalette) this.setPalette(savedPalette);
      if (savedRadius) this.setRadius(savedRadius);
    }
  }

  setPalette(palette: ThemePalette) {
    this.palette = palette;
    if (browser) {
      localStorage.setItem('app__theme_palette', palette);
      if (palette === 'zinc') {
        delete document.documentElement.dataset.theme;
      } else {
        document.documentElement.dataset.theme = palette;
      }
    }
  }

  setRadius(radius: ThemeRadius) {
    this.radius = radius;
    if (browser) {
      localStorage.setItem('app__theme_radius', radius);
      document.documentElement.dataset.radius = radius;
    }
  }
}

export const theme = new ThemeStore();
```

---

## 5. Опциональный глобальный дефолт для Self-Hosted (ENV)

Если владельцу сервера необходимо задать корпоративную палитру по умолчанию для всех новых пользователей:

1. В `.env` инстанса задается переменная:
   ```dotenv
   APP__DEFAULT_THEME=emerald
   APP__DEFAULT_RADIUS=0.625
   ```
2. Бэкенд возвращает эти значения через стандартный эндпоинт конфигурации инстанса `GET /api/v1/config`.
3. При первом посещении (когда `localStorage` пуст) клиент выставляет дефолтную тему инстанса.

---

## 6. Почему был отвергнут черновик с генерацией `/theme.css` на бэкенде

Ранее рассматривался подход сборки `/theme.css` через FastAPI из кодов shadcn-svelte (`APP__PRESET=b5E6v4EZZD`). Он был признан **антипаттерном** по следующим причинам:

1. **Мнимое применение пресетов:** Пресеты shadcn содержат стили компонентов (`nova`, `sera`) и шрифты, которые физически невозможно применить через одну инъекцию CSS-переменных без пересборки JS-бандла.
2. **Хрупкость стороннего формата:** Коды пресетов — это внутренний нестабильный формат сайта shadcn-svelte.
3. **Размытие ответственности:** Бэкенду не следует парсить и генерировать CSS для SPA-приложения.
4. **Проблемы с кэшированием:** Нехэшированный файл `/theme.css` требует `Cache-Control: no-cache`, добавляя задержку на сетевой запрос при каждой загрузке страницы.
