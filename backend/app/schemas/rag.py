"""RAG 相关模式"""
from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class BatchQueryRequest(BaseModel):
    question: str
    top_k: int = 5
    kb_ids: list[int] = []  # 空表示全部知识库


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict] = []
