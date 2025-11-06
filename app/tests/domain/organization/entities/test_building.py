from domain.organization.entities import BuildingEntity
from domain.organization.value_objects import (
    BuildingAddressValueObject,
    BuildingCoordinatesValueObject,
)


def test_building_entity_creation():
    """Test that building entity can be created with valid data."""
    address = BuildingAddressValueObject(value="г. Москва, ул. Ленина 1, офис 3")
    coordinates = BuildingCoordinatesValueObject(latitude=55.7558, longitude=37.6173)

    building = BuildingEntity(address=address, coordinates=coordinates)

    assert building.address == address
    assert building.coordinates == coordinates
    assert building.oid is not None
    assert building.created_at is not None
    assert building.updated_at is not None
