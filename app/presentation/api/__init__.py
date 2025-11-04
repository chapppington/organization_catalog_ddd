from fastapi import APIRouter

from presentation.api.healthcheck import healthcheck_router


main_router = APIRouter()

main_router.include_router(healthcheck_router)
