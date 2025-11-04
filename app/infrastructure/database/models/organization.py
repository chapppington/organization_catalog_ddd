from sqlalchemy import (
    Column,
    ForeignKey,
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
        "name": composite(OrganizationNameValueObject, ORGANIZATIONS_TABLE.c.name),
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
