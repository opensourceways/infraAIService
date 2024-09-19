from fastapi.testclient import TestClient
import pytest
from infra_ai_service.core.app import get_app  # 确保从你的应用文件导入 get_app

@pytest.fixture
def client():
    app = get_app()
    with TestClient(app) as client:
        yield client

def test_text_processing_routes(client):
    """
    测试文本处理路由。
    """
    # 例：测试 /api/text/some_endpoint
    response = client.get("/api/text/process")
    assert response.status_code == 405

def test_embedding_routes(client):
    """
    测试嵌入向量路由。
    """
    # 例：测试 /api/embedding/some_endpoint
    response = client.get("/api/embedding/embed")
    assert response.status_code == 405

def test_vector_search_routes(client):
    """
    测试向量搜索路由。
    """
    # 例：测试 /api/search/some_endpoint
    response = client.get("/api/search/query")
    assert response.status_code == 405

def test_status_routes(client):
    """
    测试状态路由。
    """
    # 例：测试 /api/status/some_endpoint
    response = client.get("/api/status/status")
    assert response.status_code == 200
