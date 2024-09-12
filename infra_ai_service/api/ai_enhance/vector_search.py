from fastapi import APIRouter

from model.model import SearchOutput, SearchInput
from service.search_service import perform_vector_search

router = APIRouter()


@router.post("/query/", response_model=SearchOutput)
async def vector_search(input_data: SearchInput):
    return await perform_vector_search(input_data)
