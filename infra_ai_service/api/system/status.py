from fastapi import APIRouter

from infra_ai_service.service.embedding_service import get_collection_status

router = APIRouter()


@router.get("/status/")
async def status():
    return await get_collection_status()
