import pytest

from application.commands.building import CreateBuildingCommand
from application.mediator import Mediator
from application.queries.building import (
    GetBuildingByIdQuery,
    GetBuildingsQuery,
)


@pytest.mark.asyncio
async def test_get_building_by_id_query(mediator: Mediator):
    """Тест получения здания по ID."""
    # Создаем здание
    building, *_ = await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    # Ищем по ID
    result = await mediator.handle_query(
        GetBuildingByIdQuery(building_id=str(building.oid)),
    )

    assert result is not None
    assert result.oid == building.oid
    assert result.address.as_generic_type() == "г. Москва, ул. Ленина 1"
    assert result.coordinates.latitude == 55.7558
    assert result.coordinates.longitude == 37.6173


@pytest.mark.asyncio
async def test_get_building_by_id_not_found(mediator: Mediator):
    """Тест получения несуществующего здания."""
    result = await mediator.handle_query(
        GetBuildingByIdQuery(building_id="00000000-0000-0000-0000-000000000000"),
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_buildings_query_with_address_filter(mediator: Mediator):
    """Тест получения списка зданий с фильтром по адресу."""
    # Создаем несколько зданий
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7560,
            longitude=37.6175,
        ),
    )
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Пушкина 1",
            latitude=55.7600,
            longitude=37.6200,
        ),
    )

    # Ищем по полному адресу
    results, total = await mediator.handle_query(
        GetBuildingsQuery(address="г. Москва, ул. Ленина 1", limit=10, offset=0),
    )

    results_list = list(results)
    assert len(results_list) == 2
    assert total == 2
    addresses = [building.address.as_generic_type() for building in results_list]
    assert "г. Москва, ул. Ленина 1" in addresses


@pytest.mark.asyncio
async def test_get_buildings_query_with_address_exact_match(mediator: Mediator):
    """Тест получения списка зданий с фильтром по точному адресу."""
    # Создаем здания
    await mediator.handle_command(
        CreateBuildingCommand(
            address="Точка 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )
    await mediator.handle_command(
        CreateBuildingCommand(
            address="Точка 1",
            latitude=55.7560,
            longitude=37.6175,
        ),
    )
    await mediator.handle_command(
        CreateBuildingCommand(
            address="Другая точка",
            latitude=55.7600,
            longitude=37.6173,
        ),
    )

    # Ищем по точному адресу
    results, total = await mediator.handle_query(
        GetBuildingsQuery(address="Точка 1", limit=10, offset=0),
    )

    results_list = list(results)
    assert len(results_list) == 2
    assert total == 2
    addresses = [building.address.as_generic_type() for building in results_list]
    assert "Точка 1" in addresses


@pytest.mark.asyncio
async def test_get_buildings_query_without_filters(mediator: Mediator):
    """Тест получения списка зданий без фильтров."""
    # Создаем несколько зданий
    await mediator.handle_command(
        CreateBuildingCommand(
            address="Здание 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )
    await mediator.handle_command(
        CreateBuildingCommand(
            address="Здание 2",
            latitude=55.7600,
            longitude=37.6200,
        ),
    )
    await mediator.handle_command(
        CreateBuildingCommand(
            address="Здание 3",
            latitude=55.7300,
            longitude=37.6000,
        ),
    )

    # Ищем без фильтров
    results, total = await mediator.handle_query(
        GetBuildingsQuery(limit=10, offset=0),
    )

    results_list = list(results)
    assert len(results_list) == 3
    assert total == 3


@pytest.mark.asyncio
async def test_get_buildings_query_pagination(mediator: Mediator):
    """Тест пагинации при получении списка зданий."""
    # Создаем 5 зданий
    for i in range(5):
        await mediator.handle_command(
            CreateBuildingCommand(
                address=f"Здание {i + 1}",
                latitude=55.7558 + i * 0.001,
                longitude=37.6173 + i * 0.001,
            ),
        )

    # Тест пагинации: берем первые 2
    results_page1, total1 = await mediator.handle_query(
        GetBuildingsQuery(limit=2, offset=0),
    )
    assert len(list(results_page1)) == 2
    assert total1 == 5

    # Берем следующие 2
    results_page2, total2 = await mediator.handle_query(
        GetBuildingsQuery(limit=2, offset=2),
    )
    assert len(list(results_page2)) == 2
    assert total2 == 5

    # Берем последний
    results_page3, total3 = await mediator.handle_query(
        GetBuildingsQuery(limit=2, offset=4),
    )
    assert len(list(results_page3)) == 1
    assert total3 == 5
