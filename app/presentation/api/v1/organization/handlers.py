from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from presentation.api.filters import (
    PaginationIn,
    PaginationOut,
)
from presentation.api.schemas import (
    ApiResponse,
    ErrorSchema,
    ListPaginatedResponse,
)
from presentation.api.v1.organization.schemas import (
    CreateOrganizationRequestSchema,
    OrganizationDetailSchema,
)

from application.commands.organization import CreateOrganizationCommand
from application.init import init_container
from application.mediator import Mediator
from application.queries.organization import (
    GetOrganizationByIdQuery,
    GetOrganizationsByActivityQuery,
    GetOrganizationsByAddressQuery,
    GetOrganizationsByNameQuery,
    GetOrganizationsByRadiusQuery,
    GetOrganizationsByRectangleQuery,
)


router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[OrganizationDetailSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[OrganizationDetailSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorSchema},
    },
)
async def create_organization(
    request: CreateOrganizationRequestSchema,
    container=Depends(init_container),
) -> ApiResponse[OrganizationDetailSchema]:
    """Создает новую организацию."""
    mediator: Mediator = container.resolve(Mediator)
    command = CreateOrganizationCommand(
        name=request.name,
        address=request.address,
        phones=request.phones,
        activities=request.activities,
    )
    results = await mediator.handle_command(command)
    organization = results[0]

    return ApiResponse[OrganizationDetailSchema](
        data=OrganizationDetailSchema.from_entity(organization),
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]],
    responses={
        status.HTTP_200_OK: {
            "model": ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]],
        },
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
)
async def get_organizations_by_name(
    name: str = Query(..., description="Название организации"),
    pagination: PaginationIn = Depends(),
    container=Depends(init_container),
) -> ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]]:
    """Поиск организаций по названию."""
    mediator: Mediator = container.resolve(Mediator)
    query = GetOrganizationsByNameQuery(
        name=name,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    organizations, total = await mediator.handle_query(query)

    items = [OrganizationDetailSchema.from_entity(org) for org in organizations]

    return ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]](
        data=ListPaginatedResponse[OrganizationDetailSchema](
            items=items,
            pagination=PaginationOut(
                limit=pagination.limit,
                offset=pagination.offset,
                total=total,
            ),
        ),
    )


@router.get(
    "/by-address",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]],
    responses={
        status.HTTP_200_OK: {
            "model": ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]],
        },
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
)
async def get_organizations_by_address(
    address: str = Query(..., description="Адрес здания"),
    pagination: PaginationIn = Depends(),
    container=Depends(init_container),
) -> ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]]:
    """Список организаций по адресу."""
    mediator: Mediator = container.resolve(Mediator)
    query = GetOrganizationsByAddressQuery(
        address=address,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    organizations, total = await mediator.handle_query(query)
    organizations_list = list(organizations)

    items = [OrganizationDetailSchema.from_entity(org) for org in organizations_list]

    return ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]](
        data=ListPaginatedResponse[OrganizationDetailSchema](
            items=items,
            pagination=PaginationOut(
                limit=pagination.limit,
                offset=pagination.offset,
                total=total,
            ),
        ),
    )


@router.get(
    "/by-activity",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]],
    responses={
        status.HTTP_200_OK: {
            "model": ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]],
        },
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
)
async def get_organizations_by_activity(
    activity_name: str = Query(..., description="Название вида деятельности"),
    pagination: PaginationIn = Depends(),
    container=Depends(init_container),
) -> ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]]:
    """Поиск организаций по виду деятельности."""
    mediator: Mediator = container.resolve(Mediator)
    query = GetOrganizationsByActivityQuery(
        activity_name=activity_name,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    organizations, total = await mediator.handle_query(query)

    items = [OrganizationDetailSchema.from_entity(org) for org in organizations]

    return ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]](
        data=ListPaginatedResponse[OrganizationDetailSchema](
            items=items,
            pagination=PaginationOut(
                limit=pagination.limit,
                offset=pagination.offset,
                total=total,
            ),
        ),
    )


@router.get(
    "/by-radius",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]],
    responses={
        status.HTTP_200_OK: {
            "model": ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]],
        },
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
)
async def get_organizations_by_radius(
    latitude: float = Query(..., description="Широта центральной точки"),
    longitude: float = Query(..., description="Долгота центральной точки"),
    radius: float = Query(..., description="Радиус поиска в метрах"),
    pagination: PaginationIn = Depends(),
    container=Depends(init_container),
) -> ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]]:
    """Поиск организаций в заданном радиусе."""
    mediator: Mediator = container.resolve(Mediator)
    query = GetOrganizationsByRadiusQuery(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    organizations, total = await mediator.handle_query(query)

    items = [OrganizationDetailSchema.from_entity(org) for org in organizations]

    return ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]](
        data=ListPaginatedResponse[OrganizationDetailSchema](
            items=items,
            pagination=PaginationOut(
                limit=pagination.limit,
                offset=pagination.offset,
                total=total,
            ),
        ),
    )


@router.get(
    "/by-rectangle",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]],
    responses={
        status.HTTP_200_OK: {
            "model": ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]],
        },
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
)
async def get_organizations_by_rectangle(
    lat_min: float = Query(..., description="Минимальная широта"),
    lat_max: float = Query(..., description="Максимальная широта"),
    lon_min: float = Query(..., description="Минимальная долгота"),
    lon_max: float = Query(..., description="Максимальная долгота"),
    pagination: PaginationIn = Depends(),
    container=Depends(init_container),
) -> ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]]:
    """Поиск организаций в прямоугольной области."""
    mediator: Mediator = container.resolve(Mediator)
    query = GetOrganizationsByRectangleQuery(
        lat_min=lat_min,
        lat_max=lat_max,
        lon_min=lon_min,
        lon_max=lon_max,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    organizations, total = await mediator.handle_query(query)

    items = [OrganizationDetailSchema.from_entity(org) for org in organizations]

    return ApiResponse[ListPaginatedResponse[OrganizationDetailSchema]](
        data=ListPaginatedResponse[OrganizationDetailSchema](
            items=items,
            pagination=PaginationOut(
                limit=pagination.limit,
                offset=pagination.offset,
                total=total,
            ),
        ),
    )


@router.get(
    "/{organization_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[OrganizationDetailSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[OrganizationDetailSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def get_organization_by_id(
    organization_id: UUID,
    container=Depends(init_container),
) -> ApiResponse[OrganizationDetailSchema]:
    """Получает организацию по ID."""
    mediator: Mediator = container.resolve(Mediator)
    query = GetOrganizationByIdQuery(organization_id=organization_id)
    organization = await mediator.handle_query(query)

    if not organization:
        return ApiResponse[OrganizationDetailSchema](
            data={},
            errors=[{"message": "Organization not found"}],
        )

    return ApiResponse[OrganizationDetailSchema](
        data=OrganizationDetailSchema.from_entity(organization),
    )
