from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from application.common.interfaces.uow import UnitOfWork


@dataclass
class BaseSQLAlchemyRepository:
    _uow: UnitOfWork

    @property
    def session(self) -> AsyncSession:
        """Возвращает сессию из Unit of Work."""
        return self._uow.session
