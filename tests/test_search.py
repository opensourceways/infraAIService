import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from infra_ai_service.model.model import SearchInput

# 导入被测试的函数
from infra_ai_service.service.search_service import perform_vector_search


class TestPerformVectorSearch(unittest.IsolatedAsyncioTestCase):
    @patch("infra_ai_service.service.search_service.pgvector")
    @patch("infra_ai_service.service.search_service.ThreadPoolExecutor")
    async def test_perform_vector_search(self, mock_executor, mock_pgvector):
        # 设置模型和数据库连接池的模拟
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.5, 0.6, 0.7]]  # 模拟的向量输出
        mock_pgvector.model = mock_model

        mock_conn = MagicMock()
        mock_cur = AsyncMock()
        mock_cur.execute = AsyncMock()
        mock_cur.fetchall = AsyncMock(
            return_value=[
                (1, "content1", [0.5, 0.6, 0.7], 0.95),
                (2, "content2", [0.5, 0.6, 0.7], 0.90),
            ]
        )
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
                [0.5, 0.6, 0.7]
            ]  # 返回编码后的向量

            # 输入数据
            test_input = SearchInput(
                query_text="This is a test query", top_n=5, score_threshold=0.9
            )

            # 调用被测试的函数
            result = await perform_vector_search(test_input)

            # 检查返回结果
            self.assertEqual(len(result.results), 2)
            self.assertEqual(result.results[0].id, "1")
            self.assertEqual(result.results[0].score, 0.95)

            # 验证方法调用
            mock_run_in_executor.assert_called_once()
            mock_cur.execute.assert_called_once()
            mock_cur.fetchall.assert_called_once()

    async def test_perform_vector_search_no_model(self):
        with self.assertRaises(HTTPException) as context:
            test_input = SearchInput(
                query_text="This is a test query", top_n=5, score_threshold=0.9
            )
            await perform_vector_search(test_input)
        self.assertEqual(context.exception.status_code, 500)
