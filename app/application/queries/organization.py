from dataclasses import dataclass
from typing import Iterable

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
    activity_id: str
    limit: int
    offset: int


@dataclass(frozen=True)
class SearchOrganizationsByNameQuery(BaseQuery):
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
    BaseQueryHandler[GetOrganizationsByAddressQuery, Iterable[OrganizationEntity]],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationsByAddressQuery,
    ) -> Iterable[OrganizationEntity]:
        return await self.organization_service.get_organizations_by_address(
            address=query.address,
            limit=query.limit,
            offset=query.offset,
        )


@dataclass(frozen=True)
class GetOrganizationsByActivityQueryHandler(
    BaseQueryHandler[GetOrganizationsByActivityQuery, Iterable[OrganizationEntity]],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationsByActivityQuery,
    ) -> Iterable[OrganizationEntity]:
        return await self.organization_service.get_organizations_by_activity(
            activity_id=query.activity_id,
            limit=query.limit,
            offset=query.offset,
        )


@dataclass(frozen=True)
class SearchOrganizationsByNameQueryHandler(
    BaseQueryHandler[SearchOrganizationsByNameQuery, Iterable[OrganizationEntity]],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: SearchOrganizationsByNameQuery,
    ) -> Iterable[OrganizationEntity]:
        return await self.organization_service.get_organizations_by_name(
            name=query.name,
            limit=query.limit,
            offset=query.offset,
        )


@dataclass(frozen=True)
class GetOrganizationsByRadiusQueryHandler(
    BaseQueryHandler[GetOrganizationsByRadiusQuery, Iterable[OrganizationEntity]],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationsByRadiusQuery,
    ) -> Iterable[OrganizationEntity]:
        return await self.organization_service.get_organizations_by_radius(
            latitude=query.latitude,
            longitude=query.longitude,
            radius=query.radius,
            limit=query.limit,
            offset=query.offset,
        )


@dataclass(frozen=True)
class GetOrganizationsByRectangleQueryHandler(
    BaseQueryHandler[GetOrganizationsByRectangleQuery, Iterable[OrganizationEntity]],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationsByRectangleQuery,
    ) -> Iterable[OrganizationEntity]:
        return await self.organization_service.get_organizations_by_rectangle(
            lat_min=query.lat_min,
            lat_max=query.lat_max,
            lon_min=query.lon_min,
            lon_max=query.lon_max,
            limit=query.limit,
            offset=query.offset,
        )
