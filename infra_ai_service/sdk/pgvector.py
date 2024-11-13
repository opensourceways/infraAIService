from loguru import logger
from psycopg_pool import ConnectionPool
from pgvector.psycopg import register_vector

from infra_ai_service.config.config import settings

pool = None


def setup_model_and_pool():
    global pool
    try:
        conn_str = (
            f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
        pool = ConnectionPool(
            conn_str,
            min_size=settings.POOL_MIN,
            max_size=settings.POOL_MAX,
            open=True,
            kwargs={"autocommit": True},
        )
        logger.info("PostgreSQL connection pool created successfully.")
        with pool.connection() as conn:
            register_vector(conn)
        setup_database(pool)
        logger.info("Database setup completed successfully.")

    except Exception as e:
        logger.error(
            f"Error setting up PostgreSQL connection pool: {e}", exc_info=True
        )
        raise


def setup_database(pool):
    with pool.connection() as conn:
        conn.execute(
            f"CREATE EXTENSION IF NOT EXISTS {settings.VECTOR_EXTENSION}"
        )
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {settings.TABLE_NAME} (
                id bigserial PRIMARY KEY,
                content text,
                os_version text,
                name text,
                embedding vector({settings.VECTOR_DIMENSION})
            )
            """
        )
        conn.execute(
            f"""
            CREATE INDEX IF NOT EXISTS {settings.TABLE_NAME}_content_idx
            ON {settings.TABLE_NAME}
            USING GIN (to_tsvector('{settings.LANGUAGE}', content))
            """
        )


def close_pool():
    """close pool"""
    global pool
    if pool:
        pool.close()
        logger.info("PostgreSQL connection pool closed.")
