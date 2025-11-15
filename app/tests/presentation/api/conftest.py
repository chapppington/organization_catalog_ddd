import asyncio

import punq
from fastapi import FastAPI
from fastapi.testclient import TestClient

import pytest

from application.commands.api_key import CreateAPIKeyCommand
from application.commands.user import CreateUserCommand
from application.init import init_container
from application.mediator import Mediator
from presentation.api.main import create_app
from tests.fixtures import init_dummy_container


@pytest.fixture(scope="module")
def container() -> punq.Container:
    """Создает один контейнер для всех тестов в модуле."""
    return init_dummy_container()


@pytest.fixture(scope="module")
def app(container: punq.Container) -> FastAPI:
    """Создает одно приложение для всех тестов в модуле."""
    app = create_app()
    app.dependency_overrides[init_container] = lambda: container

    return app


@pytest.fixture(scope="module")
def client(app: FastAPI) -> TestClient:
    """Создает один клиент для всех тестов в модуле."""
    return TestClient(app=app)


@pytest.fixture(scope="module")
def mediator(container: punq.Container) -> Mediator:
    """Создает медиатор из контейнера для всех тестов в модуле."""
    return container.resolve(Mediator)


@pytest.fixture(scope="module")
def api_key_headers(mediator: Mediator) -> dict[str, str]:
    """Создает тестового пользователя и API ключ один раз для всех тестов в
    модуле.

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
