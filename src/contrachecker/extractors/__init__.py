"""Claim extraction backends."""
from .base import ClaimExtractor
from .pattern_extractor import PatternExtractor

__all__ = ["ClaimExtractor", "PatternExtractor"]

try:
    from .llm_extractor import LLMExtractor
    __all__.append("LLMExtractor")
except ImportError:
    pass  # openai not installed
