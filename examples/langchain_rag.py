"""LangChain RAG pipeline with contradiction detection.

Requires: pip install contrachecker[langchain]
"""
from langchain_core.documents import Document
from contrachecker.integrations.langchain import ContradictionCheckerTransformer

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
