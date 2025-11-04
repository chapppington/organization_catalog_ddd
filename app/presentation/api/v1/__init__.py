from fastapi import APIRouter

from presentation.api.v1.activity.handlers import router as activity_router
from presentation.api.v1.building.handlers import router as building_router
from presentation.api.v1.organization.handlers import router as organization_router


v1_router = APIRouter()

v1_router.include_router(organization_router)
v1_router.include_router(activity_router)
v1_router.include_router(building_router)
