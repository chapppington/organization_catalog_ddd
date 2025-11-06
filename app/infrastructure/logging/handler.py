import logging
import socket
from datetime import datetime

import orjson


class LogstashHandler(logging.Handler):
    """Handler для отправки логов в Logstash через TCP."""

    def __init__(
        self,
        host: str = "logstash",
        port: int = 5000,
        project: str = "organization-catalog",
    ):
        super().__init__()
        self.host = host
        self.port = port
        self.project = project
        self.sock: socket.socket | None = None
        # Пытаемся подключиться, но не падаем если не получилось
        try:
            self.connect()
        except Exception:
            self.sock = None

    def connect(self) -> None:
        """Установка соединения с Logstash."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2)  # Таймаут для подключения
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(None)  # Убираем таймаут после подключения
        except Exception:
            self.sock = None

    def emit(self, record: logging.LogRecord) -> None:
        """Отправка лога в Logstash."""
        if not self.sock:
            self.connect()
            if not self.sock:
                # Если не удалось подключиться, просто игнорируем лог
                # чтобы не падало приложение
                return

        try:
            # Формируем данные для отправки
            log_data = {
                "level": record.levelname,
                "title": record.getMessage(),
                "timestamp": datetime.now().isoformat(),
                "project": self.project,
            }

            # Добавляем все дополнительные поля из extra
            if hasattr(record, "extra") and record.extra:
                log_data.update(record.extra)

            # Отправляем данные в Logstash
            self.sock.sendall(orjson.dumps(log_data) + b"\n")

        except Exception:
            # При ошибке закрываем соединение и пытаемся переподключиться
            # Не поднимаем исключение, чтобы не падало приложение
            self.close()
            self.connect()

    def close(self) -> None:
        """Закрытие соединения."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

        super().close()
