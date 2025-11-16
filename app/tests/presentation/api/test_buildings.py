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
async def test_create_building_success(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    url = app.url_path_for("create_building")
    address = faker.address()[:100]
    latitude = 55.7558
    longitude = 37.6173
    response: Response = client.post(
        url=url,
        json={
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
        },
        headers=api_key_headers,
    )

    assert response.is_success
    json_data = response.json()

    assert json_data["data"]["address"] == address
    assert json_data["data"]["latitude"] == latitude
    assert json_data["data"]["longitude"] == longitude


@pytest.mark.asyncio()
async def test_create_building_fail_address_too_long(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    url = app.url_path_for("create_building")
    address = faker.text(max_nb_chars=500)
    latitude = 55.7558
    longitude = 37.6173
    response: Response = client.post(
        url=url,
        json={
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
        },
        headers=api_key_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    json_data = response.json()

    assert json_data["errors"]


@pytest.mark.asyncio()
async def test_create_building_fail_address_empty(
    app: FastAPI,
    client: TestClient,
    api_key_headers: dict[str, str],
):
    url = app.url_path_for("create_building")
    latitude = 55.7558
    longitude = 37.6173
    response: Response = client.post(
        url=url,
        json={
            "address": "",
            "latitude": latitude,
            "longitude": longitude,
        },
        headers=api_key_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    json_data = response.json()

    assert json_data["errors"]


@pytest.mark.asyncio()
async def test_get_building_by_id_success(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    # Создаем здание
    create_url = app.url_path_for("create_building")
    address = faker.address()[:100]
    latitude = 55.7558
    longitude = 37.6173
    create_response: Response = client.post(
        url=create_url,
        json={
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
        },
        headers=api_key_headers,
    )
    assert create_response.is_success
    building_id = create_response.json()["data"]["oid"]

    # Получаем здание по ID
    get_url = app.url_path_for("get_building_by_id", building_id=building_id)
    response: Response = client.get(url=get_url, headers=api_key_headers)

    assert response.is_success
    json_data = response.json()

    assert json_data["data"]["oid"] == building_id
    assert json_data["data"]["address"] == address
    assert json_data["data"]["latitude"] == latitude
    assert json_data["data"]["longitude"] == longitude
    assert "created_at" in json_data["data"]
    assert "updated_at" in json_data["data"]


@pytest.mark.asyncio()
async def test_get_building_by_id_not_found(
    app: FastAPI,
    client: TestClient,
    api_key_headers: dict[str, str],
):
    building_id = uuid4()
    url = app.url_path_for("get_building_by_id", building_id=building_id)
    response: Response = client.get(url=url, headers=api_key_headers)

    assert response.is_success
    json_data = response.json()

    assert json_data["errors"]
    assert any("not found" in error["message"].lower() for error in json_data["errors"])


@pytest.mark.asyncio()
async def test_get_building_by_address_success(
    app: FastAPI,
    client: TestClient,
    faker: Faker,
    api_key_headers: dict[str, str],
):
    # Создаем здание с уникальным адресом
    create_url = app.url_path_for("create_building")
    unique_address = f"TestAddress_{faker.uuid4()}"
    latitude = 55.7558
    longitude = 37.6173
    create_response: Response = client.post(
        url=create_url,
        json={
            "address": unique_address,
            "latitude": latitude,
            "longitude": longitude,
        },
        headers=api_key_headers,
    )
    assert create_response.is_success
    building_id = create_response.json()["data"]["oid"]

    # Получаем здание по адресу
    url = app.url_path_for("get_building_by_address")
    response: Response = client.get(
        url=url,
        params={"address": unique_address},
        headers=api_key_headers,
    )

    assert response.is_success
    json_data = response.json()

    assert json_data["data"]["oid"] == building_id
    assert json_data["data"]["address"] == unique_address
    assert json_data["data"]["latitude"] == latitude
    assert json_data["data"]["longitude"] == longitude
    assert "created_at" in json_data["data"]
    assert "updated_at" in json_data["data"]


@pytest.mark.asyncio()
async def test_get_building_by_address_not_found(
    app: FastAPI,
    client: TestClient,
    api_key_headers: dict[str, str],
):
    url = app.url_path_for("get_building_by_address")
    response: Response = client.get(
        url=url,
        params={"address": "Несуществующий адрес"},
        headers=api_key_headers,
    )

    assert response.is_success
    json_data = response.json()

    assert json_data["errors"]
    assert any("not found" in error["message"].lower() for error in json_data["errors"])
