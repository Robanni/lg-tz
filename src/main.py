from fastapi import FastAPI
from fastcms import setup

from enrichment.resource import EnrichedNewsResource
from news.resource import NewsResource
from shared.config import get_settings
from shared.db import get_db
from shared.exception_handlers import setup_exception_handlers
from shared.middleware import setup_middleware


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description=settings.app_description,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    setup_middleware(app)
    setup_exception_handlers(app)

    setup(app, resources=[NewsResource, EnrichedNewsResource], get_session=get_db)

    @app.get("/health", tags=["Health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
