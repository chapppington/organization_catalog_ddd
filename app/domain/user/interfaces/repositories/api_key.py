from abc import (
    ABC,
    abstractmethod,
)
from uuid import UUID

from domain.user.entities import APIKeyEntity


class BaseAPIKeyRepository(ABC):
    @abstractmethod
    async def add(self, api_key: APIKeyEntity) -> None: ...

    @abstractmethod
    async def get_by_key(self, key: UUID) -> APIKeyEntity | None: ...
