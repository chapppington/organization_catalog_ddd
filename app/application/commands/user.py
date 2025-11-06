from dataclasses import dataclass

from application.commands.base import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.user.entities import UserEntity
from domain.user.services import UserService


@dataclass(frozen=True)
class CreateUserCommand(BaseCommand):
    username: str
    password: str


@dataclass(frozen=True)
class CreateUserCommandHandler(
    BaseCommandHandler[CreateUserCommand, UserEntity],
):
    user_service: UserService

    async def handle(self, command: CreateUserCommand) -> UserEntity:
        result = await self.user_service.create_user(
            username=command.username,
            password=command.password,
        )
        return result
