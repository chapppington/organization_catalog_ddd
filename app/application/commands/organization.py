from dataclasses import dataclass

from application.commands.base import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.organization.entities import (
    ActivityEntity,
    BuildingEntity,
    OrganizationEntity,
)
from domain.organization.services import (
    ActivityService,
    BuildingService,
    OrganizationService,
)


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


@dataclass(frozen=True)
class CreateActivityCommand(BaseCommand):
    name: str
    parent_id: str | None = None


@dataclass(frozen=True)
class CreateActivityCommandHandler(
    BaseCommandHandler[CreateActivityCommand, ActivityEntity],
):
    activity_service: ActivityService

    async def handle(self, command: CreateActivityCommand) -> ActivityEntity:
        return await self.activity_service.create_activity(
            name=command.name,
            parent_id=command.parent_id,
        )


@dataclass(frozen=True)
class CreateOrganizationCommand(BaseCommand):
    name: str
    address: str
    phones: list[str]
    activities: list[str]


@dataclass(frozen=True)
class CreateOrganizationCommandHandler(
    BaseCommandHandler[CreateOrganizationCommand, OrganizationEntity],
):
    organization_service: OrganizationService

    async def handle(self, command: CreateOrganizationCommand) -> OrganizationEntity:
        return await self.organization_service.create_organization(
            name=command.name,
            address=command.address,
            phones=command.phones,
            activities=command.activities,
        )
