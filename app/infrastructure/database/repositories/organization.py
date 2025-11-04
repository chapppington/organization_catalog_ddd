from typing import (
    Iterable,
)
from uuid import (
    UUID,
    uuid4,
)

from sqlalchemy import (
    and_,
    exists,
    select,
)

from domain.organization.entities import OrganizationEntity
from domain.organization.interfaces.repositories.filters import OrganizationFilter
from domain.organization.interfaces.repositories.organization import (
    BaseOrganizationRepository,
)
from domain.organization.value_objects import OrganizationPhoneValueObject
from infrastructure.database.models.building import BUILDINGS_TABLE
from infrastructure.database.models.organization import (
    ORGANIZATION_ACTIVITIES_TABLE,
    ORGANIZATION_PHONES_TABLE,
    ORGANIZATIONS_TABLE,
)
from infrastructure.database.repositories.base import BaseSQLAlchemyRepository


class OrganizationRepository(BaseSQLAlchemyRepository, BaseOrganizationRepository):
    async def add(self, organization: OrganizationEntity) -> None:
        """Добавляет новую организацию в базу данных."""
        # Сохраняем ID activities отдельно, т.к. они уже существуют в БД
        # и не должны обрабатываться SQLAlchemy при добавлении организации
        activity_ids = (
            [str(activity.oid) for activity in organization.activities]
            if organization.activities
            else []
        )

        # Отсоединяем building от его сессии и присоединяем к текущей
        if organization.building:
            organization.building = await self.session.merge(organization.building)

        # Убираем activities из organization перед добавлением,
        # чтобы SQLAlchemy не пытался управлять связями many-to-many
        original_activities = organization.activities
        organization.activities = []  # Очищаем список activities

        self.session.add(organization)

        # Сначала сохраняем организацию, чтобы получить ID
        await self.session.flush([organization])

        # Теперь можно добавлять телефоны и связи, т.к. организация уже в БД
        # Сохраняем телефоны отдельно
        if organization.phones:
            for phone in organization.phones:
                await self.session.execute(
                    ORGANIZATION_PHONES_TABLE.insert().values(
                        id=uuid4(),
                        organization_id=UUID(str(organization.oid)),
                        phone=phone.as_generic_type(),
                    ),
                )

        # Сохраняем связи с видами деятельности (только INSERT, без создания activities)
        if activity_ids:
            for activity_id in activity_ids:
                await self.session.execute(
                    ORGANIZATION_ACTIVITIES_TABLE.insert().values(
                        organization_id=UUID(str(organization.oid)),
                        activity_id=UUID(activity_id),
                    ),
                )

        await self.session.commit()

        # Восстанавливаем activities в объекте для возврата ПОСЛЕ commit,
        # чтобы SQLAlchemy не пытался синхронизировать связи
        organization.activities = original_activities

    async def get_by_id(self, organization_id: str) -> OrganizationEntity | None:
        """Получает организацию по ID."""
        org_uuid = UUID(organization_id)

        query = select(OrganizationEntity).where(ORGANIZATIONS_TABLE.c.id == org_uuid)
        result = await self.session.execute(query)
        organization = result.unique().scalar_one_or_none()

        if organization:
            # Загружаем телефоны отдельно
            await self._load_phones(organization)

        return organization

    async def filter(
        self,
        filters: OrganizationFilter,
    ) -> Iterable[OrganizationEntity]:
        """Фильтрует организации по заданным критериям."""
        query = select(OrganizationEntity)

        # Фильтр по имени (частичное совпадение, case-insensitive)
        if filters.name:
            query = query.where(ORGANIZATIONS_TABLE.c.name.ilike(f"%{filters.name}%"))

        # Фильтр по адресу здания
        if filters.address:
            # Используем EXISTS для фильтрации по адресу, чтобы избежать конфликта с автоматическим JOIN
            # из lazy="joined" для relationship building
            building_exists = exists(
                select(1).where(
                    and_(
                        BUILDINGS_TABLE.c.id == ORGANIZATIONS_TABLE.c.building_id,
                        BUILDINGS_TABLE.c.address.ilike(f"%{filters.address}%"),
                    ),
                ),
            )
            query = query.where(building_exists)

        # Фильтр по виду деятельности (через связь many-to-many)
        if filters.activity_name:
            from infrastructure.database.models.activity import ACTIVITIES_TABLE

            query = (
                query.join(
                    ORGANIZATION_ACTIVITIES_TABLE,
                    ORGANIZATIONS_TABLE.c.id
                    == ORGANIZATION_ACTIVITIES_TABLE.c.organization_id,
                )
                .join(
                    ACTIVITIES_TABLE,
                    ORGANIZATION_ACTIVITIES_TABLE.c.activity_id
                    == ACTIVITIES_TABLE.c.id,
                )
                .where(ACTIVITIES_TABLE.c.name.ilike(f"%{filters.activity_name}%"))
            )

        # Применяем limit и offset
        if filters.limit:
            query = query.limit(filters.limit)
        if filters.offset:
            query = query.offset(filters.offset)

        result = await self.session.execute(query)
        organizations = result.scalars().unique().all()

        # Загружаем телефоны для всех организаций
        for org in organizations:
            await self._load_phones(org)

        return organizations

    async def _load_phones(self, organization: OrganizationEntity) -> None:
        """Загружает телефоны для организации."""
        query = select(ORGANIZATION_PHONES_TABLE.c.phone).where(
            ORGANIZATION_PHONES_TABLE.c.organization_id == UUID(str(organization.oid)),
        )
        result = await self.session.execute(query)
        phones = [row[0] for row in result]
        organization.phones = [
            OrganizationPhoneValueObject(value=phone) for phone in phones
        ]
