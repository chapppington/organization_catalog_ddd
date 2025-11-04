from typing import (
    Iterable,
    NoReturn,
)
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import (
    DBAPIError,
    IntegrityError,
)

from application.common.exceptions import RepoException
from application.exceptions.activity import (
    ActivityIdAlreadyExistsException,
    ActivityWithThatNameAlreadyExistsException,
    ParentActivityNotFoundException,
)
from domain.organization.entities import ActivityEntity
from domain.organization.interfaces.repositories.activity import BaseActivityRepository
from domain.organization.interfaces.repositories.filters import ActivityFilter
from infrastructure.database.models.activity import ACTIVITIES_TABLE
from infrastructure.database.repositories.base import BaseSQLAlchemyRepository


class ActivityRepository(BaseSQLAlchemyRepository, BaseActivityRepository):
    async def add(self, activity: ActivityEntity) -> None:
        """Добавляет новую активность в базу данных."""
        self.session.add(activity)
        try:
            await self.session.flush([activity])
            await self.session.commit()
        except IntegrityError as err:
            await self.session.rollback()
            self._parse_error(err, activity)

    async def get_by_id(self, activity_id: str) -> ActivityEntity | None:
        """Получает активность по ID с автоматической загрузкой parent
        (lazy='joined')."""
        try:
            activity_uuid = UUID(activity_id)
        except (ValueError, AttributeError):
            return None

        stmt = select(ActivityEntity).where(ACTIVITIES_TABLE.c.id == activity_uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def filter(self, filters: ActivityFilter) -> Iterable[ActivityEntity]:
        """Фильтрует активности по заданным критериям."""
        stmt = select(ActivityEntity)

        # Фильтр по имени (частичное совпадение, case-insensitive)
        if filters.name:
            stmt = stmt.where(ACTIVITIES_TABLE.c.name.ilike(f"%{filters.name}%"))

        # Фильтр по parent_id
        if filters.parent_id:
            try:
                parent_uuid = UUID(filters.parent_id)
                stmt = stmt.where(ACTIVITIES_TABLE.c.parent_id == parent_uuid)
            except (ValueError, AttributeError):
                # Если parent_id невалидный UUID, возвращаем пустой результат
                return []

        result = await self.session.execute(stmt)
        return result.scalars().all()

    def _parse_error(self, err: DBAPIError, activity: ActivityEntity) -> NoReturn:
        constraint_name = getattr(
            getattr(getattr(err, "__cause__", None), "__cause__", None),
            "constraint_name",
            None,
        )

        match constraint_name:
            case "pk_activities":
                # Дублирование ID
                raise ActivityIdAlreadyExistsException(
                    activity_id=activity.oid,
                ) from err
            case "fk_activities_parent_id_activities":
                # Parent_id ссылается на несуществующую активность
                parent_id = activity.parent.oid if activity.parent else "unknown"
                raise ParentActivityNotFoundException(parent_id=parent_id) from err
            case (
                "uq_activities_name_parent"
                | "uq_activities_name_root"
                | "activities_name_parent_id_key"
            ):
                # Активность с таким именем уже существует в данной категории
                # uq_activities_name_root - для корневых элементов (parent_id IS NULL)
                # uq_activities_name_parent - для дочерних элементов (parent_id IS NOT NULL)
                # PostgreSQL создает constraint с именем "activities_name_parent_id_key" для UniqueConstraint
                parent_id = activity.parent.oid if activity.parent else None
                raise ActivityWithThatNameAlreadyExistsException(
                    name=activity.name.as_generic_type(),
                    parent_id=parent_id,
                ) from err
            case _:
                # Любая другая ошибка - пробрасываем дальше
                raise RepoException() from err
