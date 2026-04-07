"""Minimal contrachecker usage example."""
from contrachecker import check_contradictions
from contrachecker.models import Chunk

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
