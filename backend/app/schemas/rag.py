"""RAG 相关模式"""
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)


class BatchQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    kb_ids: list[int] = Field(default_factory=list)  # 空表示全部知识库


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict] = Field(default_factory=list)
