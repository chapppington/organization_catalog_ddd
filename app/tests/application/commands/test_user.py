import pytest

from application.commands.user import CreateUserCommand
from application.mediator import Mediator
from domain.user.exceptions import UserAlreadyExistsException
from domain.user.interfaces.repositories.user import BaseUserRepository


@pytest.mark.asyncio
async def test_create_user_command_success(
    user_repository: BaseUserRepository,
    mediator: Mediator,
):
    """Тест успешного создания пользователя."""
    username = "testuser"
    password = "password123"

    user, *_ = await mediator.handle_command(
        CreateUserCommand(
            username=username,
            password=password,
        ),
    )

    assert user is not None
    assert user.username.value == username
    assert user.password is not None
    assert user.password != password  # Пароль должен быть захеширован

    # Проверяем что пользователь сохранился в репозитории
    saved_user = await user_repository.get_by_id(user.oid)
    assert saved_user is not None
    assert saved_user.oid == user.oid
    assert saved_user.username.value == username


@pytest.mark.asyncio
async def test_create_user_command_duplicate_username(
    mediator: Mediator,
):
    """Тест создания пользователя с уже существующим username."""
    username = "testuser"
    password = "password123"

    # Создаем первого пользователя
    await mediator.handle_command(
        CreateUserCommand(
            username=username,
            password=password,
        ),
    )

    # Пытаемся создать второго с тем же username
    with pytest.raises(UserAlreadyExistsException):
        await mediator.handle_command(
            CreateUserCommand(
                username=username,
                password="different_password",
            ),
        )


@pytest.mark.asyncio
async def test_create_user_command_short_password(
    mediator: Mediator,
):
    """Тест создания пользователя с коротким паролем."""
    username = "testuser"
    password = "short"  # Меньше 8 символов

    from domain.user.exceptions import PasswordTooShortException

    with pytest.raises(PasswordTooShortException):
        await mediator.handle_command(
            CreateUserCommand(
                username=username,
                password=password,
            ),
        )


@pytest.mark.asyncio
async def test_create_user_command_empty_password(
    mediator: Mediator,
):
    """Тест создания пользователя с пустым паролем."""
    username = "testuser"
    password = ""

    from domain.user.exceptions import EmptyPasswordException

    with pytest.raises(EmptyPasswordException):
        await mediator.handle_command(
            CreateUserCommand(
                username=username,
                password=password,
            ),
        )


@pytest.mark.asyncio
async def test_create_user_command_password_without_letter(
    mediator: Mediator,
):
    """Тест создания пользователя с паролем без букв."""
    username = "testuser"
    password = "12345678"  # Только цифры

    from domain.user.exceptions import InvalidPasswordException

    with pytest.raises(InvalidPasswordException):
        await mediator.handle_command(
            CreateUserCommand(
                username=username,
                password=password,
            ),
        )


@pytest.mark.asyncio
async def test_create_user_command_password_without_digit(
    mediator: Mediator,
):
    """Тест создания пользователя с паролем без цифр."""
    username = "testuser"
    password = "abcdefgh"  # Только буквы

    from domain.user.exceptions import InvalidPasswordException

    with pytest.raises(InvalidPasswordException):
        await mediator.handle_command(
            CreateUserCommand(
                username=username,
                password=password,
            ),
        )
