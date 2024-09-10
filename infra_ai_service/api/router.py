from fastapi.routing import APIRouter

from infra_ai_service.api.system.views import router as system_router
from infra_ai_service.api.ai_enhance.text_process import router as text_process_router
from infra_ai_service.api.ai_enhance.embedding import router as embedding_router
from infra_ai_service.api.ai_enhance.vector_search import router as vector_search_router

api_router = APIRouter()
api_router.include_router(system_router, prefix="/system", tags=["system"])
api_router.include_router(text_process_router, prefix="/text", tags=["Text Processing"])
api_router.include_router(embedding_router, prefix="/embed", tags=["Embedding"])
api_router.include_router(vector_search_router, prefix="/search", tags=["Vector Search"])
