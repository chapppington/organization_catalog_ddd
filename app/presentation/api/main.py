from fastapi import FastAPI

from infrastructure.logging.logger import setup_logging
from presentation.api.exceptions import setup_exception_handlers
from presentation.api.healthcheck import healthcheck_router
from presentation.api.middleware.logging import LoggingMiddleware
from presentation.api.v1 import v1_router
from settings import config


def create_app() -> FastAPI:
    app = FastAPI(
        title="Organization Catalog DDD",
        description="Organization Catalog DDD",
        docs_url="/api/docs",
        debug=True,
    )

    # Инициализация логирования
    setup_logging(config)

    # Добавление middleware для логирования
    app.add_middleware(LoggingMiddleware)

    setup_exception_handlers(app)

    app.include_router(healthcheck_router)
    app.include_router(v1_router, prefix="/api/v1")
    return app
