import pytest

from application.commands.activity import CreateActivityCommand
from application.commands.building import CreateBuildingCommand
from application.commands.organization import CreateOrganizationCommand
from application.mediator import Mediator
from application.queries.organization import (
    GetOrganizationByIdQuery,
    GetOrganizationsByActivityQuery,
    GetOrganizationsByAddressQuery,
    GetOrganizationsByNameQuery,
    GetOrganizationsByRadiusQuery,
    GetOrganizationsByRectangleQuery,
)


@pytest.mark.asyncio
async def test_get_organization_by_id_query(mediator: Mediator):
    """Тест получения организации по ID."""
    # Создаем здание
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    # Создаем деятельность
    await mediator.handle_command(CreateActivityCommand(name="Еда", parent_id=None))

    # Создаем организацию
    organization, *_ = await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Рога и Копыта",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-123-4567"],
            activities=["Еда"],
        ),
    )

    # Ищем по ID
    result = await mediator.handle_query(
        GetOrganizationByIdQuery(organization_id=organization.oid),
    )

    assert result is not None
    assert result.oid == organization.oid
    assert result.name.as_generic_type() == "ООО Рога и Копыта"


@pytest.mark.asyncio
async def test_get_organization_by_id_not_found(mediator: Mediator):
    """Тест получения несуществующей организации."""
    result = await mediator.handle_query(
        GetOrganizationByIdQuery(organization_id="non-existent-id"),
    )

    assert result is None


@pytest.mark.asyncio
async def test_search_organizations_by_name_query(mediator: Mediator):
    """Тест поиска организаций по названию."""
    # Создаем здание
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    # Создаем деятельность
    await mediator.handle_command(CreateActivityCommand(name="Еда", parent_id=None))

    # Создаем несколько организаций
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Рога и Копыта",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-123-4567"],
            activities=["Еда"],
        ),
    )
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Рога Плюс",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-234-5678"],
            activities=["Еда"],
        ),
    )
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Другое название",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-345-6789"],
            activities=["Еда"],
        ),
    )

    # Ищем по названию "Рога"
    results = await mediator.handle_query(
        GetOrganizationsByNameQuery(name="Рога", limit=10, offset=0),
    )

    results_list = list(results)
    assert len(results_list) == 2
    names = [org.name.as_generic_type() for org in results_list]
    assert "ООО Рога и Копыта" in names
    assert "ООО Рога Плюс" in names


@pytest.mark.asyncio
async def test_get_organizations_by_address_query(mediator: Mediator):
    """Тест получения организаций по адресу."""
    # Создаем два здания
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Пушкина 2",
            latitude=55.7600,
            longitude=37.6200,
        ),
    )

    # Создаем деятельность
    await mediator.handle_command(CreateActivityCommand(name="Еда", parent_id=None))

    # Создаем организации в разных зданиях
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Ленина 1",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-123-4567"],
            activities=["Еда"],
        ),
    )
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Ленина 2",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-234-5678"],
            activities=["Еда"],
        ),
    )
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Пушкина",
            address="г. Москва, ул. Пушкина 2",
            phones=["+7-495-345-6789"],
            activities=["Еда"],
        ),
    )

    # Ищем по полному адресу
    results = await mediator.handle_query(
        GetOrganizationsByAddressQuery(
            address="г. Москва, ул. Ленина 1",
            limit=10,
            offset=0,
        ),
    )

    results_list = list(results)
    print(f"\nНайдено организаций: {len(results_list)}")
    for idx, org in enumerate(results_list, 1):
        print(f"\n{idx}. {org.name.as_generic_type()}")
        print(f"   ID: {org.oid}")
        print(f"   Адрес: {org.building.address.as_generic_type()}")
        print(f"   Телефоны: {[p.as_generic_type() for p in org.phones]}")
        print(f"   Деятельности: {[a.name.as_generic_type() for a in org.activities]}")
    print()
    assert len(results_list) == 2
    names = [org.name.as_generic_type() for org in results_list]
    assert "ООО Ленина 1" in names
    assert "ООО Ленина 2" in names

    # Проверяем, что организация из другого здания не попала в результаты
    assert "ООО Пушкина" not in names


@pytest.mark.asyncio
async def test_get_organizations_by_activity_query(mediator: Mediator):
    """Тест получения организаций по виду деятельности (включая вложенные)"""
    # Создаем здание
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    # Создаем иерархию деятельностей
    food, *_ = await mediator.handle_command(
        CreateActivityCommand(name="Еда", parent_id=None),
    )
    await mediator.handle_command(
        CreateActivityCommand(name="Мясная продукция", parent_id=food.oid),
    )
    await mediator.handle_command(
        CreateActivityCommand(name="Молочная продукция", parent_id=food.oid),
    )

    # Создаем организации с разными деятельностями
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Еда общая",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-123-4567"],
            activities=["Еда"],
        ),
    )
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Мясной цех",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-234-5678"],
            activities=["Мясная продукция"],
        ),
    )
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Молочный завод",
            address="г. Москва, ул. Ленина 1",
            phones=["+7-495-345-6789"],
            activities=["Молочная продукция"],
        ),
    )

    # Ищем по корневой деятельности "Еда" - должны найтись все 3
    results = await mediator.handle_query(
        GetOrganizationsByActivityQuery(activity_id=food.oid, limit=10, offset=0),
    )

    results_list = list(results)
    assert len(results_list) == 3
    names = [org.name.as_generic_type() for org in results_list]
    assert "ООО Еда общая" in names
    assert "ООО Мясной цех" in names
    assert "ООО Молочный завод" in names


