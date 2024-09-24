import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# 导入被测试的模块
from infra_ai_service.sdk.pgvector import setup_model_and_pool


class TestSetupModelAndPool(unittest.IsolatedAsyncioTestCase):
    @patch("infra_ai_service.sdk.pgvector.SentenceTransformer")
    @patch("infra_ai_service.sdk.pgvector.AsyncConnectionPool")
    @patch("infra_ai_service.sdk.pgvector.setup_database")
    async def test_setup_model_and_pool(
        self,
        mock_setup_database,
        mock_AsyncConnectionPool,
        mock_SentenceTransformer,
    ):
        # 设置模型和数据库连接池的模拟返回值
        mock_model = MagicMock()
        mock_SentenceTransformer.return_value = mock_model

        mock_pool = MagicMock()
        mock_pool.connection.return_value.__aenter__.return_value.execute = (
            AsyncMock()
        )
        mock_AsyncConnectionPool.return_value = mock_pool

        # 调用被测试的函数
        await setup_model_and_pool()

        # 检查是否创建了模型
        mock_SentenceTransformer.assert_called_once_with("model-name-here")
        # 检查是否尝试连接数据库
        mock_AsyncConnectionPool.assert_called_once()
        # 检查数据库设置函数是否被调用
        mock_setup_database.assert_called_once_with(mock_pool)
