import pytest

from application.commands.building import CreateBuildingCommand
from application.mediator import Mediator
from application.queries.building import (
    GetBuildingByAddressQuery,
    GetBuildingByIdQuery,
)


@pytest.mark.asyncio()
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
        GetBuildingByIdQuery(building_id=building.oid),
    )

    assert result is not None
    assert result.oid == building.oid
    assert result.address.as_generic_type() == "г. Москва, ул. Ленина 1"
    assert result.coordinates.latitude == 55.7558
    assert result.coordinates.longitude == 37.6173


@pytest.mark.asyncio()
async def test_get_building_by_id_not_found(mediator: Mediator):
    """Тест получения несуществующего здания."""
    result = await mediator.handle_query(
        GetBuildingByIdQuery(building_id="00000000-0000-0000-0000-000000000000"),
    )

    assert result is None


@pytest.mark.asyncio()
async def test_get_building_by_address_query(mediator: Mediator):
    """Тест получения здания по адресу."""
    building, *_ = await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    result = await mediator.handle_query(
        GetBuildingByAddressQuery(address="г. Москва, ул. Ленина 1"),
    )

    assert result is not None
    assert result.oid == building.oid
    assert result.address.as_generic_type() == "г. Москва, ул. Ленина 1"
    assert result.coordinates.latitude == 55.7558
    assert result.coordinates.longitude == 37.6173


@pytest.mark.asyncio()
async def test_get_building_by_address_not_found(mediator: Mediator):
    """Тест получения несуществующего здания по адресу."""
    result = await mediator.handle_query(
        GetBuildingByAddressQuery(address="Несуществующий адрес"),
    )

    assert result is None
