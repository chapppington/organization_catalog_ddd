import math
from typing import (
    Iterable,
    NoReturn,
)
from uuid import UUID

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.exc import (
    DBAPIError,
    IntegrityError,
)

from application.common.exceptions import RepoException
from application.exceptions.building import (
    BuildingIdAlreadyExistsException,
    BuildingWithThatAddressAlreadyExistsException,
)
from domain.organization.entities import BuildingEntity
from domain.organization.interfaces.repositories.building import BaseBuildingRepository
from domain.organization.interfaces.repositories.filters import BuildingFilter
from infrastructure.database.models.building import BUILDINGS_TABLE
from infrastructure.database.repositories.base import BaseSQLAlchemyRepository


class BuildingRepository(BaseSQLAlchemyRepository, BaseBuildingRepository):
    async def add(self, building: BuildingEntity) -> None:
        """Добавляет новое здание в базу данных."""
        self.session.add(building)
        try:
            await self.session.flush([building])
            await self.session.commit()
        except IntegrityError as err:
            await self.session.rollback()
            self._parse_error(err, building)

    async def get_by_id(self, building_id: str) -> BuildingEntity | None:
        """Получает здание по ID."""
        try:
            building_uuid = UUID(building_id)
        except (ValueError, AttributeError):
            return None

        stmt = select(BuildingEntity).where(BUILDINGS_TABLE.c.id == building_uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def filter(self, filters: BuildingFilter) -> Iterable[BuildingEntity]:
        """Фильтрует здания по заданным критериям."""
        stmt = select(BuildingEntity)

        # Фильтр по адресу (частичное совпадение, case-insensitive)
        if filters.address:
            stmt = stmt.where(BUILDINGS_TABLE.c.address.ilike(f"%{filters.address}%"))

        # Фильтр по координатам (точное совпадение)
        # Если указан radius, то latitude и longitude используются для центральной точки
        if filters.radius is not None:
            if filters.latitude is None or filters.longitude is None:
                # Радиус требует центральную точку
                return []

            # Реализация поиска по радиусу используя формулу Haversine в SQL
            R = 6371000  # Радиус Земли в метрах

            # Переводим градусы в радианы для центральной точки
            lat1_rad = math.radians(filters.latitude)

            # Вычисляем расстояние в SQL используя формулу Haversine
            lat_col = BUILDINGS_TABLE.c.latitude
            lon_col = BUILDINGS_TABLE.c.longitude

            delta_lat = func.radians(lat_col - filters.latitude)
            delta_lon = func.radians(lon_col - filters.longitude)

            a = func.power(func.sin(delta_lat / 2), 2) + func.cos(lat1_rad) * func.cos(
                func.radians(lat_col),
            ) * func.power(func.sin(delta_lon / 2), 2)
            c = 2 * func.atan2(func.sqrt(a), func.sqrt(1 - a))
            distance = R * c

            stmt = stmt.where(distance <= filters.radius)
        else:
            # Если radius не указан, используем точное совпадение
            if filters.latitude is not None:
                stmt = stmt.where(BUILDINGS_TABLE.c.latitude == filters.latitude)
            if filters.longitude is not None:
                stmt = stmt.where(BUILDINGS_TABLE.c.longitude == filters.longitude)

        # Фильтр по прямоугольнику (bounding box)
        if filters.lat_min is not None:
            stmt = stmt.where(BUILDINGS_TABLE.c.latitude >= filters.lat_min)
        if filters.lat_max is not None:
            stmt = stmt.where(BUILDINGS_TABLE.c.latitude <= filters.lat_max)
        if filters.lon_min is not None:
            stmt = stmt.where(BUILDINGS_TABLE.c.longitude >= filters.lon_min)
        if filters.lon_max is not None:
            stmt = stmt.where(BUILDINGS_TABLE.c.longitude <= filters.lon_max)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    def _parse_error(self, err: DBAPIError, building: BuildingEntity) -> NoReturn:
        constraint_name = getattr(
            getattr(getattr(err, "__cause__", None), "__cause__", None),
            "constraint_name",
            None,
        )

        match constraint_name:
            case "pk_buildings":
                # Дублирование ID
                raise BuildingIdAlreadyExistsException(
                    building_id=building.oid,
                ) from err
            case "buildings_address_key" | "uq_buildings_address":
                # Здание с таким адресом уже существует
                # PostgreSQL создает constraint с именем "buildings_address_key" для unique=True
                raise BuildingWithThatAddressAlreadyExistsException(
                    address=building.address.as_generic_type(),
                ) from err
            case _:
                # Любая другая ошибка - пробрасываем дальше
                raise RepoException() from err
