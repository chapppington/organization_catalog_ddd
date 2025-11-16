from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from presentation.api.schemas import (
    ApiResponse,
    ErrorSchema,
)
from presentation.api.v1.building.schemas import (
    BuildingDetailSchema,
    BuildingResponseSchema,
    CreateBuildingRequestSchema,
)

from application.commands.building import CreateBuildingCommand
from application.init import init_container
from application.mediator import Mediator
from application.queries.building import (
    GetBuildingByAddressQuery,
    GetBuildingByIdQuery,
)


router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[BuildingResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[BuildingResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorSchema},
    },
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
    "/by-address",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[BuildingDetailSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[BuildingDetailSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def get_building_by_address(
    address: str = Query(..., description="Адрес здания"),
    container=Depends(init_container),
) -> ApiResponse[BuildingDetailSchema]:
    """Получает здание по адресу."""
    mediator: Mediator = container.resolve(Mediator)
    query = GetBuildingByAddressQuery(address=address)
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
    "/{building_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[BuildingDetailSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[BuildingDetailSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def get_building_by_id(
    building_id: UUID,
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
