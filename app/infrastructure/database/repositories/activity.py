from typing import (
    Any,
    Iterable,
)
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.organization.entities import ActivityEntity
from domain.organization.interfaces.repositories.activity import BaseActivityRepository
from infrastructure.database.converters.activity import (
    activity_entity_to_model,
    activity_model_to_entity,
)
from infrastructure.database.main import async_session_factory
from infrastructure.database.models.activity import ActivityModel


class SQLAlchemyActivityRepository(BaseActivityRepository):
    async def add(self, activity: ActivityEntity) -> None:
        """Добавить активность."""
        async with async_session_factory() as session:
            model = activity_entity_to_model(activity)
            session.add(model)
            await session.commit()

    async def get_by_id(self, activity_id: UUID) -> ActivityEntity | None:
        """Получить активность по ID."""
        async with async_session_factory() as session:
            stmt = (
                select(ActivityModel)
                .where(ActivityModel.oid == activity_id)
                .options(selectinload(ActivityModel.parent))
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return activity_model_to_entity(result) if result else None

    async def get_by_name(self, name: str) -> ActivityEntity | None:
        """Получить активность по имени."""
        async with async_session_factory() as session:
            stmt = (
                select(ActivityModel)
                .where(ActivityModel.name == name)
                .options(selectinload(ActivityModel.parent))
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return activity_model_to_entity(result) if result else None

    async def filter(self, **filters: Any) -> Iterable[ActivityEntity]:
        """Фильтрация активностей."""
        async with async_session_factory() as session:
            stmt = select(ActivityModel).options(selectinload(ActivityModel.parent))

            for field, value in filters.items():
                field_obj = getattr(ActivityModel, field)
                stmt = stmt.where(field_obj == value)

            res = await session.execute(stmt)
            results = [activity_model_to_entity(row[0]) for row in res.all()]

            return results
