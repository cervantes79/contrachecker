"""Tests for core data models."""
import pytest
from contrachecker.models import Claim, Chunk, Contradiction, ContradictionReport


class TestClaim:
    def test_create_claim(self):
        claim = Claim(
            subject="metformin",
            relation="is_recommended_as",
            object="first_line_treatment",
            source_chunk_id="chunk_1",
            confidence=0.95,
        )
        assert claim.subject == "metformin"
        assert claim.relation == "is_recommended_as"
        assert claim.object == "first_line_treatment"
        assert claim.source_chunk_id == "chunk_1"
        assert claim.confidence == 0.95

    def test_claim_normalization(self):
        claim = Claim(
            subject="  Metformin  ",
            relation="IS_RECOMMENDED_AS",
            object="First Line Treatment",
            source_chunk_id="c1",
        )
        assert claim.subject == "metformin"
        assert claim.relation == "is_recommended_as"
        assert claim.object == "first line treatment"

    def test_claim_default_confidence(self):
        claim = Claim(subject="a", relation="r", object="b", source_chunk_id="c1")
        assert claim.confidence == 1.0

    def test_claim_matches_topic(self):
        c1 = Claim(subject="coffee", relation="effect", object="healthy", source_chunk_id="c1")
        c2 = Claim(subject="coffee", relation="effect", object="harmful", source_chunk_id="c2")
        assert c1.matches_topic(c2) is True

    def test_claim_contradicts(self):
        c1 = Claim(subject="coffee", relation="effect", object="healthy", source_chunk_id="c1")
        c2 = Claim(subject="coffee", relation="effect", object="harmful", source_chunk_id="c2")
        assert c1.contradicts(c2) is True

    def test_claim_no_contradiction_same_object(self):
        c1 = Claim(subject="coffee", relation="effect", object="healthy", source_chunk_id="c1")
        c2 = Claim(subject="coffee", relation="effect", object="healthy", source_chunk_id="c2")
        assert c1.contradicts(c2) is False

    def test_claim_no_contradiction_different_topic(self):
        c1 = Claim(subject="coffee", relation="effect", object="healthy", source_chunk_id="c1")
        c2 = Claim(subject="tea", relation="effect", object="harmful", source_chunk_id="c2")
        assert c1.contradicts(c2) is False

    def test_claim_metadata(self):
        claim = Claim(
            subject="drug_x",
            relation="treats",
            object="condition_y",
            source_chunk_id="c1",
            metadata={"date": "2023", "source_type": "guideline"},
        )
        assert claim.metadata["date"] == "2023"


class TestChunk:
    def test_create_chunk(self):
        chunk = Chunk(id="chunk_1", text="Metformin is the first-line treatment for type 2 diabetes.")
        assert chunk.id == "chunk_1"
        assert "Metformin" in chunk.text

    def test_chunk_with_metadata(self):
        chunk = Chunk(id="c1", text="Some text", metadata={"source": "guidelines_2023.pdf", "page": 42})
        assert chunk.metadata["page"] == 42


class TestContradiction:
    def test_create_direct_contradiction(self):
        c1 = Claim(subject="coffee", relation="effect", object="healthy", source_chunk_id="chunk_1")
        c2 = Claim(subject="coffee", relation="effect", object="harmful", source_chunk_id="chunk_2")
        contradiction = Contradiction(
            type="direct", claim_a=c1, claim_b=c2, confidence=0.95,
            explanation="Same subject and relation but conflicting objects",
        )
        assert contradiction.type == "direct"
        assert contradiction.confidence == 0.95

    def test_create_indirect_contradiction(self):
        c1 = Claim(subject="coffee", relation="effect", object="healthy", source_chunk_id="chunk_1")
        c2 = Claim(subject="caffeine", relation="effect", object="harmful", source_chunk_id="chunk_2")
        contradiction = Contradiction(
            type="indirect", claim_a=c1, claim_b=c2, confidence=0.8,
            explanation="coffee contains caffeine, caffeine is harmful",
            chain=["coffee", "caffeine"],
        )
        assert contradiction.type == "indirect"
        assert contradiction.chain == ["coffee", "caffeine"]

    def test_contradiction_type_validation(self):
        c1 = Claim(subject="a", relation="r", object="b", source_chunk_id="c1")
        c2 = Claim(subject="a", relation="r", object="c", source_chunk_id="c2")
        with pytest.raises(ValueError):
            Contradiction(type="invalid_type", claim_a=c1, claim_b=c2, confidence=0.5, explanation="test")


class TestContradictionReport:
    def test_empty_report(self):
        report = ContradictionReport(chunks_analyzed=3, claims_extracted=10, contradictions=[])
        assert report.has_contradictions is False
        assert report.contradiction_count == 0

    def test_report_with_contradictions(self):
        c1 = Claim(subject="a", relation="r", object="b", source_chunk_id="c1")
        c2 = Claim(subject="a", relation="r", object="c", source_chunk_id="c2")
        contradiction = Contradiction(type="direct", claim_a=c1, claim_b=c2, confidence=0.9, explanation="conflict")
        report = ContradictionReport(chunks_analyzed=2, claims_extracted=5, contradictions=[contradiction])
        assert report.has_contradictions is True
        assert report.contradiction_count == 1

    def test_report_summary(self):
        c1 = Claim(subject="a", relation="r", object="b", source_chunk_id="c1")
        c2 = Claim(subject="a", relation="r", object="c", source_chunk_id="c2")
        contradiction = Contradiction(type="direct", claim_a=c1, claim_b=c2, confidence=0.9, explanation="conflict")
        report = ContradictionReport(chunks_analyzed=2, claims_extracted=5, contradictions=[contradiction])
        summary = report.summary()
        assert "1 contradiction" in summary
        assert "2 chunks" in summary

    def test_report_prompt_injection(self):
        c1 = Claim(subject="drug_a", relation="recommended_for", object="condition_x", source_chunk_id="c1")
        c2 = Claim(subject="drug_a", relation="recommended_for", object="condition_y", source_chunk_id="c2")
        contradiction = Contradiction(type="direct", claim_a=c1, claim_b=c2, confidence=0.9, explanation="conflict")
        report = ContradictionReport(chunks_analyzed=2, claims_extracted=4, contradictions=[contradiction])
        prompt_text = report.as_prompt_context()
        assert "CONTRADICTION" in prompt_text
        assert "drug_a" in prompt_text
