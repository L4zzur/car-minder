# GitHub CLI (`gh`) Cheatsheet & Guide

Краткая шпаргалка по работе с GitHub прямо из терминала без необходимости открывать браузер.

---

## 1. Авторизация и статус

```bash
# Вход в аккаунт (однократно, выбираем GitHub.com -> HTTPS/SSH -> Web Browser)
gh auth login

# Проверить статус авторизации и текущего пользователя
gh auth status

# Обновить права/токен (если добавились новые scope, например workflow)
gh auth refresh -s workflow,repo
```

---

## 2. Pull Requests (PR) — Основной рабочий процесс

### Создание PR
```bash
# Быстро создать PR с заголовком и описанием из первого коммита ветки:
gh pr create --fill

# Создать PR с лейблом (например, bug, enhancement):
gh pr create --fill --label "bug"

# Создать с кастомным заголовком и описанием:
gh pr create --title "feat(frontend): add dark mode" --body "Closes #12"

# Интерактивный мастер создания (спросит title, body, reviewers, labels):
gh pr create
```

### Просмотр и проверка
```bash
# Статус PR для текущей ветки + статус проверок CI (GitHub Actions):
gh pr status

# Список открытых PR в репозитории:
gh pr list

# Посмотреть статус CI чеков (зеленые/красные/в процессе):
gh pr checks

# Посмотреть диффы текущего PR в терминале:
gh pr diff

# Открыть текущий PR в браузере в один клик:
gh pr view --web
```

### Редактирование и ревью
```bash
# Добавить лейбл к открытому PR текущей ветки:
gh pr edit --add-label "enhancement"

# Назначить ревьюера:
gh pr edit --add-reviewer username

# Переключиться локально на ветку чужого PR по его номеру:
gh pr checkout 42
```

### Слияние (Merge)
```bash
# Слияние по нашему регламенту (Squash and merge + удаление ветки):
gh pr merge --squash --delete-branch

# Авто-слияние (сольёт автоматически, как только пройдут все CI чеки):
gh pr merge --auto --squash --delete-branch
```

---

## 3. GitHub Actions & CI (Пайплайны)

```bash
# Список последних запусков воркфлоу:
gh run list

# Следить за выполнением текущего CI в реальном времени (лайв-логи):
gh run watch

# Посмотреть лог упавшего шага (не надо скроллить весь веб-интерфейс):
gh run view --log-failed

# Перезапустить упавший запуск:
gh run rerun <run-id>
```

---

## 4. Issues (Задачи) и Labels (Метки)

```bash
# Список задач:
gh issue list

# Создать новую задачу:
gh issue create --title "Fix mileage reset bug" --body "Steps to reproduce..." --label "bug"

# Посмотреть список доступных лейблов в репозитории:
gh label list

# Создать новый лейбл:
gh label create "backend" --color "0075ca" --description "Backend API changes"
```

---

## 5. Releases & Tags (Релизы)

```bash
# Список последних релизов:
gh release list

# Посмотреть описание последнего релиза:
gh release view

# Скачать ассеты последнего релиза:
gh release download
```

---

## 6. Полезные фишки и алиасы

### Флаг `--web` (или `-w`)
Работает почти для любой команды — мгновенно открывает соответствующую страницу в браузере:
* `gh pr view -w` — открыть текущий PR
* `gh repo view -w` — открыть главную страницу репозитория
* `gh run view -w` — открыть текущий CI run

### Кастомные алиасы `gh`
Можно настроить свои ультра-короткие команды:
```bash
# Алиас 'gh pr-ready': создать PR с авто-заполнением и сразу открыть в браузере
gh alias set pr-ready "pr create --fill --web"

# Алиас 'gh sq': squash and merge текущего PR с удалением ветки
gh alias set sq "pr merge --squash --delete-branch"
```
