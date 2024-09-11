from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from qdrant_client.http.models import PointStruct
from infra_ai_service.api.common.utils import setup_qdrant_environment
import uuid
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - '
                                               '%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

fastembed_model, qdrant_client, collection_name = setup_qdrant_environment()

router = APIRouter()


class TextInput(BaseModel):
    content: str


class EmbeddingOutput(BaseModel):
    id: str
    embedding: List[float]


@router.post("/embed/", response_model=EmbeddingOutput)
async def embed_text(input_data: TextInput):
    try:
        # 生成嵌入
        embeddings = list(fastembed_model.embed([input_data.content]))
        if not embeddings:
            logger.error("Failed to generate embedding")
            raise HTTPException(status_code=500, detail="Failed to generate "
                                                        "embedding")

        embedding_vector = embeddings[0]

        # 生成唯一ID
        point_id = str(uuid.uuid4())

        # 将嵌入存储到Qdrant
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding_vector.tolist(),
                    payload={"text": input_data.content}
                )
            ]
        )

        return EmbeddingOutput(id=point_id, embedding=embedding_vector.tolist())
    except Exception as e:
        logger.error(f"Error processing embedding: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Error processing "
                                                    "embedding: Internal "
                                                    "Server Error")


@router.get("/status/")
async def get_collection_status():
    try:
        collection_info = qdrant_client.get_collection(collection_name)
        return {
            "collection_name": collection_name,
            "vectors_count": collection_info.vectors_count,
            "status": "ready" if collection_info.status == "green" else "not "
                                                                        "ready"
        }
    except Exception as e:
        logger.error(f"Error getting collection status: {e}",
                     exc_info=True)
        raise HTTPException(status_code=400, detail="Error getting collection "
                                                    "status: Internal Server "
                                                    "Error")
