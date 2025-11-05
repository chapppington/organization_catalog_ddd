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

from domain.organization.entities import OrganizationEntity


@dataclass
class BaseOrganizationRepository(ABC):
    @abstractmethod
    async def add(self, organization: OrganizationEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, organization_id: UUID) -> OrganizationEntity | None: ...

    @abstractmethod
    async def filter(self, **filters: Any) -> Iterable[OrganizationEntity]: ...
