"""Tests for the contradiction detector."""
import pytest
from contrachecker.models import Claim, Contradiction, ContradictionReport
from contrachecker.detector import ContradictionDetector


class TestDirectContradictions:
    def test_detect_direct_contradiction(self):
        detector = ContradictionDetector()
        claims = [
            Claim(subject="metformin", relation="position", object="first_line", source_chunk_id="c1"),
            Claim(subject="metformin", relation="position", object="second_line", source_chunk_id="c2"),
        ]
        result = detector.detect(claims)
        assert len(result) == 1
        assert result[0].type == "direct"
        assert result[0].claim_a.object != result[0].claim_b.object

    def test_no_contradiction_same_object(self):
        detector = ContradictionDetector()
        claims = [
            Claim(subject="metformin", relation="treats", object="diabetes", source_chunk_id="c1"),
            Claim(subject="metformin", relation="treats", object="diabetes", source_chunk_id="c2"),
        ]
        result = detector.detect(claims)
        assert len(result) == 0

    def test_no_contradiction_different_relations(self):
        detector = ContradictionDetector()
        claims = [
            Claim(subject="coffee", relation="contains", object="caffeine", source_chunk_id="c1"),
            Claim(subject="coffee", relation="effect", object="alertness", source_chunk_id="c2"),
        ]
        result = detector.detect(claims)
        assert len(result) == 0

    def test_multiple_direct_contradictions(self):
        detector = ContradictionDetector()
        claims = [
            Claim(subject="drug_a", relation="safety", object="safe", source_chunk_id="c1"),
            Claim(subject="drug_a", relation="safety", object="unsafe", source_chunk_id="c2"),
            Claim(subject="drug_b", relation="efficacy", object="effective", source_chunk_id="c3"),
            Claim(subject="drug_b", relation="efficacy", object="ineffective", source_chunk_id="c4"),
        ]
        result = detector.detect(claims)
        assert len(result) == 2

    def test_semantic_opposition_causes_prevents(self):
        """'causes X' vs 'prevents X' on same subject = contradiction."""
        detector = ContradictionDetector()
        claims = [
            Claim(subject="aspirin", relation="prevents", object="heart attacks", source_chunk_id="c1"),
            Claim(subject="aspirin", relation="causes", object="heart attacks", source_chunk_id="c2"),
        ]
        result = detector.detect(claims)
        assert len(result) == 1
        assert result[0].type == "direct"

    def test_semantic_opposition_increases_decreases(self):
        """'increases X' vs 'decreases X' on same subject = contradiction."""
        detector = ContradictionDetector()
        claims = [
            Claim(subject="exercise", relation="increases", object="cardiovascular risk", source_chunk_id="c1"),
            Claim(subject="exercise", relation="decreases", object="cardiovascular risk", source_chunk_id="c2"),
        ]
        result = detector.detect(claims)
        assert len(result) == 1

    def test_no_opposition_different_objects(self):
        """Opposite relations but different objects = NOT a contradiction."""
        detector = ContradictionDetector()
        claims = [
            Claim(subject="drug", relation="causes", object="nausea", source_chunk_id="c1"),
            Claim(subject="drug", relation="prevents", object="headache", source_chunk_id="c2"),
        ]
        result = detector.detect(claims)
        assert len(result) == 0

    def test_three_way_contradiction(self):
        """3 claims about same topic but with 3 different objects = 3 pairs."""
        detector = ContradictionDetector()
        claims = [
            Claim(subject="treatment", relation="recommendation", object="option_a", source_chunk_id="c1"),
            Claim(subject="treatment", relation="recommendation", object="option_b", source_chunk_id="c2"),
            Claim(subject="treatment", relation="recommendation", object="option_c", source_chunk_id="c3"),
        ]
        result = detector.detect(claims)
        assert len(result) == 3


