from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    func,
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
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
    # Уникальность: имя должно быть уникальным в пределах одного parent_id
    # Для корневых элементов (parent_id IS NULL) - уникальность по name
    Index(
        "uq_activities_name_root",
        "name",
        unique=True,
        postgresql_where="parent_id IS NULL",
    ),
    # Для дочерних элементов (parent_id IS NOT NULL) - уникальность по (name, parent_id)
    Index(
        "uq_activities_name_parent",
        "name",
        "parent_id",
        unique=True,
        postgresql_where="parent_id IS NOT NULL",
    ),
)

mapper_registry.map_imperatively(
    ActivityEntity,
    ACTIVITIES_TABLE,
    properties={
        "oid": ACTIVITIES_TABLE.c.id,
        "name": composite(ActivityNameValueObject, ACTIVITIES_TABLE.c.name),
        "created_at": ACTIVITIES_TABLE.c.created_at,
        "updated_at": ACTIVITIES_TABLE.c.updated_at,
        "parent": relationship(
            ActivityEntity,
            remote_side=[ACTIVITIES_TABLE.c.id],
            foreign_keys=[ACTIVITIES_TABLE.c.parent_id],
            lazy="joined",
        ),
    },
    column_prefix="_",
)
