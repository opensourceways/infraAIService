from fastapi import APIRouter, HTTPException
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
    try:
        # 生成嵌入
        embeddings = list(fastembed_model.embed([request.text]))
        if not embeddings:
            raise ValueError("Failed to generate embedding")

        # 将numpy数组转换为普通Python列表
        embedding_list = embeddings[0].tolist()

        return EmbeddingResponse(embedding=embedding_list)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating embedding: {str(e)}")
