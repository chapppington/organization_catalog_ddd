from fastapi import (
    APIRouter,
    Depends,
)

from presentation.api.dependencies import get_api_key_from_header
from presentation.api.v1.activity.handlers import router as activity_router
from presentation.api.v1.building.handlers import router as building_router
from presentation.api.v1.organization.handlers import router as organization_router
from presentation.api.v1.user.handlers import router as user_router


v1_router = APIRouter()

# Защищаем роутеры API ключом
v1_router.include_router(
    organization_router,
    dependencies=[Depends(get_api_key_from_header)],
)
v1_router.include_router(
    activity_router,
    dependencies=[Depends(get_api_key_from_header)],
)
v1_router.include_router(
    building_router,
    dependencies=[Depends(get_api_key_from_header)],
)
v1_router.include_router(user_router)
