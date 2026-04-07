"""Claim extraction backends."""
from .base import ClaimExtractor
from .pattern_extractor import PatternExtractor

__all__ = ["ClaimExtractor", "PatternExtractor"]
