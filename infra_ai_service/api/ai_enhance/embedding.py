from fastapi import APIRouter
from pydantic import BaseModel
from fastembed.embedding import DefaultEmbedding

router = APIRouter()


class EmbeddingRequest(BaseModel):
    text: str


class EmbeddingResponse(BaseModel):
    embedding: list[float]


# Load a FastEmbed model
fastembed_model = DefaultEmbedding()


@router.post("/embed_text/", response_model=EmbeddingResponse)
async def embed_text(request: EmbeddingRequest) -> EmbeddingResponse:
    embeddings = list(fastembed_model.embed([request.text]))
    return EmbeddingResponse(embedding=embeddings[0])
