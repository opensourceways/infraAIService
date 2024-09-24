import asyncio
from concurrent.futures import ThreadPoolExecutor

import numpy
from fastapi import HTTPException

from infra_ai_service.model.model import EmbeddingOutput
from infra_ai_service.sdk import pgvector


async def create_embedding(content):
    try:
        # 确保模型已初始化
        if pgvector.model is None:
            raise HTTPException(
                status_code=500, detail="Model is not initialized"
            )

        # 使用线程池执行同步的嵌入计算
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool_executor:
            embedding_vector = await loop.run_in_executor(
                pool_executor, pgvector.model.encode, [content]
            )
            embedding_vector = embedding_vector[0]

        # 检查返回类型是否为 ndarray，如果是，则转换为列表
        if isinstance(embedding_vector, numpy.ndarray):
            embedding_vector_list = embedding_vector.tolist()
        else:
            embedding_vector_list = embedding_vector  # 假设已经是列表

        # 从连接池获取连接
        async with pgvector.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO documents (content, embedding) "
                    "VALUES (%s, %s) RETURNING id",
                    (content, embedding_vector_list),  # 使用转换后的列表
                )
                point_id = (await cur.fetchone())[0]

        return EmbeddingOutput(
            id=str(point_id), embedding=embedding_vector_list
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error processing embedding: {e}"
        )
