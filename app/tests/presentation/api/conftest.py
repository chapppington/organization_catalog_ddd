from fastapi import FastAPI
from fastapi.testclient import TestClient

import pytest

from application.init import init_container
from presentation.api.main import create_app
from tests.fixtures import init_dummy_container


@pytest.fixture
def app() -> FastAPI:
    app = create_app()
    # Создаем один контейнер для всех запросов в рамках теста
    container = init_dummy_container()
    app.dependency_overrides[init_container] = lambda: container

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app=app)
