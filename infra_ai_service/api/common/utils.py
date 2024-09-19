from fastapi import HTTPException
from fastembed.embedding import DefaultEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


def setup_qdrant_environment():
    # 初始化FastEmbed模型和Qdrant客户端
    fastembed_model = DefaultEmbedding()
    qdrant_client = QdrantClient(path="./qdrant_storage")
    collection_name = 'simi'
    # 检查集合是否存在，如果不存在则创建
    collections_list = qdrant_client.get_collections()
    exist_flag = False
    for collection in collections_list.collections:
        if collection.name == collection_name:
            exist_flag = True
            break
    if not exist_flag:
        # 获取向量维度
        sample_embedding = next(fastembed_model.embed(["Sample text"]))
        vector_size = len(sample_embedding)

        # 创建集合
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size,
                                        distance=Distance.COSINE),
        )
        print(f"Created collection: {collection_name}")
    else:
        print(f"Collection {collection_name} already exists")
    return fastembed_model, qdrant_client, collection_name
