from domain.organization.entities import BuildingEntity
from domain.organization.value_objects import (
    BuildingAddressValueObject,
    BuildingCoordinatesValueObject,
)
from infrastructure.database.models.building import BuildingModel


def building_entity_to_model(entity: BuildingEntity) -> BuildingModel:
    return BuildingModel(
        oid=entity.oid,
        address=entity.address.as_generic_type(),
        latitude=entity.coordinates.latitude,
        longitude=entity.coordinates.longitude,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def building_model_to_entity(model: BuildingModel) -> BuildingEntity:
    return BuildingEntity(
        oid=model.oid,
        address=BuildingAddressValueObject(value=model.address),
        coordinates=BuildingCoordinatesValueObject(
            latitude=model.latitude,
            longitude=model.longitude,
        ),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
