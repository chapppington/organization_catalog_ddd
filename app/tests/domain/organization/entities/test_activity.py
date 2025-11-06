import pytest

from domain.organization.entities import ActivityEntity
from domain.organization.exceptions import ActivityNestingLevelExceededException
from domain.organization.value_objects import ActivityNameValueObject


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
