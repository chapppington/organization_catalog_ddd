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
from domain.organization.interfaces.repositories.filters import (
    ActivityFilter,
    BuildingFilter,
    OrganizationFilter,
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
        building_filter = BuildingFilter(address=address)
        buildings = list(await self.building_repository.filter(building_filter))
        if not buildings:
            raise BuildingNotFoundException(address=address)
        building = buildings[0]

        # Находим все виды деятельности по названиям
        activity_entities = []
        for activity_name in activities:
            activity_filter = ActivityFilter(name=activity_name)
            found_activities = list(
                await self.activity_repository.filter(activity_filter),
            )
            if not found_activities:
                raise ActivityNotFoundException(activity_id=activity_name)
            activity_entities.append(found_activities[0])

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
        filters = OrganizationFilter(name=name)
        organizations = list(await self.organization_repository.filter(filters))
        return organizations[offset : offset + limit]

    async def get_organizations_by_address(
        self,
        address: str,
        limit: int,
        offset: int,
    ) -> Iterable[OrganizationEntity]:
        """Список всех организаций находящихся по указанному адресу."""
        filters = OrganizationFilter(address=address)
        organizations = list(await self.organization_repository.filter(filters))
        return organizations[offset : offset + limit]

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
        activity_filters = ActivityFilter(parent_id=activity_id)
        child_activities = await self.activity_repository.filter(activity_filters)

        # Собираем все названия деятельностей (корень + дети)
        activity_names = [root_activity.name.as_generic_type()]
        activity_names.extend(
            [child.name.as_generic_type() for child in child_activities],
        )

        # Ищем организации по каждой деятельности
        all_organizations = []
        for activity_name in activity_names:
            filters = OrganizationFilter(activity_name=activity_name)
            organizations = await self.organization_repository.filter(filters)
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
        building_filters = BuildingFilter(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )
        buildings = await self.building_repository.filter(building_filters)

        # Ищем организации в найденных зданиях
        all_organizations = []
        for building in buildings:
            organization_filters = OrganizationFilter(
                address=building.address.as_generic_type(),
            )
            organizations = await self.organization_repository.filter(
                organization_filters,
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
        building_filters = BuildingFilter(
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
        )
        buildings = await self.building_repository.filter(building_filters)

        # Ищем организации в найденных зданиях
        all_organizations = []
        for building in buildings:
            organization_filters = OrganizationFilter(
                address=building.address.as_generic_type(),
            )
            organizations = await self.organization_repository.filter(
                organization_filters,
            )
            all_organizations.extend(organizations)

        return all_organizations[offset : offset + limit]
