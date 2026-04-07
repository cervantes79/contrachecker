"""Core data models for contrachecker."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Claim(BaseModel):
    """A single factual claim extracted from a text chunk."""

    subject: str
    relation: str
    object: str
    source_chunk_id: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)

    @field_validator("subject", "relation", "object", mode="before")
    @classmethod
    def normalize(cls, v: str) -> str:
        return v.strip().lower()

    def matches_topic(self, other: Claim) -> bool:
        return self.subject == other.subject and self.relation == other.relation

    def contradicts(self, other: Claim) -> bool:
        return self.matches_topic(other) and self.object != other.object


class Chunk(BaseModel):
    """A text chunk from a RAG retrieval step."""

    id: str
    text: str
    metadata: dict = Field(default_factory=dict)


class Contradiction(BaseModel):
    """A detected contradiction between two claims."""

    type: Literal["direct", "indirect", "bridge"]
    claim_a: Claim
    claim_b: Claim
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    chain: list[str] = Field(default_factory=list)


class ContradictionReport(BaseModel):
    """Result of contradiction analysis on a set of chunks."""

    chunks_analyzed: int
    claims_extracted: int
    contradictions: list[Contradiction] = Field(default_factory=list)

    @property
    def has_contradictions(self) -> bool:
        return len(self.contradictions) > 0

    @property
    def contradiction_count(self) -> int:
        return len(self.contradictions)

    def summary(self) -> str:
        n = self.contradiction_count
        noun = "contradiction" if n == 1 else "contradictions"
        return (
            f"Analyzed {self.chunks_analyzed} chunks, extracted {self.claims_extracted} claims, "
            f"found {n} {noun}."
        )

    def as_prompt_context(self) -> str:
        if not self.contradictions:
            return ""
        lines = ["[CONTRADICTION REPORT]"]
        for i, c in enumerate(self.contradictions, 1):
            lines.append(
                f"CONTRADICTION {i} ({c.type}, confidence={c.confidence:.0%}): "
                f"'{c.claim_a.subject} {c.claim_a.relation} {c.claim_a.object}' "
                f"(from {c.claim_a.source_chunk_id}) CONFLICTS WITH "
                f"'{c.claim_b.subject} {c.claim_b.relation} {c.claim_b.object}' "
                f"(from {c.claim_b.source_chunk_id}). "
                f"{c.explanation}"
            )
        return "\n".join(lines)
