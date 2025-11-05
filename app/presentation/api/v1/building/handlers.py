from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from application.commands.building import CreateBuildingCommand
from application.init import init_container
from application.mediator import Mediator
from application.queries.building import (
    GetBuildingByIdQuery,
    GetBuildingsQuery,
)
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
    mediator: Mediator = container.resolve(Mediator)
    query = GetBuildingByIdQuery(building_id=building_id)
    building = await mediator.handle_query(query)

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
    mediator: Mediator = container.resolve(Mediator)
    query = GetBuildingsQuery(
        address=address,
        latitude=latitude,
        longitude=longitude,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    buildings, total = await mediator.handle_query(query)

    items = [BuildingResponseSchema.from_entity(building) for building in buildings]

    return ApiResponse[ListPaginatedResponse[BuildingResponseSchema]](
        data=ListPaginatedResponse[BuildingResponseSchema](
            items=items,
            pagination=PaginationOut(
                limit=pagination.limit,
                offset=pagination.offset,
                total=total,
            ),
        ),
    )
