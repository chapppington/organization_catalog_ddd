from dataclasses import dataclass

from application.commands.base import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.organization.entities import OrganizationEntity
from domain.organization.services import OrganizationService


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
