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
from presentation.api.v1.activity.schemas import (
    ActivityDetailSchema,
    ActivityResponseSchema,
    CreateActivityRequestSchema,
)

from application.commands.activity import CreateActivityCommand
from application.init import init_container
from application.mediator import Mediator
from application.queries.activity import (
    GetActivitiesQuery,
    GetActivityByIdQuery,
)


router = APIRouter(prefix="/activities", tags=["activities"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[ActivityResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[ActivityResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorSchema},
    },
)
async def create_activity(
    request: CreateActivityRequestSchema,
    container=Depends(init_container),
) -> ApiResponse[ActivityResponseSchema]:
    """Создает новый вид деятельности."""
    mediator: Mediator = container.resolve(Mediator)
    command = CreateActivityCommand(
        name=request.name,
        parent_id=request.parent_id,
    )
    results = await mediator.handle_command(command)
    activity = results[0]

    return ApiResponse[ActivityResponseSchema](
        data=ActivityResponseSchema.from_entity(activity),
    )


@router.get(
    "/{activity_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ActivityDetailSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[ActivityDetailSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def get_activity_by_id(
    activity_id: UUID,
    container=Depends(init_container),
) -> ApiResponse[ActivityDetailSchema]:
    """Получает вид деятельности по ID."""
    mediator: Mediator = container.resolve(Mediator)
    query = GetActivityByIdQuery(activity_id=activity_id)
    activity = await mediator.handle_query(query)

    if not activity:
        return ApiResponse[ActivityDetailSchema](
            data={},
            errors=[{"message": "Activity not found"}],
        )

    return ApiResponse[ActivityDetailSchema](
        data=ActivityDetailSchema.from_entity(activity),
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ListPaginatedResponse[ActivityResponseSchema]],
    responses={
        status.HTTP_200_OK: {
            "model": ApiResponse[ListPaginatedResponse[ActivityResponseSchema]],
        },
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
)
async def get_activities(
    name: str | None = Query(None, description="Название вида деятельности"),
    parent_id: UUID | None = Query(None, description="ID родительской деятельности"),
    pagination: PaginationIn = Depends(),
    container=Depends(init_container),
) -> ApiResponse[ListPaginatedResponse[ActivityResponseSchema]]:
    """Получает список видов деятельности с фильтрацией."""
    mediator: Mediator = container.resolve(Mediator)
    query = GetActivitiesQuery(
        name=name,
        parent_id=parent_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    activities, total = await mediator.handle_query(query)

    items = [ActivityResponseSchema.from_entity(activity) for activity in activities]

    return ApiResponse[ListPaginatedResponse[ActivityResponseSchema]](
        data=ListPaginatedResponse[ActivityResponseSchema](
            items=items,
            pagination=PaginationOut(
                limit=pagination.limit,
                offset=pagination.offset,
                total=total,
            ),
        ),
    )
