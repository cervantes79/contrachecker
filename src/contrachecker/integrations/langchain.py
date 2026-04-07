"""LangChain integration for contrachecker.

Provides a DocumentTransformer that appends contradiction reports
to retrieved documents before they reach the LLM.

Requires: pip install contrachecker[langchain]
"""
from __future__ import annotations

from typing import Any, Sequence

from langchain_core.documents import BaseDocumentTransformer, Document

from ..models import Chunk
from ..extractors.base import ClaimExtractor
from .. import check_contradictions


def langchain_docs_to_chunks(docs: Sequence[Document]) -> list[Chunk]:
    """Convert LangChain Documents to contrachecker Chunks."""
    chunks = []
    for i, doc in enumerate(docs):
        chunk_id = doc.metadata.get("id") or doc.metadata.get("source") or f"doc_{i}"
        chunks.append(
            Chunk(
                id=str(chunk_id),
                text=doc.page_content,
                metadata=dict(doc.metadata),
            )
        )
    return chunks


class ContradictionCheckerTransformer(BaseDocumentTransformer):
    """LangChain DocumentTransformer that detects contradictions.

    If contradictions are found, appends a report document to the list.
    """

    extractor: ClaimExtractor | None = None
    max_chain_depth: int = 4
    min_confidence: float = 0.0

    class Config:
        arbitrary_types_allowed = True

    def transform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> list[Document]:
        chunks = langchain_docs_to_chunks(documents)
        report = check_contradictions(
            chunks,
            extractor=self.extractor,
            max_chain_depth=self.max_chain_depth,
            min_confidence=self.min_confidence,
        )

        result = list(documents)

        if report.has_contradictions:
            report_doc = Document(
                page_content=report.as_prompt_context(),
                metadata={
                    "is_contradiction_report": True,
                    "contradiction_count": report.contradiction_count,
                    "source": "contrachecker",
                },
            )
            result.append(report_doc)

        return result
