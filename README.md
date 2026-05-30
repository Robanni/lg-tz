## Quickstart

### С mise (рекомендуется)

```bash
# 1. Установить mise
choco install mise

# 2. Клонировать и перейти в папку
cp .env.example .env

# 3. Запустить (поднимет БД и сервер)
mise run dev
```

### Без mise

```bash
# 1. Скопировать конфиг
cp .env.example .env

# 2. Поднять БД
docker compose up -d

# 3. Установить зависимости
pip install uv
uv sync

# 4. Запустить сервер
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

Приложение доступно на http://localhost:8000  
Swagger UI: http://localhost:8000/docs

## Задачи mise

| Команда | Описание |
|---------|----------|
| `mise run dev` | Поднять БД + запустить сервер |
| `mise run db` | Только поднять БД |
| `mise run db-stop` | Остановить БД |
| `mise run lint` | Линт + форматирование |
