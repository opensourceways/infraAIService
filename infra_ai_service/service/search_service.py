from fastapi import HTTPException
import logging

from infra_ai_service.model.model import SearchOutput, SearchResult, \
    SearchInput

logger = logging.getLogger(__name__)


async def perform_vector_search(input_data: SearchInput):
    pass
