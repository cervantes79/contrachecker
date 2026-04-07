"""Tests for pattern-based claim extraction."""
import pytest
from contrachecker.models import Chunk
from contrachecker.extractors.pattern_extractor import PatternExtractor


class TestPatternExtractor:
    def test_extract_is_a_relation(self):
        extractor = PatternExtractor()
        chunk = Chunk(id="c1", text="Metformin is a first-line treatment.")
        claims = extractor.extract(chunk)
        assert len(claims) >= 1
        assert any(c.relation == "is_a" for c in claims)

    def test_extract_causes_relation(self):
        extractor = PatternExtractor()
        chunk = Chunk(id="c1", text="Smoking causes lung cancer.")
        claims = extractor.extract(chunk)
        assert len(claims) >= 1
        assert any(c.relation == "causes" for c in claims)

    def test_extract_contains_relation(self):
        extractor = PatternExtractor()
        chunk = Chunk(id="c1", text="Coffee contains caffeine.")
        claims = extractor.extract(chunk)
        assert len(claims) >= 1
        assert any(c.object == "caffeine" for c in claims)

    def test_extract_comparison(self):
        extractor = PatternExtractor()
        chunk = Chunk(id="c1", text="Drug A is more effective than Drug B.")
        claims = extractor.extract(chunk)
        assert len(claims) >= 1

    def test_extract_negation(self):
        extractor = PatternExtractor()
        chunk = Chunk(id="c1", text="Aspirin does not prevent cancer.")
        claims = extractor.extract(chunk)
        assert any("not" in c.relation or "not" in c.object for c in claims)

    def test_extract_multiple_sentences(self):
        extractor = PatternExtractor()
        chunk = Chunk(
            id="c1",
            text="Coffee contains caffeine. Caffeine causes alertness. Tea also contains caffeine.",
        )
        claims = extractor.extract(chunk)
        assert len(claims) >= 3

    def test_extract_empty_text(self):
        extractor = PatternExtractor()
        chunk = Chunk(id="c1", text="")
        claims = extractor.extract(chunk)
        assert claims == []

    def test_chunk_id_propagated(self):
        extractor = PatternExtractor()
        chunk = Chunk(id="my_chunk_42", text="Water is essential for life.")
        claims = extractor.extract(chunk)
        assert all(c.source_chunk_id == "my_chunk_42" for c in claims)

    def test_recommends_relation(self):
        extractor = PatternExtractor()
        chunk = Chunk(id="c1", text="The WHO recommends vaccination for all children.")
        claims = extractor.extract(chunk)
        assert len(claims) >= 1

    def test_increases_decreases(self):
        extractor = PatternExtractor()
        chunk = Chunk(id="c1", text="Exercise decreases cardiovascular risk. Smoking increases cancer risk.")
        claims = extractor.extract(chunk)
        assert len(claims) >= 2
