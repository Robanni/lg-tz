from fastapi import FastAPI

from shared.config import get_settings
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

    @app.get("/health", tags=["Health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
