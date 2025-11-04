from dataclasses import dataclass

from application.commands.base import (
    BaseCommand,
    BaseCommandHandler,
)
from application.common.interfaces.uow import UnitOfWork
from domain.organization.entities import ActivityEntity
from domain.organization.services import ActivityService


@dataclass(frozen=True)
class CreateActivityCommand(BaseCommand):
    name: str
    parent_id: str | None = None


@dataclass(frozen=True)
class CreateActivityCommandHandler(
    BaseCommandHandler[CreateActivityCommand, ActivityEntity],
):
    activity_service: ActivityService
    uow: UnitOfWork

    async def handle(self, command: CreateActivityCommand) -> ActivityEntity:
        result = await self.activity_service.create_activity(
            name=command.name,
            parent_id=command.parent_id,
        )
        await self.uow.commit()
        return result
