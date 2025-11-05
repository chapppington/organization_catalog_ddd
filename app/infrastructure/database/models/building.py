from sqlalchemy import (
    Float,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from infrastructure.database.models.base import TimedBaseModel


class BuildingModel(TimedBaseModel):
    __tablename__ = "building"

    address: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
