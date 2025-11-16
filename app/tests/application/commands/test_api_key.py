from uuid import uuid4

import pytest

from application.commands.api_key import CreateAPIKeyCommand
from application.commands.user import CreateUserCommand
from application.mediator import Mediator
from domain.user.exceptions import UserNotFoundException
from domain.user.interfaces.repositories.api_key import BaseAPIKeyRepository


@pytest.mark.asyncio()
async def test_create_api_key_command_success(
    api_key_repository: BaseAPIKeyRepository,
    mediator: Mediator,
):
    """Тест успешного создания API ключа."""
    # Создаем пользователя
    user, *_ = await mediator.handle_command(
        CreateUserCommand(
            username="testuser",
            password="password123",
        ),
    )

    # Создаем API ключ для пользователя
    api_key, *_ = await mediator.handle_command(
        CreateAPIKeyCommand(
            user_id=user.oid,
        ),
    )

    assert api_key is not None
    assert api_key.user_id == user.oid
    assert api_key.user.oid == user.oid
    assert api_key.key is not None
    assert api_key.banned_at is None

    # Проверяем что API ключ сохранился в репозитории
    saved_api_key = await api_key_repository.get_by_key(api_key.key)
    assert saved_api_key is not None
    assert saved_api_key.key == api_key.key
    assert saved_api_key.user_id == user.oid


@pytest.mark.asyncio()
async def test_create_api_key_command_user_not_found(
    mediator: Mediator,
):
    """Тест создания API ключа для несуществующего пользователя."""
    non_existent_user_id = uuid4()

    with pytest.raises(UserNotFoundException):
        await mediator.handle_command(
            CreateAPIKeyCommand(
                user_id=non_existent_user_id,
            ),
        )


@pytest.mark.asyncio()
async def test_create_api_key_command_multiple_keys(
    api_key_repository: BaseAPIKeyRepository,
    mediator: Mediator,
):
    """Тест создания нескольких API ключей для одного пользователя."""
    # Создаем пользователя
    user, *_ = await mediator.handle_command(
        CreateUserCommand(
            username="testuser",
            password="password123",
        ),
    )

    # Создаем первый API ключ
    api_key1, *_ = await mediator.handle_command(
        CreateAPIKeyCommand(
            user_id=user.oid,
        ),
    )

    # Создаем второй API ключ
    api_key2, *_ = await mediator.handle_command(
        CreateAPIKeyCommand(
            user_id=user.oid,
        ),
    )

    assert api_key1.key != api_key2.key
    assert api_key1.user_id == api_key2.user_id

    # Проверяем что оба ключа сохранились
    saved_api_key1 = await api_key_repository.get_by_key(api_key1.key)
    saved_api_key2 = await api_key_repository.get_by_key(api_key2.key)

    assert saved_api_key1 is not None
    assert saved_api_key2 is not None
