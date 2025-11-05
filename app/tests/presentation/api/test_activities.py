from fastapi import (
    FastAPI,
    status,
)
from fastapi.testclient import TestClient

import pytest
from faker import Faker
from httpx import Response


@pytest.mark.asyncio
async def test_create_activity_success(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
):
    url = app.url_path_for("create_activity")
    name = faker.text()[:100]
    response: Response = client.post(url=url, json={"name": name})

    assert response.is_success
    json_data = response.json()

    assert json_data["data"]["name"] == name


@pytest.mark.asyncio
async def test_create_activity_fail_name_too_long(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
):
    url = app.url_path_for("create_activity")
    name = faker.text(max_nb_chars=500)
    response: Response = client.post(url=url, json={"name": name})

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    json_data = response.json()

    assert json_data["errors"]


@pytest.mark.asyncio
async def test_create_activity_fail_name_empty(
    app: FastAPI,
    client: TestClient,
):
    url = app.url_path_for("create_activity")
    response: Response = client.post(url=url, json={"name": ""})

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    json_data = response.json()

    assert json_data["errors"]


@pytest.mark.asyncio
async def test_get_activity_by_id_success(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
):
    # Создаем деятельность
    create_url = app.url_path_for("create_activity")
    name = faker.text()[:100]
    create_response: Response = client.post(url=create_url, json={"name": name})
    assert create_response.is_success
    activity_id = create_response.json()["data"]["oid"]

    # Получаем деятельность по ID
    get_url = app.url_path_for("get_activity_by_id", activity_id=activity_id)
    response: Response = client.get(url=get_url)

    assert response.is_success
    json_data = response.json()

    assert json_data["data"]["oid"] == activity_id
    assert json_data["data"]["name"] == name
    assert "created_at" in json_data["data"]
    assert "updated_at" in json_data["data"]


@pytest.mark.asyncio
async def test_get_activity_by_id_not_found(
    app: FastAPI,
    client: TestClient,
):
    from uuid import uuid4

    activity_id = str(uuid4())
    url = app.url_path_for("get_activity_by_id", activity_id=activity_id)
    response: Response = client.get(url=url)

    assert response.is_success
    json_data = response.json()

    assert json_data["errors"]
    assert any("not found" in error["message"].lower() for error in json_data["errors"])


@pytest.mark.asyncio
async def test_get_activities_success(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
):
    # Создаем несколько деятельностей
    create_url = app.url_path_for("create_activity")
    names = [faker.text()[:50] for _ in range(3)]
    created_ids = []
    for name in names:
        create_response: Response = client.post(url=create_url, json={"name": name})
        assert create_response.is_success
        created_ids.append(create_response.json()["data"]["oid"])

    # Получаем список деятельностей
    url = app.url_path_for("get_activities")
    response: Response = client.get(url=url)

    assert response.is_success
    json_data = response.json()

    assert "data" in json_data
    assert "items" in json_data["data"]
    assert "pagination" in json_data["data"]
    assert len(json_data["data"]["items"]) >= len(created_ids)
    assert json_data["data"]["pagination"]["total"] >= len(created_ids)


@pytest.mark.asyncio
async def test_get_activities_with_filter(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
):
    # Создаем деятельность с уникальным именем
    create_url = app.url_path_for("create_activity")
    unique_name = f"TestActivity_{faker.uuid4()}"
    create_response: Response = client.post(url=create_url, json={"name": unique_name})
    assert create_response.is_success

    # Получаем список деятельностей с фильтром по имени
    url = app.url_path_for("get_activities")
    response: Response = client.get(url=url, params={"name": unique_name})

    assert response.is_success
    json_data = response.json()

    assert "data" in json_data
    assert "items" in json_data["data"]
    assert len(json_data["data"]["items"]) >= 1
    assert any(item["name"] == unique_name for item in json_data["data"]["items"])
