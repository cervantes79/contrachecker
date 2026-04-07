"""Shared test fixtures for contrachecker tests."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from contrachecker.models import Claim, Chunk


@pytest.fixture
def medical_chunks():
    """Realistic medical document chunks with contradictions."""
    return [
        Chunk(
            id="guideline_2019",
            text="Metformin is the first-line treatment for type 2 diabetes.",
            metadata={"source": "ADA Guidelines 2019", "year": 2019},
        ),
        Chunk(
            id="guideline_2023",
            text="GLP-1 receptor agonists should be preferred over metformin in patients with cardiovascular risk.",
            metadata={"source": "ADA Guidelines 2023", "year": 2023},
        ),
        Chunk(
            id="review_2022",
            text="Metformin remains safe and effective for most type 2 diabetes patients.",
            metadata={"source": "Cochrane Review 2022", "year": 2022},
        ),
    ]


@pytest.fixture
def contradicting_claims():
    return (
        Claim(subject="metformin", relation="position", object="first_line", source_chunk_id="guideline_2019"),
        Claim(subject="metformin", relation="position", object="second_line", source_chunk_id="guideline_2023"),
    )


@pytest.fixture
def non_contradicting_claims():
    return (
        Claim(subject="metformin", relation="treats", object="type_2_diabetes", source_chunk_id="c1"),
        Claim(subject="metformin", relation="side_effect", object="nausea", source_chunk_id="c2"),
    )


@pytest.fixture
def indirect_contradiction_claims():
    return [
        Claim(subject="coffee", relation="contains", object="caffeine", source_chunk_id="c1"),
        Claim(subject="caffeine", relation="effect", object="harmful_to_sleep", source_chunk_id="c2"),
        Claim(subject="coffee", relation="effect", object="promotes_good_sleep", source_chunk_id="c3"),
    ]
