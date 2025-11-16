from typing import Any

from geoalchemy2 import Geography
from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class BuildingModel(TimedBaseModel):
    __tablename__ = "building"

    address: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    location: Mapped[Any] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
    )
