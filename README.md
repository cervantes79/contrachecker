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

RAG pipelines retrieve the top-K most relevant chunks and feed them to an LLM. But **relevant doesn't mean consistent**. When your retriever pulls in a 2019 guideline and a 2023 update that contradicts it, the LLM has no way to know -- it treats both as equally true.

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
# Pass enriched_docs to your LLM -- contradiction report is appended automatically
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
Retrieved Chunks -----------------------------------------------+
                                                                |
  +-----------------------------------------------------------+ |
  |                     contrachecker                          | |
  |                                                            | |
  |  1. EXTRACT CLAIMS                                         | |
  |     Chunk text -> (subject, relation, object) triples      | |
  |     Extractors: PatternExtractor | LLMExtractor | Custom   | |
  |                                                            | |
  |  2. BUILD CLAIM GRAPH                                      | |
  |     Index claims by subject, object, relation              | |
  |                                                            | |
  |  3. DETECT CONTRADICTIONS                                  | |
  |     +-- Direct: same topic, different conclusion           | |
  |     +-- Indirect: BFS finds transitive conflicts           | |
  |     +-- Bridge: new claim reveals hidden conflicts         | |
  |                                                            | |
  |  4. GENERATE REPORT                                        | |
  |     ContradictionReport with confidence scores             | |
  |     .as_prompt_context() for LLM injection                 | |
  +-----------------------------------------------------------+ |
                                                                |
  Enriched Chunks + Contradiction Report ----------------> LLM  |
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

- `.has_contradictions` -> `bool`
- `.contradiction_count` -> `int`
- `.contradictions` -> `list[Contradiction]`
- `.summary()` -> human-readable string
- `.as_prompt_context()` -> text for LLM prompt injection

### `Contradiction`

- `.type` -> `"direct" | "indirect" | "bridge"`
- `.claim_a`, `.claim_b` -> the conflicting `Claim` objects
- `.confidence` -> `float` (0-1)
- `.explanation` -> human-readable description
- `.chain` -> `list[str]` (for indirect/bridge: the connecting entities)

## Origin

contrachecker evolved from ChainOfMeaning, a symbolic reasoning engine I built exploring how to represent and reason about knowledge outside of neural networks. After iterating through 4 engine versions -- from basic LSTM-inspired gates to a 1M-rule SQLite-backed inference system -- the most valuable discovery wasn't the engine itself, but the **contradiction detection algorithms**: direct conflict detection, transitive chain analysis, and bridge contradiction discovery.

This library extracts that core value and puts it where it's most useful: between your RAG retriever and your LLM, catching the conflicts that language models can't see.

## Author

**Baris Genc** -- CS MSc, NLP researcher since 2013 (pre-word2vec era).

- Web: [gencbaris.com](https://gencbaris.com)
- Email: [info@gencbaris.com](mailto:info@gencbaris.com)

## License

MIT
