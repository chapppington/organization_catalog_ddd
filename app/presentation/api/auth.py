from authx import (
    AuthX,
    AuthXConfig,
)

from settings import config


auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY=config.jwt_secret_key,
    JWT_TOKEN_LOCATION=["cookies"],  # Используем cookies
    JWT_ACCESS_COOKIE_NAME="access_token",
    JWT_REFRESH_COOKIE_NAME="refresh_token",
    JWT_COOKIE_CSRF_PROTECT=False,  # выключаем csrf чтобы работал refresh endpoint
    JWT_COOKIE_SAMESITE="Lax",  # Lax для работы с HTTP, None требует HTTPS
    JWT_COOKIE_SECURE=False,  # False для HTTP, True для HTTPS
    JWT_COOKIE_HTTPONLY=True,  # Защита от XSS атак
    JWT_COOKIE_PATH="/",  # Путь для кук - доступны для всего сайта
)

auth_service = AuthX(config=auth_config)
