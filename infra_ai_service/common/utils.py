# infra_ai_service/common/utils.py

from infra_ai_service.config.config import settings


async def setup_database(pool):
    async with pool.connection() as conn:
        # 创建扩展名，使用配置项
        await conn.execute(
            f"CREATE EXTENSION IF NOT EXISTS {settings.VECTOR_EXTENSION}"
        )
        # 创建表，使用配置项
        await conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {settings.TABLE_NAME} (
                id bigserial PRIMARY KEY,
                content text,
                embedding vector({settings.VECTOR_DIMENSION})
            )
            """
        )
        # 创建索引，使用配置项
        await conn.execute(
            f"""
            CREATE INDEX IF NOT EXISTS {settings.TABLE_NAME}_content_idx
            ON {settings.TABLE_NAME}
            USING GIN (to_tsvector('{settings.LANGUAGE}', content))
            """
        )
