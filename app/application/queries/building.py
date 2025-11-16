from dataclasses import dataclass
from uuid import UUID

from application.queries.base import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organization.entities import BuildingEntity
from domain.organization.services.building import BuildingService


@dataclass(frozen=True)
class GetBuildingByIdQuery(BaseQuery):
    building_id: UUID


@dataclass(frozen=True)
class GetBuildingByAddressQuery(BaseQuery):
    address: str


@dataclass(frozen=True)
class GetBuildingByIdQueryHandler(
    BaseQueryHandler[GetBuildingByIdQuery, BuildingEntity | None],
):
    building_service: BuildingService

    async def handle(
        self,
        query: GetBuildingByIdQuery,
    ) -> BuildingEntity | None:
        return await self.building_service.get_building_by_id(query.building_id)


@dataclass(frozen=True)
class GetBuildingByAddressQueryHandler(
    BaseQueryHandler[GetBuildingByAddressQuery, BuildingEntity | None],
):
    building_service: BuildingService

    async def handle(
        self,
        query: GetBuildingByAddressQuery,
    ) -> BuildingEntity | None:
        return await self.building_service.get_building_by_address(query.address)
