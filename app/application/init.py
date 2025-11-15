from functools import lru_cache

from punq import (
    Container,
    Scope,
)

from application.commands.activity import (
    CreateActivityCommand,
    CreateActivityCommandHandler,
)
from application.commands.api_key import (
    CreateAPIKeyCommand,
    CreateAPIKeyCommandHandler,
)
from application.commands.building import (
    CreateBuildingCommand,
    CreateBuildingCommandHandler,
)
from application.commands.organization import (
    CreateOrganizationCommand,
    CreateOrganizationCommandHandler,
)
from application.commands.user import (
    CreateUserCommand,
    CreateUserCommandHandler,
)
from application.mediator import Mediator
from application.queries.activity import (
    GetActivitiesQuery,
    GetActivitiesQueryHandler,
    GetActivityByIdQuery,
    GetActivityByIdQueryHandler,
)
from application.queries.api_key import (
    GetAPIKeyByKeyQuery,
    GetAPIKeyByKeyQueryHandler,
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
from application.queries.user import (
    AuthenticateUserQuery,
    AuthenticateUserQueryHandler,
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
from domain.user.interfaces.repositories.api_key import BaseAPIKeyRepository
from domain.user.interfaces.repositories.user import BaseUserRepository
from domain.user.services import (
    APIKeyService,
    UserService,
)
from infrastructure.database.repositories import (
    SQLAlchemyActivityRepository,
    SQLAlchemyAPIKeyRepository,
    SQLAlchemyBuildingRepository,
    SQLAlchemyOrganizationRepository,
    SQLAlchemyUserRepository,
)
from infrastructure.database.gateways.postgres import Database
from settings.config import Config


@lru_cache(1)
def init_container():
    return _init_container()


def _init_container() -> Container:
    container = Container()

    # Регистрируем конфиг
    container.register(Config, instance=Config(), scope=Scope.singleton)

    def init_database() -> Database:
        config: Config = container.resolve(Config)
        return Database(
            url=config.postgres_connection_uri,
            ro_url=config.postgres_connection_uri,
        )

    container.register(Database, factory=init_database, scope=Scope.singleton)

    # Регистрируем репозитории
    container.register(BaseBuildingRepository, SQLAlchemyBuildingRepository)
    container.register(BaseActivityRepository, SQLAlchemyActivityRepository)
    container.register(BaseOrganizationRepository, SQLAlchemyOrganizationRepository)
    container.register(BaseUserRepository, SQLAlchemyUserRepository)
    container.register(BaseAPIKeyRepository, SQLAlchemyAPIKeyRepository)

    # Регистрируем доменные сервисы
    container.register(BuildingService)
    container.register(ActivityService)
    container.register(OrganizationService)
    container.register(UserService)
    container.register(APIKeyService)

    # Регистрируем command handlers
    container.register(CreateBuildingCommandHandler)
    container.register(CreateActivityCommandHandler)
    container.register(CreateOrganizationCommandHandler)
    container.register(CreateUserCommandHandler)
    container.register(CreateAPIKeyCommandHandler)

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
    container.register(GetAPIKeyByKeyQueryHandler)
    container.register(AuthenticateUserQueryHandler)

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
        mediator.register_command(
            CreateUserCommand,
            [container.resolve(CreateUserCommandHandler)],
        )
        mediator.register_command(
            CreateAPIKeyCommand,
            [container.resolve(CreateAPIKeyCommandHandler)],
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
        mediator.register_query(
            GetAPIKeyByKeyQuery,
            container.resolve(GetAPIKeyByKeyQueryHandler),
        )
        mediator.register_query(
            AuthenticateUserQuery,
            container.resolve(AuthenticateUserQueryHandler),
        )

        return mediator

    container.register(Mediator, factory=init_mediator, scope=Scope.singleton)

    return container
