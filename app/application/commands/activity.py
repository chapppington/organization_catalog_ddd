from dataclasses import dataclass
from uuid import UUID

from application.commands.base import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.organization.entities import ActivityEntity
from domain.organization.services import ActivityService


@dataclass(frozen=True)
class CreateActivityCommand(BaseCommand):
    name: str
    parent_id: UUID | None = None


@dataclass(frozen=True)
class CreateActivityCommandHandler(
    BaseCommandHandler[CreateActivityCommand, ActivityEntity],
):
    activity_service: ActivityService

    async def handle(self, command: CreateActivityCommand) -> ActivityEntity:
        result = await self.activity_service.create_activity(
            name=command.name,
            parent_id=command.parent_id,
        )
        return result
