from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime
from uuid import (
    UUID,
    uuid4,
)

from domain.base.entity import BaseEntity
from domain.user.value_objects import UsernameValueObject


@dataclass
class UserEntity(BaseEntity):
    username: UsernameValueObject
    password: str

    def __eq__(self, __value: "UserEntity") -> bool:
        return self.username.value == __value.username.value

    def __hash__(self) -> int:
        return hash(self.username.value)


@dataclass
class APIKeyEntity(BaseEntity):
    key: UUID = field(default_factory=uuid4, kw_only=True)
    user_id: UUID
    user: UserEntity
    last_used: datetime | None = None
    banned_at: datetime | None = None

    def __eq__(self, __value: "APIKeyEntity") -> bool:
        return self.key == __value.key

    def __hash__(self) -> int:
        return hash(self.key)
