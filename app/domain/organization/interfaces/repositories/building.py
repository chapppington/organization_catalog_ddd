from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Any,
    Iterable,
)
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
    async def filter(self, **filters: Any) -> Iterable[BuildingEntity]: ...

    @abstractmethod
    async def count(self, **filters: Any) -> int: ...
