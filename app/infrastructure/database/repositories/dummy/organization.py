from dataclasses import (
    dataclass,
    field,
)
from typing import Iterable
from uuid import UUID

from domain.organization.entities import OrganizationEntity
from domain.organization.interfaces.repositories.organization import BaseOrganizationRepository


@dataclass
class DummyInMemoryOrganizationRepository(BaseOrganizationRepository):
    _saved_organizations: list[OrganizationEntity] = field(
        default_factory=list,
        kw_only=True,
    )

    async def add(self, organization: OrganizationEntity) -> None:
        self._saved_organizations.append(organization)

    async def get_by_id(self, organization_id: str) -> OrganizationEntity | None:
        try:
            return next(
                org for org in self._saved_organizations if org.oid == organization_id
            )
        except StopIteration:
            return None

    async def get_by_name(self, name: str) -> Iterable[OrganizationEntity]:
        search_term = name.lower()
        return [
            org
            for org in self._saved_organizations
            if search_term in org.name.as_generic_type().lower()
        ]

    async def get_by_building_id(
        self, building_id: UUID,
    ) -> Iterable[OrganizationEntity]:
        return [
            org for org in self._saved_organizations if org.building.oid == building_id
        ]

    async def get_by_activity_name(
        self, activity_name: str,
    ) -> Iterable[OrganizationEntity]:
        search_term = activity_name.lower()
        return [
            org
            for org in self._saved_organizations
            if any(
                search_term in activity.name.as_generic_type().lower()
                for activity in org.activities
            )
        ]
