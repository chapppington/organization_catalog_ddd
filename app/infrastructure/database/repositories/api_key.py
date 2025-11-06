from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.user.entities import APIKeyEntity
from domain.user.interfaces.repositories.api_key import BaseAPIKeyRepository
from infrastructure.database.converters.user import (
    api_key_entity_to_model,
    api_key_model_to_entity,
)
from infrastructure.database.main import async_session_factory
from infrastructure.database.models.user import APIKeyModel


class SQLAlchemyAPIKeyRepository(BaseAPIKeyRepository):
    async def add(self, api_key: APIKeyEntity) -> None:
        async with async_session_factory() as session:
            model = api_key_entity_to_model(api_key)
            session.add(model)
            await session.commit()

    async def get_by_key(self, key: UUID) -> APIKeyEntity | None:
        async with async_session_factory() as session:
            stmt = (
                select(APIKeyModel)
                .where(APIKeyModel.key == key)
                .options(selectinload(APIKeyModel.user))
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return api_key_model_to_entity(result) if result else None
