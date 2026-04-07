"""Base interface for claim extractors."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import Chunk, Claim


@runtime_checkable
class ClaimExtractor(Protocol):
    """Protocol that all claim extractors must implement."""

    def extract(self, chunk: Chunk) -> list[Claim]: ...

    def extract_many(self, chunks: list[Chunk]) -> list[Claim]: ...
