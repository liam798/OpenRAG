"""文档相关模式"""
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    file_size: int
    chunk_count: int
    created_at: str | None = None

    class Config:
        from_attributes = True
