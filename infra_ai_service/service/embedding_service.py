from fastapi import HTTPException
from infra_ai_service.model.model import EmbeddingOutput
from infra_ai_service.sdk.pgvector import model, conn
import asyncio
from concurrent.futures import ThreadPoolExecutor


async def create_embedding(content):
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
