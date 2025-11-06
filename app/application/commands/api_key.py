from dataclasses import dataclass
from uuid import UUID

from application.commands.base import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.user.entities import APIKeyEntity
from domain.user.services import APIKeyService


@dataclass(frozen=True)
class CreateAPIKeyCommand(BaseCommand):
    user_id: UUID


@dataclass(frozen=True)
class CreateAPIKeyCommandHandler(
    BaseCommandHandler[CreateAPIKeyCommand, APIKeyEntity],
):
    api_key_service: APIKeyService

    async def handle(self, command: CreateAPIKeyCommand) -> APIKeyEntity:
        result = await self.api_key_service.create_api_key(
            user_id=command.user_id,
        )
        return result
