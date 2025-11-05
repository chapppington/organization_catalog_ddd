from typing import (
    Any,
    Iterable,
)
from uuid import UUID

from sqlalchemy import (
    insert,
    select,
)
from sqlalchemy.orm import selectinload

from domain.organization.entities import OrganizationEntity
from domain.organization.interfaces.repositories.organization import (
    BaseOrganizationRepository,
)
from infrastructure.database.converters.organization import (
    organization_activities_ids,
    organization_entity_to_model,
    organization_model_to_entity,
    organization_phones_to_models,
)
from infrastructure.database.main import async_session_factory
from infrastructure.database.models.activity import ActivityModel
from infrastructure.database.models.organization import (
    organization_activity,
    OrganizationModel,
)


class SQLAlchemyOrganizationRepository(BaseOrganizationRepository):
    async def add(self, organization: OrganizationEntity) -> None:
        """Добавить организацию с телефонами и активностями."""
        async with async_session_factory() as session:
            org_model = organization_entity_to_model(organization)
            session.add(org_model)
            await session.flush()  # привязывает org_model к сессии

            # Телефоны
            phones_models = organization_phones_to_models(org_model.oid, organization)
            session.add_all(phones_models)

            # Активности
            if organization.activities:
                activities_ids = organization_activities_ids(organization)
                # Добавляем связи напрямую через association table, чтобы избежать lazy loading
                values = [
                    {"organization_id": org_model.oid, "activity_id": activity_id}
                    for activity_id in activities_ids
                ]
                await session.execute(insert(organization_activity).values(values))

            await session.commit()

    async def get_by_id(self, organization_id: UUID) -> OrganizationEntity | None:
        """Получить организацию по ID с явной подгрузкой всех зависимостей."""
        async with async_session_factory() as session:
            stmt = (
                select(OrganizationModel)
                .where(OrganizationModel.oid == organization_id)
                .options(
                    selectinload(OrganizationModel.building),
                    selectinload(OrganizationModel.phones),
                    selectinload(OrganizationModel.activities),
                )
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return organization_model_to_entity(result) if result else None

    async def filter(self, **filters: Any) -> Iterable[OrganizationEntity]:
        """Фильтрация организаций с явной подгрузкой зависимостей."""
        async with async_session_factory() as session:
            stmt = select(OrganizationModel).options(
                selectinload(OrganizationModel.building),
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
            )

            activity_joined = False
            for field, value in filters.items():
                if field == "activity_name":
                    # Фильтр по названию активности через JOIN через association table
                    if not activity_joined:
                        stmt = stmt.join(OrganizationModel.activities)
                        activity_joined = True
                    stmt = stmt.where(ActivityModel.name == value)
                elif field == "name":
                    # Частичный поиск по имени организации
                    stmt = stmt.where(OrganizationModel.name.ilike(f"%{value}%"))
                else:
                    # Обычные поля модели
                    try:
                        field_obj = getattr(OrganizationModel, field)
                        stmt = stmt.where(field_obj == value)
                    except AttributeError:
                        # Игнорируем неизвестные поля
                        continue

            # Добавляем distinct, если был JOIN с activities (many-to-many может дать дубликаты)
            if activity_joined:
                stmt = stmt.distinct()

            res = await session.execute(stmt)
            results = [organization_model_to_entity(row[0]) for row in res.all()]
            return results
