"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from precedentpal.api.errors import install_error_handlers
from precedentpal.api.middleware import RequestContextMiddleware
from precedentpal.api.routes.documents import router as documents_router
from precedentpal.api.routes.health import router as health_router
from precedentpal.config import Settings, get_settings
from precedentpal.logging_setup import configure_logging
from precedentpal.store import RecordStore


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    store = RecordStore(settings.data_file)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        store.load()
        yield

    app = FastAPI(
        title="PrecedentPal API",
        version="0.1.0",
        description="Search and retrieve Indian Supreme Court precedent records.",
        lifespan=lifespan,
    )
    app.state.store = store
    app.add_middleware(RequestContextMiddleware)
    install_error_handlers(app)
    app.include_router(health_router)
    app.include_router(documents_router)
    return app
