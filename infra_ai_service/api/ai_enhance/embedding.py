from fastapi import APIRouter

from infra_ai_service.model.model import EmbeddingOutput, TextInput
from infra_ai_service.service.embedding_service import create_embedding

router = APIRouter()


@router.post("", response_model=EmbeddingOutput)
async def embed_text(input_data: TextInput):
    return create_embedding(
        input_data.content, input_data.os_version, input_data.name
    )
