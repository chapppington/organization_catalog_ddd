from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from domain.organization.entities import BuildingEntity
from domain.organization.interfaces.repositories.filters import BuildingFilter


@dataclass
class BaseBuildingRepository(ABC):
    @abstractmethod
    async def add(self, building: BuildingEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, building_id: str) -> BuildingEntity | None: ...

    @abstractmethod
    async def filter(self, filters: BuildingFilter) -> Iterable[BuildingEntity]: ...
