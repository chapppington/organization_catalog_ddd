from functools import lru_cache

from punq import (
    Container,
    Scope,
)

from application.commands.activity import (
    CreateActivityCommand,
    CreateActivityCommandHandler,
)
from application.commands.building import (
    CreateBuildingCommand,
    CreateBuildingCommandHandler,
)
from application.commands.organization import (
    CreateOrganizationCommand,
    CreateOrganizationCommandHandler,
)
from application.mediator import Mediator
from application.queries.organization import (
    GetOrganizationByIdQuery,
    GetOrganizationByIdQueryHandler,
    GetOrganizationsByActivityQuery,
    GetOrganizationsByActivityQueryHandler,
    GetOrganizationsByAddressQuery,
    GetOrganizationsByAddressQueryHandler,
    GetOrganizationsByNameQuery,
    GetOrganizationsByNameQueryHandler,
    GetOrganizationsByRadiusQuery,
    GetOrganizationsByRadiusQueryHandler,
    GetOrganizationsByRectangleQuery,
    GetOrganizationsByRectangleQueryHandler,
)
from domain.organization.interfaces.repositories.activity import BaseActivityRepository
from domain.organization.interfaces.repositories.building import BaseBuildingRepository
from domain.organization.interfaces.repositories.organization import (
    BaseOrganizationRepository,
)
from domain.organization.services import (
    ActivityService,
    BuildingService,
    OrganizationService,
)
from infrastructure.database.main import (
    build_sa_engine,
    build_sa_session_factory,
)
from infrastructure.database.repositories.activity import ActivityRepository
from infrastructure.database.repositories.building import BuildingRepository
from infrastructure.database.repositories.organization import OrganizationRepository
from settings.config import Config


@lru_cache(1)
def init_container():
    return _init_container()


def _init_container() -> Container:
    container = Container()

    # Регистрируем конфиг
    config = Config()
    container.register(Config, instance=config, scope=Scope.singleton)

    engine = build_sa_engine()
    session_factory = build_sa_session_factory(engine)

    session = session_factory()

    def init_activity_repository() -> BaseActivityRepository:
        return ActivityRepository(session=session)

    def init_building_repository() -> BaseBuildingRepository:
        return BuildingRepository(session=session)

    def init_organization_repository() -> BaseOrganizationRepository:
        return OrganizationRepository(session=session)

    container.register(
        BaseOrganizationRepository,
        factory=init_organization_repository,
    )

    container.register(
        BaseBuildingRepository,
        factory=init_building_repository,
    )

    container.register(
        BaseActivityRepository,
        factory=init_activity_repository,
    )

    # Регистрируем доменные сервисы
    container.register(BuildingService, scope=Scope.singleton)
    container.register(ActivityService, scope=Scope.singleton)
    container.register(OrganizationService, scope=Scope.singleton)

    # Регистрируем command handlers
    container.register(CreateBuildingCommandHandler)
    container.register(CreateActivityCommandHandler)
    container.register(CreateOrganizationCommandHandler)

    # Регистрируем query handlers
    container.register(GetOrganizationByIdQueryHandler)
    container.register(GetOrganizationsByAddressQueryHandler)
    container.register(GetOrganizationsByActivityQueryHandler)
    container.register(GetOrganizationsByNameQueryHandler)
    container.register(GetOrganizationsByRadiusQueryHandler)
    container.register(GetOrganizationsByRectangleQueryHandler)

    # Инициализируем медиатор
    def init_mediator() -> Mediator:
        mediator = Mediator()

        # Регистрируем commands
        mediator.register_command(
            CreateBuildingCommand,
            [container.resolve(CreateBuildingCommandHandler)],
        )
        mediator.register_command(
            CreateActivityCommand,
            [container.resolve(CreateActivityCommandHandler)],
        )
        mediator.register_command(
            CreateOrganizationCommand,
            [container.resolve(CreateOrganizationCommandHandler)],
        )

        # Регистрируем queries
        mediator.register_query(
            GetOrganizationByIdQuery,
            container.resolve(GetOrganizationByIdQueryHandler),
        )
        mediator.register_query(
            GetOrganizationsByAddressQuery,
            container.resolve(GetOrganizationsByAddressQueryHandler),
        )
        mediator.register_query(
            GetOrganizationsByActivityQuery,
            container.resolve(GetOrganizationsByActivityQueryHandler),
        )
        mediator.register_query(
            GetOrganizationsByNameQuery,
            container.resolve(GetOrganizationsByNameQueryHandler),
        )
        mediator.register_query(
            GetOrganizationsByRadiusQuery,
            container.resolve(GetOrganizationsByRadiusQueryHandler),
        )
        mediator.register_query(
            GetOrganizationsByRectangleQuery,
            container.resolve(GetOrganizationsByRectangleQueryHandler),
        )

        return mediator

    container.register(Mediator, factory=init_mediator)

    return container
