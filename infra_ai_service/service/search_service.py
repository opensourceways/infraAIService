# infraAIService/infra_ai_service/service/search_service.py
from loguru import logger
from fastapi import HTTPException

from infra_ai_service.model.model import (
    SearchInput,
    SearchOutput,
    SearchResult,
)
from infra_ai_service.sdk import pgvector, ai_proxy


async def prepare_vector(input_data: SearchInput):
    try:
        response = ai_proxy.embedding(input_data.query_text)
        logger.info(
            f"query text: {input_data.query_text} "
            f"embedding: {response.embeddings}"
        )
        return response.embeddings
    except Exception as e:
        logger.error(f"prepare vector failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"prepare vector failed: {str(e)}"
        )


async def perform_vector_search(input_data: SearchInput):
    embedding_vector_list = await prepare_vector(input_data)

    try:

        async with pgvector.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, content, embedding,
                     1 - (embedding <=> %s::vector)
                    AS similarity, name
                    FROM documents
                    WHERE os_version=%s
                    ORDER BY similarity DESC
                    LIMIT %s
                    """,
                    (
                        embedding_vector_list,
                        input_data.os_version,
                        input_data.top_n,
                    ),
                )
                rows = await cur.fetchall()

        results = []
        for row in rows:
            similarity = row[3]
            if similarity >= input_data.score_threshold:
                results.append(
                    SearchResult(
                        id=str(row[0]),
                        score=similarity,
                        text=row[1],
                        name=row[4],
                    )
                )

        return SearchOutput(results=results)
    except Exception as e:
        logger.error(f"pgvector query failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"pgvector query failed: {str(e)}"
        )
