from fastapi.routing import APIRouter

from api.ai_enhance.spec_repair_process import \
    router as spec_repair_process
from api.ai_enhance.text_process import \
    router as text_process_router
from api.ai_enhance.embedding import \
    router as embedding_router
from api.ai_enhance.vector_search import \
    router as vector_search_router
from api.ai_enhance.extrac_features_process import \
    router as feature_insert

api_router = APIRouter()
api_router.include_router(spec_repair_process, prefix="/spec-repair",
                          tags=["repair"])
api_router.include_router(feature_insert, prefix="/feature-insert", 
                          tags=["repair"])
api_router.include_router(text_process_router, prefix="/text", tags=["text"])
api_router.include_router(embedding_router, prefix="/embedding",
                          tags=["embedding"])
api_router.include_router(vector_search_router, prefix="/search",
                          tags=["search"])
