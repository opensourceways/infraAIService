from fastapi import APIRouter

from infra_ai_service.model.model import SearchInput, SearchOutput
from infra_ai_service.service.search_service import perform_vector_search

router = APIRouter()


@router.post("/query/", response_model=SearchOutput)
async def vector_search(input_data: SearchInput):
    return await perform_vector_search(input_data)
