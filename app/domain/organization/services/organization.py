from dataclasses import dataclass
from typing import Iterable

from domain.organization.entities import OrganizationEntity
from domain.organization.exceptions import (
    ActivityNotFoundException,
    BuildingNotFoundException,
)
from domain.organization.interfaces.repositories import (
    BaseActivityRepository,
    BaseBuildingRepository,
    BaseOrganizationRepository,
)
from domain.organization.value_objects import (
    OrganizationNameValueObject,
    OrganizationPhoneValueObject,
)


@dataclass
class OrganizationService:
    organization_repository: BaseOrganizationRepository
    building_repository: BaseBuildingRepository
    activity_repository: BaseActivityRepository

    async def create_organization(
        self,
        name: str,
        address: str,
        phones: list[str],
        activities: list[str],
    ) -> OrganizationEntity:
        """Создает новую организацию.

        Args:
            name: Название организации
            address: Адрес здания
            phones: Список телефонов
            activities: Список названий видов деятельности

        Raises:
            BuildingNotFoundException: Если здание не найдено
            ActivityNotFoundException: Если хотя бы одна деятельность не найдена

        """
        # Находим здание по адресу
        building = await self.building_repository.get_by_address(address)

        if not building:
            raise BuildingNotFoundException(address=address)

        # Находим все виды деятельности по названиям
        activity_entities = []

        for activity_name in activities:
            activity = await self.activity_repository.get_by_name(name=activity_name)

            if not activity:
                raise ActivityNotFoundException(activity_id=activity_name)

            activity_entities.append(activity)

        # Создаем организацию
        organization = OrganizationEntity(
            name=OrganizationNameValueObject(name),
            building=building,
            phones=[OrganizationPhoneValueObject(phone) for phone in phones],
            activities=activity_entities,
        )

        await self.organization_repository.add(organization)

        return organization

    async def get_organization_by_id(
        self,
        organization_id: str,
    ) -> OrganizationEntity | None:
        """Вывод информации об организации по её идентификатору."""
        return await self.organization_repository.get_by_id(organization_id)

    async def get_organizations_by_name(
        self,
        name: str,
        limit: int,
        offset: int,
    ) -> Iterable[OrganizationEntity]:
        """Поиск организации по названию."""
        organizations = list(await self.organization_repository.filter(name=name))
        return organizations[offset : offset + limit]

    async def get_organizations_by_address(
        self,
        address: str,
        limit: int,
        offset: int,
    ) -> Iterable[OrganizationEntity]:
        """Список всех организаций находящихся по указанному адресу."""
        # Ищем здания по частичному совпадению адреса
        buildings = await self.building_repository.filter(address=address)
        buildings_list = list(buildings)

        if not buildings_list:
            return []

        # Собираем организации из всех найденных зданий
        all_organizations = []
        for building in buildings_list:
            organizations = await self.organization_repository.filter(
                building_id=building.oid,
            )
            all_organizations.extend(organizations)

        organizations_list = list(all_organizations)
        return organizations_list[offset : offset + limit]

    async def get_organizations_by_activity(
        self,
        activity_id: str,
        limit: int,
        offset: int,
    ) -> Iterable[OrganizationEntity]:
        """Поиск организаций по виду деятельности (включая вложенные)

        Например, поиск по "Еда" найдет организации с видами деятельности:
        - Еда
        - Мясная продукция
        - Молочная продукция

        """
        root_activity = await self.activity_repository.get_by_id(activity_id)
        if not root_activity:
            return []

        # Получаем всех детей из дерева деятельности
        child_activities = await self.activity_repository.filter(parent_id=activity_id)

        # Собираем все названия деятельностей (корень + дети)
        activity_names = [root_activity.name.as_generic_type()]
        activity_names.extend(
            [child.name.as_generic_type() for child in child_activities],
        )

        # Ищем организации по каждой деятельности
        all_organizations = []
        for activity_name in activity_names:
            organizations = await self.organization_repository.filter(
                activity_name=activity_name,
            )
            all_organizations.extend(organizations)

        # Убираем дубликаты через set (используется __hash__ по oid)
        unique_organizations = list(set(all_organizations))

        return unique_organizations[offset : offset + limit]

    async def get_organizations_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        limit: int,
        offset: int,
    ) -> Iterable[OrganizationEntity]:
        """Список организаций в заданном радиусе относительно точки на
        карте."""
        buildings = await self.building_repository.filter(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )

        # Ищем организации в найденных зданиях
        all_organizations = []
        for building in buildings:
            organizations = await self.organization_repository.filter(
                address=building.address.as_generic_type(),
            )
            all_organizations.extend(organizations)

        return all_organizations[offset : offset + limit]

    async def get_organizations_by_rectangle(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        limit: int,
        offset: int,
    ) -> Iterable[OrganizationEntity]:
        """Список организаций в прямоугольной области."""

        buildings = await self.building_repository.filter(
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
        )

        # Ищем организации в найденных зданиях
        all_organizations = []
        for building in buildings:
            organizations = await self.organization_repository.filter(
                address=building.address.as_generic_type(),
            )
            all_organizations.extend(organizations)

        return all_organizations[offset : offset + limit]
