from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from application.queries.base import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organization.entities import ActivityEntity
from domain.organization.services.activity import ActivityService


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
    activity_service: ActivityService

    async def handle(
        self,
        query: GetActivityByIdQuery,
    ) -> ActivityEntity | None:
        return await self.activity_service.get_activity_by_id(query.activity_id)


@dataclass(frozen=True)
class GetActivitiesQueryHandler(
    BaseQueryHandler[
        GetActivitiesQuery,
        tuple[Iterable[ActivityEntity], int],
    ],
):
    activity_service: ActivityService

    async def handle(
        self,
        query: GetActivitiesQuery,
    ) -> tuple[Iterable[ActivityEntity], int]:
        return await self.activity_service.get_activities(
            name=query.name,
            parent_id=query.parent_id,
            limit=query.limit,
            offset=query.offset,
        )
