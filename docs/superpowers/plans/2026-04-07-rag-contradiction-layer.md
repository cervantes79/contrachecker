# RAG Contradiction Detection Layer - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform ChainOfMeaning from a standalone rule engine into `contrachecker` — a Python library that detects contradictions between retrieved document chunks in any RAG pipeline.

**Architecture:** Chunks come in, claims (triples) are extracted via pluggable extractors (LLM-based or pattern-based), then the contradiction detector finds direct, indirect, and bridge contradictions between claims. Output is a structured report that can be injected into the LLM prompt or used programmatically. Integrations provided for LangChain, LlamaIndex, and standalone use.

**Tech Stack:** Python 3.11+, pydantic v2, pytest, LangChain (optional integration), OpenAI/Anthropic (optional for LLM-based extraction), FastAPI (optional API server)

---

## File Structure

```
chainofmeaning/                          # repo root (rename not needed — pip name is contrachecker)
├── README.md                            # Full product README
├── pyproject.toml                       # Package config, deps, entry points
├── LICENSE                              # MIT
├── .gitignore                           # Updated
│
├── src/
│   └── contrachecker/                   # Main package
│       ├── __init__.py                  # Public API exports
│       ├── models.py                    # Pydantic models: Claim, Chunk, Contradiction, Report
│       ├── detector.py                  # Core: ContradictionDetector (rewritten from engine_v4)
│       ├── extractors/
│       │   ├── __init__.py              # Extractor registry
│       │   ├── base.py                  # BaseExtractor protocol
│       │   ├── llm_extractor.py         # LLM-based claim extraction (OpenAI/Anthropic)
│       │   └── pattern_extractor.py     # Regex/rule-based claim extraction (zero-dep)
│       └── integrations/
│           ├── __init__.py
│           └── langchain.py             # LangChain document transformer
│
├── tests/
│   ├── conftest.py                      # Shared fixtures
│   ├── test_models.py                   # Model validation tests
│   ├── test_detector.py                 # Core contradiction detection tests
│   ├── test_pattern_extractor.py        # Pattern extractor tests
│   ├── test_llm_extractor.py            # LLM extractor tests (mocked)
│   ├── test_langchain_integration.py    # LangChain integration tests
│   └── test_end_to_end.py              # Full pipeline tests
│
├── examples/
│   ├── quickstart.py                    # Minimal usage example
│   ├── langchain_rag.py                 # LangChain RAG with contradiction detection
│   └── medical_docs.py                  # Medical document contradiction example
│
└── legacy/                              # Old engine code (preserved, not imported)
    ├── engine_v1.py
    ├── engine_v2.py
    ├── engine_v3.py
    ├── engine_v4.py
    ├── storage.py
    ├── taxonomy.py
    ├── decision_tree.py
    └── ...
```

## What gets reused from existing code

The contradiction detection algorithms from `engine_v4.py` are the core value. Specifically:
- **Direct contradiction**: same (subject, relation), different object — `contradicts()` method
- **Indirect contradiction**: BFS backward chaining finds transitive conflicts — `_detect_indirect_contradictions()`
- **Bridge contradiction**: new claim connects previously unrelated conflicting claims — `_detect_bridge_contradictions()`
- **Support counting**: measures how well-supported a claim is — `_count_support()`
- **BFS path finding**: `_find_path()` for chain discovery

What gets dropped:
- SQLite persistence (stateless per-request is the right model for a middleware)
- Decision tree routing (RAG already handles relevance filtering)
- Taxonomy clustering (may revisit later, not MVP)
- Chat interface, bulk load, all test infrastructure

---

## Task 0: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `LICENSE`
- Modify: `.gitignore`
- Move: `src/engine.py`, `src/engine_v2.py`, `src/engine_v3.py`, `src/engine_v4.py`, `src/storage.py`, `src/taxonomy.py`, `src/decision_tree.py`, `src/__init__.py` → `legacy/`
- Move: `tests/autopsy.py`, `tests/autopsy_v2.py`, `tests/autopsy_v3.py`, `tests/growth_test.py`, `tests/scale_test.py`, `tests/million_test.py`, `tests/query_test.py`, `tests/__init__.py` → `legacy/tests/`
- Move: `expected/` → `legacy/expected/`
- Move: `tools/` → `legacy/tools/`
- Move: `reports/` → `legacy/reports/`
- Move: `chat.py` → `legacy/chat.py`
- Create: `src/contrachecker/__init__.py` (empty placeholder)

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "contrachecker"
version = "0.1.0"
description = "Detect contradictions between retrieved documents in RAG pipelines"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [
    { name = "Baris Genc", email = "info@gencbaris.com" },
]
keywords = ["rag", "contradiction", "detection", "llm", "nlp", "fact-checking"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Text Processing :: Linguistic",
]
dependencies = [
    "pydantic>=2.0",
]

[project.optional-dependencies]
llm = ["openai>=1.0"]
langchain = ["langchain-core>=0.2"]
all = ["openai>=1.0", "langchain-core>=0.2"]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
]

[project.urls]
Homepage = "https://gencbaris.com"
Repository = "https://github.com/barisgenc/contrachecker"
Issues = "https://github.com/barisgenc/contrachecker/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/contrachecker"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create LICENSE**

```
MIT License

Copyright (c) 2024-2026 Baris Genc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Move legacy code**

```bash
mkdir -p legacy/tests legacy/expected legacy/tools legacy/reports

# Move engine files
mv src/engine.py src/engine_v2.py src/engine_v3.py src/engine_v4.py legacy/
mv src/storage.py src/taxonomy.py src/decision_tree.py legacy/
mv src/__init__.py legacy/

# Move tests
mv tests/autopsy.py tests/autopsy_v2.py tests/autopsy_v3.py legacy/tests/
mv tests/growth_test.py tests/scale_test.py tests/million_test.py legacy/tests/
mv tests/query_test.py legacy/tests/
mv tests/__init__.py legacy/tests/ 2>/dev/null || true

