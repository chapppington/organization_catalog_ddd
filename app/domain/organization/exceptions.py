from dataclasses import dataclass
from uuid import UUID

from domain.base.exceptions import ApplicationException


@dataclass(eq=False)
class OrganizationException(ApplicationException):
    @property
    def message(self) -> str:
        return "Organization exception occurred"


@dataclass(eq=False)
class EmptyOrganizationNameException(OrganizationException):
    @property
    def message(self) -> str:
        return "Organization name is empty"


@dataclass(eq=False)
class EmptyOrganizationPhoneException(OrganizationException):
    @property
    def message(self) -> str:
        return "Organization phone number is empty"


@dataclass(eq=False)
class InvalidOrganizationPhoneException(OrganizationException):
    phone: str

    @property
    def message(self) -> str:
        return f"Invalid organization phone number format: {self.phone}"


@dataclass(eq=False)
class EmptyBuildingAddressException(OrganizationException):
    @property
    def message(self) -> str:
        return "Building address is empty"


@dataclass(eq=False)
class BuildingAddressTooLongException(OrganizationException):
    address_length: int
    max_length: int

    @property
    def message(self) -> str:
        return (
            f"Building address is too long. Current length is {self.address_length}, "
            f"maximum allowed length is {self.max_length}"
        )


@dataclass(eq=False)
class InvalidBuildingLatitudeException(OrganizationException):
    latitude: float

    @property
    def message(self) -> str:
        return f"Invalid building latitude value: {self.latitude}. Latitude must be between -90 and 90 degrees"


@dataclass(eq=False)
class InvalidBuildingLongitudeException(OrganizationException):
    longitude: float

    @property
    def message(self) -> str:
        return f"Invalid building longitude value: {self.longitude}. Longitude must be between -180 and 180 degrees"


@dataclass(eq=False)
class InvalidBuildingCoordinatesException(OrganizationException):
    latitude: float
    longitude: float

    @property
    def message(self) -> str:
        return f"Invalid building coordinates: latitude={self.latitude}, longitude={self.longitude}"


@dataclass(eq=False)
class EmptyActivityNameException(OrganizationException):
    @property
    def message(self) -> str:
        return "Activity name is empty"


@dataclass(eq=False)
class ActivityNameTooLongException(OrganizationException):
    name_length: int
    max_length: int

    @property
    def message(self) -> str:
        return (
            f"Activity name is too long. Current length is {self.name_length}, "
            f"maximum allowed length is {self.max_length}"
        )


@dataclass(eq=False)
class ActivityNestingLevelExceededException(OrganizationException):
    current_level: int
    max_level: int

    @property
    def message(self) -> str:
        return (
            f"Activity nesting level exceeded. Current level is {self.current_level}, "
            f"maximum allowed level is {self.max_level}"
        )


@dataclass(eq=False)
class ActivityNotFoundException(OrganizationException):
    activity_id: UUID

    @property
    def message(self) -> str:
        return f"Activity with id {self.activity_id} not found"


@dataclass(eq=False)
class BuildingNotFoundException(OrganizationException):
    address: str

    @property
    def message(self) -> str:
        return f"Building with address {self.address} not found"
