from dataclasses import (
    dataclass,
    field,
)
from typing import Iterable

from domain.organization.entities import OrganizationEntity
from domain.organization.interfaces.repositories.filters import OrganizationFilter
from domain.organization.interfaces.repositories.organization import (
    BaseOrganizationRepository,
)


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

    async def filter(self, filters: OrganizationFilter) -> Iterable[OrganizationEntity]:
        results = self._saved_organizations.copy()

        if filters.name:
            search_term = filters.name.lower()
            results = [
                org
                for org in results
                if search_term in org.name.as_generic_type().lower()
            ]

        if filters.address:
            search_term = filters.address.lower()
            results = [
                org
                for org in results
                if search_term in org.building.address.as_generic_type().lower()
            ]

        if filters.activity_name:
            search_term = filters.activity_name.lower()
            results = [
                org
                for org in results
                if any(
                    search_term in activity.name.as_generic_type().lower()
                    for activity in org.activities
                )
            ]

        return results
