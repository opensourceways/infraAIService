from fastapi import HTTPException
import unittest
from unittest.mock import patch, MagicMock

from infra_ai_service.service.embedding_service import create_embedding
from infra_ai_service.model.model import EmbeddingOutput


class TestCreateEmbedding(unittest.TestCase):
    @patch("infra_ai_service.sdk.pgvector.pool", new_callable=MagicMock)
    @patch("infra_ai_service.sdk.ai_proxy.embedding")
    def test_create_embedding_success(self, mock_embedding, mock_pool):

        mock_embedding.return_value = [0.1] * 1024
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone()[0].return_value = [1]
        mock_connection.__enter__.return_value.cursor.return_value = (
            mock_cursor
        )
        mock_pool.connection.return_value = mock_connection

        result = create_embedding("test content", "v1.0", "test_name")
        self.assertIsInstance(result, EmbeddingOutput)
        self.assertEqual(result.embedding, [0.1] * 1024)
        mock_embedding.assert_called_once_with("test content")

    @patch("infra_ai_service.sdk.pgvector.pool", new_callable=MagicMock)
    @patch("infra_ai_service.sdk.ai_proxy.embedding")
    def test_create_embedding_db_failure(self, mock_embedding, mock_pool):
        # Mock the embedding response
        mock_embedding.return_value = [0.1] * 1024

        # Simulate an exception in the database connection
        mock_pool.connection.side_effect = Exception("Mocked database error")

        with self.assertRaises(HTTPException) as context:
            create_embedding("test content", "v1.0", "test_name")

        self.assertIn("Error processing embedding", str(context.exception))
        mock_embedding.assert_called_once_with("test content")
        mock_pool.connection.assert_called_once()
