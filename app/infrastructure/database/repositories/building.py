from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from infrastructure.database.converters.building import (
    building_entity_to_model,
    building_model_to_entity,
)
from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.building import BuildingModel
from sqlalchemy import (
    func,
    select,
)

from domain.organization.entities import BuildingEntity
from domain.organization.interfaces.repositories.building import BaseBuildingRepository


@dataclass
class SQLAlchemyBuildingRepository(BaseBuildingRepository):
    database: Database

    async def add(self, building: BuildingEntity) -> None:
        async with self.database.get_session() as session:
            model = building_entity_to_model(building)
            session.add(model)
            await session.commit()

    async def get_by_id(self, building_id: UUID) -> BuildingEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = select(BuildingModel).where(BuildingModel.oid == building_id)
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return building_model_to_entity(result) if result else None

    async def get_by_address(self, address: str) -> BuildingEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = select(BuildingModel).where(BuildingModel.address == address)
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return building_model_to_entity(result) if result else None

    async def filter_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float,
    ) -> Iterable[BuildingEntity]:
        async with self.database.get_read_only_session() as session:
            center_point_wkt = f"POINT({longitude} {latitude})"
            center_point = func.ST_GeogFromText(center_point_wkt)

            stmt = select(BuildingModel).where(
                BuildingModel.location.ST_DWithin(center_point, radius_meters),
            )

            res = await session.execute(stmt)
            results = [building_model_to_entity(row[0]) for row in res.all()]

            return results

    async def filter_by_bounding_box(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
    ) -> Iterable[BuildingEntity]:
        async with self.database.get_read_only_session() as session:
            # 5 точек потому что полигон должен быть замкнутым (последняя точка должна быть такой же как первая)
            bbox_wkt = (
                f"POLYGON(({lon_min} {lat_min}, {lon_max} {lat_min}, "
                f"{lon_max} {lat_max}, {lon_min} {lat_max}, {lon_min} {lat_min}))"
            )
            bbox_geography = func.ST_GeogFromText(bbox_wkt)

            stmt = select(BuildingModel).where(
                BuildingModel.location.ST_Intersects(bbox_geography),
            )

            res = await session.execute(stmt)
            results = [building_model_to_entity(row[0]) for row in res.all()]

            return results
