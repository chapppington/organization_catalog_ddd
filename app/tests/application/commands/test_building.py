import pytest

from application.commands.building import CreateBuildingCommand
from application.mediator import Mediator
from domain.organization.exceptions import (
    EmptyBuildingAddressException,
    InvalidBuildingLatitudeException,
    InvalidBuildingLongitudeException,
)
from domain.organization.interfaces.repositories.building import BaseBuildingRepository


@pytest.mark.asyncio()
async def test_create_building_command_success(
    building_repository: BaseBuildingRepository,
    mediator: Mediator,
):
    """Тест успешного создания здания."""
    address = "г. Москва, ул. Ленина 1"
    latitude = 55.7558
    longitude = 37.6173

    building, *_ = await mediator.handle_command(
        CreateBuildingCommand(
            address=address,
            latitude=latitude,
            longitude=longitude,
        ),
    )

    assert building is not None
    assert building.address.as_generic_type() == address
    assert building.coordinates.latitude == latitude
    assert building.coordinates.longitude == longitude

    # Проверяем что здание сохранилось в репозитории
    saved_building = await building_repository.get_by_id(building.oid)
    assert saved_building is not None
    assert saved_building.oid == building.oid


@pytest.mark.asyncio()
async def test_create_building_command_invalid_latitude(
    mediator: Mediator,
):
    """Тест создания здания с невалидной широтой."""
    with pytest.raises(InvalidBuildingLatitudeException):
        await mediator.handle_command(
            CreateBuildingCommand(
                address="г. Москва, ул. Ленина 1",
                latitude=100.0,  # Невалидная широта (макс 90)
                longitude=37.6173,
            ),
        )


@pytest.mark.asyncio()
async def test_create_building_command_invalid_longitude(
    mediator: Mediator,
):
    """Тест создания здания с невалидной долготой."""
    with pytest.raises(InvalidBuildingLongitudeException):
        await mediator.handle_command(
            CreateBuildingCommand(
                address="г. Москва, ул. Ленина 1",
                latitude=55.7558,
                longitude=200.0,  # Невалидная долгота (макс 180)
            ),
        )


@pytest.mark.asyncio()
async def test_create_building_command_empty_address(
    mediator: Mediator,
):
    """Тест создания здания с пустым адресом."""
    with pytest.raises(EmptyBuildingAddressException):
        await mediator.handle_command(
            CreateBuildingCommand(
                address="",  # Пустой адрес
                latitude=55.7558,
                longitude=37.6173,
            ),
        )
