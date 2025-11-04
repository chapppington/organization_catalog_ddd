import pytest

from application.commands.activity import CreateActivityCommand
from application.commands.building import CreateBuildingCommand
from application.commands.organization import CreateOrganizationCommand
from application.mediator import Mediator
from domain.organization.exceptions import (
    ActivityNotFoundException,
    BuildingNotFoundException,
    EmptyOrganizationNameException,
    EmptyOrganizationPhoneException,
)
from domain.organization.interfaces.repositories.organization import (
    BaseOrganizationRepository,
)


@pytest.mark.asyncio
async def test_create_organization_command_success(
    organization_repository: BaseOrganizationRepository,
    mediator: Mediator,
):
    """Тест успешного создания организации."""
    # Создаем здание
    building, *_ = await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    # Создаем деятельности
    food_activity, *_ = await mediator.handle_command(
        CreateActivityCommand(name="Еда", parent_id=None),
    )
    await mediator.handle_command(
        CreateActivityCommand(name="Мясная продукция", parent_id=food_activity.oid),
    )

    # Создаем организацию
    organization, *_ = await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Рога и Копыта",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-123-4567", "+7-923-666-1313"],
            activities=["Еда", "Мясная продукция"],
        ),
    )

    assert organization is not None
    assert organization.name.as_generic_type() == "ООО Рога и Копыта"
    assert organization.building.oid == building.oid
    assert len(organization.phones) == 2
    assert len(organization.activities) == 2

    # Проверяем что организация сохранилась в репозитории
    saved_organization = await organization_repository.get_by_id(organization.oid)
    assert saved_organization is not None
    assert saved_organization.oid == organization.oid


@pytest.mark.asyncio
async def test_create_organization_command_building_not_found(
    mediator: Mediator,
):
    """Тест создания организации с несуществующим зданием."""
    # Создаем деятельность
    await mediator.handle_command(
        CreateActivityCommand(name="Еда", parent_id=None),
    )

    # Пытаемся создать организацию с несуществующим адресом
    with pytest.raises(BuildingNotFoundException):
        await mediator.handle_command(
            CreateOrganizationCommand(
                name="ООО Рога",
                address="Несуществующий адрес",
                phones=["123"],
                activities=["Еда"],
            ),
        )


@pytest.mark.asyncio
async def test_create_organization_command_activity_not_found(
    mediator: Mediator,
):
    """Тест создания организации с несуществующей деятельностью."""
    # Создаем здание
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    # Пытаемся создать организацию с несуществующей деятельностью
    with pytest.raises(ActivityNotFoundException):
        await mediator.handle_command(
            CreateOrganizationCommand(
                name="ООО Рога",
                address="г. Москва, ул. Ленина 1",
                phones=["+7-495-123-4567"],
                activities=["Несуществующая деятельность"],
            ),
        )


@pytest.mark.asyncio
async def test_create_organization_command_empty_name(
    mediator: Mediator,
):
    """Тест создания организации с пустым названием."""
    # Создаем здание
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    # Создаем деятельность
    await mediator.handle_command(
        CreateActivityCommand(name="Еда", parent_id=None),
    )

    # Пытаемся создать организацию с пустым названием
    with pytest.raises(EmptyOrganizationNameException):
        await mediator.handle_command(
            CreateOrganizationCommand(
                name="",
                address="г. Москва, ул. Ленина 1",
                phones=["+7-495-123-4567"],
                activities=["Еда"],
            ),
        )


@pytest.mark.asyncio
async def test_create_organization_command_invalid_phone(
    mediator: Mediator,
):
    """Тест создания организации с невалидным телефоном."""
    # Создаем здание
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    # Создаем деятельность
    await mediator.handle_command(
        CreateActivityCommand(name="Еда", parent_id=None),
    )

    # Пытаемся создать организацию с пустым телефоном
    with pytest.raises(EmptyOrganizationPhoneException):
        await mediator.handle_command(
            CreateOrganizationCommand(
                name="ООО Рога",
                address="г. Москва, ул. Ленина 1",
                phones=[""],  # Пустой телефон
                activities=["Еда"],
            ),
        )


@pytest.mark.asyncio
async def test_create_organization_command_multiple_phones_and_activities(
    mediator: Mediator,
):
    """Тест создания организации с несколькими телефонами и деятельностями."""
    # Создаем здание
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    # Создаем несколько деятельностей
    food, *_ = await mediator.handle_command(
        CreateActivityCommand(name="Еда", parent_id=None),
    )
    await mediator.handle_command(
        CreateActivityCommand(name="Мясная продукция", parent_id=food.oid),
    )
    await mediator.handle_command(
        CreateActivityCommand(name="Молочная продукция", parent_id=food.oid),
    )

    # Создаем организацию с несколькими телефонами и деятельностями
    organization, *_ = await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Продукты",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-123-4567", "+7-495-234-5678", "+7-923-666-1313"],
            activities=["Мясная продукция", "Молочная продукция"],
        ),
    )

    assert len(organization.phones) == 3
    assert len(organization.activities) == 2

    # Проверяем телефоны
    phone_values = [phone.as_generic_type() for phone in organization.phones]
    assert "+7-495-123-4567" in phone_values
    assert "+7-495-234-5678" in phone_values
    assert "+7-923-666-1313" in phone_values

    # Проверяем деятельности
    activity_names = [
        activity.name.as_generic_type() for activity in organization.activities
    ]
    assert "Мясная продукция" in activity_names
    assert "Молочная продукция" in activity_names
