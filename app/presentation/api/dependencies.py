from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from presentation.api.auth import auth_service

from application.init import init_container
from application.mediator import Mediator
from application.queries.api_key import GetAPIKeyByKeyQuery
from domain.user.entities import APIKeyEntity


security = HTTPBearer(
    scheme_name="api_key",
    description="Просто вставьте API ключ в поле ниже",
)


async def get_refresh_token_payload(
    request: Request,
) -> dict:
    """Dependency для получения payload из refresh токена."""
    return await auth_service.refresh_token_required(request)


async def get_access_token_payload(
    request: Request,
) -> dict:
    """Dependency для получения payload из access токена."""
    return await auth_service.access_token_required(request)


async def api_key_required(
    authorization: HTTPAuthorizationCredentials = Depends(security),
    container=Depends(init_container),
) -> APIKeyEntity:
    """Dependency для защиты эндпоинтов API ключом."""

    try:
        api_key_uuid = UUID(authorization.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
        )

    mediator: Mediator = container.resolve(Mediator)
    query = GetAPIKeyByKeyQuery(key=api_key_uuid)
    return await mediator.handle_query(query)
