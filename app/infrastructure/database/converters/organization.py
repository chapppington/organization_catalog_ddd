from uuid import (
    UUID,
    uuid4,
)

from infrastructure.database.converters.activity import activity_model_to_entity
from infrastructure.database.converters.building import building_model_to_entity
from infrastructure.database.models.organization import (
    OrganizationModel,
    OrganizationPhoneModel,
)

from domain.organization.entities import OrganizationEntity
from domain.organization.value_objects import (
    OrganizationNameValueObject,
    OrganizationPhoneValueObject,
)


def organization_entity_to_model(entity: OrganizationEntity) -> OrganizationModel:
    return OrganizationModel(
        oid=entity.oid,
        name=entity.name.as_generic_type(),
        building_id=entity.building.oid,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def organization_model_to_entity(model: OrganizationModel) -> OrganizationEntity:
    return OrganizationEntity(
        oid=model.oid,
        name=OrganizationNameValueObject(value=model.name),
        building=building_model_to_entity(model.building),
        phones=[OrganizationPhoneValueObject(p.phone) for p in model.phones],
        activities=[activity_model_to_entity(a) for a in model.activities],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def organization_phones_to_models(
    organization_id: UUID,
    entity: OrganizationEntity,
) -> list[OrganizationPhoneModel]:
    return [
        OrganizationPhoneModel(
            oid=uuid4(),
            organization_id=organization_id,
            phone=phone.as_generic_type(),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        for phone in entity.phones
    ]


def organization_activities_ids(entity: OrganizationEntity) -> list[UUID]:
    return [activity.oid for activity in entity.activities]
