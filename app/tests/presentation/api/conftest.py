import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

import punq
import pytest
from presentation.api.main import create_app

from application.commands.api_key import CreateAPIKeyCommand
from application.commands.user import CreateUserCommand
from application.init import init_container
from application.mediator import Mediator
from tests.fixtures import init_dummy_container


@pytest.fixture(scope="function")
def container() -> punq.Container:
    """Создает контейнер для каждого теста."""
    return init_dummy_container()


@pytest.fixture(scope="function")
def app(container: punq.Container) -> FastAPI:
    """Создает приложение для каждого теста."""
    app = create_app()
    app.dependency_overrides[init_container] = lambda: container

    return app


@pytest.fixture(scope="function")
def client(app: FastAPI) -> TestClient:
    """Создает тестовый клиент для каждого теста."""
    return TestClient(app=app)


@pytest.fixture(scope="function")
def mediator(container: punq.Container) -> Mediator:
    """Создает медиатор из контейнера для каждого теста."""
    return container.resolve(Mediator)


@pytest.fixture(scope="function")
def api_key_headers(mediator: Mediator) -> dict[str, str]:
    """Создает тестового пользователя и API ключ для каждого теста.

    Возвращает заголовки для использования в тестах.

    """

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
