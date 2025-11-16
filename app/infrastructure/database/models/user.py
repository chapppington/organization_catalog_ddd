from datetime import datetime
from typing import Optional
from uuid import UUID

from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import (
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class UserModel(TimedBaseModel):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    password: Mapped[str] = mapped_column(Text, nullable=False)

    api_keys: Mapped[list["APIKeyModel"]] = relationship(
        "APIKeyModel",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class APIKeyModel(TimedBaseModel):
    __tablename__ = "api_key"

    key: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        nullable=False,
        unique=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("user.oid", ondelete="CASCADE"),
        nullable=False,
    )
    last_used: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    banned_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="api_keys",
        lazy="selectin",
    )
