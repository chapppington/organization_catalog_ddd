from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from authx.exceptions import AuthXException
from presentation.api.schemas import ApiResponse

from domain.base.exceptions import ApplicationException
from domain.user.exceptions import (
    APIKeyBannedException,
    APIKeyNotFoundException,
    InvalidCredentialsException,
)


async def application_exception_handler(
    request: Request,
    exc: ApplicationException,
) -> ORJSONResponse:
    """Общий обработчик для всех исключений приложения."""
    exception_name = exc.__class__.__name__

    # Определяем статус код на основе типа исключения
    if isinstance(exc, APIKeyNotFoundException | InvalidCredentialsException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, APIKeyBannedException):
        status_code = status.HTTP_403_FORBIDDEN
    elif "NotFound" in exception_name:
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return ORJSONResponse(
        status_code=status_code,
        content=ApiResponse(
            data={},
            errors=[{"message": exc.message}],
        ).model_dump(),
    )


async def authx_exception_handler(
    request: Request,
    exc: AuthXException,
) -> ORJSONResponse:
    """Обработчик для исключений authx (отсутствие/невалидность токена)."""
    return ORJSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ApiResponse(
            data={},
            errors=[{"message": str(exc)}],
        ).model_dump(),
    )


async def api_key_authentication_handler(
    request: Request,
    exc: HTTPException,
) -> ORJSONResponse:
    # Обрабатываем только ошибки аутентификации/авторизации
    if exc.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
        error_message = exc.detail
        # Улучшаем сообщение для случая отсутствия API ключа
        if error_message == "Not authenticated" or "Not authenticated" in error_message:
            error_message = "API key is required"

        return ORJSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(
                data={},
                errors=[{"message": error_message}],
            ).model_dump(),
        )

    # Для других HTTPException возвращаем стандартный формат
    return ORJSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            data={},
            errors=[{"message": exc.detail}],
        ).model_dump(),
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> ORJSONResponse:
    errors = []

    # Обрабатываем ошибки валидации
    for error in exc.errors():
        # Формируем путь к полю
        field_path = " -> ".join(str(loc) for loc in error.get("loc", []))

        # Формируем сообщение об ошибке
        error_type = error.get("type", "validation_error")
        error_msg = error.get("msg", "Validation error")

        # Создаем понятное сообщение
        if field_path:
            message = f"{field_path}: {error_msg}"
        else:
            message = error_msg

        errors.append(
            {
                "message": message,
                "type": error_type,
                "field": field_path if field_path else None,
            },
        )

    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ApiResponse(
            data={},
            errors=errors,
        ).model_dump(),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Настраивает обработчики исключений для FastAPI приложения."""
    # Общий обработчик для всех исключений приложения
    app.add_exception_handler(ApplicationException, application_exception_handler)

    # Обработчик для исключений authx
    app.add_exception_handler(AuthXException, authx_exception_handler)

    # Обработчик для ошибок валидации (422)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    # Обработчик для ошибок аутентификации API ключа
    app.add_exception_handler(HTTPException, api_key_authentication_handler)
