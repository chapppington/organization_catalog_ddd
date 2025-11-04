from dataclasses import dataclass

from application.commands.base import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.organization.entities import BuildingEntity
from domain.organization.services import BuildingService


@dataclass(frozen=True)
class CreateBuildingCommand(BaseCommand):
    address: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class CreateBuildingCommandHandler(
    BaseCommandHandler[CreateBuildingCommand, BuildingEntity],
):
    building_service: BuildingService

    async def handle(self, command: CreateBuildingCommand) -> BuildingEntity:
        return await self.building_service.create_building(
            address=command.address,
            latitude=command.latitude,
            longitude=command.longitude,
        )
