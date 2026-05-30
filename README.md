## Быстрый старт

### Вариант 1 — только Docker (рекомендуется для проверки)

Требования: Docker + Docker Compose.

```bash
# 1. Скопировать конфиг и переключить DATABASE_URL на db-хост
cp .env.example .env
```

Открыть `.env`, раскомментировать строки с `db` и закомментировать строки с `localhost`:

```dotenv
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5436/lg_tz       # закомментировать
# ALEMBIC_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5436/lg_tz  # закомментировать
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/lg_tz               # раскомментировать
ALEMBIC_DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/lg_tz       # раскомментировать
```

```bash
docker compose up --build
```

Приложение доступно на http://localhost:8000  
Swagger UI: http://localhost:8000/docs

```bash
# Запустить миграции + seed (первый раз)
docker compose --profile migration run --rm migrate
```

---

## Проверка функциональности

### 1. Получить список новостей → взять `id`

```
GET http://localhost:8000/news/
```

### 2. Поставить новость в очередь обогащения

```
POST http://localhost:8000/enrichment/jobs
Content-Type: application/json

{ "news_id": <id из шага 1> }
```

Ответ содержит `job_id`.

### 3. Проверить статус задачи

```
GET http://localhost:8000/enrichment/jobs/<job_id>
```

Ждать пока `status` станет `done`.

### 4. Посмотреть результат

```
GET http://localhost:8000/news/<news_id>/card
```

---

### Вариант 2 — локально с mise

Требования: Docker, [mise](https://mise.jdx.dev/).

```bash
cp .env.example .env
mise run dev
```

---

### Вариант 3 — локально без mise

Требования: Docker, Python 3.12+, [uv](https://docs.astral.sh/uv/).

```bash
# 1. Конфиг (DATABASE_URL должен указывать на localhost)
cp .env.example .env

# 2. Поднять БД
docker compose up -d db

# 3. Зависимости
pip install uv
uv sync

# 4. Сервер
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

---

## Архитектура

### Слои

Каждый модуль (`news`, `enrichment`) следует одной схеме:

```
router → service → repo → model
```

Роутер принимает запрос, сервис содержит бизнес-логику, репо изолирует работу с БД(В src\enrichment\service.py абстракция чуть течет но там это обосновано)

### Парсер

`parsing` строится вокруг абстрактного базового класса `BaseSiteParser` с методом `parse(url, html) -> ParsedArticle`. Конкретные реализации (`rbc_ru`, `ria_ru`, `GenericParser`) регистрируются в глобальном `ParserRegistry` по домену. При обогащении репо выбирает парсер через `registry.get(domain)`, при отсутствии специфичного — использует `GenericParser` (trafilatura + BeautifulSoup).

### Воркер обогащения

При старте приложения lifespan-хук запускает фоновую coroutine `enrichment_worker()`. Она раз в 5 секунд забирает из БД до 5 задач со статусом `pending` и запускает их параллельно через `asyncio.gather()`. Явной очереди в памяти нет — роль очереди играет таблица `enrichment_jobs`.
В реальном проде надо выносить либо в отдельный сервис либо в Celery.
---

## Задачи mise

| Команда | Описание |
|---------|----------|
| `mise run dev` | Поднять БД + запустить сервер |
| `mise run db` | Только поднять БД |
| `mise run db-stop` | Остановить БД |
| `mise run lint` | Линт + форматирование |
