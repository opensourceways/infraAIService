from fastapi import APIRouter

from api.ai_enhance.text_process import TextInput
from api.common.utils import setup_qdrant_environment

from model.model import EmbeddingOutput
from service.embedding_service import create_embedding, \
    get_collection_status

router = APIRouter()


@router.post("/embed/", response_model=EmbeddingOutput)
async def embed_text(input_data: TextInput):
    return await create_embedding(input_data.content)


@router.get("/status/")
async def status():
    return await get_collection_status()
