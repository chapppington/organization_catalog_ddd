from dataclasses import dataclass
from uuid import UUID

from application.queries.base import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.user.entities import APIKeyEntity
from domain.user.services import APIKeyService


@dataclass(frozen=True)
class GetAPIKeyByKeyQuery(BaseQuery):
    key: UUID


@dataclass(frozen=True)
class GetAPIKeyByKeyQueryHandler(
    BaseQueryHandler[GetAPIKeyByKeyQuery, APIKeyEntity],
):
    api_key_service: APIKeyService

    async def handle(
        self,
        query: GetAPIKeyByKeyQuery,
    ) -> APIKeyEntity:
        return await self.api_key_service.get_api_key(query.key)
