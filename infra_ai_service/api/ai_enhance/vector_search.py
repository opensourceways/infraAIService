from fastapi import APIRouter
from pydantic import BaseModel
from fastembed.embedding import DefaultEmbedding
from qdrant_client import QdrantClient

router = APIRouter()


class SearchRequest(BaseModel):
    text: str
    limit: int


class SearchResult(BaseModel):
    results: list[dict]


# Load a FastEmbed model
fastembed_model = DefaultEmbedding()
client = QdrantClient(url="http://localhost:6333")
collection_name = 'test_simi'


@router.post("/search_vectors/", response_model=SearchResult)
async def search_vectors(request: SearchRequest) -> SearchResult:
    query_vector = list(fastembed_model.embed([request.text]))
    search_results = client.search(collection_name=collection_name,
                                   query_vector=query_vector[0],
                                   limit=request.limit, score_threshold=0.7)
    return SearchResult(results=search_results)
