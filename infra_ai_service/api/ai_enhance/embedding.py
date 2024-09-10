from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from fastembed.embedding import DefaultEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import numpy as np
import uuid

router = APIRouter()


class TextInput(BaseModel):
    content: str


class EmbeddingOutput(BaseModel):
    id: str
    embedding: List[float]


# 初始化FastEmbed模型
fastembed_model = DefaultEmbedding()

# 初始化Qdrant客户端
qdrant_client = QdrantClient(url="http://localhost:6333")
collection_name = 'test_simi'

# 检查集合是否存在，如果不存在则创建
try:
    qdrant_client.get_collection(collection_name)
    print(f"Collection {collection_name} already exists")
except HTTPException as e:
    # 获取向量维度
    sample_embedding = next(fastembed_model.embed(["Sample text"]))
    vector_size = len(sample_embedding)

    # 创建集合
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    print(f"Created collection: {collection_name}")


@router.post("/embed/", response_model=EmbeddingOutput)
async def embed_text(input_data: TextInput):
    try:
        # 生成嵌入
        embeddings = list(fastembed_model.embed([input_data.content]))
        if not embeddings:
            raise ValueError("Failed to generate embedding")

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
        raise HTTPException(status_code=400,
                            detail=f"Error processing embedding: {str(e)}")


@router.get("/status/")
async def get_collection_status():
    try:
        collection_info = qdrant_client.get_collection(collection_name)
        return {
            "collection_name": collection_name,
            "vectors_count": collection_info.vectors_count,
            "status": "ready" if collection_info.status == "green" else "not ready"
        }
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=f"Error getting collection status: {str(e)}")
