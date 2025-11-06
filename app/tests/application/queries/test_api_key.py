from uuid import uuid4

import pytest

from application.commands.api_key import CreateAPIKeyCommand
from application.commands.user import CreateUserCommand
from application.mediator import Mediator
from application.queries.api_key import GetAPIKeyByKeyQuery
from domain.user.exceptions import APIKeyNotFoundException


@pytest.mark.asyncio
async def test_get_api_key_by_key_query_success(mediator: Mediator):
    """Тест успешного получения API ключа по ключу."""
    # Создаем пользователя
    user, *_ = await mediator.handle_command(
        CreateUserCommand(
            username="testuser",
            password="password123",
        ),
    )

    # Создаем API ключ
    api_key, *_ = await mediator.handle_command(
        CreateAPIKeyCommand(
            user_id=user.oid,
        ),
    )

    # Получаем API ключ по ключу
    result = await mediator.handle_query(
        GetAPIKeyByKeyQuery(key=api_key.key),
    )

    assert result is not None
    assert result.key == api_key.key
    assert result.user_id == user.oid
    assert result.user.oid == user.oid


@pytest.mark.asyncio
async def test_get_api_key_by_key_query_not_found(mediator: Mediator):
    """Тест получения несуществующего API ключа."""
    non_existent_key = uuid4()

    with pytest.raises(APIKeyNotFoundException):
        await mediator.handle_query(
            GetAPIKeyByKeyQuery(key=non_existent_key),
        )
