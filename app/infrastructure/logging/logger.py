import logging

from settings.config import Config
from infrastructure.logging.handler import LogstashHandler


def setup_logging(config: Config) -> None:
    """Настройка логгера с Logstash handler."""
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.INFO)

    # Очищаем существующие handlers
    if logger.handlers:
        logger.handlers.clear()

    # Создаем Logstash handler
    # Если Logstash недоступен, handler все равно создастся,
    # но будет пытаться подключиться при каждом emit()
    try:
        logstash_handler = LogstashHandler(
            host=config.logstash_host,
            port=config.logstash_port,
            project=config.logstash_project,
        )
        logstash_handler.setLevel(logging.INFO)

        # Добавляем handler к логгеру
        logger.addHandler(logstash_handler)
    except Exception:
        # Если не удалось создать handler, просто продолжаем без логирования в Logstash
        # Приложение должно работать даже если Logstash недоступен
        pass

    logger.propagate = False


def get_logger(name: str = "app_logger") -> logging.Logger:
    """Получить настроенный логгер."""
    return logging.getLogger(name)
