from datetime import datetime

from pydantic import BaseModel

from domain.organization.entities import BuildingEntity


class CreateBuildingRequestSchema(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingResponseSchema(BaseModel):
    oid: str
    address: str
    latitude: float
    longitude: float

    @classmethod
    def from_entity(cls, entity: BuildingEntity) -> "BuildingResponseSchema":
        return cls(
            oid=str(entity.oid),
            address=entity.address.as_generic_type(),
            latitude=entity.coordinates.latitude,
            longitude=entity.coordinates.longitude,
        )


class BuildingDetailSchema(BaseModel):
    oid: str
    address: str
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: BuildingEntity) -> "BuildingDetailSchema":
        return cls(
            oid=str(entity.oid),
            address=entity.address.as_generic_type(),
            latitude=entity.coordinates.latitude,
            longitude=entity.coordinates.longitude,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
