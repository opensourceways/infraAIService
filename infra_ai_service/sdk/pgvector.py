from sentence_transformers import SentenceTransformer
from psycopg_pool import AsyncConnectionPool
from infra_ai_service.common.utils import setup_database

# 初始化模型
model = None
# 创建连接池（暂时不初始化）
pool = None


async def setup_model_and_pool():
    global model, pool
    # 初始化模型
    model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    # 创建异步连接池
    pool = AsyncConnectionPool(
        "dbname=pgvector user=postgres password=postgres "
        "host=localhost port=5432",
        open=True
    )
    # 设置数据库
    await setup_database(pool)
