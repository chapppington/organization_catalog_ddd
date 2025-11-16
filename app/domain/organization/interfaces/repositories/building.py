from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from domain.organization.entities import BuildingEntity


@dataclass
class BaseBuildingRepository(ABC):
    @abstractmethod
    async def add(self, building: BuildingEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, building_id: UUID) -> BuildingEntity | None: ...

    @abstractmethod
    async def get_by_address(self, address: str) -> BuildingEntity | None: ...

    @abstractmethod
    async def filter_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float,
    ) -> Iterable[BuildingEntity]: ...

    @abstractmethod
    async def filter_by_bounding_box(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
    ) -> Iterable[BuildingEntity]: ...
