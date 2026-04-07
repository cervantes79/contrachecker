I just open-sourced contrachecker — a Python library that catches contradictions between documents before your LLM blindly trusts them.

Here's the problem: RAG pipelines retrieve the most relevant chunks and feed them to an LLM. But relevant doesn't mean consistent. When your retriever pulls a 2019 guideline and a 2023 update that contradicts it, the LLM has no way to know — it treats both as equally true.

contrachecker sits between your retriever and your LLM, detecting three types of contradictions:

- Direct: "Drug X is safe" vs "Drug X is unsafe"
- Indirect: "Coffee contains caffeine" + "Caffeine disrupts sleep" contradicts "Coffee promotes sleep"
- Bridge: A new fact connects two previously unrelated conflicting claims

It's a one-liner:

from contrachecker import check_contradictions

report = check_contradictions(chunks)
print(report.as_prompt_context())
# Injects contradiction warnings into your LLM prompt

The backstory: I've been working on semantic NLP since 2013 — before word2vec was even published. My MSc thesis explored word co-occurrence patterns for question answering. Over the past years, I built a symbolic reasoning engine called ChainOfMeaning, iterating through 4 versions — from LSTM-inspired gates to a million-rule SQLite-backed inference system.

The engine itself wasn't the breakthrough. The contradiction detection algorithms were. So I extracted that core value and put it where it's most useful: inside RAG pipelines.

Who needs this: Anyone building RAG systems for medical, legal, financial, or enterprise knowledge — domains where contradictory sources can lead to dangerous answers.

- LangChain integration included
- Zero-dependency pattern extractor + OpenAI-powered extractor
- 61 tests, MIT licensed

pip install contrachecker

GitHub: https://github.com/cervantes79/contrachecker
PyPI: https://pypi.org/project/contrachecker/

I'd love feedback — especially from anyone dealing with contradictory retrieval results in production.

#RAG #LLM #NLP #Python #OpenSource #AI
