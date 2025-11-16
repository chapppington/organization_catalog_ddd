from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from application.exceptions.activity import ActivityWithThatNameAlreadyExistsException
from domain.organization.entities import ActivityEntity
from domain.organization.exceptions import ActivityNotFoundException
from domain.organization.interfaces.repositories import BaseActivityRepository
from domain.organization.value_objects import ActivityNameValueObject


@dataclass
class ActivityService:
    activity_repository: BaseActivityRepository

    async def create_activity(
        self,
        name: str,
        parent_id: UUID | None = None,
    ) -> ActivityEntity:
        existing_activity = await self.activity_repository.get_by_name(name)
        if existing_activity:
            raise ActivityWithThatNameAlreadyExistsException(
                name=name,
                parent_id=parent_id,
            )

        parent = None
        if parent_id:
            parent = await self.activity_repository.get_by_id(parent_id)
            if not parent:
                raise ActivityNotFoundException(activity_id=parent_id)

        activity = ActivityEntity(
            name=ActivityNameValueObject(name),
            parent=parent,
        )
        await self.activity_repository.add(activity)
        return activity

    async def get_activity_by_id(
        self,
        activity_id: UUID,
    ) -> ActivityEntity | None:
        """Получить активность по ID."""
        return await self.activity_repository.get_by_id(activity_id)

    async def get_activities(
        self,
        name: str | None = None,
        parent_id: UUID | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[Iterable[ActivityEntity], int]:
        """Получить список активностей с фильтрацией и пагинацией."""
        filters_dict = {}
        if name is not None:
            filters_dict["name"] = name
        if parent_id is not None:
            filters_dict["parent_id"] = parent_id

        activities = list(await self.activity_repository.filter(**filters_dict))
        total = len(activities)

        paginated_activities = activities[offset : offset + limit]

        return paginated_activities, total