@pytest.mark.asyncio
async def test_get_organizations_by_radius_query(mediator: Mediator):
    """Тест получения организаций в радиусе от точки."""
    # Создаем здания на разном расстоянии
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, Кремль",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, Парк Горького",
            latitude=55.7300,
            longitude=37.6000,
        ),
    )

    # Создаем деятельность
    await mediator.handle_command(CreateActivityCommand(name="Еда", parent_id=None))

    # Создаем организации
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО В центре",
            address="г. Москва, Кремль",
            phones=["+7-495-123-4567"],
            activities=["Еда"],
        ),
    )
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО В парке",
            address="г. Москва, Парк Горького",
            phones=["+7-495-234-5678"],
            activities=["Еда"],
        ),
    )

    # Ищем в радиусе 1км от Кремля
    results = await mediator.handle_query(
        GetOrganizationsByRadiusQuery(
            latitude=55.7558,
            longitude=37.6173,
            radius=1000,  # 1 км
            limit=10,
            offset=0,
        ),
    )

    results_list = list(results)
    # В радиусе 1км должна быть только организация в Кремле
    assert len(results_list) == 1
    assert results_list[0].name.as_generic_type() == "ООО В центре"


@pytest.mark.asyncio
async def test_get_organizations_by_rectangle_query(mediator: Mediator):
    """Тест получения организаций в прямоугольной области."""
    # Создаем здания в разных точках
    await mediator.handle_command(
        CreateBuildingCommand(
            address="Точка 1",
            latitude=55.7500,
            longitude=37.6000,
        ),
    )
    await mediator.handle_command(
        CreateBuildingCommand(
            address="Точка 2",
            latitude=55.7600,
            longitude=37.6100,
        ),
    )
    await mediator.handle_command(
        CreateBuildingCommand(
            address="Точка 3 (вне области)",
            latitude=55.8000,
            longitude=37.7000,
        ),
    )

    # Создаем деятельность
    await mediator.handle_command(CreateActivityCommand(name="Еда", parent_id=None))

    # Создаем организации
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Точка 1",
            address="Точка 1",
            phones=["+7-495-123-4567"],
            activities=["Еда"],
        ),
    )
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Точка 2",
            address="Точка 2",
            phones=["+7-495-234-5678"],
            activities=["Еда"],
        ),
    )
    await mediator.handle_command(
        CreateOrganizationCommand(
            name="ООО Точка 3",
            address="Точка 3 (вне области)",
            phones=["+7-495-345-6789"],
            activities=["Еда"],
        ),
    )

    # Ищем в прямоугольнике (должны найтись только точки 1 и 2)
    results = await mediator.handle_query(
        GetOrganizationsByRectangleQuery(
            lat_min=55.7400,
            lat_max=55.7700,
            lon_min=37.5900,
            lon_max=37.6200,
            limit=10,
            offset=0,
        ),
    )

    results_list = list(results)
    assert len(results_list) == 2
    names = [org.name.as_generic_type() for org in results_list]
    assert "ООО Точка 1" in names
    assert "ООО Точка 2" in names


@pytest.mark.asyncio
async def test_search_organizations_pagination(mediator: Mediator):
    """Тест пагинации при поиске организаций."""
    # Создаем здание
    await mediator.handle_command(
        CreateBuildingCommand(
            address="г. Москва, ул. Ленина 1",
            latitude=55.7558,
            longitude=37.6173,
        ),
    )

    # Создаем деятельность
    await mediator.handle_command(CreateActivityCommand(name="Еда", parent_id=None))

    # Создаем 5 организаций
    for i in range(5):
        await mediator.handle_command(
            CreateOrganizationCommand(
                name=f"ООО Тест {i + 1}",
                address="г. Москва, ул. Ленина 1",
                phones=[f"+7-495-{100 + i:03d}-0000"],
                activities=["Еда"],
            ),
        )

    # Тест пагинации: берем первые 2
    results_page1 = await mediator.handle_query(
        GetOrganizationsByNameQuery(name="Тест", limit=2, offset=0),
    )
    assert len(list(results_page1)) == 2

    # Берем следующие 2
    results_page2 = await mediator.handle_query(
        GetOrganizationsByNameQuery(name="Тест", limit=2, offset=2),
    )
    assert len(list(results_page2)) == 2

    # Берем последний
    results_page3 = await mediator.handle_query(
        GetOrganizationsByNameQuery(name="Тест", limit=2, offset=4),
    )
    assert len(list(results_page3)) == 1
