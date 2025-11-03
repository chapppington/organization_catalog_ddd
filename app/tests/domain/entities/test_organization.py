import pytest

from domain.organization.entities import (
    ActivityEntity,
    BuildingEntity,
    OrganizationEntity,
)
from domain.organization.exceptions import ActivityNestingLevelExceededException
from domain.organization.value_objects import (
    ActivityNameValueObject,
    BuildingAddressValueObject,
    BuildingCoordinatesValueObject,
    OrganizationNameValueObject,
    OrganizationPhoneValueObject,
)


def test_activity_entity_calculate_nesting_level(config):
    """Test that activity nesting level is calculated correctly."""
    max_level = config.max_activity_nesting_level
    # Test at least 3 levels or up to max_level, whichever is smaller
    test_levels = min(3, max_level)

    activities = []
    parent = None
    for i in range(test_levels):
        activity = ActivityEntity(
            name=ActivityNameValueObject(value=f"Level {i + 1}"),
            parent=parent,
        )
        activities.append(activity)
        parent = activity

    # Verify each level is calculated correctly
    for i, activity in enumerate(activities):
        assert activity._calculate_nesting_level() == i + 1


def test_activity_entity_allows_valid_nesting_levels(config):
    """Test that valid nesting levels are allowed."""
    max_level = config.max_activity_nesting_level

    # Create levels up to max_level (should work without exceptions)
    activities = []
    parent = None
    for i in range(max_level):
        activity = ActivityEntity(
            name=ActivityNameValueObject(value=f"Level {i + 1}"),
            parent=parent,
        )
        activities.append(activity)
        parent = activity

    # All should be created without exceptions
    for i, activity in enumerate(activities):
        assert activity._calculate_nesting_level() == i + 1


def test_activity_entity_prevents_exceeding_max_nesting_level(config):
    """Test that activity nesting level cannot exceed maximum allowed level."""
    max_level = config.max_activity_nesting_level

    # Create max_level levels (should work)
    activities = []
    parent = None
    for i in range(max_level):
        activity = ActivityEntity(
            name=ActivityNameValueObject(value=f"Level {i + 1}"),
            parent=parent,
        )
        activities.append(activity)
        parent = activity

    # Try to create level max_level + 1 (should fail)
    with pytest.raises(ActivityNestingLevelExceededException) as exc_info:
        ActivityEntity(
            name=ActivityNameValueObject(value="Exceeding level"),
            parent=activities[-1],
        )

    assert exc_info.value.current_level == max_level + 1
    assert exc_info.value.max_level == max_level


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
