import re
from dataclasses import dataclass
from uuid import UUID

import bcrypt

from domain.user.entities import UserEntity
from domain.user.exceptions import (
    EmptyPasswordException,
    InvalidCredentialsException,
    InvalidPasswordException,
    PasswordTooShortException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from domain.user.interfaces.repositories.user import BaseUserRepository
from domain.user.value_objects import UsernameValueObject


MIN_PASSWORD_LENGTH = 8


@dataclass
class UserService:
    user_repository: BaseUserRepository

    def _validate_password(self, password: str) -> None:
        """Валидирует пароль перед хешированием."""
        if not password:
            raise EmptyPasswordException()

        if len(password) < MIN_PASSWORD_LENGTH:
            raise PasswordTooShortException(
                password_length=len(password),
                min_length=MIN_PASSWORD_LENGTH,
            )

        # Password should contain at least one letter and one digit
        has_letter = bool(re.search(r"[a-zA-Z]", password))
        has_digit = bool(re.search(r"\d", password))

        if not (has_letter and has_digit):
            raise InvalidPasswordException(
                reason="Password must contain at least one letter and one digit",
            )

    async def create_user(
        self,
        username: str,
        password: str,
    ) -> UserEntity:
        """Создает нового пользователя."""
        # Проверяем, не существует ли уже пользователь с таким именем пользователя
        username_exists = await self.user_repository.check_username_exists(username)

        if username_exists:
            raise UserAlreadyExistsException(username=username)

        # Валидируем пароль
        self._validate_password(password)

        # Хешируем пароль
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        user = UserEntity(
            username=UsernameValueObject(username),
            password=hashed_password,
        )

        await self.user_repository.add(user)
        return user

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> UserEntity:
        """Получает пользователя по ID."""
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundException(user_id=user_id)

        return user

    async def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> UserEntity:
        """Аутентифицирует пользователя по username и password.

        Для безопасности не раскрывает, существует ли пользователь с
        таким username. Всегда выбрасывает InvalidCredentialsException
        при неверных данных.

        """
        # Получаем пользователя по username
        user = await self.user_repository.get_by_username(username)

        # Если пользователь не найден, все равно проверяем пароль
        # чтобы время выполнения было одинаковым и не было утечки информации
        if user:
            password_valid = bcrypt.checkpw(
                password.encode("utf-8"),
                user.password.encode("utf-8"),
            )
        else:
            # Создаем фиктивный хеш для проверки, чтобы время выполнения было одинаковым
            # Это предотвращает timing attack (утечку информации через время ответа)
            dummy_hash = bcrypt.hashpw(
                b"dummy_password",
                bcrypt.gensalt(),
            )
            password_valid = bcrypt.checkpw(
                password.encode("utf-8"),
                dummy_hash,
            )
            # Все равно будет False, но время выполнения будет примерно одинаковым

        # Если пользователь не найден или пароль неверен - выбрасываем одинаковое исключение
        # Это не позволяет определить, существует ли пользователь с таким username
        if not user or not password_valid:
            raise InvalidCredentialsException()

        return user
