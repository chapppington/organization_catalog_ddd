from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from infrastructure.database.converters.activity import (
    activity_entity_to_model,
    activity_model_to_entity,
)
from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.activity import ActivityModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.organization.entities import ActivityEntity
from domain.organization.interfaces.repositories.activity import BaseActivityRepository


@dataclass
class SQLAlchemyActivityRepository(BaseActivityRepository):
    database: Database

    async def add(self, activity: ActivityEntity) -> None:
        async with self.database.get_session() as session:
            model = activity_entity_to_model(activity)
            session.add(model)
            await session.commit()

    async def get_by_id(self, activity_id: UUID) -> ActivityEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(ActivityModel)
                .where(ActivityModel.oid == activity_id)
                .options(selectinload(ActivityModel.parent))
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return activity_model_to_entity(result) if result else None

    async def get_by_name(self, name: str) -> ActivityEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = select(ActivityModel).where(ActivityModel.name == name).options(selectinload(ActivityModel.parent))
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return activity_model_to_entity(result) if result else None

    async def filter(self, **filters: Any) -> Iterable[ActivityEntity]:
        async with self.database.get_read_only_session() as session:
            stmt = select(ActivityModel).options(selectinload(ActivityModel.parent))

            for field, value in filters.items():
                field_obj = getattr(ActivityModel, field)
                stmt = stmt.where(field_obj == value)

            res = await session.execute(stmt)
            results = [activity_model_to_entity(row[0]) for row in res.all()]

            return results
