from dataclasses import dataclass

from application.exceptions.base import LogicException


@dataclass(eq=False)
class BuildingWithThatAddressAlreadyExistsException(LogicException):
    address: str

    @property
    def message(self):
        return f'Building with address "{self.address}" already exists.'


@dataclass(eq=False)
class BuildingNotFoundException(LogicException):
    building_oid: str

    @property
    def message(self):
        return "Building with this ID not found."


@dataclass(eq=False)
class BuildingIdAlreadyExistsException(LogicException):
    building_id: str

    @property
    def message(self):
        return f"Building with ID {self.building_id} already exists."
