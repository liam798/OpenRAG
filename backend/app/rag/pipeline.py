"""RAG 管道：分块、检索、生成"""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from app.core.config import settings
from app.rag.vector_store import add_documents_to_kb, similarity_search, similarity_search_with_score


TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)


def chunk_and_embed(kb_id: int, content: str, metadata: dict | None = None) -> int:
    """
    将文本分块并存入向量库，返回块数量
    """
    chunks = TEXT_SPLITTER.split_text(content)
    docs = [
        Document(page_content=c, metadata=metadata or {"knowledge_base_id": kb_id})
        for c in chunks
    ]
    if docs:
        add_documents_to_kb(kb_id, docs)
    return len(docs)


def format_docs(docs: list[Document]) -> str:
    """将检索到的文档格式化为上下文"""
    return "\n\n---\n\n".join(d.page_content for d in docs)


RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个基于知识库的问答助手。请根据以下检索到的上下文回答用户问题。
如果上下文中没有相关信息，请如实说明。
回答要准确、简洁。"""),
    ("human", "上下文：\n{context}\n\n问题：{question}"),
])


def query_kbs(kb_ids: list[int], question: str, top_k: int = 5) -> tuple[str, list[dict]]:
    """
    多知识库 RAG 问答，kb_ids 为空时需由调用方传入全部可访问的 kb_id
    """
    all_scored: list[tuple[Document, float]] = []
    for kb_id in kb_ids:
        for doc, score in similarity_search_with_score(kb_id, question, k=top_k):
            doc.metadata = doc.metadata or {}
            doc.metadata["_kb_id"] = kb_id
            all_scored.append((doc, score))
    if not all_scored:
        return "知识库中暂无相关文档，请先上传文档。", []
    # 按相似度分数升序排序（距离越小越相似），取前 top_k
    all_scored.sort(key=lambda x: x[1])
    docs = [d for d, _ in all_scored[:top_k]]
    context = format_docs(docs)
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )
    chain = RAG_PROMPT | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})
    sources = [
        {"content": d.page_content[:200] + "..." if len(d.page_content) > 200 else d.page_content}
        for d in docs
    ]
    return answer, sources


def query_kb(kb_id: int, question: str, top_k: int = 5) -> tuple[str, list[dict]]:
    """
    RAG 问答：检索 + 生成
    返回 (答案, 来源列表)
    """
    docs = similarity_search(kb_id, question, k=top_k)
    if not docs:
        return "知识库中暂无相关文档，请先上传文档。", []

    context = format_docs(docs)
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )
    chain = RAG_PROMPT | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    sources = [
        {"content": d.page_content[:200] + "..." if len(d.page_content) > 200 else d.page_content}
        for d in docs
    ]
    return answer, sources
