from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class TextInput(BaseModel):
    content: str


class TextOutput(BaseModel):
    modified_content: str


def clean_text(text: str) -> str:
    return re.sub(r'[{}[\]()@.#\\_\':\/-]', '', text)


@router.post("/process/", response_model=TextOutput)
async def process_text(input_data: TextInput):
    try:
        modified_text = clean_text(input_data.content)
        return TextOutput(modified_content=modified_text)
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error processing text: {str(e)}")
