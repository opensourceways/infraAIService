# infraAIService/infra_ai_service/service/search_service.py

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException

from infra_ai_service.model.model import SearchInput, SearchOutput, \
    SearchResult
from infra_ai_service.sdk import pgvector

logger = logging.getLogger(__name__)


async def perform_vector_search(input_data: SearchInput):
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

        # 将 ndarray 转换为列表
        embedding_vector_list = embedding_vector.tolist()

        # 从连接池获取连接
        async with pgvector.pool.connection() as conn:
            async with conn.cursor() as cur:
                # 执行向量搜索查询，显式转换参数为 vector 类型
                await cur.execute(
                    """
                    SELECT id, content, embedding,
                     1 - (embedding <#> %s::vector)
                    AS similarity
                    FROM documents
                    ORDER BY similarity DESC
                    LIMIT %s
                    """,
                    (embedding_vector_list, input_data.top_n),
                )
                rows = await cur.fetchall()

        # 转换搜索结果为输出格式
        results = []
        for row in rows:
            similarity = row[3]  # 相似度得分
            if similarity >= input_data.score_threshold:
                results.append(
                    SearchResult(id=str(row[0]), score=similarity,
                                 text=row[1])  # 内容
                )

        return SearchOutput(results=results)
    except Exception as e:
        logger.error(f"执行向量搜索时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500,
                            detail=f"执行向量搜索时出错: {str(e)}")
