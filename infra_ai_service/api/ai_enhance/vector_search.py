from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from infra_ai_service.api.common.utils import setup_qdrant_environment
import logging

router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
fastembed_model, qdrant_client, collection_name = setup_qdrant_environment()


class SearchInput(BaseModel):
    query_text: str
    top_n: int = 5
    score_threshold: float = 0.7


class SearchResult(BaseModel):
    id: str
    score: float


class SearchOutput(BaseModel):
    results: List[SearchResult]


@router.post("/query/", response_model=SearchOutput)
async def vector_search(input_data: SearchInput):
    try:
        # 检查集合是否存在
        if not qdrant_client.get_collection(collection_name):
            logger.error(f"Collection {collection_name} does not exist",
                         exc_info=True)
            raise ValueError(f"Collection {collection_name} does not exist")

        # 生成查询文本的嵌入
        query_vector = list(fastembed_model.embed([input_data.query_text]))
        if not query_vector:
            logger.error(f"Failed to generate query embedding",
                         exc_info=True)
            raise ValueError("Failed to generate query embedding")

        # 执行向量搜索
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector[0],
            limit=input_data.top_n,
            score_threshold=input_data.score_threshold
        )

        # 转换搜索结果为输出格式
        results = [
            SearchResult(
                id=str(result.id),
                score=result.score,
                text=result.payload.get('text', 'No text available')
            )
            for result in search_results
        ]

        return SearchOutput(results=results)
    except Exception as e:
        logger.error(f"Error performing vector search: {str(e)}",
                     exc_info=True)
        raise HTTPException(status_code=500,
                            detail=f"Error performing vector search: {str(e)}")
