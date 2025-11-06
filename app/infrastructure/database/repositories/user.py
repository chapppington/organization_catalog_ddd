from uuid import UUID

from sqlalchemy import select

from domain.user.entities import UserEntity
from domain.user.interfaces.repositories.user import BaseUserRepository
from infrastructure.database.converters.user import (
    user_entity_to_model,
    user_model_to_entity,
)
from infrastructure.database.main import async_session_factory
from infrastructure.database.models.user import UserModel


class SQLAlchemyUserRepository(BaseUserRepository):
    async def add(self, user: UserEntity) -> None:
        async with async_session_factory() as session:
            model = user_entity_to_model(user)
            session.add(model)
            await session.commit()

    async def get_by_id(self, user_id: UUID) -> UserEntity | None:
        async with async_session_factory() as session:
            stmt = select(UserModel).where(UserModel.oid == user_id)
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return user_model_to_entity(result) if result else None

    async def get_by_username(self, username: str) -> UserEntity | None:
        async with async_session_factory() as session:
            stmt = select(UserModel).where(UserModel.username.ilike(username))
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return user_model_to_entity(result) if result else None

    async def check_username_exists(self, username: str) -> bool:
        async with async_session_factory() as session:
            stmt = select(UserModel).where(UserModel.username.ilike(username))
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()

            return result is not None
