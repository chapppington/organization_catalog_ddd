from dataclasses import dataclass
from uuid import UUID

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
