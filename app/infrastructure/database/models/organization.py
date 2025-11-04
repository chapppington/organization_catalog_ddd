from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    func,
    String,
    Table,
    UUID,
)
from sqlalchemy.orm import (
    composite,
    relationship,
)

from domain.organization.entities import (
    ActivityEntity,
    BuildingEntity,
    OrganizationEntity,
)
from domain.organization.value_objects import OrganizationNameValueObject

from .base import (
    mapper_registry,
    TimedBaseModel,
)


ORGANIZATIONS_TABLE = Table(
    "organizations",
    TimedBaseModel.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column(
        "building_id",
        UUID(as_uuid=True),
        ForeignKey("buildings.id"),
        nullable=False,
    ),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
)

ORGANIZATION_PHONES_TABLE = Table(
    "organization_phones",
    TimedBaseModel.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "organization_id",
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    ),
    Column("phone", String, nullable=False),
)

ORGANIZATION_ACTIVITIES_TABLE = Table(
    "organization_activities",
    TimedBaseModel.metadata,
    Column(
        "organization_id",
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        UUID(as_uuid=True),
        ForeignKey("activities.id"),
        primary_key=True,
    ),
)

mapper_registry.map_imperatively(
    OrganizationEntity,
    ORGANIZATIONS_TABLE,
    properties={
        "oid": ORGANIZATIONS_TABLE.c.id,
        "name": composite(OrganizationNameValueObject, ORGANIZATIONS_TABLE.c.name),
        "created_at": ORGANIZATIONS_TABLE.c.created_at,
        "updated_at": ORGANIZATIONS_TABLE.c.updated_at,
        "building": relationship(
            BuildingEntity,
            foreign_keys=[ORGANIZATIONS_TABLE.c.building_id],
            lazy="joined",
        ),
        "activities": relationship(
            ActivityEntity,
            secondary=ORGANIZATION_ACTIVITIES_TABLE,
            lazy="joined",
        ),
    },
    column_prefix="_",
)
