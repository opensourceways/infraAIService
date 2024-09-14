import asyncio
from infra_ai_service.api.common.utils import setup_pgvector_environment

# 初始化模型和数据库连接
async def init():
    global model, conn
    model, conn = await setup_pgvector_environment()

# 运行初始化函数
asyncio.run(init())
