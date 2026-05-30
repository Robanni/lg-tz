import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from shared.exceptions import AppError

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        logger.error(
            "AppError handled: status=%s detail=%s",
            exc.status_code,
            exc.message,
            exc_info=exc.status_code >= 500,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("Validation error: errors=%s", exc.errors())
        return JSONResponse(
            status_code=422,
            content={"detail": "Некорректные входные данные"},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error: type=%s", type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={"detail": "Внутренняя ошибка сервера"},
        )
