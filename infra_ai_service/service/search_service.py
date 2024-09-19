import logging

from fastapi import HTTPException

from infra_ai_service.model.model import SearchInput, SearchOutput, SearchResult
from infra_ai_service.sdk.qdrant import collection_name, fastembed_model, qdrant_client

logger = logging.getLogger(__name__)


async def perform_vector_search(input_data: SearchInput):
    try:
        # 检查集合是否存在
        collection_info = qdrant_client.get_collection(collection_name)
        if not collection_info:
            logger.error(f"Collection {collection_name} does not exist")
            raise HTTPException(
                status_code=404,
                detail=f"Collection {collection_name} does " f"not exist",
            )

        # 生成查询文本的嵌入
        query_vector = list(fastembed_model.embed([input_data.query_text]))
        if not query_vector:
            logger.error("Failed to generate query embedding")
            raise HTTPException(
                status_code=500, detail="Failed to generate query embedding"
            )

        # 执行向量搜索
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector[0],
            limit=input_data.top_n,
            score_threshold=input_data.score_threshold,
        )

        # 转换搜索结果为输出格式
        results = [
            SearchResult(
                id=str(result.id),
                score=result.score,
                text=result.payload.get("text", "No text available"),
            )
            for result in search_results
        ]

        return SearchOutput(results=results)
    except Exception as e:
        logger.error(f"Error performing vector search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error performing vector search: " f"{str(e)}"
        )
