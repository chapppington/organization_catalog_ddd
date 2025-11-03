from dataclasses import (
    dataclass,
    field,
)
from typing import Optional

from domain.base.entity import BaseEntity
from domain.organization.exceptions import ActivityNestingLevelExceededException
from domain.organization.value_objects import (
    ActivityNameValueObject,
    BuildingAddressValueObject,
    BuildingCoordinatesValueObject,
    OrganizationNameValueObject,
    OrganizationPhoneValueObject,
)
from settings import config


@dataclass(eq=False)
class ActivityEntity(BaseEntity):
    name: ActivityNameValueObject
    parent: Optional["ActivityEntity"] = field(default=None, kw_only=True)

    def __post_init__(self):
        self._validate_nesting_level()

    def _validate_nesting_level(self):
        """Validate that the activity nesting level does not exceed the maximum
        allowed level."""
        max_level = config.max_activity_nesting_level
        level = self._calculate_nesting_level()
        if level > max_level:
            raise ActivityNestingLevelExceededException(
                current_level=level,
                max_level=max_level,
            )

    def _calculate_nesting_level(self) -> int:
        """Calculate the nesting level of this activity in the hierarchy."""
        if self.parent is None:
            return 1

        return 1 + self.parent._calculate_nesting_level()


@dataclass(eq=False)
class BuildingEntity(BaseEntity):
    address: BuildingAddressValueObject
    coordinates: BuildingCoordinatesValueObject


@dataclass(eq=False)
class OrganizationEntity(BaseEntity):
    name: OrganizationNameValueObject
    building: BuildingEntity
    phones: list[OrganizationPhoneValueObject] = field(
        default_factory=list,
        kw_only=True,
    )
    activities: list[ActivityEntity] = field(default_factory=list, kw_only=True)
