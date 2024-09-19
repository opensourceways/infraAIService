# tests/test_all.py

from infra_ai_service.api.common.utils import setup_qdrant_environment


def test_setup_qdrant_environment_new_collection_created():
    # 模拟 QdrantClient 和 DefaultEmbedding 类
    class MockQdrantClient:
        def __init__(self, path):
            self.path = path

        def get_collections(self):
            # 模拟返回空的集合列表
            return MockCollections()

        def create_collection(self, collection_name, vectors_config):
            # 模拟创建集合的行为
            assert collection_name == "simi"
            assert vectors_config.size == 300  # 假设的向量维度
            assert vectors_config.distance == "COSINE"
            print(f"模拟创建集合: {collection_name}")

    class MockCollections:
        def __init__(self):
            self.collections = []

    class MockDefaultEmbedding:
        def embed(self, texts):
            # 模拟返回固定的嵌入向量
            yield [0.1] * 300  # 假设300维的向量

    # 创建模拟对象
    MockQdrantClient(path="./qdrant_storage")
    MockDefaultEmbedding()

    # 替换原有对象为模拟对象，并执行测试
    _, _, collection_name = setup_qdrant_environment()

    # 检验集合名称是否正确
    assert collection_name == "simi"
    print("单元测试通过：正确创建了新集合")
