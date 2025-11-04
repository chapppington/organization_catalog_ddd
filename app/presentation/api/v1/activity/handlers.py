from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from application.commands.activity import CreateActivityCommand
from application.init import init_container
from application.mediator import Mediator
from domain.organization.interfaces.repositories.activity import BaseActivityRepository
from domain.organization.interfaces.repositories.filters import ActivityFilter
from presentation.api.filters import (
    PaginationIn,
    PaginationOut,
)
from presentation.api.schemas import (
    ApiResponse,
    ListPaginatedResponse,
)
from presentation.api.v1.activity.schemas import (
    ActivityDetailSchema,
    ActivityResponseSchema,
    CreateActivityRequestSchema,
)


router = APIRouter(prefix="/activities", tags=["activities"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[ActivityResponseSchema],
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
)
async def get_activity_by_id(
    activity_id: str,
    container=Depends(init_container),
) -> ApiResponse[ActivityDetailSchema]:
    """Получает вид деятельности по ID."""
    repository: BaseActivityRepository = container.resolve(BaseActivityRepository)
    activity = await repository.get_by_id(activity_id)

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
)
async def get_activities(
    name: str | None = Query(None, description="Название вида деятельности"),
    parent_id: str | None = Query(None, description="ID родительской деятельности"),
    pagination: PaginationIn = Depends(),
    container=Depends(init_container),
) -> ApiResponse[ListPaginatedResponse[ActivityResponseSchema]]:
    """Получает список видов деятельности с фильтрацией."""
    repository: BaseActivityRepository = container.resolve(BaseActivityRepository)
    filters = ActivityFilter(name=name, parent_id=parent_id)
    activities = list(await repository.filter(filters))

    items = [
        ActivityResponseSchema.from_entity(activity)
        for activity in activities[
            pagination.offset : pagination.offset + pagination.limit
        ]
    ]

    return ApiResponse[ListPaginatedResponse[ActivityResponseSchema]](
        data=ListPaginatedResponse[ActivityResponseSchema](
            items=items,
            pagination=PaginationOut(
                limit=pagination.limit,
                offset=pagination.offset,
            ),
        ),
    )
