from dataclasses import dataclass
from uuid import UUID

from application.exceptions.base import LogicException


@dataclass(eq=False)
class ActivityWithThatNameAlreadyExistsException(LogicException):
    name: str
    parent_id: UUID | None = None

    @property
    def message(self):
        if self.parent_id:
            return f"Activity with name '{self.name}' already exists in this category."
        return f"Root activity with name '{self.name}' already exists."


@dataclass(eq=False)
class ActivityNotFoundException(LogicException):
    activity_oid: UUID

    @property
    def message(self):
        return "Activity with this ID not found."


@dataclass(eq=False)
class ActivityIdAlreadyExistsException(LogicException):
    activity_id: UUID

    @property
    def message(self):
        return f"Activity with ID {self.activity_id} already exists."


@dataclass(eq=False)
class ParentActivityNotFoundException(LogicException):
    parent_id: UUID

    @property
    def message(self):
        return f"Parent activity with ID {self.parent_id} not found."
