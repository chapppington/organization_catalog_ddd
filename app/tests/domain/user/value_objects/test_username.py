import pytest

from domain.user.exceptions import (
    EmptyUsernameException,
    InvalidUsernameException,
    UsernameTooLongException,
)
from domain.user.value_objects import UsernameValueObject


@pytest.mark.parametrize(
    "username,should_raise",
    [
        ("user123", False),
        ("test_user", False),
        ("admin", False),
        ("user_123", False),
        ("", True),  # Пустой username
        ("ab", True),  # Слишком короткий (< 3)
        ("a" * 256, True),  # Слишком длинный (> 255)
        ("user-name", True),  # Содержит дефис
        ("_user", True),  # Начинается с подчеркивания
        ("123user", False),  # Начинается с цифры - OK
        ("user-name-test", True),  # Содержит дефисы
    ],
)
def test_username_value_object(username, should_raise):
    """Тест валидации username."""
    if should_raise:
        with pytest.raises(
            (
                EmptyUsernameException,
                InvalidUsernameException,
                UsernameTooLongException,
            ),
        ):
            UsernameValueObject(value=username)
    else:
        obj = UsernameValueObject(value=username)
        assert obj.as_generic_type() == username
