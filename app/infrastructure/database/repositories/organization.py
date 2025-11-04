from typing import (
    Iterable,
    NoReturn,
)
from uuid import (
    UUID,
    uuid4,
)

from sqlalchemy import select
from sqlalchemy.exc import (
    DBAPIError,
    IntegrityError,
)

from application.common.exceptions import RepoException
from application.exceptions.organization import (
    OrganizationIdAlreadyExistsException,
    OrganizationWithThatNameAlreadyExistsException,
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
        self.session.add(organization)

        # Сохраняем телефоны отдельно
        if organization.phones:
            for phone in organization.phones:
                await self.session.execute(
                    ORGANIZATION_PHONES_TABLE.insert().values(
                        id=uuid4(),
                        organization_id=UUID(organization.oid),
                        phone=phone.as_generic_type(),
                    ),
                )

        # Сохраняем связи с видами деятельности
        if organization.activities:
            for activity in organization.activities:
                await self.session.execute(
                    ORGANIZATION_ACTIVITIES_TABLE.insert().values(
                        organization_id=UUID(organization.oid),
                        activity_id=UUID(activity.oid),
                    ),
                )

        try:
            await self.session.flush([organization])
            await self.session.commit()
        except IntegrityError as err:
            await self.session.rollback()
            self._parse_error(err, organization)

    async def get_by_id(self, organization_id: str) -> OrganizationEntity | None:
        """Получает организацию по ID."""
        try:
            org_uuid = UUID(organization_id)
        except (ValueError, AttributeError):
            return None

        stmt = select(OrganizationEntity).where(ORGANIZATIONS_TABLE.c.id == org_uuid)
        result = await self.session.execute(stmt)
        organization = result.scalar_one_or_none()

        if organization:
            # Загружаем телефоны отдельно
            await self._load_phones(organization)

        return organization

    async def filter(
        self,
        filters: OrganizationFilter,
    ) -> Iterable[OrganizationEntity]:
        """Фильтрует организации по заданным критериям."""
        stmt = select(OrganizationEntity)

        # Фильтр по имени (частичное совпадение, case-insensitive)
        if filters.name:
            stmt = stmt.where(ORGANIZATIONS_TABLE.c.name.ilike(f"%{filters.name}%"))

        # Фильтр по адресу здания
        if filters.address:
            stmt = stmt.join(
                BUILDINGS_TABLE,
                ORGANIZATIONS_TABLE.c.building_id == BUILDINGS_TABLE.c.id,
            ).where(BUILDINGS_TABLE.c.address.ilike(f"%{filters.address}%"))

        # Фильтр по виду деятельности (через связь many-to-many)
        if filters.activity_name:
            from infrastructure.database.models.activity import ACTIVITIES_TABLE

            stmt = (
                stmt.join(
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
            stmt = stmt.limit(filters.limit)
        if filters.offset:
            stmt = stmt.offset(filters.offset)

        result = await self.session.execute(stmt)
        organizations = result.scalars().unique().all()

        # Загружаем телефоны для всех организаций
        for org in organizations:
            await self._load_phones(org)

        return organizations

    async def _load_phones(self, organization: OrganizationEntity) -> None:
        """Загружает телефоны для организации."""
        stmt = select(ORGANIZATION_PHONES_TABLE.c.phone).where(
            ORGANIZATION_PHONES_TABLE.c.organization_id == UUID(organization.oid),
        )
        result = await self.session.execute(stmt)
        phones = [row[0] for row in result]
        organization.phones = [
            OrganizationPhoneValueObject(value=phone) for phone in phones
        ]

    def _parse_error(
        self,
        err: DBAPIError,
        organization: OrganizationEntity,
    ) -> NoReturn:
        """Парсит ошибки БД и выбрасывает соответствующие доменные
        исключения."""
        constraint_name = getattr(
            getattr(getattr(err, "__cause__", None), "__cause__", None),
            "constraint_name",
            None,
        )

        match constraint_name:
            case "pk_organizations":
                # Дублирование ID
                raise OrganizationIdAlreadyExistsException(
                    organization_id=organization.oid,
                ) from err
            case "organizations_name_key" | "uq_organizations_name":
                # Организация с таким именем уже существует
                raise OrganizationWithThatNameAlreadyExistsException(
                    name=organization.name.as_generic_type(),
                ) from err
            case _:
                # Любая другая ошибка - пробрасываем дальше
                raise RepoException() from err
