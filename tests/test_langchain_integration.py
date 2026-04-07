"""Tests for LangChain integration."""
import pytest

try:
    from langchain_core.documents import Document
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

pytestmark = pytest.mark.skipif(not HAS_LANGCHAIN, reason="langchain-core not installed")


class TestContradictionChecker:
    def test_transform_documents(self):
        from contrachecker.integrations.langchain import ContradictionCheckerTransformer

        transformer = ContradictionCheckerTransformer()
        docs = [
            Document(page_content="Coffee is healthy.", metadata={"source": "doc1"}),
            Document(page_content="Coffee is harmful.", metadata={"source": "doc2"}),
        ]
        result = transformer.transform_documents(docs)
        assert len(result) >= len(docs)
        report_doc = result[-1]
        assert "CONTRADICTION" in report_doc.page_content or report_doc.metadata.get("is_contradiction_report")

    def test_no_contradictions(self):
        from contrachecker.integrations.langchain import ContradictionCheckerTransformer

        transformer = ContradictionCheckerTransformer()
        docs = [
            Document(page_content="Water is essential.", metadata={"source": "doc1"}),
            Document(page_content="Exercise is beneficial.", metadata={"source": "doc2"}),
        ]
        result = transformer.transform_documents(docs)
        assert len(result) == 2

    def test_metadata_preserved(self):
        from contrachecker.integrations.langchain import ContradictionCheckerTransformer

        transformer = ContradictionCheckerTransformer()
        docs = [
            Document(page_content="Coffee is healthy.", metadata={"source": "doc1", "page": 1}),
            Document(page_content="Coffee is harmful.", metadata={"source": "doc2", "page": 5}),
        ]
        result = transformer.transform_documents(docs)
        assert result[0].metadata["page"] == 1

    def test_from_chunks_utility(self):
        from contrachecker.integrations.langchain import langchain_docs_to_chunks
        from contrachecker.models import Chunk

        docs = [
            Document(page_content="Hello world.", metadata={"id": "custom_id"}),
            Document(page_content="Another doc."),
        ]
        chunks = langchain_docs_to_chunks(docs)
        assert len(chunks) == 2
        assert isinstance(chunks[0], Chunk)
        assert chunks[0].text == "Hello world."
