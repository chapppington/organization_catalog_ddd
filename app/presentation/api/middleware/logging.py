import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from infrastructure.logging.logger import get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов и ответов в Logstash."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с логированием."""
        start_time = time.time()

        # Получаем информацию о запросе
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Выполняем запрос
        try:
            response = await call_next(request)
            status_code = response.status_code
            process_time = time.time() - start_time

            # Логируем успешный запрос
            self.logger.info(
                f"{method} {url} - {status_code}",
                extra={
                    "method": method,
                    "url": url,
                    "status_code": status_code,
                    "process_time": round(process_time, 4),
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "type": "http_request",
                },
            )

        except Exception as e:
            process_time = time.time() - start_time
            status_code = 500

            # Логируем ошибку
            self.logger.error(
                f"{method} {url} - {status_code} - {str(e)}",
                extra={
                    "method": method,
                    "url": url,
                    "status_code": status_code,
                    "process_time": round(process_time, 4),
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "error": str(e),
                    "type": "http_request",
                },
                exc_info=True,
            )
            raise

        return response
