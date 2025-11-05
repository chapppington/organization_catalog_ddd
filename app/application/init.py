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
from application.queries.activity import (
    GetActivitiesQuery,
    GetActivitiesQueryHandler,
    GetActivityByIdQuery,
    GetActivityByIdQueryHandler,
)
from application.queries.building import (
    GetBuildingByIdQuery,
    GetBuildingByIdQueryHandler,
    GetBuildingsQuery,
    GetBuildingsQueryHandler,
)
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
from infrastructure.database.repositories.activity import SQLAlchemyActivityRepository
from infrastructure.database.repositories.building import SQLAlchemyBuildingRepository
from infrastructure.database.repositories.organization import (
    SQLAlchemyOrganizationRepository,
)
from settings.config import Config


@lru_cache(1)
def init_container():
    return _init_container()


def _init_container() -> Container:
    container = Container()

    # Регистрируем конфиг
    container.register(Config, instance=Config(), scope=Scope.singleton)

    # Регистрируем репозитории
    container.register(
        BaseBuildingRepository,
        instance=SQLAlchemyBuildingRepository(),
        scope=Scope.singleton,
    )
    container.register(
        BaseActivityRepository,
        instance=SQLAlchemyActivityRepository(),
        scope=Scope.singleton,
    )
    container.register(
        BaseOrganizationRepository,
        instance=SQLAlchemyOrganizationRepository(),
        scope=Scope.singleton,
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
    container.register(GetActivityByIdQueryHandler)
    container.register(GetActivitiesQueryHandler)
    container.register(GetBuildingByIdQueryHandler)
    container.register(GetBuildingsQueryHandler)
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
            GetActivityByIdQuery,
            container.resolve(GetActivityByIdQueryHandler),
        )
        mediator.register_query(
            GetActivitiesQuery,
            container.resolve(GetActivitiesQueryHandler),
        )
        mediator.register_query(
            GetBuildingByIdQuery,
            container.resolve(GetBuildingByIdQueryHandler),
        )
        mediator.register_query(
            GetBuildingsQuery,
            container.resolve(GetBuildingsQueryHandler),
        )
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
