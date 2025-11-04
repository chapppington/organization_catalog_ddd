from sqlalchemy import (
    Column,
    Float,
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
)

mapper_registry.map_imperatively(
    BuildingEntity,
    BUILDINGS_TABLE,
    properties={
        "address": composite(BuildingAddressValueObject, BUILDINGS_TABLE.c.address),
        "coordinates": composite(
            BuildingCoordinatesValueObject,
            BUILDINGS_TABLE.c.latitude,
            BUILDINGS_TABLE.c.longitude,
        ),
    },
    column_prefix="_",
)
