import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

import pytest

from application.commands.api_key import CreateAPIKeyCommand
from application.commands.user import CreateUserCommand
from application.init import init_container
from application.mediator import Mediator
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


@pytest.fixture
def api_key_headers(app: FastAPI) -> dict[str, str]:
    """Создает тестового пользователя и API ключ, возвращает заголовки для
    использования в тестах."""

    container = app.dependency_overrides[init_container]()
    mediator: Mediator = container.resolve(Mediator)

    # Создаем пользователя
    user, *_ = asyncio.run(
        mediator.handle_command(
            CreateUserCommand(
                username="test_user",
                password="test_password123",
            ),
        ),
    )

    # Создаем API ключ
    api_key_entity, *_ = asyncio.run(
        mediator.handle_command(
            CreateAPIKeyCommand(
                user_id=user.oid,
            ),
        ),
    )

    return {"Authorization": f"Bearer {api_key_entity.key}"}
