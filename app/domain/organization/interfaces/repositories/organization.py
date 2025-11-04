from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from domain.organization.entities import OrganizationEntity
from domain.organization.interfaces.repositories.filters import OrganizationFilter


@dataclass
class BaseOrganizationRepository(ABC):
    @abstractmethod
    async def add(self, organization: OrganizationEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, organization_id: str) -> OrganizationEntity | None: ...

    @abstractmethod
    async def filter(
        self,
        filters: OrganizationFilter,
    ) -> Iterable[OrganizationEntity]: ...
