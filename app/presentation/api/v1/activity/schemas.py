from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)

from domain.organization.entities import ActivityEntity


class CreateActivityRequestSchema(BaseModel):
    name: str
    parent_id: UUID | None = Field(None, examples=[None])


class ActivityResponseSchema(BaseModel):
    oid: UUID
    name: str
    parent_id: UUID | None = None

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
    parent_id: UUID | None = None
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
