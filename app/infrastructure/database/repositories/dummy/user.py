from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.user.entities import UserEntity
from domain.user.interfaces.repositories.user import BaseUserRepository


@dataclass
class DummyInMemoryUserRepository(BaseUserRepository):
    _saved_users: list[UserEntity] = field(default_factory=list, kw_only=True)

    async def add(self, user: UserEntity) -> None:
        self._saved_users.append(user)

    async def get_by_id(self, user_id: UUID) -> UserEntity | None:
        try:
            return next(user for user in self._saved_users if user.oid == user_id)
        except StopIteration:
            return None

    async def get_by_username(self, username: str) -> UserEntity | None:
        search_term = username.lower()
        try:
            return next(
                user
                for user in self._saved_users
                if user.username.as_generic_type().lower() == search_term
            )
        except StopIteration:
            return None

    async def check_username_exists(self, username: str) -> bool:
        search_term = username.lower()
        try:
            next(
                user
                for user in self._saved_users
                if user.username.as_generic_type().lower() == search_term
            )
            return True
        except StopIteration:
            return False
