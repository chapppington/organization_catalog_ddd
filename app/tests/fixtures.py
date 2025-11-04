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
from infrastructure.database.repositories.dummy import (
    DummyInMemoryActivityRepository,
    DummyInMemoryBuildingRepository,
    DummyInMemoryOrganizationRepository,
)


def init_dummy_container() -> Container:
    """Инициализирует контейнер с dummy репозиториями для тестов.

    Перетирает реальные SQLAlchemy репозитории на in-memory реализации

    """
    container = _init_container()

    # Перетираем реальные репозитории на dummy (in-memory)
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

    return container
