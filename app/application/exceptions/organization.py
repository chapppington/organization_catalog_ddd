from dataclasses import dataclass

from application.exceptions.base import LogicException


@dataclass(eq=False)
class OrganizationWithThatNameAlreadyExistsException(LogicException):
    name: str

    @property
    def message(self):
        return f"Organization with name '{self.name}' already exists."


@dataclass(eq=False)
class OrganizationNotFoundException(LogicException):
    organization_oid: str

    @property
    def message(self):
        return "Organization with this ID not found."
