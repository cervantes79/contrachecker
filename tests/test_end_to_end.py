"""End-to-end tests: chunks in, contradiction report out."""
import pytest
from contrachecker import check_contradictions, ContradictionDetector
from contrachecker.models import Chunk, Claim
from contrachecker.extractors import PatternExtractor


class TestPublicAPI:
    def test_check_contradictions_function(self):
        chunks = [
            Chunk(id="c1", text="Coffee is healthy."),
            Chunk(id="c2", text="Coffee is harmful."),
        ]
        report = check_contradictions(chunks)
        assert report.chunks_analyzed == 2
        assert report.has_contradictions is True

    def test_check_contradictions_no_conflicts(self):
        chunks = [
            Chunk(id="c1", text="Water is essential."),
            Chunk(id="c2", text="Exercise is beneficial."),
        ]
        report = check_contradictions(chunks)
        assert report.has_contradictions is False

    def test_check_contradictions_with_custom_extractor(self):
        extractor = PatternExtractor()
        chunks = [
            Chunk(id="c1", text="Drug A causes weight gain."),
            Chunk(id="c2", text="Drug A causes weight loss."),
        ]
        report = check_contradictions(chunks, extractor=extractor)
        assert report.has_contradictions is True

    def test_check_contradictions_from_raw_claims(self):
        claims = [
            Claim(subject="policy_a", relation="effect", object="growth", source_chunk_id="doc1"),
            Claim(subject="policy_a", relation="effect", object="recession", source_chunk_id="doc2"),
        ]
        detector = ContradictionDetector()
        contradictions = detector.detect(claims)
        assert len(contradictions) >= 1

    def test_report_as_prompt_context(self):
        chunks = [
            Chunk(id="c1", text="Coffee is healthy."),
            Chunk(id="c2", text="Coffee is harmful."),
        ]
        report = check_contradictions(chunks)
        prompt = report.as_prompt_context()
        assert "CONTRADICTION" in prompt

    def test_medical_scenario(self, medical_chunks):
        """Use medical_chunks fixture from conftest."""
        report = check_contradictions(medical_chunks)
        assert report.chunks_analyzed == 3


class TestImports:
    def test_top_level_imports(self):
        from contrachecker import check_contradictions
        from contrachecker import ContradictionDetector
        from contrachecker.models import Claim, Chunk, Contradiction, ContradictionReport
        from contrachecker.extractors import PatternExtractor, ClaimExtractor

    def test_version(self):
        import contrachecker
        assert hasattr(contrachecker, "__version__")
        assert contrachecker.__version__ == "0.1.0"
