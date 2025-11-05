from typing import (
    Any,
    Iterable,
)
from uuid import UUID

from sqlalchemy import (
    func,
    select,
)

from domain.organization.entities import BuildingEntity
from domain.organization.interfaces.repositories.building import BaseBuildingRepository
from infrastructure.database.converters.building import (
    building_entity_to_model,
    building_model_to_entity,
)
from infrastructure.database.main import async_session_factory
from infrastructure.database.models.building import BuildingModel


class SQLAlchemyBuildingRepository(BaseBuildingRepository):
    async def add(self, building: BuildingEntity) -> None:
        """Добавить здание."""
        async with async_session_factory() as session:
            model = building_entity_to_model(building)
            session.add(model)
            await session.commit()

    async def get_by_id(self, building_id: UUID) -> BuildingEntity | None:
        """Получить здание по ID."""
        async with async_session_factory() as session:
            stmt = select(BuildingModel).where(BuildingModel.oid == building_id)
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return building_model_to_entity(result) if result else None

    async def get_by_address(self, address: str) -> BuildingEntity | None:
        """Получить здание по адресу."""
        async with async_session_factory() as session:
            stmt = select(BuildingModel).where(BuildingModel.address == address)
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return building_model_to_entity(result) if result else None

    async def filter(self, **filters: Any) -> Iterable[BuildingEntity]:
        """Фильтрация зданий."""
        async with async_session_factory() as session:
            stmt = select(BuildingModel)

            for field, value in filters.items():
                field_obj = getattr(BuildingModel, field)
                stmt = stmt.where(field_obj == value)

            res = await session.execute(stmt)
            results = [building_model_to_entity(row[0]) for row in res.all()]

            return results

    async def count(self, **filters: Any) -> int:
        """Подсчет зданий."""
        async with async_session_factory() as session:
            stmt = select(func.count(BuildingModel.oid))

            for field, value in filters.items():
                field_obj = getattr(BuildingModel, field)
                stmt = stmt.where(field_obj == value)

            res = await session.execute(stmt)
            return res.scalar_one()
