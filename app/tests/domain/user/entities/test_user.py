from domain.user.entities import UserEntity
from domain.user.value_objects import UsernameValueObject


def test_user_entity_creation():
    """Тест создания пользователя."""
    username = UsernameValueObject(value="testuser")
    password = "hashed_password_123"

    user = UserEntity(
        username=username,
        password=password,
    )

    assert user.username == username
    assert user.password == password
    assert user.oid is not None
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_entity_equality():
    """Тест сравнения пользователей."""
    username1 = UsernameValueObject(value="testuser")
    username2 = UsernameValueObject(value="testuser")
    username3 = UsernameValueObject(value="otheruser")

    user1 = UserEntity(username=username1, password="hash1")
    user2 = UserEntity(username=username2, password="hash2")
    user3 = UserEntity(username=username3, password="hash1")

    # Пользователи с одинаковым username должны быть равны
    assert user1 == user2

    # Пользователи с разным username не равны
    assert user1 != user3


def test_user_entity_hash():
    """Тест хеширования пользователя."""
    username1 = UsernameValueObject(value="testuser")
    username2 = UsernameValueObject(value="testuser")

    user1 = UserEntity(username=username1, password="hash1")
    user2 = UserEntity(username=username2, password="hash2")

    # Пользователи с одинаковым username должны иметь одинаковый hash
    assert hash(user1) == hash(user2)
