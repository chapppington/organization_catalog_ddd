from typing import List
from uuid import UUID

from infrastructure.database.models.base import TimedBaseModel
from infrastructure.database.models.building import BuildingModel
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


organization_activity = Table(
    "organization_activity",
    TimedBaseModel.metadata,
    Column(
        "organization_id",
        UUIDType(as_uuid=True),
        ForeignKey("organization.oid", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        UUIDType(as_uuid=True),
        ForeignKey("activity.oid", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class OrganizationPhoneModel(TimedBaseModel):
    __tablename__ = "organization_phone"

    organization_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("organization.oid", ondelete="CASCADE"),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(String(50), nullable=False)

    organization: Mapped["OrganizationModel"] = relationship(back_populates="phones")


class OrganizationModel(TimedBaseModel):
    __tablename__ = "organization"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    building_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("building.oid", ondelete="CASCADE"),
        nullable=False,
    )
    building: Mapped[BuildingModel] = relationship("BuildingModel")

    phones: Mapped[List[OrganizationPhoneModel]] = relationship(
        "OrganizationPhoneModel",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )

    activities: Mapped[List["ActivityModel"]] = relationship(  # noqa  # pyright: ignore[reportUndefinedVariable]
        "ActivityModel",
        secondary=organization_activity,
        back_populates="organizations",
        lazy="selectin",
        passive_deletes=True,
    )
