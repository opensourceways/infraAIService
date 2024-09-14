from typing import List

from pydantic import BaseModel


class SearchInput(BaseModel):
    query_text: str
    top_n: int = 5
    score_threshold: float = 0.7


class SearchResult(BaseModel):
    id: str
    score: float
    text: str  # 假设我们想返回结果中的文本


class SearchOutput(BaseModel):
    results: List[SearchResult]


class TextInput(BaseModel):
    content: str


class EmbeddingOutput(BaseModel):
    id: str
    embedding: List[float]


class PointStruct(BaseModel):  # 假设这是一个业务模型，也需要放在这里
    id: str
    vector: List[float]
    payload: dict


class TextOutput(BaseModel):
    modified_content: str
