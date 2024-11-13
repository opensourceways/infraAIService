from loguru import logger
from fastapi import HTTPException
from infra_ai_service.model.model import EmbeddingOutput
from infra_ai_service.sdk import pgvector, ai_proxy


def create_embedding(content, os_version, name):
    try:
        embeddings = ai_proxy.embedding(content)
        with pgvector.pool.connection() as conn:
            with conn.cursor() as cur:
                logger.info("execute insert into embedding pgvector")
                cur.execute(
                    """
                    INSERT INTO documents
                    (content, embedding, os_version, name)
                    VALUES (%s, %s, %s, %s) RETURNING id
                    """,
                    (content, embeddings, os_version, name),
                )
                point_id = cur.fetchone()[0]

        logger.info(f"embedding insert into pgvector {point_id}")
        return EmbeddingOutput(id=str(point_id), embedding=embeddings)
    except Exception as e:
        logger.error(f"Error processing embedding: {e}", exc_info=True)
        raise HTTPException(
            status_code=400, detail=f"Error processing embedding: {e}"
        )
