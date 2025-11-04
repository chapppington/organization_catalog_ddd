from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from domain.organization.entities import ActivityEntity


class CreateActivityRequestSchema(BaseModel):
    name: str
    parent_id: Optional[str] = None


class ActivityResponseSchema(BaseModel):
    oid: str
    name: str
    parent_id: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: ActivityEntity) -> "ActivityResponseSchema":
        return cls(
            oid=str(entity.oid),
            name=entity.name.as_generic_type(),
            parent_id=str(entity.parent.oid) if entity.parent else None,
        )


class ActivityDetailSchema(BaseModel):
    oid: str
    name: str
    parent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: ActivityEntity) -> "ActivityDetailSchema":
        return cls(
            oid=str(entity.oid),
            name=entity.name.as_generic_type(),
            parent_id=str(entity.parent.oid) if entity.parent else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
