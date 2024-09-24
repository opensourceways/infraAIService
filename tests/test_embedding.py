import asyncio
import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from infra_ai_service.model.model import EmbeddingOutput

# 导入被测试的函数
from infra_ai_service.service.embedding_service import create_embedding


class TestCreateEmbedding(unittest.IsolatedAsyncioTestCase):
    @patch("infra_ai_service.service.embedding_service.pgvector")
    @patch("infra_ai_service.service.embedding_service.ThreadPoolExecutor")
    async def test_create_embedding(self, mock_executor, mock_pgvector):
        # 设置模型和数据库连接池的模拟
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]  # 模拟的向量输出
        mock_pgvector.model = mock_model

        mock_conn = MagicMock()
        mock_cur = AsyncMock()
        mock_cur.execute = AsyncMock()
        mock_cur.fetchone = AsyncMock(return_value=[uuid.uuid4()])
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cur
        mock_pgvector.pool.connection.return_value.__aenter__.return_value = (
            mock_conn
        )

        # 模拟线程池执行器
        loop = asyncio.get_running_loop()
        with patch.object(
            loop, "run_in_executor", new_callable=AsyncMock
        ) as mock_run_in_executor:
            mock_run_in_executor.return_value = [
                [0.1, 0.2, 0.3]
            ]  # 返回编码后的向量

            # 输入数据
            test_content = "This is a test sentence"

            # 调用被测试的函数
            result = await create_embedding(test_content)

            # 检查返回结果
            self.assertIsInstance(result, EmbeddingOutput)
            self.assertEqual(result.embedding, [0.1, 0.2, 0.3])

            # 验证方法调用
            mock_run_in_executor.assert_called_once()
            mock_cur.execute.assert_called_once()
            mock_cur.fetchone.assert_called_once()

    async def test_create_embedding_no_model(self):
        with self.assertRaises(HTTPException) as context:
            await create_embedding("test input")
        self.assertEqual(context.exception.status_code, 400)
