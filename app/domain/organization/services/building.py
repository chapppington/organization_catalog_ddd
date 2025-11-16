from dataclasses import dataclass
from uuid import UUID

from domain.organization.entities import BuildingEntity
from domain.organization.interfaces.repositories import BaseBuildingRepository
from domain.organization.value_objects import (
    BuildingAddressValueObject,
    BuildingCoordinatesValueObject,
)


@dataclass
class BuildingService:
    building_repository: BaseBuildingRepository

    async def create_building(
        self,
        address: str,
        latitude: float,
        longitude: float,
    ) -> BuildingEntity:
        building = BuildingEntity(
            address=BuildingAddressValueObject(address),
            coordinates=BuildingCoordinatesValueObject(
                latitude=latitude,
                longitude=longitude,
            ),
        )
        await self.building_repository.add(building)
        return building

    async def get_building_by_id(
        self,
        building_id: UUID,
    ) -> BuildingEntity:
        return await self.building_repository.get_by_id(building_id)

    async def get_building_by_address(
        self,
        address: str,
    ) -> BuildingEntity:
        return await self.building_repository.get_by_address(address)
