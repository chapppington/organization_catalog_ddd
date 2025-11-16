from dataclasses import dataclass
from typing import (
    Any,
    Iterable,
)
from uuid import UUID

from infrastructure.database.converters.organization import (
    organization_activities_ids,
    organization_entity_to_model,
    organization_model_to_entity,
    organization_phones_to_models,
)
from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.activity import ActivityModel
from infrastructure.database.models.organization import (
    organization_activity,
    OrganizationModel,
)
from sqlalchemy import (
    insert,
    select,
)
from sqlalchemy.orm import selectinload

from domain.organization.entities import OrganizationEntity
from domain.organization.interfaces.repositories.organization import BaseOrganizationRepository


@dataclass
class SQLAlchemyOrganizationRepository(BaseOrganizationRepository):
    database: Database

    async def add(self, organization: OrganizationEntity) -> None:
        async with self.database.get_session() as session:
            org_model = organization_entity_to_model(organization)
            session.add(org_model)
            await session.flush()

            # Телефоны
            phones_models = organization_phones_to_models(org_model.oid, organization)
            session.add_all(phones_models)

            # Активности
            if organization.activities:
                activities_ids = organization_activities_ids(organization)
                values = [
                    {"organization_id": org_model.oid, "activity_id": activity_id}
                    for activity_id in activities_ids
                ]
                await session.execute(insert(organization_activity).values(values))

            await session.commit()

    async def get_by_id(self, organization_id: UUID) -> OrganizationEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(OrganizationModel)
                .where(OrganizationModel.oid == organization_id)
                .options(
                    selectinload(OrganizationModel.building),
                    selectinload(OrganizationModel.phones),
                    selectinload(OrganizationModel.activities),
                )
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return organization_model_to_entity(result) if result else None

    async def get_by_name(self, name: str) -> OrganizationEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(OrganizationModel)
                .where(OrganizationModel.name == name)
                .options(
                    selectinload(OrganizationModel.building),
                    selectinload(OrganizationModel.phones),
                    selectinload(OrganizationModel.activities),
                )
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return organization_model_to_entity(result) if result else None

    async def filter(self, **filters: Any) -> Iterable[OrganizationEntity]:
        async with self.database.get_read_only_session() as session:
            stmt = select(OrganizationModel).options(
                selectinload(OrganizationModel.building),
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
            )

            activity_joined = False
            for field, value in filters.items():
                if field == "activity_name":
                    if not activity_joined:
                        stmt = stmt.join(OrganizationModel.activities)
                        activity_joined = True
                    stmt = stmt.where(ActivityModel.name == value)
                elif field == "name":
                    stmt = stmt.where(OrganizationModel.name.ilike(f"%{value}%"))
                else:
                    try:
                        field_obj = getattr(OrganizationModel, field)
                        stmt = stmt.where(field_obj == value)
                    except AttributeError:
                        continue

            if activity_joined:
                stmt = stmt.distinct()

            res = await session.execute(stmt)
            results = [organization_model_to_entity(row[0]) for row in res.all()]
            return results
