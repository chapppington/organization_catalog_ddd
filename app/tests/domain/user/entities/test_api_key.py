from datetime import datetime
from uuid import uuid4

from domain.user.entities import (
    APIKeyEntity,
    UserEntity,
)
from domain.user.value_objects import UsernameValueObject


def test_api_key_entity_creation():
    """Тест создания API key."""
    user = UserEntity(
        username=UsernameValueObject(value="testuser"),
        password="hashed_password",
    )
    user_id = user.oid

    api_key = APIKeyEntity(
        user_id=user_id,
        user=user,
    )

    assert api_key.user_id == user_id
    assert api_key.user == user
    assert api_key.key is not None
    assert api_key.last_used is None
    assert api_key.banned_at is None
    assert api_key.oid is not None
    assert api_key.created_at is not None
    assert api_key.updated_at is not None


def test_api_key_entity_with_custom_key():
    """Тест создания API key с заданным ключом."""
    user = UserEntity(
        username=UsernameValueObject(value="testuser"),
        password="hashed_password",
    )
    custom_key = uuid4()

    api_key = APIKeyEntity(
        key=custom_key,
        user_id=user.oid,
        user=user,
    )

    assert api_key.key == custom_key


def test_api_key_entity_with_last_used():
    """Тест API key с last_used."""
    user = UserEntity(
        username=UsernameValueObject(value="testuser"),
        password="hashed_password",
    )
    last_used = datetime.now()

    api_key = APIKeyEntity(
        user_id=user.oid,
        user=user,
        last_used=last_used,
    )

    assert api_key.last_used == last_used


def test_api_key_entity_with_banned_at():
    """Тест API key с banned_at."""
    user = UserEntity(
        username=UsernameValueObject(value="testuser"),
        password="hashed_password",
    )
    banned_at = datetime.now()

    api_key = APIKeyEntity(
        user_id=user.oid,
        user=user,
        banned_at=banned_at,
    )

    assert api_key.banned_at == banned_at


def test_api_key_entity_equality():
    """Тест сравнения API keys."""
    user = UserEntity(
        username=UsernameValueObject(value="testuser"),
        password="hashed_password",
    )
    key = uuid4()

    api_key1 = APIKeyEntity(
        key=key,
        user_id=user.oid,
        user=user,
    )
    api_key2 = APIKeyEntity(
        key=key,
        user_id=user.oid,
        user=user,
    )
    api_key3 = APIKeyEntity(
        key=uuid4(),
        user_id=user.oid,
        user=user,
    )

    # API keys с одинаковым key должны быть равны
    assert api_key1 == api_key2

    # API keys с разным key не равны
    assert api_key1 != api_key3


def test_api_key_entity_hash():
    """Тест хеширования API key."""
    user = UserEntity(
        username=UsernameValueObject(value="testuser"),
        password="hashed_password",
    )
    key = uuid4()

    api_key1 = APIKeyEntity(
        key=key,
        user_id=user.oid,
        user=user,
    )
    api_key2 = APIKeyEntity(
        key=key,
        user_id=user.oid,
        user=user,
    )

    # API keys с одинаковым key должны иметь одинаковый hash
    assert hash(api_key1) == hash(api_key2)
