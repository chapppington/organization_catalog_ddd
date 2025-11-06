from domain.user.entities import (
    APIKeyEntity,
    UserEntity,
)
from domain.user.value_objects import UsernameValueObject
from infrastructure.database.models.user import (
    APIKeyModel,
    UserModel,
)


def user_entity_to_model(entity: UserEntity) -> UserModel:
    return UserModel(
        oid=entity.oid,
        username=entity.username.value,
        password=entity.password,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def user_model_to_entity(model: UserModel) -> UserEntity:
    return UserEntity(
        oid=model.oid,
        username=UsernameValueObject(value=model.username),
        password=model.password,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def api_key_entity_to_model(entity: APIKeyEntity) -> APIKeyModel:
    return APIKeyModel(
        oid=entity.oid,
        key=entity.key,
        user_id=entity.user_id,
        last_used=entity.last_used,
        banned_at=entity.banned_at,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def api_key_model_to_entity(
    model: APIKeyModel,
    user: UserEntity | None = None,
) -> APIKeyEntity:
    if user is None:
        user = user_model_to_entity(model.user)

    return APIKeyEntity(
        oid=model.oid,
        key=model.key,
        user_id=model.user_id,
        user=user,
        last_used=model.last_used,
        banned_at=model.banned_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
