FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir --timeout=120 uv && uv sync --no-dev --frozen

FROM python:3.12-slim AS runtime
RUN adduser --disabled-password --no-create-home app
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY src/ ./src/
COPY scripts/ ./scripts/
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
