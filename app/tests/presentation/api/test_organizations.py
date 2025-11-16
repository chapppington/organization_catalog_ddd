from uuid import uuid4

from fastapi import (
    FastAPI,
    status,
)
from fastapi.testclient import TestClient

import pytest
from faker import Faker
from httpx import Response


@pytest.mark.asyncio()
async def test_create_organization_success(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    # Создаем здание
    building_url = app.url_path_for("create_building")
    address = faker.address()[:100]
    latitude = 55.7558
    longitude = 37.6173
    building_response: Response = client.post(
        url=building_url,
        json={
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
        },
        headers=api_key_headers,
    )
    assert building_response.is_success

    # Создаем деятельность
    activity_url = app.url_path_for("create_activity")
    activity_name = f"TestActivity_{faker.uuid4()}"
    activity_response: Response = client.post(
        url=activity_url,
        json={"name": activity_name},
        headers=api_key_headers,
    )
    assert activity_response.is_success

    # Создаем организацию
    url = app.url_path_for("create_organization")
    name = faker.company()[:100]
    phones = ["+7-495-123-4567", "+7-923-666-1313"]
    response: Response = client.post(
        url=url,
        json={
            "name": name,
            "address": address,
            "phones": phones,
            "activities": [activity_name],
        },
        headers=api_key_headers,
    )

    assert response.is_success
    json_data = response.json()

    assert json_data["data"]["name"] == name
    assert json_data["data"]["phones"] == phones
    assert len(json_data["data"]["activities"]) == 1


@pytest.mark.asyncio()
async def test_create_organization_fail_name_empty(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    # Создаем здание
    building_url = app.url_path_for("create_building")
    address = faker.address()[:100]
    building_response: Response = client.post(
        url=building_url,
        json={
            "address": address,
            "latitude": 55.7558,
            "longitude": 37.6173,
        },
        headers=api_key_headers,
    )
    assert building_response.is_success

    # Создаем деятельность
    activity_url = app.url_path_for("create_activity")
    activity_name = f"TestActivity_{faker.uuid4()}"
    activity_response: Response = client.post(
        url=activity_url,
        json={"name": activity_name},
        headers=api_key_headers,
    )
    assert activity_response.is_success

    # Создаем организацию с пустым именем
    url = app.url_path_for("create_organization")
    response: Response = client.post(
        url=url,
        json={
            "name": "",
            "address": address,
            "phones": ["+7-495-123-4567"],
            "activities": [activity_name],
        },
        headers=api_key_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    json_data = response.json()

    assert json_data["errors"]


@pytest.mark.asyncio()
async def test_create_organization_fail_invalid_phone(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    # Создаем здание
    building_url = app.url_path_for("create_building")
    address = faker.address()[:100]
    building_response: Response = client.post(
        url=building_url,
        json={
            "address": address,
            "latitude": 55.7558,
            "longitude": 37.6173,
        },
        headers=api_key_headers,
    )
    assert building_response.is_success

    # Создаем деятельность
    activity_url = app.url_path_for("create_activity")
    activity_name = f"TestActivity_{faker.uuid4()}"
    activity_response: Response = client.post(
        url=activity_url,
        json={"name": activity_name},
        headers=api_key_headers,
    )
    assert activity_response.is_success

    # Создаем организацию с невалидным телефоном
    url = app.url_path_for("create_organization")
    name = faker.company()[:100]
    response: Response = client.post(
        url=url,
        json={
            "name": name,
            "address": address,
            "phones": ["123"],  # Невалидный телефон (слишком короткий)
            "activities": [activity_name],
        },
        headers=api_key_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    json_data = response.json()

    assert json_data["errors"]


@pytest.mark.asyncio()
async def test_create_organization_fail_empty_phone(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    # Создаем здание
    building_url = app.url_path_for("create_building")
    address = faker.address()[:100]
    building_response: Response = client.post(
        url=building_url,
        json={
            "address": address,
            "latitude": 55.7558,
            "longitude": 37.6173,
        },
        headers=api_key_headers,
    )
    assert building_response.is_success

    # Создаем деятельность
    activity_url = app.url_path_for("create_activity")
    activity_name = f"TestActivity_{faker.uuid4()}"
    activity_response: Response = client.post(
        url=activity_url,
        json={"name": activity_name},
        headers=api_key_headers,
    )
    assert activity_response.is_success

    # Создаем организацию с пустым телефоном в списке
    url = app.url_path_for("create_organization")
    name = faker.company()[:100]
    response: Response = client.post(
        url=url,
        json={
            "name": name,
            "address": address,
            "phones": [""],  # Пустой телефон
            "activities": [activity_name],
        },
        headers=api_key_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    json_data = response.json()

    assert json_data["errors"]


@pytest.mark.asyncio()
async def test_get_organization_by_id_success(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    # Создаем здание
    building_url = app.url_path_for("create_building")
    address = faker.address()[:100]
    building_response: Response = client.post(
        url=building_url,
        json={
            "address": address,
            "latitude": 55.7558,
            "longitude": 37.6173,
        },
        headers=api_key_headers,
    )
    assert building_response.is_success

    # Создаем деятельность
    activity_url = app.url_path_for("create_activity")
    activity_name = f"TestActivity_{faker.uuid4()}"
    activity_response: Response = client.post(
        url=activity_url,
        json={"name": activity_name},
        headers=api_key_headers,
    )
    assert activity_response.is_success

    # Создаем организацию
    create_url = app.url_path_for("create_organization")
    name = faker.company()[:100]
    phones = ["+7-495-123-4567"]
    create_response: Response = client.post(
        url=create_url,
        json={
            "name": name,
            "address": address,
            "phones": phones,
            "activities": [activity_name],
        },
        headers=api_key_headers,
    )
    assert create_response.is_success
    organization_id = create_response.json()["data"]["oid"]

    # Получаем организацию по ID
    get_url = app.url_path_for(
        "get_organization_by_id",
        organization_id=organization_id,
    )
    response: Response = client.get(url=get_url, headers=api_key_headers)

    assert response.is_success
    json_data = response.json()

    assert json_data["data"]["oid"] == organization_id
    assert json_data["data"]["name"] == name
    assert json_data["data"]["phones"] == phones
    assert "created_at" in json_data["data"]
    assert "updated_at" in json_data["data"]
    assert "building" in json_data["data"]
    assert "activities" in json_data["data"]


@pytest.mark.asyncio()
async def test_get_organization_by_id_not_found(
    app: FastAPI,
    client: TestClient,
    api_key_headers: dict[str, str],
):
    organization_id = uuid4()
    url = app.url_path_for("get_organization_by_id", organization_id=organization_id)
    response: Response = client.get(url=url, headers=api_key_headers)

    assert response.is_success
    json_data = response.json()

    assert json_data["errors"]
    assert any("not found" in error["message"].lower() for error in json_data["errors"])


@pytest.mark.asyncio()
async def test_get_organizations_by_name_success(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    # Создаем здание
    building_url = app.url_path_for("create_building")
    address = faker.address()[:100]
    building_response: Response = client.post(
        url=building_url,
        json={
            "address": address,
            "latitude": 55.7558,
            "longitude": 37.6173,
        },
        headers=api_key_headers,
    )
    assert building_response.is_success

    # Создаем деятельность
    activity_url = app.url_path_for("create_activity")
    activity_name = f"TestActivity_{faker.uuid4()}"
    activity_response: Response = client.post(
        url=activity_url,
        json={"name": activity_name},
        headers=api_key_headers,
    )
    assert activity_response.is_success

    # Создаем несколько организаций с похожими именами
    create_url = app.url_path_for("create_organization")
    base_name = f"TestOrg_{faker.uuid4()}"
    names = [f"{base_name}_1", f"{base_name}_2"]
    created_ids = []
    for name in names:
        create_response: Response = client.post(
            url=create_url,
            json={
                "name": name,
                "address": address,
                "phones": ["+7-495-123-4567"],
                "activities": [activity_name],
            },
            headers=api_key_headers,
        )
        assert create_response.is_success
        created_ids.append(create_response.json()["data"]["oid"])

    # Получаем список организаций по имени
    url = app.url_path_for("get_organizations_by_name")
    response: Response = client.get(
        url=url,
        params={"name": base_name},
        headers=api_key_headers,
    )

    assert response.is_success
    json_data = response.json()

    assert "data" in json_data
    assert "items" in json_data["data"]
    assert "pagination" in json_data["data"]
    assert len(json_data["data"]["items"]) >= len(created_ids)
    assert json_data["data"]["pagination"]["total"] >= len(created_ids)


@pytest.mark.asyncio()
async def test_get_organizations_by_address_success(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    # Создаем здание с уникальным адресом
    building_url = app.url_path_for("create_building")
    unique_address = f"TestAddress_{faker.uuid4()}"
    building_response: Response = client.post(
        url=building_url,
        json={
            "address": unique_address,
            "latitude": 55.7558,
            "longitude": 37.6173,
        },
        headers=api_key_headers,
    )
    assert building_response.is_success

    # Создаем деятельность
    activity_url = app.url_path_for("create_activity")
    activity_name = f"TestActivity_{faker.uuid4()}"
    activity_response: Response = client.post(
        url=activity_url,
        json={"name": activity_name},
        headers=api_key_headers,
    )
    assert activity_response.is_success

    # Создаем несколько организаций по одному адресу
    create_url = app.url_path_for("create_organization")
    names = [faker.company()[:50] for _ in range(2)]
    created_ids = []
    for name in names:
        create_response: Response = client.post(
            url=create_url,
            json={
                "name": name,
                "address": unique_address,
                "phones": ["+7-495-123-4567"],
                "activities": [activity_name],
            },
            headers=api_key_headers,
        )
        assert create_response.is_success
        created_ids.append(create_response.json()["data"]["oid"])

    # Получаем список организаций по адресу
    url = app.url_path_for("get_organizations_by_address")
    response: Response = client.get(
        url=url,
        params={"address": unique_address},
        headers=api_key_headers,
    )

    assert response.is_success
    json_data = response.json()

    assert "data" in json_data
    assert "items" in json_data["data"]
    assert "pagination" in json_data["data"]
    assert len(json_data["data"]["items"]) >= len(created_ids)
    assert json_data["data"]["pagination"]["total"] >= len(created_ids)


@pytest.mark.asyncio()
async def test_create_organization_fail_duplicate_name(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    """Тест создания организации с дублирующимся названием."""
    # Создаем здание
    building_url = app.url_path_for("create_building")
    address = faker.address()[:100]
    building_response: Response = client.post(
        url=building_url,
        json={
            "address": address,
            "latitude": 55.7558,
            "longitude": 37.6173,
        },
        headers=api_key_headers,
    )
    assert building_response.is_success

    # Создаем деятельность
    activity_url = app.url_path_for("create_activity")
    activity_name = f"TestActivity_{faker.uuid4()}"
    activity_response: Response = client.post(
        url=activity_url,
        json={"name": activity_name},
        headers=api_key_headers,
    )
    assert activity_response.is_success

    # Создаем организацию
    url = app.url_path_for("create_organization")
    name = f"TestOrg_{faker.uuid4()}"

    create_response: Response = client.post(
        url=url,
        json={
            "name": name,
            "address": address,
            "phones": ["+7-495-123-4567"],
            "activities": [activity_name],
        },
        headers=api_key_headers,
    )
    assert create_response.is_success

    # Пытаемся создать организацию с тем же названием
    duplicate_response: Response = client.post(
        url=url,
        json={
            "name": name,
            "address": address,
            "phones": ["+7-495-234-5678"],
            "activities": [activity_name],
        },
        headers=api_key_headers,
    )

    assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST
    json_data = duplicate_response.json()

    assert json_data["errors"]
    assert any("already exists" in error["message"].lower() for error in json_data["errors"])
