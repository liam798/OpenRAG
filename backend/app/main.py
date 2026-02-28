"""OpenRAG 主应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.knowledge_bases import router as kb_router
from app.api.rag import router as rag_router
from app.api.activities import router as activities_router

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(kb_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(activities_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "OpenRAG API", "docs": "/docs"}
