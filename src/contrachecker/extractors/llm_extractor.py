"""LLM-based claim extractor using OpenAI-compatible APIs.

Requires: pip install contrachecker[llm]
"""
from __future__ import annotations

import json
import logging

from ..models import Chunk, Claim

logger = logging.getLogger(__name__)

_EXTRACTION_PROMPT = """Extract factual claims from the following text as JSON.

Each claim should be a triple: subject, relation, object.
- subject: the main entity the claim is about
- relation: the relationship or predicate (e.g., "causes", "treats", "is", "contains", "increases")
- object: what the subject relates to

Return ONLY valid JSON in this format:
{{"claims": [{{"subject": "...", "relation": "...", "object": "..."}}]}}

If no clear factual claims can be extracted, return: {{"claims": []}}

Text:
---
{text}
---"""


def _call_llm(api_key: str, model: str, prompt: str) -> str:
    """Call OpenAI-compatible API. Separated for easy mocking."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


class LLMExtractor:
    """Extract claims using an LLM (OpenAI-compatible API).

    Args:
        api_key: OpenAI API key.
        model: Model name (default: gpt-4o-mini).
        base_url: Optional base URL for OpenAI-compatible APIs.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str | None = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def extract(self, chunk: Chunk) -> list[Claim]:
        if not chunk.text.strip():
            return []

        prompt = _EXTRACTION_PROMPT.format(text=chunk.text)

        try:
            raw = _call_llm(self.api_key, self.model, prompt)
            data = json.loads(raw)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Failed to parse LLM response for chunk %s: %s", chunk.id, e)
            return []

        claims: list[Claim] = []
        for item in data.get("claims", []):
            if not all(k in item for k in ("subject", "relation", "object")):
                continue
            claims.append(
                Claim(
                    subject=item["subject"],
                    relation=item["relation"],
                    object=item["object"],
                    source_chunk_id=chunk.id,
                    confidence=0.9,
                )
            )
        return claims

    def extract_many(self, chunks: list[Chunk]) -> list[Claim]:
        claims: list[Claim] = []
        for chunk in chunks:
            claims.extend(self.extract(chunk))
        return claims
