import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastcms import setup

from enrichment.resource import EnrichedNewsResource
from enrichment.router import router as enrichment_router
from enrichment.service import run_pending
from news.resource import NewsResource
from shared.config import get_settings
from shared.db import SessionLocal, get_db
from shared.exception_handlers import setup_exception_handlers
from shared.middleware import setup_middleware

logger = logging.getLogger(__name__)

_WORKER_INTERVAL = 30  # seconds


async def enrichment_worker() -> None:
    while True:
        try:
            async with SessionLocal() as session:
                await run_pending(session)
        except Exception:
            logger.exception("enrichment_worker error")
        await asyncio.sleep(_WORKER_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(enrichment_worker())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description=settings.app_description,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    setup_middleware(app)
    setup_exception_handlers(app)

    setup(app, resources=[NewsResource, EnrichedNewsResource], get_session=get_db)
    app.include_router(enrichment_router)

    @app.get("/health", tags=["Health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
