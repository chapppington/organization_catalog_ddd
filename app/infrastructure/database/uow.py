from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.exceptions import (
    CommitException,
    RollbackException,
)
from application.common.interfaces.uow import UnitOfWork


@dataclass
class SQLAlchemyUoW(UnitOfWork):
    session: AsyncSession

    async def commit(self) -> None:
        try:
            await self.session.commit()
        except SQLAlchemyError as err:
            raise CommitException from err

    async def rollback(self) -> None:
        try:
            await self.session.rollback()
        except SQLAlchemyError as err:
            raise RollbackException from err