# Move other dirs
mv expected/* legacy/expected/ 2>/dev/null || true
mv tools/* legacy/tools/ 2>/dev/null || true
mv reports/* legacy/reports/ 2>/dev/null || true
mv chat.py legacy/

# Remove empty dirs
rmdir expected tools reports 2>/dev/null || true

# Remove pycache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

- [ ] **Step 4: Create package directory and empty init**

```bash
mkdir -p src/contrachecker/extractors src/contrachecker/integrations
touch src/contrachecker/__init__.py
touch src/contrachecker/extractors/__init__.py
touch src/contrachecker/integrations/__init__.py
```

- [ ] **Step 5: Update .gitignore**

Replace `.gitignore` with:
```
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.eggs/

# Virtual env
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp

# Testing
.coverage
htmlcov/
.pytest_cache/

# SQLite (legacy)
*.db
*.db-wal
*.db-shm

# Claude Code
.claude/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 6: Verify structure and commit**

```bash
ls -la src/contrachecker/
ls -la legacy/
python -c "import sys; sys.path.insert(0,'src'); import contrachecker; print('OK')"
git add -A
git commit -m "chore: restructure project for contrachecker library

Move legacy engine code to legacy/, create src/contrachecker/ package
structure with pyproject.toml for pip-installable library."
```

---

## Task 1: Core Models

**Files:**
- Create: `src/contrachecker/models.py`
- Create: `tests/test_models.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Write failing tests for models**

```python
# tests/test_models.py
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
        chunk = Chunk(
            id="chunk_1",
            text="Metformin is the first-line treatment for type 2 diabetes.",
        )
        assert chunk.id == "chunk_1"
        assert "Metformin" in chunk.text

    def test_chunk_with_metadata(self):
        chunk = Chunk(
            id="c1",
            text="Some text",
            metadata={"source": "guidelines_2023.pdf", "page": 42},
        )
        assert chunk.metadata["page"] == 42


class TestContradiction:
    def test_create_direct_contradiction(self):
        c1 = Claim(subject="coffee", relation="effect", object="healthy", source_chunk_id="chunk_1")
        c2 = Claim(subject="coffee", relation="effect", object="harmful", source_chunk_id="chunk_2")
        contradiction = Contradiction(
            type="direct",
            claim_a=c1,
            claim_b=c2,
            confidence=0.95,
            explanation="Same subject and relation but conflicting objects",
        )
        assert contradiction.type == "direct"
        assert contradiction.confidence == 0.95

    def test_create_indirect_contradiction(self):
        c1 = Claim(subject="coffee", relation="effect", object="healthy", source_chunk_id="chunk_1")
        c2 = Claim(subject="caffeine", relation="effect", object="harmful", source_chunk_id="chunk_2")
        contradiction = Contradiction(
            type="indirect",
            claim_a=c1,
            claim_b=c2,
            confidence=0.8,
            explanation="coffee contains caffeine, caffeine is harmful",
            chain=["coffee", "caffeine"],
        )
        assert contradiction.type == "indirect"
        assert contradiction.chain == ["coffee", "caffeine"]

    def test_contradiction_type_validation(self):
        c1 = Claim(subject="a", relation="r", object="b", source_chunk_id="c1")
        c2 = Claim(subject="a", relation="r", object="c", source_chunk_id="c2")
        with pytest.raises(ValueError):
            Contradiction(
                type="invalid_type",
                claim_a=c1,
                claim_b=c2,
                confidence=0.5,
                explanation="test",
            )


class TestContradictionReport:
    def test_empty_report(self):
        report = ContradictionReport(
            chunks_analyzed=3,
            claims_extracted=10,
            contradictions=[],
        )
        assert report.has_contradictions is False
        assert report.contradiction_count == 0

    def test_report_with_contradictions(self):
        c1 = Claim(subject="a", relation="r", object="b", source_chunk_id="c1")
        c2 = Claim(subject="a", relation="r", object="c", source_chunk_id="c2")
        contradiction = Contradiction(
            type="direct",
            claim_a=c1,
            claim_b=c2,
            confidence=0.9,
            explanation="conflict",
        )
        report = ContradictionReport(
            chunks_analyzed=2,
            claims_extracted=5,
            contradictions=[contradiction],
        )
        assert report.has_contradictions is True
        assert report.contradiction_count == 1

    def test_report_summary(self):
        c1 = Claim(subject="a", relation="r", object="b", source_chunk_id="c1")
        c2 = Claim(subject="a", relation="r", object="c", source_chunk_id="c2")
        contradiction = Contradiction(
            type="direct", claim_a=c1, claim_b=c2, confidence=0.9, explanation="conflict"
        )
        report = ContradictionReport(
            chunks_analyzed=2,
            claims_extracted=5,
            contradictions=[contradiction],
        )
        summary = report.summary()
        assert "1 contradiction" in summary
        assert "2 chunks" in summary

    def test_report_prompt_injection(self):
        """Report can generate text suitable for LLM prompt injection."""
        c1 = Claim(subject="drug_a", relation="recommended_for", object="condition_x", source_chunk_id="c1")
        c2 = Claim(subject="drug_a", relation="recommended_for", object="condition_y", source_chunk_id="c2")
        contradiction = Contradiction(
            type="direct", claim_a=c1, claim_b=c2, confidence=0.9, explanation="conflict"
        )
        report = ContradictionReport(
            chunks_analyzed=2, claims_extracted=4, contradictions=[contradiction]
        )
        prompt_text = report.as_prompt_context()
        assert "CONTRADICTION" in prompt_text
        assert "drug_a" in prompt_text
```

- [ ] **Step 2: Create conftest with shared fixtures**

```python
# tests/conftest.py
"""Shared test fixtures for contrachecker tests."""
import sys
import os
import pytest

# Ensure src/ is on the path for imports
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
    """A pair of directly contradicting claims."""
    return (
        Claim(subject="metformin", relation="position", object="first_line", source_chunk_id="guideline_2019"),
        Claim(subject="metformin", relation="position", object="second_line", source_chunk_id="guideline_2023"),
    )


@pytest.fixture
def non_contradicting_claims():
    """Claims that do not contradict each other."""
    return (
        Claim(subject="metformin", relation="treats", object="type_2_diabetes", source_chunk_id="c1"),
        Claim(subject="metformin", relation="side_effect", object="nausea", source_chunk_id="c2"),
    )


@pytest.fixture
def indirect_contradiction_claims():
    """Claims that contradict through a chain."""
    return [
        Claim(subject="coffee", relation="contains", object="caffeine", source_chunk_id="c1"),
        Claim(subject="caffeine", relation="effect", object="harmful_to_sleep", source_chunk_id="c2"),
        Claim(subject="coffee", relation="effect", object="promotes_good_sleep", source_chunk_id="c3"),
    ]
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:/Users/cerva/Documents/projects/chainofmeaning
python -m pytest tests/test_models.py -v 2>&1 | head -30
```

Expected: FAIL — `ModuleNotFoundError: No module named 'contrachecker.models'`

- [ ] **Step 4: Implement models**

```python
# src/contrachecker/models.py
"""Core data models for contrachecker."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Claim(BaseModel):
    """A single factual claim extracted from a text chunk.

    Represents a (subject, relation, object) triple with provenance.
    """

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
        """True if both claims are about the same subject+relation."""
        return self.subject == other.subject and self.relation == other.relation

    def contradicts(self, other: Claim) -> bool:
        """True if claims share subject+relation but differ in object."""
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
        """Format contradictions as text to inject into an LLM prompt."""
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
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_models.py -v
```

Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add src/contrachecker/models.py tests/test_models.py tests/conftest.py
git commit -m "feat: add core data models (Claim, Chunk, Contradiction, Report)"
```

---

## Task 2: Contradiction Detector (Core Engine)

**Files:**
- Create: `src/contrachecker/detector.py`
- Create: `tests/test_detector.py`

This is the heart of the library — rewritten from `engine_v4.py` but stateless and focused purely on contradiction detection.

- [ ] **Step 1: Write failing tests for direct contradiction detection**

```python
# tests/test_detector.py
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

    def test_three_way_contradiction(self):
        """3 claims about same topic but with 3 different objects = 3 pairs."""
        detector = ContradictionDetector()
        claims = [
            Claim(subject="treatment", relation="recommendation", object="option_a", source_chunk_id="c1"),
            Claim(subject="treatment", relation="recommendation", object="option_b", source_chunk_id="c2"),
            Claim(subject="treatment", relation="recommendation", object="option_c", source_chunk_id="c3"),
        ]
        result = detector.detect(claims)
        # 3 choose 2 = 3 contradiction pairs
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
        """Unrelated claims should not produce indirect contradictions."""
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
            # This claim bridges coffee and caffeine
            Claim(subject="coffee", relation="contains", object="caffeine", source_chunk_id="c3"),
        ]
        result = detector.detect(claims)
        # Should detect some form of contradiction linking coffee and caffeine
        assert len(result) >= 1


class TestDetectorConfig:
    def test_max_chain_depth(self):
        detector = ContradictionDetector(max_chain_depth=1)
        claims = [
            Claim(subject="a", relation="leads_to", object="b", source_chunk_id="c1"),
            Claim(subject="b", relation="leads_to", object="c", source_chunk_id="c2"),
            Claim(subject="a", relation="quality", object="good", source_chunk_id="c3"),
            Claim(subject="c", relation="quality", object="bad", source_chunk_id="c4"),
        ]
        result = detector.detect(claims)
        indirect = [c for c in result if c.type == "indirect"]
        # depth 1 can't find a->b->c chain (needs depth 2)
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_detector.py -v 2>&1 | head -10
```

Expected: FAIL — `ModuleNotFoundError: No module named 'contrachecker.detector'`

- [ ] **Step 3: Implement ContradictionDetector**

```python
# src/contrachecker/detector.py
"""Core contradiction detection engine.

Adapted from ChainOfMeaning v4 engine. Detects three types of contradictions
between claims: direct, indirect (via reasoning chains), and bridge
(a new claim connecting previously unrelated conflicting claims).
"""
from __future__ import annotations

from collections import defaultdict, deque

from .models import Claim, Contradiction


class ContradictionDetector:
    """Stateless contradiction detector for a set of claims.

    Args:
        max_chain_depth: Maximum BFS depth for indirect/bridge detection.
        min_confidence: Ignore claims below this confidence threshold.
    """

    def __init__(self, max_chain_depth: int = 4, min_confidence: float = 0.0):
        self.max_chain_depth = max_chain_depth
        self.min_confidence = min_confidence

    def detect(self, claims: list[Claim]) -> list[Contradiction]:
        """Find all contradictions among the given claims.

        Returns a list of Contradiction objects sorted by confidence (highest first).
        """
        claims = [c for c in claims if c.confidence >= self.min_confidence]
        if len(claims) < 2:
            return []

        # Build indexes
        by_subject: dict[str, list[Claim]] = defaultdict(list)
        by_object: dict[str, list[Claim]] = defaultdict(list)
        by_topic: dict[tuple[str, str], list[Claim]] = defaultdict(list)

        for claim in claims:
            by_subject[claim.subject].append(claim)
            by_object[claim.object].append(claim)
            by_topic[(claim.subject, claim.relation)].append(claim)

        results: list[Contradiction] = []
        seen: set[tuple[str, str]] = set()  # (chunk_id_a, chunk_id_b) pairs

        # 1. Direct contradictions
        for topic_claims in by_topic.values():
            for i, a in enumerate(topic_claims):
                for b in topic_claims[i + 1 :]:
                    if a.object != b.object:
                        pair_key = tuple(sorted([a.source_chunk_id, b.source_chunk_id]))
                        # Allow multiple contradictions from same chunk pair
                        item_key = (a.subject, a.relation, a.object, b.object)
                        if item_key not in seen:
                            seen.add(item_key)
                            results.append(
                                Contradiction(
                                    type="direct",
                                    claim_a=a,
                                    claim_b=b,
                                    confidence=min(a.confidence, b.confidence),
                                    explanation=(
                                        f"Both claim '{a.subject}' has '{a.relation}' "
                                        f"but disagree: '{a.object}' vs '{b.object}'"
                                    ),
                                )
                            )

        # 2. Indirect contradictions (via chains)
        self._detect_indirect(claims, by_subject, by_object, by_topic, results)

        # 3. Bridge contradictions
        self._detect_bridges(claims, by_subject, by_topic, results)

        results.sort(key=lambda c: c.confidence, reverse=True)
        return results

    def _detect_indirect(
        self,
        claims: list[Claim],
        by_subject: dict[str, list[Claim]],
        by_object: dict[str, list[Claim]],
        by_topic: dict[tuple[str, str], list[Claim]],
        results: list[Contradiction],
    ) -> None:
        """Detect indirect contradictions via BFS backward chaining.

        Example: coffee-contains->caffeine + caffeine-effect->bad_sleep
        contradicts coffee-effect->good_sleep because coffee reaches caffeine.
        """
        by_relation: dict[str, list[Claim]] = defaultdict(list)
        for claim in claims:
            by_relation[claim.relation].append(claim)

        seen_indirect: set[tuple[str, str, str, str]] = set()

        for claim in claims:
            # BFS backward from claim.subject to find all reachable entities
            reachable = self._bfs_backward(claim.subject, by_object)
            if not reachable:
                continue

            # Check if any claim with same relation but different object
            # exists for a reachable entity
            for other in by_relation.get(claim.relation, []):
                if other.subject not in reachable:
                    continue
                if other.subject == claim.subject:
                    continue  # Direct, not indirect
                if other.object == claim.object:
                    continue  # Same conclusion, no contradiction

                key = tuple(sorted([
                    f"{claim.subject}:{claim.object}",
                    f"{other.subject}:{other.object}",
                ]))
                if key in seen_indirect:
                    continue
                seen_indirect.add(key)

                chain = self._find_path(
                    other.subject, claim.subject, by_subject
                )
                if chain:
                    results.append(
                        Contradiction(
                            type="indirect",
                            claim_a=other,
                            claim_b=claim,
                            confidence=min(other.confidence, claim.confidence) * 0.8,
                            explanation=(
                                f"'{other.subject}' reaches '{claim.subject}' "
                                f"via chain {' -> '.join(chain)}, but they disagree "
                                f"on '{claim.relation}': "
                                f"'{other.object}' vs '{claim.object}'"
                            ),
                            chain=chain,
                        )
                    )

    def _detect_bridges(
        self,
        claims: list[Claim],
        by_subject: dict[str, list[Claim]],
        by_topic: dict[tuple[str, str], list[Claim]],
        results: list[Contradiction],
    ) -> None:
        """Detect bridge contradictions.

        A bridge occurs when a claim connects two previously unrelated
        entities that have conflicting claims on the same relation.
        """
        seen_bridge: set[tuple[str, str, str, str]] = set()

        for claim in claims:
            # Find what claim.subject also claims
            sibling_claims = by_subject.get(claim.subject, [])

            # Find what's reachable from claim.subject
            reachable = self._bfs_forward(claim.subject, by_subject)
            if not reachable:
                continue

            for sibling in sibling_claims:
                if sibling is claim:
                    continue
                # Check if any reachable entity contradicts sibling
                for entity in reachable:
                    if entity == claim.subject:
                        continue
                    for other in by_subject.get(entity, []):
                        if other.relation != sibling.relation:
                            continue
                        if other.object == sibling.object:
                            continue
                        if other.subject == sibling.subject:
                            continue

                        key = tuple(sorted([
                            f"{sibling.subject}:{sibling.object}",
                            f"{other.subject}:{other.object}",
                        ]))
                        if key in seen_bridge:
                            continue
                        seen_bridge.add(key)

                        chain = self._find_path(
                            sibling.subject, other.subject, by_subject
                        )
                        if chain:
                            results.append(
                                Contradiction(
                                    type="bridge",
                                    claim_a=sibling,
                                    claim_b=other,
                                    confidence=min(sibling.confidence, other.confidence) * 0.7,
                                    explanation=(
                                        f"'{claim.subject} {claim.relation} {claim.object}' "
                                        f"bridges '{sibling.subject}' to '{other.subject}', "
                                        f"revealing conflict on '{sibling.relation}': "
                                        f"'{sibling.object}' vs '{other.object}'"
                                    ),
                                    chain=chain,
                                )
                            )

    def _bfs_backward(
        self, start: str, by_object: dict[str, list[Claim]]
    ) -> set[str]:
        """BFS backward: find all entities that can reach 'start'."""
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(start, 0)])
        while queue:
            current, depth = queue.popleft()
            if depth >= self.max_chain_depth:
                continue
            for claim in by_object.get(current, []):
                prev = claim.subject
                if prev not in visited:
                    visited.add(prev)
                    queue.append((prev, depth + 1))
        return visited

    def _bfs_forward(
        self, start: str, by_subject: dict[str, list[Claim]]
    ) -> set[str]:
        """BFS forward: find all entities reachable from 'start'."""
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(start, 0)])
        while queue:
            current, depth = queue.popleft()
            if depth >= self.max_chain_depth:
                continue
            for claim in by_subject.get(current, []):
                next_node = claim.object
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, depth + 1))
        return visited

    def _find_path(
        self, start: str, target: str, by_subject: dict[str, list[Claim]]
    ) -> list[str] | None:
        """BFS to find a path from start to target through claim chains."""
        if start == target:
            return [start]
        queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
        visited: set[str] = {start}
        while queue:
            current, path = queue.popleft()
            if len(path) - 1 >= self.max_chain_depth:
                continue
            for claim in by_subject.get(current, []):
                next_node = claim.object
                if next_node == target:
                    return path + [next_node]
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_detector.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/contrachecker/detector.py tests/test_detector.py
git commit -m "feat: add ContradictionDetector with direct, indirect, bridge detection"
```

---

## Task 3: Pattern-Based Extractor (Zero Dependencies)

**Files:**
- Create: `src/contrachecker/extractors/base.py`
- Create: `src/contrachecker/extractors/pattern_extractor.py`
- Modify: `src/contrachecker/extractors/__init__.py`
- Create: `tests/test_pattern_extractor.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_pattern_extractor.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_pattern_extractor.py -v 2>&1 | head -10
```

Expected: FAIL

- [ ] **Step 3: Implement base extractor protocol**

```python
# src/contrachecker/extractors/base.py
"""Base interface for claim extractors."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import Chunk, Claim


@runtime_checkable
class ClaimExtractor(Protocol):
    """Protocol that all claim extractors must implement."""

    def extract(self, chunk: Chunk) -> list[Claim]:
        """Extract claims from a single text chunk."""
        ...

    def extract_many(self, chunks: list[Chunk]) -> list[Claim]:
        """Extract claims from multiple chunks."""
        ...
```

- [ ] **Step 4: Implement PatternExtractor**

```python
# src/contrachecker/extractors/pattern_extractor.py
"""Regex/pattern-based claim extractor. Zero external dependencies.

Handles common English sentence patterns to extract (subject, relation, object)
claims. Not as accurate as LLM-based extraction, but fast and free.
"""
from __future__ import annotations

import re

from ..models import Chunk, Claim

# Sentence-level patterns: (regex, relation_name, subject_group, object_group)
_PATTERNS: list[tuple[str, str, int, int]] = [
    # "X is a Y" / "X is an Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+is\s+an?\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "is_a", 1, 2),
    # "X is Y" (adjective/state)
    (r"(\b[A-Z][\w\s]{1,40}?)\s+is\s+((?:not\s+)?[\w\s]{2,30}?)(?:\.|,|;|$)", "is", 1, 2),
    # "X causes Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+causes?\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "causes", 1, 2),
    # "X contains Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+contains?\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "contains", 1, 2),
    # "X leads to Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+leads?\s+to\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "leads_to", 1, 2),
    # "X increases Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+increases?\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "increases", 1, 2),
    # "X decreases Y" / "X reduces Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+(?:decreases?|reduces?)\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "decreases", 1, 2),
    # "X prevents Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+prevents?\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "prevents", 1, 2),
    # "X does not prevent/cause Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+does\s+not\s+(\w+)\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "not_{verb}", 1, 3),
    # "X recommends Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+recommends?\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "recommends", 1, 2),
    # "X should be preferred over Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+should\s+be\s+preferred\s+over\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "preferred_over", 1, 2),
    # "X is more ADJ than Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+is\s+more\s+(\w+)\s+than\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "more_{adj}_than", 1, 3),
    # "X treats Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+treats?\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "treats", 1, 2),
    # "X requires Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+requires?\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "requires", 1, 2),
    # "X also contains Y" / "X also causes Y"
    (r"(\b[A-Z][\w\s]{1,40}?)\s+also\s+(\w+s?)\s+([\w\s]{2,40}?)(?:\.|,|;|$)", "{verb}", 1, 3),
]

_COMPILED = [
    (re.compile(pattern, re.IGNORECASE), rel, sg, og)
    for pattern, rel, sg, og in _PATTERNS
]


class PatternExtractor:
    """Extract claims from text using regex patterns.

    Fast, deterministic, zero-dependency extractor. Best for structured
    or semi-structured text with clear subject-verb-object patterns.
    """

    def extract(self, chunk: Chunk) -> list[Claim]:
        if not chunk.text.strip():
            return []

        claims: list[Claim] = []
        seen: set[tuple[str, str, str]] = set()

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", chunk.text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Capitalize first letter for pattern matching
            if sentence[0].islower():
                sentence = sentence[0].upper() + sentence[1:]

            for compiled, relation_template, subj_group, obj_group in _COMPILED:
                for match in compiled.finditer(sentence):
                    groups = match.groups()
                    subject = groups[subj_group - 1].strip()
                    obj = groups[obj_group - 1].strip()

                    # Build relation name from template
                    relation = relation_template
                    if "{verb}" in relation:
                        verb = groups[1].strip().lower().rstrip("s")
                        relation = verb
                    elif "{adj}" in relation:
                        adj = groups[1].strip().lower()
                        relation = relation.replace("{adj}", adj)
                    elif "not_{verb}" in relation:
                        verb = groups[1].strip().lower()
                        relation = f"not_{verb}"

                    key = (subject.lower(), relation.lower(), obj.lower())
                    if key not in seen:
                        seen.add(key)
                        claims.append(
                            Claim(
                                subject=subject,
                                relation=relation,
                                object=obj,
                                source_chunk_id=chunk.id,
                                confidence=0.7,  # Pattern-based = lower confidence
                            )
                        )

        return claims

    def extract_many(self, chunks: list[Chunk]) -> list[Claim]:
        claims: list[Claim] = []
        for chunk in chunks:
            claims.extend(self.extract(chunk))
        return claims
```

- [ ] **Step 5: Update extractors __init__**

```python
# src/contrachecker/extractors/__init__.py
"""Claim extraction backends."""
from .base import ClaimExtractor
from .pattern_extractor import PatternExtractor

__all__ = ["ClaimExtractor", "PatternExtractor"]
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
python -m pytest tests/test_pattern_extractor.py -v
```

Expected: All PASS (some pattern tests may need tuning — adjust patterns if needed)

- [ ] **Step 7: Commit**

```bash
git add src/contrachecker/extractors/ tests/test_pattern_extractor.py
git commit -m "feat: add pattern-based claim extractor (zero dependencies)"
```

---

## Task 4: LLM-Based Extractor

**Files:**
- Create: `src/contrachecker/extractors/llm_extractor.py`
- Create: `tests/test_llm_extractor.py`

- [ ] **Step 1: Write failing tests (mocked LLM calls)**

```python
# tests/test_llm_extractor.py
"""Tests for LLM-based claim extraction (mocked)."""
import json
import pytest
from unittest.mock import MagicMock, patch
from contrachecker.models import Chunk
from contrachecker.extractors.llm_extractor import LLMExtractor


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response with extracted claims."""
    return {
        "claims": [
            {"subject": "metformin", "relation": "is", "object": "first-line treatment for type 2 diabetes"},
            {"subject": "metformin", "relation": "reduces", "object": "blood glucose levels"},
        ]
    }


class TestLLMExtractor:
    def test_extract_parses_llm_response(self, mock_openai_response):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = json.dumps(mock_openai_response)
            extractor = LLMExtractor(api_key="test-key")
            chunk = Chunk(id="c1", text="Metformin is the first-line treatment for type 2 diabetes.")
            claims = extractor.extract(chunk)
            assert len(claims) == 2
            assert claims[0].subject == "metformin"
            assert claims[0].source_chunk_id == "c1"

    def test_extract_many_batches(self, mock_openai_response):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = json.dumps(mock_openai_response)
            extractor = LLMExtractor(api_key="test-key")
            chunks = [
                Chunk(id="c1", text="Text one."),
                Chunk(id="c2", text="Text two."),
            ]
            claims = extractor.extract_many(chunks)
            assert len(claims) == 4  # 2 per chunk
            assert mock_call.call_count == 2

    def test_handles_malformed_response(self):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = "not valid json {"
            extractor = LLMExtractor(api_key="test-key")
            chunk = Chunk(id="c1", text="Some text.")
            claims = extractor.extract(chunk)
            assert claims == []

    def test_handles_empty_claims_list(self):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = json.dumps({"claims": []})
            extractor = LLMExtractor(api_key="test-key")
            chunk = Chunk(id="c1", text="Some text.")
            claims = extractor.extract(chunk)
            assert claims == []

    def test_custom_model(self, mock_openai_response):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = json.dumps(mock_openai_response)
            extractor = LLMExtractor(api_key="test-key", model="gpt-4o-mini")
            chunk = Chunk(id="c1", text="Text.")
            extractor.extract(chunk)
            call_kwargs = mock_call.call_args
            assert "gpt-4o-mini" in str(call_kwargs)

    def test_prompt_contains_chunk_text(self, mock_openai_response):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = json.dumps(mock_openai_response)
            extractor = LLMExtractor(api_key="test-key")
            chunk = Chunk(id="c1", text="Aspirin prevents heart attacks.")
            extractor.extract(chunk)
            prompt_sent = str(mock_call.call_args)
            assert "Aspirin prevents heart attacks" in prompt_sent
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_llm_extractor.py -v 2>&1 | head -10
```

Expected: FAIL

- [ ] **Step 3: Implement LLMExtractor**

```python
# src/contrachecker/extractors/llm_extractor.py
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
{"claims": [{"subject": "...", "relation": "...", "object": "..."}]}

If no clear factual claims can be extracted, return: {"claims": []}

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

    More accurate than PatternExtractor but requires an API key and costs money.

    Args:
        api_key: OpenAI API key.
        model: Model name (default: gpt-4o-mini for cost efficiency).
        base_url: Optional base URL for OpenAI-compatible APIs.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str | None = None,
    ):
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
                    confidence=0.9,  # LLM-based = higher confidence
                )
            )
        return claims

    def extract_many(self, chunks: list[Chunk]) -> list[Claim]:
        claims: list[Claim] = []
        for chunk in chunks:
            claims.extend(self.extract(chunk))
        return claims
```

- [ ] **Step 4: Update extractors __init__**

Replace `src/contrachecker/extractors/__init__.py`:
```python
"""Claim extraction backends."""
from .base import ClaimExtractor
from .pattern_extractor import PatternExtractor

__all__ = ["ClaimExtractor", "PatternExtractor"]

try:
    from .llm_extractor import LLMExtractor
    __all__.append("LLMExtractor")
except ImportError:
    pass  # openai not installed
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/test_llm_extractor.py -v
```

Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add src/contrachecker/extractors/ tests/test_llm_extractor.py
git commit -m "feat: add LLM-based claim extractor (OpenAI-compatible)"
```

---

## Task 5: Public API & Package Init

**Files:**
- Modify: `src/contrachecker/__init__.py`
- Create: `tests/test_end_to_end.py`

- [ ] **Step 1: Write failing end-to-end tests**

```python
# tests/test_end_to_end.py
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
        # At minimum, pattern extractor should find the metformin contradiction
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_end_to_end.py -v 2>&1 | head -10
```

Expected: FAIL

- [ ] **Step 3: Implement public API**

```python
# src/contrachecker/__init__.py
"""contrachecker - Detect contradictions between retrieved documents in RAG pipelines.

Usage:
    from contrachecker import check_contradictions
    from contrachecker.models import Chunk

    chunks = [
        Chunk(id="doc1", text="Coffee is healthy."),
        Chunk(id="doc2", text="Coffee is harmful."),
    ]
    report = check_contradictions(chunks)
    print(report.summary())
"""
from __future__ import annotations

__version__ = "0.1.0"

from .models import Chunk, Claim, Contradiction, ContradictionReport
from .detector import ContradictionDetector
from .extractors.base import ClaimExtractor
from .extractors.pattern_extractor import PatternExtractor


def check_contradictions(
    chunks: list[Chunk],
    *,
    extractor: ClaimExtractor | None = None,
    max_chain_depth: int = 4,
    min_confidence: float = 0.0,
) -> ContradictionReport:
    """Analyze chunks for contradictions. Main entry point.

    Args:
        chunks: Text chunks from RAG retrieval.
        extractor: Claim extractor to use (default: PatternExtractor).
        max_chain_depth: Max BFS depth for indirect contradiction detection.
        min_confidence: Ignore claims below this confidence.

    Returns:
        ContradictionReport with all detected contradictions.
    """
    if extractor is None:
        extractor = PatternExtractor()

    claims = extractor.extract_many(chunks)

    detector = ContradictionDetector(
        max_chain_depth=max_chain_depth,
        min_confidence=min_confidence,
    )
    contradictions = detector.detect(claims)

    return ContradictionReport(
        chunks_analyzed=len(chunks),
        claims_extracted=len(claims),
        contradictions=contradictions,
    )


__all__ = [
    "check_contradictions",
    "ContradictionDetector",
    "Chunk",
    "Claim",
    "Contradiction",
    "ContradictionReport",
    "PatternExtractor",
    "ClaimExtractor",
    "__version__",
]
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/contrachecker/__init__.py tests/test_end_to_end.py
git commit -m "feat: add public API - check_contradictions() one-liner entry point"
```

---

## Task 6: LangChain Integration

**Files:**
- Create: `src/contrachecker/integrations/langchain.py`
- Modify: `src/contrachecker/integrations/__init__.py`
- Create: `tests/test_langchain_integration.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_langchain_integration.py
"""Tests for LangChain integration."""
import pytest

try:
    from langchain_core.documents import Document
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

pytestmark = pytest.mark.skipif(not HAS_LANGCHAIN, reason="langchain-core not installed")


class TestContradictionChecker:
    def test_transform_documents(self):
        from contrachecker.integrations.langchain import ContradictionCheckerTransformer

        transformer = ContradictionCheckerTransformer()
        docs = [
            Document(page_content="Coffee is healthy.", metadata={"source": "doc1"}),
            Document(page_content="Coffee is harmful.", metadata={"source": "doc2"}),
        ]
        result = transformer.transform_documents(docs)
        # Original docs + contradiction report doc appended
        assert len(result) >= len(docs)
        # Last document should contain the contradiction report
        report_doc = result[-1]
        assert "CONTRADICTION" in report_doc.page_content or report_doc.metadata.get("is_contradiction_report")

    def test_no_contradictions(self):
        from contrachecker.integrations.langchain import ContradictionCheckerTransformer

        transformer = ContradictionCheckerTransformer()
        docs = [
            Document(page_content="Water is essential.", metadata={"source": "doc1"}),
            Document(page_content="Exercise is beneficial.", metadata={"source": "doc2"}),
        ]
        result = transformer.transform_documents(docs)
        # When no contradictions, no report doc appended
        assert len(result) == 2

    def test_metadata_preserved(self):
        from contrachecker.integrations.langchain import ContradictionCheckerTransformer

        transformer = ContradictionCheckerTransformer()
        docs = [
            Document(page_content="Coffee is healthy.", metadata={"source": "doc1", "page": 1}),
            Document(page_content="Coffee is harmful.", metadata={"source": "doc2", "page": 5}),
        ]
        result = transformer.transform_documents(docs)
        # Original doc metadata is untouched
        assert result[0].metadata["page"] == 1

    def test_from_chunks_utility(self):
        from contrachecker.integrations.langchain import langchain_docs_to_chunks
        from contrachecker.models import Chunk

        docs = [
            Document(page_content="Hello world.", metadata={"id": "custom_id"}),
            Document(page_content="Another doc."),
        ]
        chunks = langchain_docs_to_chunks(docs)
        assert len(chunks) == 2
        assert isinstance(chunks[0], Chunk)
        assert chunks[0].text == "Hello world."
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_langchain_integration.py -v 2>&1 | head -10
```

Expected: FAIL (or skip if langchain not installed)

- [ ] **Step 3: Implement LangChain integration**

```python
# src/contrachecker/integrations/langchain.py
"""LangChain integration for contrachecker.

Provides a DocumentTransformer that appends contradiction reports
to retrieved documents before they reach the LLM.

Requires: pip install contrachecker[langchain]
"""
from __future__ import annotations

from typing import Any, Sequence
import hashlib

from langchain_core.documents import BaseDocumentTransformer, Document

from ..models import Chunk
from ..extractors.base import ClaimExtractor
from .. import check_contradictions


def langchain_docs_to_chunks(docs: Sequence[Document]) -> list[Chunk]:
    """Convert LangChain Documents to contrachecker Chunks."""
    chunks = []
    for i, doc in enumerate(docs):
        chunk_id = doc.metadata.get("id") or doc.metadata.get("source") or f"doc_{i}"
        chunks.append(
            Chunk(
                id=str(chunk_id),
                text=doc.page_content,
                metadata=dict(doc.metadata),
            )
        )
    return chunks


class ContradictionCheckerTransformer(BaseDocumentTransformer):
    """LangChain DocumentTransformer that detects contradictions.

    Use in a RAG pipeline between retrieval and LLM generation:

        retriever | ContradictionCheckerTransformer() | llm

    If contradictions are found, appends a report document to the list.
    """

    extractor: ClaimExtractor | None = None
    max_chain_depth: int = 4
    min_confidence: float = 0.0

    class Config:
        arbitrary_types_allowed = True

    def transform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> list[Document]:
        chunks = langchain_docs_to_chunks(documents)
        report = check_contradictions(
            chunks,
            extractor=self.extractor,
            max_chain_depth=self.max_chain_depth,
            min_confidence=self.min_confidence,
        )

        result = list(documents)

        if report.has_contradictions:
            report_doc = Document(
                page_content=report.as_prompt_context(),
                metadata={
                    "is_contradiction_report": True,
                    "contradiction_count": report.contradiction_count,
                    "source": "contrachecker",
                },
            )
            result.append(report_doc)

        return result
```

- [ ] **Step 4: Update integrations __init__**

```python
# src/contrachecker/integrations/__init__.py
"""Framework integrations for contrachecker."""

__all__: list[str] = []

try:
    from .langchain import ContradictionCheckerTransformer, langchain_docs_to_chunks
    __all__.extend(["ContradictionCheckerTransformer", "langchain_docs_to_chunks"])
except ImportError:
    pass  # langchain not installed
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/test_langchain_integration.py -v
```

Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add src/contrachecker/integrations/ tests/test_langchain_integration.py
git commit -m "feat: add LangChain DocumentTransformer integration"
```

---

## Task 7: Examples

**Files:**
- Create: `examples/quickstart.py`
- Create: `examples/langchain_rag.py`
- Create: `examples/medical_docs.py`

- [ ] **Step 1: Create quickstart example**

```python
# examples/quickstart.py
"""Minimal contrachecker usage example."""
from contrachecker import check_contradictions
from contrachecker.models import Chunk

# Simulate chunks retrieved from a RAG pipeline
chunks = [
    Chunk(
        id="guidelines_2019",
        text="Metformin is the first-line treatment for type 2 diabetes.",
        metadata={"source": "ADA Guidelines 2019"},
    ),
    Chunk(
        id="guidelines_2023",
        text="GLP-1 receptor agonists should be preferred over metformin in patients with cardiovascular risk.",
        metadata={"source": "ADA Guidelines 2023"},
    ),
    Chunk(
        id="review_2022",
        text="Metformin remains safe and effective for most patients with type 2 diabetes.",
        metadata={"source": "Cochrane Review 2022"},
    ),
]

# One line — that's it
report = check_contradictions(chunks)

print(report.summary())
print()

if report.has_contradictions:
    print("Contradictions found:")
    for c in report.contradictions:
        print(f"  [{c.type}] {c.explanation}")
    print()
    print("Prompt context for LLM:")
    print(report.as_prompt_context())
else:
    print("No contradictions detected.")
```

- [ ] **Step 2: Create LangChain example**

```python
# examples/langchain_rag.py
"""LangChain RAG pipeline with contradiction detection.

Requires: pip install contrachecker[langchain] openai
"""
from langchain_core.documents import Document
from contrachecker.integrations.langchain import ContradictionCheckerTransformer

# Simulated retrieval results
retrieved_docs = [
    Document(
        page_content="Remote work increases employee productivity by 13% according to Stanford research.",
        metadata={"source": "stanford_study_2023.pdf"},
    ),
    Document(
        page_content="Remote work decreases team productivity due to reduced collaboration.",
        metadata={"source": "microsoft_report_2024.pdf"},
    ),
    Document(
        page_content="Hybrid work models combine the benefits of both remote and office work.",
        metadata={"source": "mckinsey_analysis_2024.pdf"},
    ),
]

# Add contradiction detection to the pipeline
checker = ContradictionCheckerTransformer()
enriched_docs = checker.transform_documents(retrieved_docs)

print(f"Input: {len(retrieved_docs)} docs")
print(f"Output: {len(enriched_docs)} docs")
print()

for doc in enriched_docs:
    if doc.metadata.get("is_contradiction_report"):
        print("=== CONTRADICTION REPORT ===")
        print(doc.page_content)
    else:
        print(f"[{doc.metadata.get('source', 'unknown')}]")
        print(f"  {doc.page_content[:80]}...")
```

- [ ] **Step 3: Create medical docs example**

```python
# examples/medical_docs.py
"""Medical document contradiction detection example.

Demonstrates how contrachecker catches conflicts between clinical guidelines,
research papers, and drug databases.
"""
from contrachecker import check_contradictions
from contrachecker.models import Chunk, Claim
from contrachecker.detector import ContradictionDetector

# Scenario: Direct claims from different medical sources
# (In production, these would come from an LLM extractor processing PDF chunks)
claims = [
    # Source 1: 2019 guidelines
    Claim(subject="metformin", relation="recommended_as", object="first_line_therapy",
          source_chunk_id="ada_2019", confidence=0.95,
          metadata={"year": 2019, "type": "guideline"}),

    # Source 2: 2023 guidelines (updated recommendation)
    Claim(subject="metformin", relation="recommended_as", object="second_line_for_cv_risk",
          source_chunk_id="ada_2023", confidence=0.95,
          metadata={"year": 2023, "type": "guideline"}),

    # Source 3: Drug interaction database
    Claim(subject="metformin", relation="contraindicated_with", object="contrast_dye",
          source_chunk_id="drug_db", confidence=0.9),

    # Source 4: Recent study challenges the contraindication
    Claim(subject="metformin", relation="safe_with", object="contrast_dye",
          source_chunk_id="nejm_2024", confidence=0.85,
          metadata={"year": 2024, "type": "rct"}),

    # Indirect chain: metformin -> lactic acidosis risk -> kidney patients
    Claim(subject="metformin", relation="risk", object="lactic_acidosis",
          source_chunk_id="fda_label", confidence=0.9),
    Claim(subject="lactic_acidosis", relation="dangerous_for", object="kidney_patients",
          source_chunk_id="fda_label", confidence=0.95),
    Claim(subject="metformin", relation="safe_for", object="kidney_patients",
          source_chunk_id="kdigo_2023", confidence=0.8,
          metadata={"year": 2023, "note": "updated: safe if eGFR > 30"}),
]

# Detect contradictions
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
```

- [ ] **Step 4: Commit**

```bash
git add examples/
git commit -m "feat: add usage examples (quickstart, langchain, medical)"
```

---

## Task 8: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README**

```markdown
# contrachecker

**Catch contradictions between documents before your LLM blindly trusts them.**

contrachecker is a lightweight Python library that detects contradictions between retrieved document chunks in RAG (Retrieval-Augmented Generation) pipelines. It sits between your retriever and your LLM, ensuring the model knows when its sources disagree.

```python
from contrachecker import check_contradictions
from contrachecker.models import Chunk

report = check_contradictions([
    Chunk(id="2019", text="Metformin is the first-line treatment for type 2 diabetes."),
    Chunk(id="2023", text="GLP-1 agonists should be preferred over metformin for cardiovascular risk patients."),
])

print(report.summary())
# Analyzed 2 chunks, extracted 4 claims, found 1 contradiction.

print(report.as_prompt_context())
# [CONTRADICTION REPORT]
# CONTRADICTION 1 (direct, confidence=70%): 'metformin is first-line treatment' CONFLICTS WITH ...
```

## Why?

RAG pipelines retrieve the top-K most relevant chunks and feed them to an LLM. But **relevant doesn't mean consistent**. When your retriever pulls in a 2019 guideline and a 2023 update that contradicts it, the LLM has no way to know — it treats both as equally true.

contrachecker solves this by detecting three types of contradictions:

| Type | Example | How it's found |
|------|---------|---------------|
| **Direct** | Doc A says "Drug X is safe", Doc B says "Drug X is unsafe" | Same subject + relation, different conclusion |
| **Indirect** | "Coffee contains caffeine" + "Caffeine disrupts sleep" contradicts "Coffee promotes sleep" | BFS chain traversal finds transitive conflicts |
| **Bridge** | Adding "Coffee contains caffeine" reveals a hidden conflict between existing "Coffee is healthy" and "Caffeine is harmful" | New claim connects previously unrelated contradictions |

## Install

```bash
pip install contrachecker                  # Core (pattern-based extraction)
pip install contrachecker[llm]             # + OpenAI-based extraction
pip install contrachecker[langchain]       # + LangChain integration
pip install contrachecker[all]             # Everything
```

## Quick Start

### Standalone

```python
from contrachecker import check_contradictions
from contrachecker.models import Chunk

chunks = [
    Chunk(id="doc1", text="Remote work increases productivity by 13%."),
    Chunk(id="doc2", text="Remote work decreases team productivity."),
]

report = check_contradictions(chunks)

if report.has_contradictions:
    for c in report.contradictions:
        print(f"[{c.type}] {c.explanation}")
```

### With LangChain

```python
from langchain_core.documents import Document
from contrachecker.integrations.langchain import ContradictionCheckerTransformer

docs = [...]  # your retrieved documents
checker = ContradictionCheckerTransformer()
enriched_docs = checker.transform_documents(docs)
# Pass enriched_docs to your LLM — contradiction report is appended automatically
```

### With Pre-Extracted Claims

If you already have structured claims (from your own NLP pipeline, a knowledge graph, etc.):

```python
from contrachecker.models import Claim
from contrachecker.detector import ContradictionDetector

claims = [
    Claim(subject="metformin", relation="status", object="first_line", source_chunk_id="doc1"),
    Claim(subject="metformin", relation="status", object="second_line", source_chunk_id="doc2"),
]

detector = ContradictionDetector(max_chain_depth=4)
contradictions = detector.detect(claims)
```

### LLM-Powered Extraction

For higher accuracy claim extraction (requires OpenAI API key):

```python
from contrachecker import check_contradictions
from contrachecker.extractors import LLMExtractor

extractor = LLMExtractor(api_key="sk-...")
report = check_contradictions(chunks, extractor=extractor)
```

## How It Works

```
Retrieved Chunks ──────────────────────────────────────────────┐
                                                               │
  ┌──────────────────────────────────────────────────────────┐ │
  │                     contrachecker                        │ │
  │                                                          │ │
  │  1. EXTRACT CLAIMS                                       │ │
  │     Chunk text → (subject, relation, object) triples     │ │
  │     Extractors: PatternExtractor | LLMExtractor | Custom │ │
  │                                                          │ │
  │  2. BUILD CLAIM GRAPH                                    │ │
  │     Index claims by subject, object, relation            │ │
  │                                                          │ │
  │  3. DETECT CONTRADICTIONS                                │ │
  │     ├── Direct: same topic, different conclusion         │ │
  │     ├── Indirect: BFS finds transitive conflicts         │ │
  │     └── Bridge: new claim reveals hidden conflicts       │ │
  │                                                          │ │
  │  4. GENERATE REPORT                                      │ │
  │     ContradictionReport with confidence scores           │ │
  │     .as_prompt_context() for LLM injection               │ │
  └──────────────────────────────────────────────────────────┘ │
                                                               │
  Enriched Chunks + Contradiction Report ──────────────── LLM  │
```

## Claim Extractors

| Extractor | Accuracy | Speed | Cost | Dependencies |
|-----------|----------|-------|------|--------------|
| `PatternExtractor` | Medium | Fast | Free | None |
| `LLMExtractor` | High | Slow | ~$0.001/chunk | `openai` |
| Custom | Your choice | Your choice | Your choice | Implement `ClaimExtractor` protocol |

### Custom Extractor

```python
from contrachecker.models import Chunk, Claim
from contrachecker.extractors.base import ClaimExtractor

class MyExtractor:
    def extract(self, chunk: Chunk) -> list[Claim]:
        # Your extraction logic here
        ...

    def extract_many(self, chunks: list[Chunk]) -> list[Claim]:
        return [claim for chunk in chunks for claim in self.extract(chunk)]
```

## Use Cases

- **Medical/Pharma**: Detect when clinical guidelines, drug databases, and research papers contradict each other
- **Legal**: Find conflicting precedents or regulatory interpretations across retrieved case law
- **Finance**: Catch inconsistent analyst recommendations or conflicting market data
- **Enterprise Knowledge**: Surface contradictions in internal documentation, policies, and SOPs
- **Journalism/Research**: Fact-check across multiple sources before generating summaries

## API Reference

### `check_contradictions(chunks, *, extractor=None, max_chain_depth=4, min_confidence=0.0)`

Main entry point. Extracts claims from chunks and detects contradictions.

**Parameters:**
- `chunks`: List of `Chunk` objects
- `extractor`: `ClaimExtractor` instance (default: `PatternExtractor`)
- `max_chain_depth`: Max BFS depth for indirect detection (default: 4)
- `min_confidence`: Ignore claims below this threshold (default: 0.0)

**Returns:** `ContradictionReport`

### `ContradictionReport`

- `.has_contradictions` → `bool`
- `.contradiction_count` → `int`
- `.contradictions` → `list[Contradiction]`
- `.summary()` → human-readable string
- `.as_prompt_context()` → text for LLM prompt injection

### `Contradiction`

- `.type` → `"direct" | "indirect" | "bridge"`
- `.claim_a`, `.claim_b` → the conflicting `Claim` objects
- `.confidence` → `float` (0-1)
- `.explanation` → human-readable description
- `.chain` → `list[str]` (for indirect/bridge: the connecting entities)

## Origin

contrachecker evolved from [ChainOfMeaning](https://github.com/barisgenc/contrachecker), a symbolic reasoning engine I built exploring how to represent and reason about knowledge outside of neural networks. After iterating through 4 engine versions — from basic LSTM-inspired gates to a 1M-rule SQLite-backed inference system — the most valuable discovery wasn't the engine itself, but the **contradiction detection algorithms**: direct conflict detection, transitive chain analysis, and bridge contradiction discovery.

This library extracts that core value and puts it where it's most useful: between your RAG retriever and your LLM, catching the conflicts that language models can't see.

## Author

**Baris Genc** — CS MSc, NLP researcher since 2013 (pre-word2vec era).

- Web: [gencbaris.com](https://gencbaris.com)
- Email: [info@gencbaris.com](mailto:info@gencbaris.com)

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README with examples, API reference, architecture"
```

---

## Task 9: Final Integration & Cleanup

**Files:**
- Remove: `chainofmeaning-claude-code-prompt.md` (old prompt file, not part of library)
- Verify all tests pass

- [ ] **Step 1: Clean up leftover files**

```bash
# Move the old prompt file to legacy
mv chainofmeaning-claude-code-prompt.md legacy/ 2>/dev/null || true
# Remove old rules directory if empty
rm -rf rules/ 2>/dev/null || true
# Remove old expected/tools/reports directories if still around
rm -rf expected/ tools/ reports/ 2>/dev/null || true
```

- [ ] **Step 2: Run full test suite**

```bash
python -m pytest tests/ -v --tb=short
```

Expected: All tests PASS

- [ ] **Step 3: Test pip install in dev mode**

```bash
pip install -e ".[dev,all]"
python -c "from contrachecker import check_contradictions; print('Import OK')"
python -c "from contrachecker.models import Chunk, Claim; print('Models OK')"
python -c "from contrachecker.integrations.langchain import ContradictionCheckerTransformer; print('LangChain OK')"
python examples/quickstart.py
```

Expected: All OK, quickstart prints contradiction report

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "chore: final cleanup - remove legacy artifacts, verify all tests pass"
```

---

## Post-Plan Self-Review

**Spec coverage:**
- [x] Core contradiction detection (direct, indirect, bridge)
- [x] Pattern-based extractor (zero-dep)
- [x] LLM-based extractor (OpenAI)
- [x] LangChain integration
- [x] Public API (`check_contradictions()` one-liner)
- [x] Tests for every component
- [x] README with author info, gencbaris.com, info@gencbaris.com
- [x] Examples (quickstart, langchain, medical)
- [x] Legacy code preserved
- [x] pip-installable package

**Placeholder scan:** No TBDs, TODOs, or "implement later" found.

**Type consistency:** `Claim`, `Chunk`, `Contradiction`, `ContradictionReport`, `ContradictionDetector`, `PatternExtractor`, `LLMExtractor`, `ClaimExtractor`, `ContradictionCheckerTransformer` — all consistent across tasks.
