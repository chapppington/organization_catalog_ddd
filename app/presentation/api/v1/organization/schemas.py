from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from domain.organization.entities import (
    ActivityEntity,
    BuildingEntity,
    OrganizationEntity,
)


# Activity Schemas
class CreateActivityRequestSchema(BaseModel):
    name: str
    parent_id: Optional[UUID] = None


class ActivityResponseSchema(BaseModel):
    oid: UUID
    name: str
    parent_id: Optional[UUID] = None

    @classmethod
    def from_entity(cls, entity: ActivityEntity) -> "ActivityResponseSchema":
        return cls(
            oid=entity.oid,
            name=entity.name.as_generic_type(),
            parent_id=entity.parent.oid if entity.parent else None,
        )


class ActivityDetailSchema(BaseModel):
    oid: UUID
    name: str
    parent_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: ActivityEntity) -> "ActivityDetailSchema":
        return cls(
            oid=entity.oid,
            name=entity.name.as_generic_type(),
            parent_id=entity.parent.oid if entity.parent else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


# Building Schemas
class CreateBuildingRequestSchema(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingResponseSchema(BaseModel):
    oid: UUID
    address: str
    latitude: float
    longitude: float

    @classmethod
    def from_entity(cls, entity: BuildingEntity) -> "BuildingResponseSchema":
        return cls(
            oid=entity.oid,
            address=entity.address.as_generic_type(),
            latitude=entity.coordinates.latitude,
            longitude=entity.coordinates.longitude,
        )


class BuildingDetailSchema(BaseModel):
    oid: UUID
    address: str
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: BuildingEntity) -> "BuildingDetailSchema":
        return cls(
            oid=entity.oid,
            address=entity.address.as_generic_type(),
            latitude=entity.coordinates.latitude,
            longitude=entity.coordinates.longitude,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


# Organization Schemas
class CreateOrganizationRequestSchema(BaseModel):
    name: str
    address: str
    phones: list[str]
    activities: list[str]


class OrganizationResponseSchema(BaseModel):
    oid: UUID
    name: str
    building_id: UUID
    phones: list[str]
    activity_ids: list[UUID]

    @classmethod
    def from_entity(cls, entity: OrganizationEntity) -> "OrganizationResponseSchema":
        return cls(
            oid=entity.oid,
            name=entity.name.as_generic_type(),
            building_id=entity.building.oid,
            phones=[phone.as_generic_type() for phone in entity.phones],
            activity_ids=[activity.oid for activity in entity.activities],
        )


class OrganizationDetailSchema(BaseModel):
    oid: UUID
    name: str
    building: BuildingDetailSchema
    phones: list[str]
    activities: list[ActivityDetailSchema]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: OrganizationEntity) -> "OrganizationDetailSchema":
        return cls(
            oid=entity.oid,
            name=entity.name.as_generic_type(),
            building=BuildingDetailSchema.from_entity(entity.building),
            phones=[phone.as_generic_type() for phone in entity.phones],
            activities=[
                ActivityDetailSchema.from_entity(activity)
                for activity in entity.activities
            ],
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
