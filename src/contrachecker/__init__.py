"""contrachecker - Detect contradictions between retrieved documents in RAG pipelines.

Usage:
    from contrachecker import check_contradictions
    from contrachecker.models import Chunk

    chunks = [
        Chunk(id="doc1", text="Coffee is healthy."),
        Chunk(id="doc2", text="Coffee is harmful."),
    ]
    report = check_contradictions(chunks)
    print(report.summary())
"""
from __future__ import annotations

__version__ = "0.1.0"

from .models import Chunk, Claim, Contradiction, ContradictionReport
from .detector import ContradictionDetector
from .extractors.base import ClaimExtractor
from .extractors.pattern_extractor import PatternExtractor


def check_contradictions(
    chunks: list[Chunk],
    *,
    extractor: ClaimExtractor | None = None,
    max_chain_depth: int = 4,
    min_confidence: float = 0.0,
) -> ContradictionReport:
    """Analyze chunks for contradictions. Main entry point.

    Args:
        chunks: Text chunks from RAG retrieval.
        extractor: Claim extractor to use (default: PatternExtractor).
        max_chain_depth: Max BFS depth for indirect contradiction detection.
        min_confidence: Ignore claims below this confidence.

    Returns:
        ContradictionReport with all detected contradictions.
    """
    if extractor is None:
        extractor = PatternExtractor()

    claims = extractor.extract_many(chunks)

    detector = ContradictionDetector(
        max_chain_depth=max_chain_depth,
        min_confidence=min_confidence,
    )
    contradictions = detector.detect(claims)

    return ContradictionReport(
        chunks_analyzed=len(chunks),
        claims_extracted=len(claims),
        contradictions=contradictions,
    )


__all__ = [
    "check_contradictions",
    "ContradictionDetector",
    "Chunk",
    "Claim",
    "Contradiction",
    "ContradictionReport",
    "PatternExtractor",
    "ClaimExtractor",
    "__version__",
]
