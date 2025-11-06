import pytest

from application.commands.user import CreateUserCommand
from application.mediator import Mediator
from application.queries.user import AuthenticateUserQuery
from domain.user.exceptions import InvalidCredentialsException


@pytest.mark.asyncio
async def test_authenticate_user_query_success(mediator: Mediator):
    """Тест успешной аутентификации пользователя."""
    username = "testuser"
    password = "password123"

    # Создаем пользователя
    user, *_ = await mediator.handle_command(
        CreateUserCommand(
            username=username,
            password=password,
        ),
    )

    # Аутентифицируем пользователя
    authenticated_user = await mediator.handle_query(
        AuthenticateUserQuery(
            username=username,
            password=password,
        ),
    )

    assert authenticated_user is not None
    assert authenticated_user.oid == user.oid
    assert authenticated_user.username.value == username


@pytest.mark.asyncio
async def test_authenticate_user_query_invalid_password(mediator: Mediator):
    """Тест аутентификации с неверным паролем."""
    username = "testuser"
    password = "password123"
    wrong_password = "wrongpassword"

    # Создаем пользователя
    await mediator.handle_command(
        CreateUserCommand(
            username=username,
            password=password,
        ),
    )

    # Пытаемся аутентифицироваться с неверным паролем
    with pytest.raises(InvalidCredentialsException):
        await mediator.handle_query(
            AuthenticateUserQuery(
                username=username,
                password=wrong_password,
            ),
        )


@pytest.mark.asyncio
async def test_authenticate_user_query_user_not_found(mediator: Mediator):
    """Тест аутентификации несуществующего пользователя."""
    username = "nonexistent"
    password = "password123"

    # Пытаемся аутентифицироваться с несуществующим пользователем
    with pytest.raises(InvalidCredentialsException):
        await mediator.handle_query(
            AuthenticateUserQuery(
                username=username,
                password=password,
            ),
        )


@pytest.mark.asyncio
async def test_authenticate_user_query_case_insensitive_username(mediator: Mediator):
    """Тест аутентификации с username в разном регистре."""
    username = "TestUser"
    password = "password123"

    # Создаем пользователя
    user, *_ = await mediator.handle_command(
        CreateUserCommand(
            username=username,
            password=password,
        ),
    )

    # Аутентифицируем с username в нижнем регистре
    authenticated_user = await mediator.handle_query(
        AuthenticateUserQuery(
            username=username.lower(),
            password=password,
        ),
    )

    assert authenticated_user is not None
    assert authenticated_user.oid == user.oid
