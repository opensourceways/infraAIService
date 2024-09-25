# infraAIService/infra_ai_service/service/search_service.py

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

import numpy
from fastapi import HTTPException

from infra_ai_service.model.model import (
    SearchInput,
    SearchOutput,
    SearchResult,
)
from infra_ai_service.sdk import pgvector

logger = logging.getLogger(__name__)


async def prepare_vector(input_data: SearchInput):
    try:
        # 确保模型已初始化
        if pgvector.model is None:
            logger.error("模型未初始化")
            raise HTTPException(status_code=500, detail="模型未初始化")

        # 生成查询文本的嵌入向量
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool_executor:
            embedding_vector = await loop.run_in_executor(
                pool_executor, pgvector.model.encode, [input_data.query_text]
            )
            embedding_vector = embedding_vector[0]

        # 检查返回类型是否为 ndarray，如果是，则转换为列表
        if isinstance(embedding_vector, numpy.ndarray):
            embedding_vector_list = embedding_vector.tolist()
        else:
            embedding_vector_list = embedding_vector  # 假设已经是列表

        return embedding_vector_list
    except Exception as e:
        logger.error(f"准备向量时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"准备向量时出错: {str(e)}"
        )


async def perform_vector_search(input_data: SearchInput):
    embedding_vector_list = await prepare_vector(input_data)

    try:
        # 从连接池获取连接
        async with pgvector.pool.connection() as conn:
            async with conn.cursor() as cur:
                # 执行向量搜索查询，显式转换参数为 vector 类型
                await cur.execute(
                    """
                    SELECT id, content, embedding,
                     1 - (embedding <#> %s::vector)
                    AS similarity, name
                    FROM documents
                    WHERE os_version=%s
                    ORDER BY similarity DESC
                    LIMIT %s
                    """,
                    (
                        embedding_vector_list,
                        input_data.os_version,
                        input_data.top_n,
                    ),
                )
                rows = await cur.fetchall()

        # 转换搜索结果为输出格式
        results = []
        for row in rows:
            similarity = row[3]  # 相似度得分
            if similarity >= input_data.score_threshold:
                results.append(
                    SearchResult(
                        id=str(row[0]),
                        score=similarity,
                        text=row[1],
                        name=row[4],
                    )  # 内容
                )

        return SearchOutput(results=results)
    except Exception as e:
        logger.error(f"执行向量搜索时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"执行向量搜索时出错: {str(e)}"
        )
