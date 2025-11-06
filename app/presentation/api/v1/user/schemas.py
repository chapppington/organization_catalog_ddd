from uuid import UUID

from pydantic import BaseModel

from domain.user.entities import (
    APIKeyEntity,
    UserEntity,
)


class RegisterRequestSchema(BaseModel):
    username: str
    password: str


class LoginRequestSchema(BaseModel):
    username: str
    password: str


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenResponseSchema(BaseModel):
    access_token: str


class UserResponseSchema(BaseModel):
    oid: UUID
    username: str

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "UserResponseSchema":
        return cls(
            oid=entity.oid,
            username=entity.username.as_generic_type(),
        )


class APIKeyResponseSchema(BaseModel):
    oid: UUID
    key: UUID
    user_id: UUID
    last_used: str | None = None
    banned_at: str | None = None

    @classmethod
    def from_entity(cls, entity: APIKeyEntity) -> "APIKeyResponseSchema":
        return cls(
            oid=entity.oid,
            key=entity.key,
            user_id=entity.user_id,
            last_used=entity.last_used.isoformat() if entity.last_used else None,
            banned_at=entity.banned_at.isoformat() if entity.banned_at else None,
        )
