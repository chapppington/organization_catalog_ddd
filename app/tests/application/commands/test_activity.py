import pytest

from application.commands.activity import CreateActivityCommand
from application.mediator import Mediator
from domain.organization.exceptions import (
    ActivityNestingLevelExceededException,
    ActivityNotFoundException,
    EmptyActivityNameException,
)
from domain.organization.interfaces.repositories.activity import BaseActivityRepository
from settings.config import Config


@pytest.mark.asyncio
async def test_create_activity_command_success(
    activity_repository: BaseActivityRepository,
    mediator: Mediator,
):
    """Тест успешного создания корневой деятельности."""
    name = "Еда"

    activity, *_ = await mediator.handle_command(
        CreateActivityCommand(
            name=name,
            parent_id=None,
        ),
    )

    assert activity is not None
    assert activity.name.as_generic_type() == name
    assert activity.parent is None

    # Проверяем что деятельность сохранилась в репозитории
    saved_activity = await activity_repository.get_by_id(activity.oid)
    assert saved_activity is not None
    assert saved_activity.oid == activity.oid


@pytest.mark.asyncio
async def test_create_activity_command_with_parent(
    activity_repository: BaseActivityRepository,
    mediator: Mediator,
):
    """Тест создания вложенной деятельности."""
    # Создаем родительскую деятельность
    parent_activity, *_ = await mediator.handle_command(
        CreateActivityCommand(
            name="Еда",
            parent_id=None,
        ),
    )

    # Создаем дочернюю деятельность
    child_activity, *_ = await mediator.handle_command(
        CreateActivityCommand(
            name="Мясная продукция",
            parent_id=parent_activity.oid,
        ),
    )

    assert child_activity is not None
    assert child_activity.name.as_generic_type() == "Мясная продукция"
    assert child_activity.parent is not None
    assert child_activity.parent.oid == parent_activity.oid

    # Проверяем что деятельность сохранилась в репозитории
    saved_activity = await activity_repository.get_by_id(child_activity.oid)
    assert saved_activity is not None


@pytest.mark.asyncio
async def test_create_activity_command_parent_not_found(
    mediator: Mediator,
):
    """Тест создания деятельности с несуществующим родителем."""
    with pytest.raises(ActivityNotFoundException):
        await mediator.handle_command(
            CreateActivityCommand(
                name="Дочерняя деятельность",
                parent_id="non-existent-id",
            ),
        )


@pytest.mark.asyncio
async def test_create_activity_command_empty_name(
    mediator: Mediator,
):
    """Тест создания деятельности с пустым названием."""
    with pytest.raises(EmptyActivityNameException):
        await mediator.handle_command(
            CreateActivityCommand(
                name="",
                parent_id=None,
            ),
        )


@pytest.mark.asyncio
async def test_create_activity_command_max_nesting_level(
    mediator: Mediator,
    config: Config,
):
    """Тест проверки максимального уровня вложенности."""
    max_level = config.max_activity_nesting_level

    # Создаем цепочку деятельностей до максимального уровня
    parent_id = None
    activities = []

    for i in range(max_level):
        activity, *_ = await mediator.handle_command(
            CreateActivityCommand(
                name=f"Level {i + 1}",
                parent_id=parent_id,
            ),
        )
        activities.append(activity)
        parent_id = activity.oid

    # Последняя созданная деятельность должна быть на максимальном уровне
    last_activity = activities[-1]
    assert last_activity._calculate_nesting_level() == max_level

    # Попытка создать еще один уровень должна вызвать исключение
    with pytest.raises(ActivityNestingLevelExceededException):
        await mediator.handle_command(
            CreateActivityCommand(
                name="Exceeding level",
                parent_id=last_activity.oid,
            ),
        )
