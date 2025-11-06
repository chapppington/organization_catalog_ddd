from dataclasses import dataclass

from application.queries.base import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.user.entities import UserEntity
from domain.user.services import UserService


@dataclass(frozen=True)
class AuthenticateUserQuery(BaseQuery):
    username: str
    password: str


@dataclass(frozen=True)
class AuthenticateUserQueryHandler(
    BaseQueryHandler[AuthenticateUserQuery, UserEntity],
):
    user_service: UserService

    async def handle(
        self,
        query: AuthenticateUserQuery,
    ) -> UserEntity:
        return await self.user_service.authenticate_user(
            username=query.username,
            password=query.password,
        )
