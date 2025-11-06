from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from application.init import init_container
from application.mediator import Mediator
from application.queries.api_key import GetAPIKeyByKeyQuery
from domain.user.entities import APIKeyEntity
from domain.user.exceptions import APIKeyNotFoundException


security = HTTPBearer(
    scheme_name="api_key",
    description="Просто вставьте API ключ в поле ниже",
)


async def api_key_required(
    authorization: HTTPAuthorizationCredentials = Depends(security),
    container=Depends(init_container),
) -> APIKeyEntity:
    """Dependency для защиты эндпоинтов API ключом.

    Ожидает API ключ в заголовке Authorization в формате: Bearer
    <api_key>

    """
    try:
        # Парсим API ключ из заголовка Authorization
        api_key_str = authorization.credentials

        try:
            api_key_uuid = UUID(api_key_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key format",
            )

        # Получаем API ключ через медиатор
        mediator: Mediator = container.resolve(Mediator)
        query = GetAPIKeyByKeyQuery(key=api_key_uuid)

        try:
            api_key = await mediator.handle_query(query)
        except APIKeyNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key not found",
            )

        # Проверяем, не забанен ли ключ (это уже проверяется в сервисе)
        if api_key.banned_at:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key is banned",
            )

        return api_key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid API key: {str(e)}",
        )
