from collections.abc import Iterable
from dataclasses import dataclass

from application.queries.base import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organization.entities import OrganizationEntity
from domain.organization.services import OrganizationService


@dataclass(frozen=True)
class GetOrganizationByIdQuery(BaseQuery):
    organization_id: str


@dataclass(frozen=True)
class GetOrganizationsByAddressQuery(BaseQuery):
    address: str
    limit: int
    offset: int


@dataclass(frozen=True)
class GetOrganizationsByActivityQuery(BaseQuery):
    activity_name: str
    limit: int
    offset: int


@dataclass(frozen=True)
class GetOrganizationsByNameQuery(BaseQuery):
    name: str
    limit: int
    offset: int


@dataclass(frozen=True)
class GetOrganizationsByRadiusQuery(BaseQuery):
    latitude: float
    longitude: float
    radius: float
    limit: int
    offset: int


@dataclass(frozen=True)
class GetOrganizationsByRectangleQuery(BaseQuery):
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float
    limit: int
    offset: int


@dataclass(frozen=True)
class GetOrganizationByIdQueryHandler(
    BaseQueryHandler[GetOrganizationByIdQuery, OrganizationEntity | None],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationByIdQuery,
    ) -> OrganizationEntity | None:
        return await self.organization_service.get_organization_by_id(
            query.organization_id,
        )


@dataclass(frozen=True)
class GetOrganizationsByAddressQueryHandler(
    BaseQueryHandler[
        GetOrganizationsByAddressQuery,
        tuple[Iterable[OrganizationEntity], int],
    ],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationsByAddressQuery,
    ) -> tuple[Iterable[OrganizationEntity], int]:
        return await self.organization_service.get_organizations_by_address(
            address=query.address,
            limit=query.limit,
            offset=query.offset,
        )


@dataclass(frozen=True)
class GetOrganizationsByActivityQueryHandler(
    BaseQueryHandler[
        GetOrganizationsByActivityQuery,
        tuple[Iterable[OrganizationEntity], int],
    ],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationsByActivityQuery,
    ) -> tuple[Iterable[OrganizationEntity], int]:
        return await self.organization_service.get_organizations_by_activity(
            activity_name=query.activity_name,
            limit=query.limit,
            offset=query.offset,
        )


@dataclass(frozen=True)
class GetOrganizationsByNameQueryHandler(
    BaseQueryHandler[
        GetOrganizationsByNameQuery,
        tuple[Iterable[OrganizationEntity], int],
    ],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationsByNameQuery,
    ) -> tuple[Iterable[OrganizationEntity], int]:
        return await self.organization_service.get_organizations_by_name(
            name=query.name,
            limit=query.limit,
            offset=query.offset,
        )


@dataclass(frozen=True)
class GetOrganizationsByRadiusQueryHandler(
    BaseQueryHandler[
        GetOrganizationsByRadiusQuery,
        tuple[Iterable[OrganizationEntity], int],
    ],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationsByRadiusQuery,
    ) -> tuple[Iterable[OrganizationEntity], int]:
        return await self.organization_service.get_organizations_by_radius(
            latitude=query.latitude,
            longitude=query.longitude,
            radius=query.radius,
            limit=query.limit,
            offset=query.offset,
        )


@dataclass(frozen=True)
class GetOrganizationsByRectangleQueryHandler(
    BaseQueryHandler[
        GetOrganizationsByRectangleQuery,
        tuple[Iterable[OrganizationEntity], int],
    ],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationsByRectangleQuery,
    ) -> tuple[Iterable[OrganizationEntity], int]:
        return await self.organization_service.get_organizations_by_rectangle(
            lat_min=query.lat_min,
            lat_max=query.lat_max,
            lon_min=query.lon_min,
            lon_max=query.lon_max,
            limit=query.limit,
            offset=query.offset,
        )
