from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.user.entities import APIKeyEntity
from domain.user.interfaces.repositories.api_key import BaseAPIKeyRepository


@dataclass
class DummyInMemoryAPIKeyRepository(BaseAPIKeyRepository):
    _saved_api_keys: list[APIKeyEntity] = field(default_factory=list, kw_only=True)

    async def add(self, api_key: APIKeyEntity) -> None:
        self._saved_api_keys.append(api_key)

    async def get_by_key(self, key: UUID) -> APIKeyEntity | None:
        try:
            return next(
                api_key for api_key in self._saved_api_keys if api_key.key == key
            )
        except StopIteration:
            return None
