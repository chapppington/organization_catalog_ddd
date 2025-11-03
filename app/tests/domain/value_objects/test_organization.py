import pytest

from domain.organization.exceptions import (
    EmptyActivityNameException,
    EmptyBuildingAddressException,
    EmptyOrganizationNameException,
    EmptyOrganizationPhoneException,
    InvalidBuildingLatitudeException,
    InvalidBuildingLongitudeException,
    InvalidOrganizationPhoneException,
)
from domain.organization.value_objects import (
    ActivityNameValueObject,
    BuildingAddressValueObject,
    BuildingCoordinatesValueObject,
    OrganizationNameValueObject,
    OrganizationPhoneValueObject,
)


@pytest.mark.parametrize(
    "name,should_raise",
    [
        ("ООО Рога и Копыта", False),
        ("ИП Иванов", False),
        ("Торговый дом", False),
        ("", True),
    ],
)
def test_organization_name_value_object(name, should_raise):
    if should_raise:
        with pytest.raises(EmptyOrganizationNameException):
            OrganizationNameValueObject(value=name)
    else:
        obj = OrganizationNameValueObject(value=name)
        assert obj.as_generic_type() == name


@pytest.mark.parametrize(
    "phone,should_raise",
    [
        ("+7 (495) 123-45-67", False),
        ("8-923-666-13-13", False),
        ("+7 (495) 222-22-22", False),
        ("+7 (495) 333-33-33", False),
        ("+1 (555) 123-4567", False),
        ("5551234567", False),
        ("", True),
        ("123", True),
        ("2-222-222", True),  # Too short (only 7 digits)
        ("3-333-333", True),  # Too short (only 7 digits)
        ("++1234567890", True),
        ("invalid-phone", True),
        ("abc", True),
    ],
)
def test_organization_phone_value_object(phone, should_raise):
    if should_raise:
        with pytest.raises(
            (EmptyOrganizationPhoneException, InvalidOrganizationPhoneException),
        ):
            OrganizationPhoneValueObject(value=phone)
    else:
        obj = OrganizationPhoneValueObject(value=phone)
        assert obj.as_generic_type() == phone


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


@pytest.mark.parametrize(
    "name,should_raise",
    [
        ("Еда", False),
        ("Мясная продукция", False),
        ("Молочная продукция", False),
        ("Автомобили", False),
        ("Грузовые", False),
        ("Легковые", False),
        ("Запчасти", False),
        ("Аксессуары", False),
        ("", True),
    ],
)
def test_activity_name_value_object(name, should_raise):
    if should_raise:
        with pytest.raises(EmptyActivityNameException):
            ActivityNameValueObject(value=name)
    else:
        obj = ActivityNameValueObject(value=name)
        assert obj.as_generic_type() == name
