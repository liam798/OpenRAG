"""向量存储 - 基于 LangChain PGVector"""
import os
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from app.core.config import settings


def get_collection_name(kb_id: int) -> str:
    """知识库对应的向量集合名称"""
    return f"kb_{kb_id}"


def get_embeddings():
    """获取 Embedding 模型（临时清除代理环境变量以避免 OpenAI 客户端 proxies 参数兼容性问题）"""
    # 某些环境下 HTTP_PROXY 会导致 langchain-openai 传入 proxies，新版 openai 客户端不支持
    old_proxies = {k: os.environ.pop(k, None) for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy")}
    try:
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY,
        )
    finally:
        for k, v in old_proxies.items():
            if v is not None:
                os.environ[k] = v


def get_vector_store(kb_id: int):
    """获取指定知识库的向量存储"""
    return PGVector(
        connection_string=settings.DATABASE_URL,
        embedding_function=get_embeddings(),
        collection_name=get_collection_name(kb_id),
        use_jsonb=True,
    )


def add_documents_to_kb(kb_id: int, documents: list[Document]) -> None:
    """向知识库添加文档块"""
    store = get_vector_store(kb_id)
    store.add_documents(documents)


def similarity_search(kb_id: int, query: str, k: int = 5) -> list[Document]:
    """相似度搜索"""
    store = get_vector_store(kb_id)
    return store.similarity_search(query, k=k)


def similarity_search_with_score(kb_id: int, query: str, k: int = 5) -> list[tuple[Document, float]]:
    """相似度搜索（带分数，用于跨知识库合并排序）"""
    store = get_vector_store(kb_id)
    return store.similarity_search_with_score(query, k=k)


def delete_kb_vectors(kb_id: int) -> None:
    """删除知识库所有向量（删除知识库时调用）"""
    store = get_vector_store(kb_id)
    store.delete_collection()
