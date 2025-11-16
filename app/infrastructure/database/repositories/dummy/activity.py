from collections.abc import Iterable
from dataclasses import (
    dataclass,
    field,
)
from typing import Any
from uuid import UUID

from domain.organization.entities import ActivityEntity
from domain.organization.interfaces.repositories.activity import BaseActivityRepository


@dataclass
class DummyInMemoryActivityRepository(BaseActivityRepository):
    _saved_activities: list[ActivityEntity] = field(default_factory=list, kw_only=True)

    async def add(self, activity: ActivityEntity) -> None:
        self._saved_activities.append(activity)

    async def get_by_id(self, activity_id: UUID) -> ActivityEntity | None:
        try:
            return next(activity for activity in self._saved_activities if activity.oid == activity_id)
        except StopIteration:
            return None

    async def get_by_name(self, name: str) -> ActivityEntity | None:
        try:
            search_term = name.lower()
            return next(
                activity
                for activity in self._saved_activities
                if activity.name.as_generic_type().lower() == search_term
            )
        except StopIteration:
            return None

    async def filter(self, **filters: Any) -> Iterable[ActivityEntity]:
        results = self._saved_activities.copy()

        if filters.get("name"):
            search_term = filters["name"].lower()
            results = [activity for activity in results if search_term in activity.name.as_generic_type().lower()]

        if filters.get("parent_id"):
            results = [
                activity for activity in results if activity.parent and activity.parent.oid == filters["parent_id"]
            ]

        return results
