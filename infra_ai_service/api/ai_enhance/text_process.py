from fastapi import APIRouter

from infra_ai_service.model.model import TextInput, TextOutput
from infra_ai_service.service.text_service import process_text

router = APIRouter()


@router.post("/process/", response_model=TextOutput)
async def process_text_api(input_data: TextInput):
    return await process_text(input_data.content)
