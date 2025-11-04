from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from domain.organization.entities import ActivityEntity
from domain.organization.interfaces.repositories.filters import ActivityFilter


@dataclass
class BaseActivityRepository(ABC):
    @abstractmethod
    async def add(self, activity: ActivityEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, activity_id: str) -> ActivityEntity | None: ...

    @abstractmethod
    async def filter(self, filters: ActivityFilter) -> Iterable[ActivityEntity]: ...
