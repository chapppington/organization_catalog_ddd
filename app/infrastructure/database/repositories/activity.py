from typing import Iterable
from uuid import UUID

from sqlalchemy import select

from domain.organization.entities import ActivityEntity
from domain.organization.interfaces.repositories.activity import BaseActivityRepository
from domain.organization.interfaces.repositories.filters import ActivityFilter
from infrastructure.database.models.activity import ACTIVITIES_TABLE
from infrastructure.database.repositories.base import BaseSQLAlchemyRepository


class ActivityRepository(BaseSQLAlchemyRepository, BaseActivityRepository):
    async def add(self, activity: ActivityEntity) -> None:
        """Добавляет новую активность в базу данных."""
        self.session.add(activity)
        await self.session.commit()

    async def get_by_id(self, activity_id: str) -> ActivityEntity | None:
        """Получает активность по ID с автоматической загрузкой parent."""
        activity_uuid = UUID(activity_id)

        query = select(ActivityEntity).where(ACTIVITIES_TABLE.c.id == activity_uuid)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def filter(self, filters: ActivityFilter) -> Iterable[ActivityEntity]:
        """Фильтрует активности по заданным критериям."""
        query = select(ActivityEntity)

        # Фильтр по имени (частичное совпадение, case-insensitive)
        if filters.name:
            query = query.where(ACTIVITIES_TABLE.c.name.ilike(f"%{filters.name}%"))

        # Фильтр по parent_id
        if filters.parent_id:
            parent_uuid = UUID(filters.parent_id)
            query = query.where(ACTIVITIES_TABLE.c.parent_id == parent_uuid)

        result = await self.session.execute(query)
        return result.scalars().all()
