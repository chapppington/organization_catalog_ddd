from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    String,
    Table,
    UUID,
)
from sqlalchemy.orm import (
    composite,
    relationship,
)

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
    # Уникальность: имя должно быть уникальным в пределах одного parent_id
    Index("uq_activities_name_parent", "name", "parent_id", unique=True),
)

mapper_registry.map_imperatively(
    ActivityEntity,
    ACTIVITIES_TABLE,
    properties={
        "name": composite(ActivityNameValueObject, ACTIVITIES_TABLE.c.name),
        "parent": relationship(
            ActivityEntity,
            remote_side=[ACTIVITIES_TABLE.c.id],
            foreign_keys=[ACTIVITIES_TABLE.c.parent_id],
            lazy="joined",
        ),
    },
    column_prefix="_",
)
