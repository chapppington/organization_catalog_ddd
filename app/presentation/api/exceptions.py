from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from authx.exceptions import AuthXException
from presentation.api.schemas import ApiResponse

from application.exceptions.activity import ActivityNotFoundException
from application.exceptions.base import LogicException
from application.exceptions.building import BuildingNotFoundException
from application.exceptions.organization import OrganizationNotFoundException
from domain.organization.exceptions import (
    ActivityNotFoundException as DomainActivityNotFoundException,
    BuildingNotFoundException as DomainBuildingNotFoundException,
    OrganizationException,
)
from domain.user.exceptions import (
    InvalidCredentialsException,
    UserException,
)


async def logic_exception_handler(
    request: Request,
    exc: LogicException,
) -> JSONResponse:
    """Обработчик для логических исключений приложения."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ApiResponse(
            data={},
            errors=[{"message": exc.message}],
        ).model_dump(),
    )


async def activity_not_found_handler(
    request: Request,
    exc: ActivityNotFoundException | DomainActivityNotFoundException,
) -> JSONResponse:
    """Обработчик для случая, когда активность не найдена."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ApiResponse(
            data={},
            errors=[{"message": exc.message}],
        ).model_dump(),
    )


async def building_not_found_handler(
    request: Request,
    exc: BuildingNotFoundException | DomainBuildingNotFoundException,
) -> JSONResponse:
    """Обработчик для случая, когда здание не найдено."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ApiResponse(
            data={},
            errors=[{"message": exc.message}],
        ).model_dump(),
    )


async def organization_not_found_handler(
    request: Request,
    exc: OrganizationNotFoundException,
) -> JSONResponse:
    """Обработчик для случая, когда организация не найдена."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ApiResponse(
            data={},
            errors=[{"message": exc.message}],
        ).model_dump(),
    )


async def organization_exception_handler(
    request: Request,
    exc: OrganizationException,
) -> JSONResponse:
    """Обработчик для доменных исключений организации."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ApiResponse(
            data={},
            errors=[{"message": exc.message}],
        ).model_dump(),
    )


async def invalid_credentials_handler(
    request: Request,
    exc: InvalidCredentialsException,
) -> JSONResponse:
    """Обработчик для неверных учетных данных."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ApiResponse(
            data={},
            errors=[{"message": exc.message}],
        ).model_dump(),
    )


async def user_exception_handler(
    request: Request,
    exc: UserException,
) -> JSONResponse:
    """Обработчик для доменных исключений пользователя."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ApiResponse(
            data={},
            errors=[{"message": exc.message}],
        ).model_dump(),
    )


async def authx_exception_handler(
    request: Request,
    exc: AuthXException,
) -> JSONResponse:
    """Обработчик для исключений authx (отсутствие/невалидность токена)."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ApiResponse(
            data={},
            errors=[{"message": str(exc)}],
        ).model_dump(),
    )


async def api_key_authentication_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Обработчик для ошибок аутентификации API ключа.

    Обрабатывает HTTPException с кодами 401/403 и форматирует их в
    ApiResponse.

    """
    # Обрабатываем только ошибки аутентификации/авторизации
    if exc.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
        error_message = exc.detail
        # Улучшаем сообщение для случая отсутствия API ключа
        if error_message == "Not authenticated" or "Not authenticated" in error_message:
            error_message = "API key is required"

        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(
                data={},
                errors=[{"message": error_message}],
            ).model_dump(),
        )

    # Для других HTTPException возвращаем стандартный формат
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            data={},
            errors=[{"message": exc.detail}],
        ).model_dump(),
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Обработчик для ошибок валидации (422 Unprocessable Entity).

    Форматирует ошибки валидации FastAPI/Pydantic в формат ApiResponse.

    """
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

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ApiResponse(
            data={},
            errors=errors,
        ).model_dump(),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Настраивает обработчики исключений для FastAPI приложения."""
    # Регистрируем обработчик для логических исключений приложения
    app.add_exception_handler(LogicException, logic_exception_handler)

    # Обработчик для доменных исключений организации (возвращают 400)
    app.add_exception_handler(OrganizationException, organization_exception_handler)

    # Специфичные обработчики для NotFound исключений (возвращают 404)
    app.add_exception_handler(ActivityNotFoundException, activity_not_found_handler)
    app.add_exception_handler(
        DomainActivityNotFoundException,
        activity_not_found_handler,
    )
    app.add_exception_handler(BuildingNotFoundException, building_not_found_handler)
    app.add_exception_handler(
        DomainBuildingNotFoundException,
        building_not_found_handler,
    )
    app.add_exception_handler(
        OrganizationNotFoundException,
        organization_not_found_handler,
    )

    # Обработчики для исключений пользователей
    app.add_exception_handler(InvalidCredentialsException, invalid_credentials_handler)
    app.add_exception_handler(UserException, user_exception_handler)

    # Обработчик для исключений authx
    app.add_exception_handler(AuthXException, authx_exception_handler)

    # Обработчик для ошибок валидации (422)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    # Обработчик для ошибок аутентификации API ключа
    app.add_exception_handler(HTTPException, api_key_authentication_handler)
