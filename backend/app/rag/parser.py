"""文档解析：支持 txt、pdf"""
from io import BytesIO


def parse_document(content: bytes, filename: str, content_type: str) -> str:
    """根据文件类型解析文档内容为纯文本"""
    name = (filename or "").lower()
    ct = (content_type or "").lower()

    if name.endswith(".txt") or name.endswith(".md") or "text/plain" in ct or "text/markdown" in ct:
        return content.decode("utf-8", errors="ignore")

    if name.endswith(".pdf") or "application/pdf" in ct:
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(content))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception:
            return content.decode("utf-8", errors="ignore")

    if name.endswith(".docx") or "application/vnd.openxmlformats" in ct:
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return content.decode("utf-8", errors="ignore")

    # 默认按文本处理
    return content.decode("utf-8", errors="ignore")
