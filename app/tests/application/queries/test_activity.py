import pytest

from application.commands.activity import CreateActivityCommand
from application.mediator import Mediator
from application.queries.activity import (
    GetActivitiesQuery,
    GetActivityByIdQuery,
)


@pytest.mark.asyncio()
async def test_get_activity_by_id_query(mediator: Mediator):
    """Тест получения деятельности по ID."""
    # Создаем деятельность
    activity, *_ = await mediator.handle_command(
        CreateActivityCommand(name="Еда", parent_id=None),
    )

    # Ищем по ID
    result = await mediator.handle_query(
        GetActivityByIdQuery(activity_id=activity.oid),
    )

    assert result is not None
    assert result.oid == activity.oid
    assert result.name.as_generic_type() == "Еда"


@pytest.mark.asyncio()
async def test_get_activity_by_id_not_found(mediator: Mediator):
    """Тест получения несуществующей деятельности."""
    result = await mediator.handle_query(
        GetActivityByIdQuery(activity_id="00000000-0000-0000-0000-000000000000"),
    )

    assert result is None


@pytest.mark.asyncio()
async def test_get_activities_query_with_name_filter(mediator: Mediator):
    """Тест получения списка деятельностей с фильтром по названию."""
    # Создаем несколько деятельностей
    await mediator.handle_command(CreateActivityCommand(name="Еда", parent_id=None))
    await mediator.handle_command(CreateActivityCommand(name="Одежда", parent_id=None))
    await mediator.handle_command(
        CreateActivityCommand(name="Еда на вынос", parent_id=None),
    )

    # Ищем по названию "Еда"
    results, total = await mediator.handle_query(
        GetActivitiesQuery(name="Еда", limit=10, offset=0),
    )

    results_list = list(results)
    assert len(results_list) == 2
    assert total == 2
    names = [activity.name.as_generic_type() for activity in results_list]
    assert "Еда" in names
    assert "Еда на вынос" in names


@pytest.mark.asyncio()
async def test_get_activities_query_with_parent_id_filter(mediator: Mediator):
    """Тест получения списка деятельностей с фильтром по parent_id."""
    # Создаем родительскую деятельность
    parent, *_ = await mediator.handle_command(
        CreateActivityCommand(name="Еда", parent_id=None),
    )

    # Создаем дочерние деятельности
    await mediator.handle_command(
        CreateActivityCommand(name="Мясная продукция", parent_id=parent.oid),
    )
    await mediator.handle_command(
        CreateActivityCommand(name="Молочная продукция", parent_id=parent.oid),
    )

    # Создаем деятельность без родителя
    await mediator.handle_command(CreateActivityCommand(name="Одежда", parent_id=None))

    # Ищем по parent_id
    results, total = await mediator.handle_query(
        GetActivitiesQuery(parent_id=parent.oid, limit=10, offset=0),
    )

    results_list = list(results)
    assert len(results_list) == 2
    assert total == 2
    names = [activity.name.as_generic_type() for activity in results_list]
    assert "Мясная продукция" in names
    assert "Молочная продукция" in names


@pytest.mark.asyncio()
async def test_get_activities_query_with_both_filters(mediator: Mediator):
    """Тест получения списка деятельностей с фильтрами по name и parent_id."""
    # Создаем родительскую деятельность
    parent, *_ = await mediator.handle_command(
        CreateActivityCommand(name="Еда", parent_id=None),
    )

    # Создаем дочерние деятельности
    await mediator.handle_command(
        CreateActivityCommand(name="Мясная продукция", parent_id=parent.oid),
    )
    await mediator.handle_command(
        CreateActivityCommand(name="Молочная продукция", parent_id=parent.oid),
    )

    # Ищем по parent_id и name
    results, total = await mediator.handle_query(
        GetActivitiesQuery(
            name="Мясная продукция",
            parent_id=parent.oid,
            limit=10,
            offset=0,
        ),
    )

    results_list = list(results)
    assert len(results_list) == 1
    assert total == 1
    assert results_list[0].name.as_generic_type() == "Мясная продукция"


@pytest.mark.asyncio()
async def test_get_activities_query_without_filters(mediator: Mediator):
    """Тест получения списка деятельностей без фильтров."""
    # Создаем несколько деятельностей
    await mediator.handle_command(CreateActivityCommand(name="Еда", parent_id=None))
    await mediator.handle_command(CreateActivityCommand(name="Одежда", parent_id=None))
    await mediator.handle_command(CreateActivityCommand(name="Техника", parent_id=None))

    # Ищем без фильтров
    results, total = await mediator.handle_query(
        GetActivitiesQuery(limit=10, offset=0),
    )

    results_list = list(results)
    assert len(results_list) == 3
    assert total == 3


@pytest.mark.asyncio()
async def test_get_activities_query_pagination(mediator: Mediator):
    """Тест пагинации при получении списка деятельностей."""
    # Создаем 5 деятельностей
    for i in range(5):
        await mediator.handle_command(
            CreateActivityCommand(name=f"Деятельность {i + 1}", parent_id=None),
        )

    # Тест пагинации: берем первые 2
    results_page1, total1 = await mediator.handle_query(
        GetActivitiesQuery(limit=2, offset=0),
    )
    assert len(list(results_page1)) == 2
    assert total1 == 5

    # Берем следующие 2
    results_page2, total2 = await mediator.handle_query(
        GetActivitiesQuery(limit=2, offset=2),
    )
    assert len(list(results_page2)) == 2
    assert total2 == 5

    # Берем последний
    results_page3, total3 = await mediator.handle_query(
        GetActivitiesQuery(limit=2, offset=4),
    )
    assert len(list(results_page3)) == 1
    assert total3 == 5
