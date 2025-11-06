from domain.organization.entities import (
    ActivityEntity,
    BuildingEntity,
    OrganizationEntity,
)
from domain.organization.value_objects import (
    ActivityNameValueObject,
    BuildingAddressValueObject,
    BuildingCoordinatesValueObject,
    OrganizationNameValueObject,
    OrganizationPhoneValueObject,
)


def test_organization_entity_creation():
    """Test that organization entity can be created with valid data."""
    name = OrganizationNameValueObject(value="ООО Рога и Копыта")
    phone1 = OrganizationPhoneValueObject(value="+7 (495) 222-22-22")
    phone2 = OrganizationPhoneValueObject(value="+7 (495) 333-33-33")
    phones = [phone1, phone2]

    address = BuildingAddressValueObject(value="г. Москва, ул. Блюхера, 32/1")
    coordinates = BuildingCoordinatesValueObject(latitude=55.7558, longitude=37.6173)
    building = BuildingEntity(address=address, coordinates=coordinates)

    activity1 = ActivityEntity(name=ActivityNameValueObject(value="Молочная продукция"))
    activity2 = ActivityEntity(name=ActivityNameValueObject(value="Мясная продукция"))
    activities = [activity1, activity2]

    organization = OrganizationEntity(
        name=name,
        phones=phones,
        building=building,
        activities=activities,
    )

    assert organization.name == name
    assert organization.phones == phones
    assert len(organization.phones) == 2
    assert organization.building == building
    assert organization.activities == activities
    assert len(organization.activities) == 2
    assert organization.oid is not None


def test_organization_entity_with_empty_lists():
    """Test that organization entity can be created with empty phones and
    activities lists."""
    name = OrganizationNameValueObject(value="ООО Рога и Копыта")

    address = BuildingAddressValueObject(value="г. Москва, ул. Блюхера, 32/1")
    coordinates = BuildingCoordinatesValueObject(latitude=55.7558, longitude=37.6173)
    building = BuildingEntity(address=address, coordinates=coordinates)

    organization = OrganizationEntity(
        name=name,
        building=building,
    )

    assert organization.name == name
    assert organization.phones == []
    assert organization.activities == []
    assert organization.building == building
