from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import get_settings


def setup_middleware(app: FastAPI) -> None:
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
