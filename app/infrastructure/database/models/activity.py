from typing import (
    List,
    Optional,
)
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from infrastructure.database.models.base import TimedBaseModel


class ActivityModel(TimedBaseModel):
    __tablename__ = "activity"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("activity.oid", ondelete="SET NULL"),
        nullable=True,
    )

    parent: Mapped[Optional["ActivityModel"]] = relationship(
        "ActivityModel",
        remote_side=lambda: [ActivityModel.oid],
        backref="children",
        lazy="selectin",
    )

    # Используем строку для OrganizationModel, чтобы избежать кросс-импорта
    organizations: Mapped[List["OrganizationModel"]] = relationship(  # noqa: F821
        "OrganizationModel",
        secondary="organization_activity",
        back_populates="activities",
        lazy="selectin",
        passive_deletes=True,
    )
