import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException
from infra_ai_service.sdk.pgvector import model, conn
from infra_ai_service.model.model import PointStruct, EmbeddingOutput
from infra_ai_service.sdk.qdrant import fastembed_model, qdrant_client, \
    collection_name


async def create_embedding(content):
    try:
        embeddings = list(fastembed_model.embed([content]))
        if not embeddings:
            raise HTTPException(status_code=500,
                                detail="Failed to generate embedding")

        embedding_vector = embeddings[0]
        point_id = str(uuid.uuid4())

        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding_vector.tolist(),
                    payload={"text": content}
                )
            ]
        )

        return EmbeddingOutput(id=point_id,
                               embedding=embedding_vector.tolist())
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=f"Error processing embedding: {e}")


async def create_embedding_v2(content):
    try:
        # 使用线程池执行同步的嵌入计算
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            embedding_vector = await loop.run_in_executor(
                pool, model.encode, [content]
            )
            embedding_vector = embedding_vector[0]

        # 将嵌入向量插入数据库
        async with conn.cursor() as cur:
            await cur.execute(
                'INSERT INTO documents (content, embedding) VALUES (%s, %s) RETURNING id',
                (content, embedding_vector)
            )
            point_id = (await cur.fetchone())[0]

        return EmbeddingOutput(id=point_id, embedding=embedding_vector.tolist())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing "
                                                    f"embedding: {e}")


async def get_collection_status():
    try:
        async with conn.cursor() as cur:
            await cur.execute('SELECT COUNT(*) FROM documents')
            vectors_count = (await cur.fetchone())[0]
        return {
            "collection_name": 'documents',
            "vectors_count": vectors_count,
            "status": "ready"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error getting "
                                                    f"collection status: {e}")
