from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.responses import JSONResponse

from application.exceptions.activity import ActivityNotFoundException
from application.exceptions.base import LogicException
from application.exceptions.building import BuildingNotFoundException
from application.exceptions.organization import OrganizationNotFoundException
from domain.organization.exceptions import (
    ActivityNotFoundException as DomainActivityNotFoundException,
    BuildingNotFoundException as DomainBuildingNotFoundException,
)
from presentation.api.schemas import ApiResponse


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


def setup_exception_handlers(app: FastAPI) -> None:
    """Настраивает обработчики исключений для FastAPI приложения."""
    # Регистрируем обработчик для логических исключений приложения
    app.add_exception_handler(LogicException, logic_exception_handler)

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
