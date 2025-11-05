from domain.organization.entities import ActivityEntity
from domain.organization.value_objects import ActivityNameValueObject
from infrastructure.database.models.activity import ActivityModel


def activity_entity_to_model(entity: ActivityEntity) -> ActivityModel:
    """Конвертирует ActivityEntity в ActivityModel."""
    return ActivityModel(
        oid=entity.oid,
        name=entity.name.as_generic_type(),
        parent_id=entity.parent.oid if entity.parent else None,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def activity_model_to_entity(model: ActivityModel) -> ActivityEntity:
    """Конвертирует ActivityModel в ActivityEntity."""
    return ActivityEntity(
        oid=model.oid,
        name=ActivityNameValueObject(value=model.name),
        parent=activity_model_to_entity(model.parent) if model.parent else None,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
