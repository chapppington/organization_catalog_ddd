import math
from dataclasses import (
    dataclass,
    field,
)
from typing import Iterable

from domain.organization.entities import BuildingEntity
from domain.organization.interfaces.repositories.building import BaseBuildingRepository
from domain.organization.interfaces.repositories.filters import BuildingFilter


@dataclass
class DummyInMemoryBuildingRepository(BaseBuildingRepository):
    _saved_buildings: list[BuildingEntity] = field(default_factory=list, kw_only=True)

    async def add(self, building: BuildingEntity) -> None:
        self._saved_buildings.append(building)

    @staticmethod
    def _calculate_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Вычисляет расстояние между двумя точками в метрах (формула
        Haversine)"""
        R = 6371000  # Радиус Земли в метрах

        # Переводим градусы в радианы
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Формула Haversine
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    async def get_by_id(self, building_id: str) -> BuildingEntity | None:
        try:
            return next(
                building
                for building in self._saved_buildings
                if building.oid == building_id
            )
        except StopIteration:
            return None

    async def filter(self, filters: BuildingFilter) -> Iterable[BuildingEntity]:
        results = self._saved_buildings.copy()

        if filters.address:
            search_term = filters.address.lower()
            results = [
                building
                for building in results
                if search_term in building.address.as_generic_type().lower()
            ]

        # Фильтрация по радиусу
        if (
            filters.latitude is not None
            and filters.longitude is not None
            and filters.radius is not None
        ):
            filtered = []
            for building in results:
                distance = self._calculate_distance(
                    filters.latitude,
                    filters.longitude,
                    building.coordinates.latitude,
                    building.coordinates.longitude,
                )
                if distance <= filters.radius:
                    filtered.append(building)
            results = filtered

        # Фильтрация по прямоугольной области
        if (
            filters.lat_min is not None
            and filters.lat_max is not None
            and filters.lon_min is not None
            and filters.lon_max is not None
        ):
            results = [
                building
                for building in results
                if (
                    filters.lat_min <= building.coordinates.latitude <= filters.lat_max
                    and filters.lon_min
                    <= building.coordinates.longitude
                    <= filters.lon_max
                )
            ]

        return results
