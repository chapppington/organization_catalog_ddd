from dataclasses import dataclass
from typing import (
    Iterable,
    Tuple,
)
from uuid import UUID

from application.queries.base import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organization.entities import ActivityEntity
from domain.organization.interfaces.repositories.activity import BaseActivityRepository


@dataclass(frozen=True)
class GetActivityByIdQuery(BaseQuery):
    activity_id: UUID


@dataclass(frozen=True)
class GetActivitiesQuery(BaseQuery):
    name: str | None = None
    parent_id: UUID | None = None
    limit: int = 10
    offset: int = 0


@dataclass(frozen=True)
class GetActivityByIdQueryHandler(
    BaseQueryHandler[GetActivityByIdQuery, ActivityEntity | None],
):
    activity_repository: BaseActivityRepository

    async def handle(
        self,
        query: GetActivityByIdQuery,
    ) -> ActivityEntity | None:
        return await self.activity_repository.get_by_id(query.activity_id)


@dataclass(frozen=True)
class GetActivitiesQueryHandler(
    BaseQueryHandler[
        GetActivitiesQuery,
        Tuple[Iterable[ActivityEntity], int],
    ],
):
    activity_repository: BaseActivityRepository

    async def handle(
        self,
        query: GetActivitiesQuery,
    ) -> Tuple[Iterable[ActivityEntity], int]:
        filters_dict = {}
        if query.name is not None:
            filters_dict["name"] = query.name
        if query.parent_id is not None:
            filters_dict["parent_id"] = query.parent_id

        activities = list(await self.activity_repository.filter(**filters_dict))
        total = len(activities)

        paginated_activities = activities[query.offset : query.offset + query.limit]

        return paginated_activities, total
