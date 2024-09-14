from fastapi import HTTPException
from fastembed.embedding import DefaultEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
from psycopg import AsyncConnection
from pgvector.psycopg import register_vector_async



def setup_qdrant_environment():
    # 初始化FastEmbed模型和Qdrant客户端
    fastembed_model = DefaultEmbedding()
    qdrant_client = QdrantClient(url="http://localhost:6333")
    collection_name = 'test_simi'

    # 检查集合是否存在，如果不存在则创建
    try:
        qdrant_client.get_collection(collection_name)
        print(f"Collection {collection_name} already exists")
    except HTTPException as e:
        # 获取向量维度
        sample_embedding = next(fastembed_model.embed(["Sample text"]))
        vector_size = len(sample_embedding)

        # 创建集合
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size,
                                        distance=Distance.COSINE),
        )
        print(f"Created collection: {collection_name}")
    return fastembed_model, qdrant_client, collection_name

async def setup_pgvector_environment():
    # 初始化 SentenceTransformer 模型
    model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

    # 连接到 PostgreSQL 数据库
    conn = await AsyncConnection.connect(
        dbname='your_database_name',
        user='your_user',
        password='your_password',
        host='your_host',
        port='your_port',
        autocommit=True
    )

    # 注册 pgvector 并创建必要的表和索引
    await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
    await register_vector_async(conn)
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

    return model, conn