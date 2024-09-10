from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re

router = APIRouter()


class TextRequest(BaseModel):
    content: str


class TextResponse(BaseModel):
    processed_content: str


def clean_text(text: str) -> str:
    cleaned_text = re.sub(r'[{}[\]()@.#\\_\':\/-]', '', text)
    return cleaned_text


@router.post("/process_text/", response_model=TextResponse)
async def process_text(request: TextRequest) -> TextResponse:
    processed_text = clean_text(request.content)
    return TextResponse(processed_content=processed_text)
