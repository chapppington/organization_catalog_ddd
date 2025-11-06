from dataclasses import (
    dataclass,
    field,
)

from domain.base.value_object import BaseValueObject
from domain.organization.exceptions import (
    BuildingAddressTooLongException,
    EmptyBuildingAddressException,
    InvalidBuildingLatitudeException,
    InvalidBuildingLongitudeException,
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


@dataclass(frozen=True)
class BuildingCoordinatesValueObject(BaseValueObject):
    latitude: float
    longitude: float
    value: tuple[float, float] = field(init=False, repr=False)

    def __post_init__(self):
        # Set the value field after initialization
        object.__setattr__(self, "value", (self.latitude, self.longitude))
        super().__post_init__()

    def validate(self):
        # Latitude must be between -90 and 90 degrees
        if not -90 <= self.latitude <= 90:
            raise InvalidBuildingLatitudeException(latitude=self.latitude)

        # Longitude must be between -180 and 180 degrees
        if not -180 <= self.longitude <= 180:
            raise InvalidBuildingLongitudeException(longitude=self.longitude)

    def as_generic_type(self) -> tuple[float, float]:
        return (self.latitude, self.longitude)
