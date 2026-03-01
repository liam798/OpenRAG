import unittest
from unittest.mock import patch

from langchain_core.documents import Document

from app.core.config import settings
from app.rag import pipeline


class RagPipelineTests(unittest.TestCase):
    @patch("app.rag.pipeline.similarity_search")
    @patch("app.rag.pipeline._generate_answer")
    def test_query_kb_degrades_when_llm_fails(self, mock_generate, mock_search):
        mock_search.return_value = [Document(page_content="示例内容", metadata={})]
        mock_generate.side_effect = RuntimeError("llm down")

        answer, sources = pipeline.query_kb(1, "这是一个问题", top_k=3)

        self.assertIn("暂时无法调用大模型", answer)
        self.assertEqual(len(sources), 1)
        self.assertIn("content", sources[0])

    @patch("app.rag.pipeline.similarity_search")
    def test_query_kb_top_k_is_clamped(self, mock_search):
        mock_search.return_value = []

        answer, sources = pipeline.query_kb(1, "test", top_k=999)

        self.assertEqual(answer, "知识库中暂无相关文档，请先上传文档。")
        self.assertEqual(sources, [])
        args, kwargs = mock_search.call_args
        self.assertEqual(args[0], 1)
        self.assertEqual(args[1], "test")
        self.assertEqual(kwargs["k"], settings.RAG_TOP_K_MAX)

    @patch("app.rag.pipeline.similarity_search_with_score")
    @patch("app.rag.pipeline._generate_answer", return_value="ok")
    def test_query_kbs_merge_and_keep_kb_id(self, _mock_generate, mock_search):
        mock_search.side_effect = [
            [(Document(page_content="kb1-1", metadata={}), 0.2)],
            [(Document(page_content="kb2-1", metadata={}), 0.1)],
        ]

        answer, sources = pipeline.query_kbs([1, 2], "问题", top_k=1)

        self.assertEqual(answer, "ok")
        self.assertEqual(len(sources), 1)
        self.assertIn(sources[0]["knowledge_base_id"], {1, 2})


if __name__ == "__main__":
    unittest.main()
