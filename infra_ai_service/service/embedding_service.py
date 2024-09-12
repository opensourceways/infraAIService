from fastapi import HTTPException
import uuid

from model.model import PointStruct, EmbeddingOutput
from sdk.qdrant import fastembed_model, qdrant_client, \
    collection_name


async def create_embedding(content):
    try:
        embeddings = list(fastembed_model.embed([content]))
        if not embeddings:
            raise HTTPException(status_code=500,
                                detail="Failed to generate embedding")

        embedding_vector = embeddings[0]
        point_id = str(uuid.uuid4())

        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding_vector.tolist(),
                    payload={"text": content}
                )
            ]
        )

        return EmbeddingOutput(id=point_id,
                               embedding=embedding_vector.tolist())
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=f"Error processing embedding: {e}")


async def get_collection_status():
    try:
        collection_info = qdrant_client.get_collection(collection_name)
        return {
            "collection_name": collection_name,
            "vectors_count": collection_info.vectors_count,
            "status": "ready" if collection_info.status == "green"
            else "not ready"
        }
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=f"Error getting collection status: {e}")
