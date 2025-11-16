from dataclasses import dataclass
from typing import (
    Iterable,
    Tuple,
)

from application.exceptions.organization import OrganizationWithThatNameAlreadyExistsException
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
        existing_organization = await self.organization_repository.get_by_name(name)

        if existing_organization:
            raise OrganizationWithThatNameAlreadyExistsException(
                name=name,
            )

        building = await self.building_repository.get_by_address(address)

        if not building:
            raise BuildingNotFoundException(address=address)

        activity_entities = []

        for activity_name in activities:
            activity = await self.activity_repository.get_by_name(name=activity_name)

            if not activity:
                raise ActivityNotFoundException(activity_id=activity_name)

            activity_entities.append(activity)

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
        return await self.organization_repository.get_by_id(organization_id)

    async def get_organizations_by_name(
        self,
        name: str,
        limit: int,
        offset: int,
    ) -> Tuple[Iterable[OrganizationEntity], int]:
        organizations = list(await self.organization_repository.filter(name=name))
        total = len(organizations)
        return organizations[offset : offset + limit], total

    async def get_organizations_by_address(
        self,
        address: str,
        limit: int,
        offset: int,
    ) -> Tuple[Iterable[OrganizationEntity], int]:
        building = await self.building_repository.get_by_address(address)

        if not building:
            return [], 0

        organizations = await self.organization_repository.filter(
            building_id=building.oid,
        )
        all_organizations = list(organizations)

        organizations_list = list(all_organizations)
        total = len(organizations_list)
        return organizations_list[offset : offset + limit], total

    async def get_organizations_by_activity(
        self,
        activity_name: str,
        limit: int,
        offset: int,
    ) -> Tuple[Iterable[OrganizationEntity], int]:
        """Поиск организаций по виду деятельности (включая вложенные)

        Например, поиск по "Еда" найдет организации с видами деятельности:
        - Еда
        - Мясная продукция
        - Молочная продукция

        """
        root_activity = await self.activity_repository.get_by_name(name=activity_name)
        if not root_activity:
            return [], 0

        # Получаем всех детей из дерева деятельности
        child_activities = await self.activity_repository.filter(
            parent_id=root_activity.oid,
        )

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
        total = len(unique_organizations)

        return unique_organizations[offset : offset + limit], total

    async def get_organizations_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        limit: int,
        offset: int,
    ) -> Tuple[Iterable[OrganizationEntity], int]:
        """Список организаций в заданном радиусе относительно точки на
        карте."""
        buildings = await self.building_repository.filter_by_radius(
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius,
        )

        # Ищем организации в найденных зданиях
        all_organizations = []
        for building in buildings:
            organizations = await self.organization_repository.filter(
                address=building.address.as_generic_type(),
            )
            all_organizations.extend(organizations)

        # Убираем дубликаты через set (используется __hash__ по oid)
        unique_organizations = list(set(all_organizations))
        total = len(unique_organizations)

        return unique_organizations[offset : offset + limit], total

    async def get_organizations_by_rectangle(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        limit: int,
        offset: int,
    ) -> Tuple[Iterable[OrganizationEntity], int]:
        """Список организаций в прямоугольной области."""

        buildings = await self.building_repository.filter_by_bounding_box(
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

        # Убираем дубликаты через set (используется __hash__ по oid)
        unique_organizations = list(set(all_organizations))
        total = len(unique_organizations)

        return unique_organizations[offset : offset + limit], total
