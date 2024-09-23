from fastapi import HTTPException
from fastembed.embedding import DefaultEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


async def setup_database(pool):
    async with pool.connection() as conn:
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id bigserial PRIMARY KEY,
                content text,
                embedding vector(384)
            )
        ''')
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS documents_content_idx
            ON documents USING GIN (to_tsvector('english', content))
        ''')