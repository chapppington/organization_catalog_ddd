from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Table,
    UUID,
)
from sqlalchemy.orm import composite

from domain.organization.entities import ActivityEntity
from domain.organization.value_objects import ActivityNameValueObject

from .base import (
    mapper_registry,
    TimedBaseModel,
)


ACTIVITIES_TABLE = Table(
    "activities",
    TimedBaseModel.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String, nullable=False),
    Column("parent_id", UUID(as_uuid=True), ForeignKey("activities.id"), nullable=True),
)

mapper_registry.map_imperatively(
    ActivityEntity,
    ACTIVITIES_TABLE,
    properties={
        "name": composite(ActivityNameValueObject, ACTIVITIES_TABLE.c.name),
    },
    column_prefix="_",
)
