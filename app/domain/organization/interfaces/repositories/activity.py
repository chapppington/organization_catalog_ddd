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

from domain.organization.entities import ActivityEntity


@dataclass
class BaseActivityRepository(ABC):
    @abstractmethod
    async def add(self, activity: ActivityEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, activity_id: UUID) -> ActivityEntity | None: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> ActivityEntity | None: ...

    @abstractmethod
    async def filter(self, **filters: Any) -> Iterable[ActivityEntity]: ...
