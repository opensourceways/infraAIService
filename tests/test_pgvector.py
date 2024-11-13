import unittest
from unittest.mock import patch, MagicMock
from infra_ai_service.sdk.pgvector import (
    setup_model_and_pool,
    settings,
)


class TestSetupModelAndPool(unittest.TestCase):
    @patch("infra_ai_service.sdk.pgvector.ConnectionPool")
    @patch("infra_ai_service.sdk.pgvector.register_vector")
    @patch("infra_ai_service.sdk.pgvector.setup_database")
    def test_setup_model_and_pool(
        self, mock_setup_database, mock_register_vector, mock_connection_pool
    ):
        # Mock connection pool
        mock_pool = MagicMock()
        mock_connection_pool.return_value = mock_pool

        # Call the function
        setup_model_and_pool()

        # Assertions
        mock_connection_pool.assert_called_once_with(
            f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
            min_size=settings.POOL_MIN,
            max_size=settings.POOL_MAX,
            open=True,
            kwargs={"autocommit": True},
        )
        mock_register_vector.assert_called_once_with(
            mock_pool.connection().__enter__()
        )
        mock_setup_database.assert_called_once_with(mock_pool)
