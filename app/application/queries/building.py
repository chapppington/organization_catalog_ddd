from dataclasses import dataclass
from typing import (
    Iterable,
    Tuple,
)
from uuid import UUID

from application.queries.base import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organization.entities import BuildingEntity
from domain.organization.interfaces.repositories.building import BaseBuildingRepository


@dataclass(frozen=True)
class GetBuildingByIdQuery(BaseQuery):
    building_id: UUID


@dataclass(frozen=True)
class GetBuildingsQuery(BaseQuery):
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    limit: int = 10
    offset: int = 0


@dataclass(frozen=True)
class GetBuildingByIdQueryHandler(
    BaseQueryHandler[GetBuildingByIdQuery, BuildingEntity | None],
):
    building_repository: BaseBuildingRepository

    async def handle(
        self,
        query: GetBuildingByIdQuery,
    ) -> BuildingEntity | None:
        return await self.building_repository.get_by_id(query.building_id)


@dataclass(frozen=True)
class GetBuildingsQueryHandler(
    BaseQueryHandler[
        GetBuildingsQuery,
        Tuple[Iterable[BuildingEntity], int],
    ],
):
    building_repository: BaseBuildingRepository

    async def handle(
        self,
        query: GetBuildingsQuery,
    ) -> Tuple[Iterable[BuildingEntity], int]:
        filters_dict = {}
        if query.address is not None:
            filters_dict["address"] = query.address
        if query.latitude is not None:
            filters_dict["latitude"] = query.latitude
        if query.longitude is not None:
            filters_dict["longitude"] = query.longitude

        buildings = list(await self.building_repository.filter(**filters_dict))
        total = len(buildings)

        paginated_buildings = buildings[query.offset : query.offset + query.limit]

        return paginated_buildings, total
