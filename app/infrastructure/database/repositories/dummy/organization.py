from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Any,
    Iterable,
)

from domain.organization.entities import OrganizationEntity
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

    async def filter(self, **filters: Any) -> Iterable[OrganizationEntity]:
        results = self._saved_organizations.copy()

        if "name" in filters and filters["name"]:
            search_term = filters["name"].lower()
            results = [
                org
                for org in results
                if search_term in org.name.as_generic_type().lower()
            ]

        if "address" in filters and filters["address"]:
            search_term = filters["address"].lower()
            results = [
                org
                for org in results
                if org.building.address.as_generic_type().lower() == search_term
            ]

        if "building_id" in filters and filters["building_id"]:
            building_id = filters["building_id"]
            results = [org for org in results if org.building.oid == building_id]

        if "activity_name" in filters and filters["activity_name"]:
            search_term = filters["activity_name"].lower()
            results = [
                org
                for org in results
                if any(
                    search_term in activity.name.as_generic_type().lower()
                    for activity in org.activities
                )
            ]

        return results

    async def count(self, **filters: Any) -> int:
        results = list(await self.filter(**filters))
        return len(results)
