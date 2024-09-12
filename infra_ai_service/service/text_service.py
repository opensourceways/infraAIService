import re
from fastapi import HTTPException
import logging

from model.model import TextOutput

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    try:
        # 正确转义正则表达式中的特殊字符
        return re.sub(r'[{}\[\]()@.#\\_\':\/-]', '', text)
    except re.error as e:
        logger.error(f"Regex error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Regex processing error")


async def process_text(input_content: str) -> TextOutput:
    try:
        modified_text = clean_text(input_content)
        return TextOutput(modified_content=modified_text)
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400,
                            detail=f"Error processing text: {str(e)}")
