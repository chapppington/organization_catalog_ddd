import math
from collections.abc import Iterable
from dataclasses import (
    dataclass,
    field,
)

from domain.organization.entities import BuildingEntity
from domain.organization.interfaces.repositories.building import BaseBuildingRepository


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
        R = 6371000

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    async def get_by_id(self, building_id: str) -> BuildingEntity | None:
        try:
            return next(building for building in self._saved_buildings if building.oid == building_id)
        except StopIteration:
            return None

    async def get_by_address(self, address: str) -> BuildingEntity | None:
        try:
            search_term = address.lower()
            return next(
                building
                for building in self._saved_buildings
                if building.address.as_generic_type().lower() == search_term
            )
        except StopIteration:
            return None

    async def filter_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float,
    ) -> Iterable[BuildingEntity]:
        results = []
        for building in self._saved_buildings:
            distance = self._calculate_distance(
                latitude,
                longitude,
                building.coordinates.latitude,
                building.coordinates.longitude,
            )
            if distance <= radius_meters:
                results.append(building)
        return results

    async def filter_by_bounding_box(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
    ) -> Iterable[BuildingEntity]:
        return [
            building
            for building in self._saved_buildings
            if (
                lat_min <= building.coordinates.latitude <= lat_max
                and lon_min <= building.coordinates.longitude <= lon_max
            )
        ]
