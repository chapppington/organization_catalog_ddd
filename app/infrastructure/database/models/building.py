from sqlalchemy import (
    Column,
    DateTime,
    Float,
    func,
    String,
    Table,
    UUID,
)
from sqlalchemy.orm import composite

from domain.organization.entities import BuildingEntity
from domain.organization.value_objects import (
    BuildingAddressValueObject,
    BuildingCoordinatesValueObject,
)

from .base import (
    mapper_registry,
    TimedBaseModel,
)


BUILDINGS_TABLE = Table(
    "buildings",
    TimedBaseModel.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("address", String, nullable=False, unique=True),
    Column("latitude", Float, nullable=False),
    Column("longitude", Float, nullable=False),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
)

mapper_registry.map_imperatively(
    BuildingEntity,
    BUILDINGS_TABLE,
    properties={
        "oid": BUILDINGS_TABLE.c.id,
        "address": composite(BuildingAddressValueObject, BUILDINGS_TABLE.c.address),
        "coordinates": composite(
            BuildingCoordinatesValueObject,
            BUILDINGS_TABLE.c.latitude,
            BUILDINGS_TABLE.c.longitude,
        ),
        "created_at": BUILDINGS_TABLE.c.created_at,
        "updated_at": BUILDINGS_TABLE.c.updated_at,
    },
    column_prefix="_",
)
