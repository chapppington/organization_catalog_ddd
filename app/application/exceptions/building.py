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
