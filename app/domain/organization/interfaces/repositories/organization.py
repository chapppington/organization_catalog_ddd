from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from domain.organization.entities import OrganizationEntity


@dataclass
class BaseOrganizationRepository(ABC):
    @abstractmethod
    async def add(self, organization: OrganizationEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, organization_id: UUID) -> OrganizationEntity | None: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Iterable[OrganizationEntity]: ...

    @abstractmethod
    async def get_by_building_id(
        self,
        building_id: UUID,
    ) -> Iterable[OrganizationEntity]: ...

    @abstractmethod
    async def get_by_activity_name(
        self,
        activity_name: str,
    ) -> Iterable[OrganizationEntity]: ...
