from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastembed.embedding import DefaultEmbedding
from qdrant_client import QdrantClient

router = APIRouter()


class SearchRequest(BaseModel):
    query_text: str
    top_n: int = 5
    score_threshold: float = 0.7


class SearchResult(BaseModel):
    id: str
    score: float


# 初始化FastEmbed模型和Qdrant客户端
fastembed_model = DefaultEmbedding()
qdrant_client = QdrantClient(url="http://localhost:6333")
collection_name = 'test_simi'


@router.post("/search_vectors/", response_model=SearchResult)
async def search_vectors(input_data: SearchRequest) -> SearchResult:
    try:
        # 生成查询文本的嵌入
        query_vector = list(fastembed_model.embed([input_data.query_text]))
        if not query_vector:
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
            SearchResult(id=str(result.id), score=result.score)
            for result in search_results
        ]

        return SearchResult(results=results)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error performing vector search: {str(e)}")
