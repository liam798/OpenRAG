from pydantic import BaseModel, Field


class MemoryCleanupRequest(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)


class MemoryCleanupResponse(BaseModel):
    deleted_rows: int
    deleted_vectors: int
    skipped_vectors: int
