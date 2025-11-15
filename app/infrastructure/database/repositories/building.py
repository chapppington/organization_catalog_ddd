import math
from dataclasses import dataclass
from typing import (
    Any,
    Iterable,
)
from uuid import UUID

from sqlalchemy import (
    func,
    literal,
    select,
)

from domain.organization.entities import BuildingEntity
from domain.organization.interfaces.repositories.building import BaseBuildingRepository
from infrastructure.database.converters.building import (
    building_entity_to_model,
    building_model_to_entity,
)
from infrastructure.database.models.building import BuildingModel
from infrastructure.database.gateways.postgres import Database


@dataclass
class SQLAlchemyBuildingRepository(BaseBuildingRepository):
    database: Database

    @staticmethod
    def _haversine_distance_sql(
        center_latitude: float,
        center_longitude: float,
    ) -> Any:
        """Вычисляет SQL-выражение для расстояния по формуле Haversine.

        Args:
            center_latitude: Широта центральной точки
            center_longitude: Долгота центральной точки

        Returns:
            SQL-выражение для вычисления расстояния в метрах

        """
        R = 6371000  # Радиус Земли в метрах

        # Преобразуем в радианы
        lat1_rad = math.radians(center_latitude)
        lon1_rad = math.radians(center_longitude)

        # Вычисляем расстояние для каждого здания
        # Используем PostgreSQL функции: radians, sin, cos, acos
        distance_expr = (
            literal(R)
            * func.acos(
                func.least(
                    literal(1.0),
                    literal(math.sin(lat1_rad))
                    * func.sin(func.radians(BuildingModel.latitude))
                    + literal(math.cos(lat1_rad))
                    * func.cos(func.radians(BuildingModel.latitude))
                    * func.cos(
                        func.radians(BuildingModel.longitude) - literal(lon1_rad),
                    ),
                ),
            )
            * literal(2)
        )

        return distance_expr

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

    async def filter(self, **filters: Any) -> Iterable[BuildingEntity]:
        async with self.database.get_read_only_session() as session:
            stmt = select(BuildingModel)

            # Обработка географических параметров (радиус)
            if (
                "latitude" in filters
                and "longitude" in filters
                and "radius" in filters
                and filters["latitude"] is not None
                and filters["longitude"] is not None
                and filters["radius"] is not None
            ):
                center_lat = filters["latitude"]
                center_lon = filters["longitude"]
                radius_meters = filters["radius"]

                distance_expr = self._haversine_distance_sql(center_lat, center_lon)
                stmt = stmt.where(distance_expr <= radius_meters)

            # Обработка прямоугольной области
            elif (
                "lat_min" in filters
                and "lat_max" in filters
                and "lon_min" in filters
                and "lon_max" in filters
                and filters["lat_min"] is not None
                and filters["lat_max"] is not None
                and filters["lon_min"] is not None
                and filters["lon_max"] is not None
            ):
                stmt = stmt.where(
                    BuildingModel.latitude >= filters["lat_min"],
                    BuildingModel.latitude <= filters["lat_max"],
                    BuildingModel.longitude >= filters["lon_min"],
                    BuildingModel.longitude <= filters["lon_max"],
                )

            # Обработка обычных полей модели
            for field, value in filters.items():
                # Пропускаем географические параметры, они уже обработаны выше
                if field in (
                    "latitude",
                    "longitude",
                    "radius",
                    "lat_min",
                    "lat_max",
                    "lon_min",
                    "lon_max",
                ):
                    continue

                try:
                    field_obj = getattr(BuildingModel, field)
                    stmt = stmt.where(field_obj == value)
                except AttributeError:
                    # Игнорируем неизвестные поля
                    continue

            res = await session.execute(stmt)
            results = [building_model_to_entity(row[0]) for row in res.all()]

            return results
