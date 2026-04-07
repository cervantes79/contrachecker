"""Medical document contradiction detection example.

Demonstrates how contrachecker catches conflicts between clinical guidelines,
research papers, and drug databases.
"""
from contrachecker.models import Claim
from contrachecker.detector import ContradictionDetector

claims = [
    Claim(subject="metformin", relation="recommended_as", object="first_line_therapy",
          source_chunk_id="ada_2019", confidence=0.95,
          metadata={"year": 2019, "type": "guideline"}),

    Claim(subject="metformin", relation="recommended_as", object="second_line_for_cv_risk",
          source_chunk_id="ada_2023", confidence=0.95,
          metadata={"year": 2023, "type": "guideline"}),

    Claim(subject="metformin", relation="contraindicated_with", object="contrast_dye",
          source_chunk_id="drug_db", confidence=0.9),

    Claim(subject="metformin", relation="safe_with", object="contrast_dye",
          source_chunk_id="nejm_2024", confidence=0.85,
          metadata={"year": 2024, "type": "rct"}),

    Claim(subject="metformin", relation="risk", object="lactic_acidosis",
          source_chunk_id="fda_label", confidence=0.9),
    Claim(subject="lactic_acidosis", relation="dangerous_for", object="kidney_patients",
          source_chunk_id="fda_label", confidence=0.95),
    Claim(subject="metformin", relation="safe_for", object="kidney_patients",
          source_chunk_id="kdigo_2023", confidence=0.8,
          metadata={"year": 2023, "note": "updated: safe if eGFR > 30"}),
]

detector = ContradictionDetector(max_chain_depth=3)
contradictions = detector.detect(claims)

print(f"Analyzed {len(claims)} claims, found {len(contradictions)} contradictions:\n")

for i, c in enumerate(contradictions, 1):
    print(f"{'='*60}")
    print(f"Contradiction {i} [{c.type.upper()}] (confidence: {c.confidence:.0%})")
    print(f"  Claim A: {c.claim_a.subject} {c.claim_a.relation} {c.claim_a.object}")
    print(f"    Source: {c.claim_a.source_chunk_id}")
    print(f"  Claim B: {c.claim_b.subject} {c.claim_b.relation} {c.claim_b.object}")
    print(f"    Source: {c.claim_b.source_chunk_id}")
    if c.chain:
        print(f"  Chain: {' -> '.join(c.chain)}")
    print(f"  Explanation: {c.explanation}")
