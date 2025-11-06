import pytest

from domain.organization.exceptions import (
    EmptyBuildingAddressException,
    InvalidBuildingLatitudeException,
    InvalidBuildingLongitudeException,
)
from domain.organization.value_objects import (
    BuildingAddressValueObject,
    BuildingCoordinatesValueObject,
)


@pytest.mark.parametrize(
    "address,should_raise",
    [
        ("г. Москва, ул. Ленина 1, офис 3", False),
        ("г. Москва, ул. Блюхера, 32/1", False),
        ("Санкт-Петербург, Невский проспект, д. 28", False),
        ("", True),
    ],
)
def test_building_address_value_object(address, should_raise):
    if should_raise:
        with pytest.raises(EmptyBuildingAddressException):
            BuildingAddressValueObject(value=address)
    else:
        obj = BuildingAddressValueObject(value=address)
        assert obj.as_generic_type() == address


@pytest.mark.parametrize(
    "latitude,longitude,should_raise",
    [
        (55.7558, 37.6173, False),  # Moscow
        (59.9343, 30.3351, False),  # Saint Petersburg
        (0.0, 0.0, False),  # Prime meridian and equator
        (-90.0, -180.0, False),  # South pole and westernmost point
        (90.0, 180.0, False),  # North pole and easternmost point
        (91.0, 0.0, True),  # Invalid latitude
        (-91.0, 0.0, True),  # Invalid latitude
        (0.0, 181.0, True),  # Invalid longitude
        (0.0, -181.0, True),  # Invalid longitude
        (45.5, 120.3, False),  # Valid coordinates
    ],
)
def test_building_coordinates_value_object(latitude, longitude, should_raise):
    if should_raise:
        with pytest.raises(
            (InvalidBuildingLatitudeException, InvalidBuildingLongitudeException),
        ):
            BuildingCoordinatesValueObject(latitude=latitude, longitude=longitude)
    else:
        obj = BuildingCoordinatesValueObject(latitude=latitude, longitude=longitude)
        assert obj.as_generic_type() == (latitude, longitude)
        assert obj.latitude == latitude
        assert obj.longitude == longitude
