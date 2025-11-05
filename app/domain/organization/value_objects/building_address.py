from dataclasses import dataclass

from domain.base.value_object import BaseValueObject
from domain.organization.exceptions import (
    BuildingAddressTooLongException,
    EmptyBuildingAddressException,
)


@dataclass(frozen=True)
class BuildingAddressValueObject(BaseValueObject):
    value: str
    MAX_LENGTH = 255

    def validate(self):
        if not self.value:
            raise EmptyBuildingAddressException()
        if len(self.value) > self.MAX_LENGTH:
            raise BuildingAddressTooLongException(
                address_length=len(self.value),
                max_length=self.MAX_LENGTH,
            )

    def as_generic_type(self) -> str:
        return str(self.value)
