import requests
from loguru import logger

from infra_ai_service.config.config import settings


def embedding(content):
    url = f"{settings.PROXY_URL}/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.PROXY_TOKEN}",
    }
    body = {
        "prompt": content,
        "model": "bge-large-en-v1.5",
        "encoding_format": "float",
    }
    logger.info(f"embedding url: {url}  headers: {headers}")
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        try:
            response_data = response.json()
            embeddings = response_data.get("embeddings")

            if embeddings is not None:
                logger.info(f"embedding context: {embeddings}")
                return embeddings
            else:
                logger.error("No embeddings found in the response.")
                raise ValueError("No embeddings found in the response.")
        except ValueError as e:
            logger.error(f"Failed to parse the response: {e}")
            raise
    else:
        logger.error(
            f"Failed to get embeddings, status code: {response.status_code}"
        )
        raise Exception(f"Error fetching embeddings: {response.status_code}")


def chat(model, message, *args):
    url = f"{settings.PROXY_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.PROXY_TOKEN}",
    }
    body = {
        "prompt": message,
        "model": model,
        "max_tokens": 512,
        "temperature": 0,
    }
    logger.info(f"chat url: {url}  headers: {headers}")
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        try:
            response_data = response.json()
            answer = response_data.get("choices")[0].get("text")

            if answer is not None:
                logger.info(f"answer context: {answer}")
                return answer
            else:
                logger.error("No answer found in the response.")
                return None
        except ValueError as e:
            logger.error(f"Failed to parse the response: {e}")
            raise
    else:
        logger.error(f"Failed to chat, status code: {response.status_code}")
        raise Exception(f"Error to chat: {response.status_code}")
