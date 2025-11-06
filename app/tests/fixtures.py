from punq import (
    Container,
    Scope,
)

from application.init import _init_container
from domain.organization.interfaces.repositories.activity import BaseActivityRepository
from domain.organization.interfaces.repositories.building import BaseBuildingRepository
from domain.organization.interfaces.repositories.organization import (
    BaseOrganizationRepository,
)
from domain.user.interfaces.repositories.api_key import BaseAPIKeyRepository
from domain.user.interfaces.repositories.user import BaseUserRepository
from infrastructure.database.repositories.dummy import (
    DummyInMemoryActivityRepository,
    DummyInMemoryAPIKeyRepository,
    DummyInMemoryBuildingRepository,
    DummyInMemoryOrganizationRepository,
    DummyInMemoryUserRepository,
)


def init_dummy_container() -> Container:
    """Инициализирует контейнер с dummy репозиториями для тестов."""
    container = _init_container()

    container.register(
        BaseOrganizationRepository,
        DummyInMemoryOrganizationRepository,
        scope=Scope.singleton,
    )

    container.register(
        BaseBuildingRepository,
        DummyInMemoryBuildingRepository,
        scope=Scope.singleton,
    )

    container.register(
        BaseActivityRepository,
        DummyInMemoryActivityRepository,
        scope=Scope.singleton,
    )

    container.register(
        BaseUserRepository,
        DummyInMemoryUserRepository,
        scope=Scope.singleton,
    )

    container.register(
        BaseAPIKeyRepository,
        DummyInMemoryAPIKeyRepository,
        scope=Scope.singleton,
    )

    return container