class TestIndirectContradictions:
    def test_detect_indirect_via_chain(self):
        """coffee -contains-> caffeine, caffeine -effect-> bad_sleep, coffee -effect-> good_sleep"""
        detector = ContradictionDetector()
        claims = [
            Claim(subject="coffee", relation="contains", object="caffeine", source_chunk_id="c1"),
            Claim(subject="caffeine", relation="effect", object="disrupts_sleep", source_chunk_id="c2"),
            Claim(subject="coffee", relation="effect", object="promotes_sleep", source_chunk_id="c3"),
        ]
        result = detector.detect(claims)
        indirect = [c for c in result if c.type == "indirect"]
        assert len(indirect) >= 1
        assert any("caffeine" in c.chain for c in indirect)

    def test_no_indirect_when_no_chain(self):
        detector = ContradictionDetector()
        claims = [
            Claim(subject="coffee", relation="effect", object="alertness", source_chunk_id="c1"),
            Claim(subject="tea", relation="effect", object="calm", source_chunk_id="c2"),
        ]
        result = detector.detect(claims)
        assert len(result) == 0

    def test_indirect_with_longer_chain(self):
        """A -> B -> C, and A contradicts C on some relation."""
        detector = ContradictionDetector()
        claims = [
            Claim(subject="a", relation="leads_to", object="b", source_chunk_id="c1"),
            Claim(subject="b", relation="leads_to", object="c", source_chunk_id="c2"),
            Claim(subject="a", relation="quality", object="good", source_chunk_id="c3"),
            Claim(subject="c", relation="quality", object="bad", source_chunk_id="c4"),
        ]
        result = detector.detect(claims)
        indirect = [c for c in result if c.type == "indirect"]
        assert len(indirect) >= 1


class TestBridgeContradictions:
    def test_bridge_contradiction(self):
        """Existing: A-effect->good, C-effect->bad. Bridge: A-contains->C links them."""
        detector = ContradictionDetector()
        claims = [
            Claim(subject="coffee", relation="effect", object="healthy", source_chunk_id="c1"),
            Claim(subject="caffeine", relation="effect", object="harmful", source_chunk_id="c2"),
            Claim(subject="coffee", relation="contains", object="caffeine", source_chunk_id="c3"),
        ]
        result = detector.detect(claims)
        assert len(result) >= 1


class TestDetectorConfig:
    def test_max_chain_depth(self):
        """With max_chain_depth=1, a 2-hop chain should not produce an indirect contradiction.

        Chain: a -contains-> b -produces-> c (2 hops, using different relations
        for each link so the chain links themselves don't contradict).
        Contradiction on 'quality': a=good, c=bad.
        At depth 1, BFS from c backward reaches only b, not a — so no indirect found.
        """
        detector = ContradictionDetector(max_chain_depth=1)
        claims = [
            Claim(subject="a", relation="contains", object="b", source_chunk_id="c1"),
            Claim(subject="b", relation="produces", object="c", source_chunk_id="c2"),
            Claim(subject="a", relation="quality", object="good", source_chunk_id="c3"),
            Claim(subject="c", relation="quality", object="bad", source_chunk_id="c4"),
        ]
        result = detector.detect(claims)
        indirect = [c for c in result if c.type == "indirect"]
        assert len(indirect) == 0

    def test_min_confidence_filter(self):
        detector = ContradictionDetector(min_confidence=0.5)
        claims = [
            Claim(subject="a", relation="r", object="x", source_chunk_id="c1", confidence=0.3),
            Claim(subject="a", relation="r", object="y", source_chunk_id="c2", confidence=0.3),
        ]
        result = detector.detect(claims)
        assert len(result) == 0

    def test_empty_claims(self):
        detector = ContradictionDetector()
        result = detector.detect([])
        assert len(result) == 0

    def test_single_claim(self):
        detector = ContradictionDetector()
        claims = [Claim(subject="a", relation="r", object="b", source_chunk_id="c1")]
        result = detector.detect(claims)
        assert len(result) == 0
