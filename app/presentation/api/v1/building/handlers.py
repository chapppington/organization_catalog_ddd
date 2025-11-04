from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from application.commands.building import CreateBuildingCommand
from application.init import init_container
from application.mediator import Mediator
from domain.organization.interfaces.repositories.building import BaseBuildingRepository
from domain.organization.interfaces.repositories.filters import BuildingFilter
from presentation.api.filters import (
    PaginationIn,
    PaginationOut,
)
from presentation.api.schemas import (
    ApiResponse,
    ListPaginatedResponse,
)
from presentation.api.v1.building.schemas import (
    BuildingDetailSchema,
    BuildingResponseSchema,
    CreateBuildingRequestSchema,
)


router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[BuildingResponseSchema],
)
async def create_building(
    request: CreateBuildingRequestSchema,
    container=Depends(init_container),
) -> ApiResponse[BuildingResponseSchema]:
    """Создает новое здание."""
    mediator: Mediator = container.resolve(Mediator)
    command = CreateBuildingCommand(
        address=request.address,
        latitude=request.latitude,
        longitude=request.longitude,
    )
    results = await mediator.handle_command(command)
    building = results[0]

    return ApiResponse[BuildingResponseSchema](
        data=BuildingResponseSchema.from_entity(building),
    )


@router.get(
    "/{building_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[BuildingDetailSchema],
)
async def get_building_by_id(
    building_id: str,
    container=Depends(init_container),
) -> ApiResponse[BuildingDetailSchema]:
    """Получает здание по ID."""
    repository: BaseBuildingRepository = container.resolve(BaseBuildingRepository)
    building = await repository.get_by_id(building_id)

    if not building:
        return ApiResponse[BuildingDetailSchema](
            data={},
            errors=[{"message": "Building not found"}],
        )

    return ApiResponse[BuildingDetailSchema](
        data=BuildingDetailSchema.from_entity(building),
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ListPaginatedResponse[BuildingResponseSchema]],
)
async def get_buildings(
    address: str | None = Query(None, description="Адрес здания"),
    latitude: float | None = Query(None, description="Широта"),
    longitude: float | None = Query(None, description="Долгота"),
    pagination: PaginationIn = Depends(),
    container=Depends(init_container),
) -> ApiResponse[ListPaginatedResponse[BuildingResponseSchema]]:
    """Получает список зданий с фильтрацией."""
    repository: BaseBuildingRepository = container.resolve(BaseBuildingRepository)
    filters = BuildingFilter(
        address=address,
        latitude=latitude,
        longitude=longitude,
    )
    buildings = list(await repository.filter(filters))

    items = [
        BuildingResponseSchema.from_entity(building)
        for building in buildings[
            pagination.offset : pagination.offset + pagination.limit
        ]
    ]

    return ApiResponse[ListPaginatedResponse[BuildingResponseSchema]](
        data=ListPaginatedResponse[BuildingResponseSchema](
            items=items,
            pagination=PaginationOut(
                limit=pagination.limit,
                offset=pagination.offset,
            ),
        ),
    )
