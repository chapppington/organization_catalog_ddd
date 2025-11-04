from dataclasses import dataclass

from application.exceptions.base import LogicException


@dataclass(eq=False)
class ActivityWithThatNameAlreadyExistsException(LogicException):
    name: str
    parent_id: str | None = None

    @property
    def message(self):
        if self.parent_id:
            return f'Activity with name "{self.name}" already exists in this category.'
        return f'Root activity with name "{self.name}" already exists.'


@dataclass(eq=False)
class ActivityNotFoundException(LogicException):
    activity_oid: str

    @property
    def message(self):
        return "Activity with this ID not found."
