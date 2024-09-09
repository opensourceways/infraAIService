from fastapi.routing import APIRouter

from infra_ai_service.api.example.views import router as example_router
from infra_ai_service.api.system.views import router as system_router

api_router = APIRouter()
api_router.include_router(system_router, prefix="/system", tags=["system"])
api_router.include_router(example_router, prefix="/example", tags=["example"])
