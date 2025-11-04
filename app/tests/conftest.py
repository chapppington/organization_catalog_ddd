from punq import Container
from pytest import fixture

from application.mediator import Mediator
from domain.organization.interfaces.repositories.activity import BaseActivityRepository
from domain.organization.interfaces.repositories.building import BaseBuildingRepository
from domain.organization.interfaces.repositories.organization import (
    BaseOrganizationRepository,
)
from settings.config import Config
from tests.fixtures import init_dummy_container


@fixture(scope="function")
def container() -> Container:
    return init_dummy_container()


@fixture()
def mediator(container: Container) -> Mediator:
    return container.resolve(Mediator)


@fixture()
def organization_repository(container: Container) -> BaseOrganizationRepository:
    return container.resolve(BaseOrganizationRepository)


@fixture()
def building_repository(container: Container) -> BaseBuildingRepository:
    return container.resolve(BaseBuildingRepository)


@fixture()
def activity_repository(container: Container) -> BaseActivityRepository:
    return container.resolve(BaseActivityRepository)


@fixture()
def config(container: Container) -> Config:
    return container.resolve(Config)
