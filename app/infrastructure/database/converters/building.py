from geoalchemy2.shape import to_shape
from infrastructure.database.models.building import BuildingModel

from domain.organization.entities import BuildingEntity
from domain.organization.value_objects import (
    BuildingAddressValueObject,
    BuildingCoordinatesValueObject,
)


def building_entity_to_model(entity: BuildingEntity) -> BuildingModel:
    location = f"POINT({entity.coordinates.longitude} {entity.coordinates.latitude})"

    return BuildingModel(
        oid=entity.oid,
        address=entity.address.as_generic_type(),
        location=location,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def building_model_to_entity(model: BuildingModel) -> BuildingEntity:
    shape = to_shape(model.location)
    longitude = shape.x
    latitude = shape.y

    return BuildingEntity(
        oid=model.oid,
        address=BuildingAddressValueObject(value=model.address),
        coordinates=BuildingCoordinatesValueObject(
            latitude=latitude,
            longitude=longitude,
        ),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
