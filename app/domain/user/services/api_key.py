from dataclasses import dataclass
from uuid import UUID

from domain.user.entities import APIKeyEntity
from domain.user.exceptions import (
    APIKeyBannedException,
    APIKeyNotFoundException,
    UserNotFoundException,
)
from domain.user.interfaces.repositories.api_key import BaseAPIKeyRepository
from domain.user.interfaces.repositories.user import BaseUserRepository


@dataclass
class APIKeyService:
    api_key_repository: BaseAPIKeyRepository
    user_repository: BaseUserRepository

    async def create_api_key(
        self,
        user_id: UUID,
    ) -> APIKeyEntity:
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundException(user_id=user_id)

        api_key = APIKeyEntity(
            user_id=user_id,
            user=user,
        )

        await self.api_key_repository.add(api_key)

        return api_key

    async def get_api_key(
        self,
        key: UUID,
    ) -> APIKeyEntity:
        api_key = await self.api_key_repository.get_by_key(key)

        if not api_key:
            raise APIKeyNotFoundException(api_key=key)

        if api_key.banned_at:
            raise APIKeyBannedException(api_key=key)

        return api_key
