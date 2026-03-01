"""公共记忆相关模式"""
from pydantic import BaseModel, Field
from typing import Any


class MemoryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    metadata: dict[str, Any] | None = None
    ttl_seconds: int = Field(default=-1, description="-1 表示永久")


class MemoryQuery(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=50)
    metadata_filter: dict[str, Any] | None = None


class MemoryResponse(BaseModel):
    id: int
    knowledge_base_id: int
    user_id: int
    content: str
    metadata: dict[str, Any] | None = None
    ttl_seconds: int
    expires_at: str | None = None
    created_at: str | None = None

    class Config:
        from_attributes = True
