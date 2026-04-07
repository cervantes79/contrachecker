"""Pattern-based claim extractor using compiled regex patterns."""
from __future__ import annotations

import re

from ..models import Chunk, Claim

# ---------------------------------------------------------------------------
# Sentence splitter — split on . ! ? followed by whitespace or end-of-string,
# but keep the delimiter attached to the preceding token so we don't lose it.
# ---------------------------------------------------------------------------
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

# ---------------------------------------------------------------------------
# Compiled patterns — each entry is (relation_label, compiled_pattern).
# Groups MUST be named:  (?P<subj>...)  and  (?P<obj>...)
# Patterns are ordered from most specific to least specific so that more
# precise matches are tried first.
# ---------------------------------------------------------------------------

# Reusable fragments
_NP = r"[A-Za-z][A-Za-z0-9 \-]+"   # simple noun-phrase (no punctuation)

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # "X does not VERB Y"  →  not_VERB
    (
        "not_{verb}",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+does\s+not\s+(?P<verb>[a-z]+)\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X is more ADJ than Y"  →  more_ADJ_than
    (
        "more_{adj}_than",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+is\s+more\s+(?P<adj>[a-z]+)\s+than\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X should be preferred over Y"  →  preferred_over
    (
        "preferred_over",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+should\s+be\s+preferred\s+over\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X leads to Y"  →  leads_to
    (
        "leads_to",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+leads?\s+to\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X is associated with Y"  →  associated_with
    (
        "associated_with",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+is\s+associated\s+with\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X is a/an/the Y"  →  is_a  (must come AFTER more-specific "is" patterns)
    (
        "is_a",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+is\s+(?:an?\s+|the\s+)(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X is ADJ"  →  is_property  (bare predicate adjective, e.g. "Coffee is healthy")
    # Must come AFTER all other "is" patterns to avoid shadowing them.
    # Excludes articles (a, an, the) which are handled by is_a.
    (
        "is_property",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+is\s+(?P<obj>(?!(?:a|an|the)\b)[a-z][a-z\-]+)(?:[.!?,;:\s]|$)",
            re.IGNORECASE,
        ),
    ),
    # "X causes Y"
    (
        "causes",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+causes?\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X contains Y"
    (
        "contains",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+contains?\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X increases Y"
    (
        "increases",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+increases?\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X decreases Y"
    (
        "decreases",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+decreases?\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X recommends Y"
    (
        "recommends",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+recommends?\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X prevents Y"
    (
        "prevents",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+prevents?\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X treats Y"
    (
        "treats",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+treats?\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X requires Y"
    (
        "requires",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+requires?\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
    # "X also VERB Y"  — generic "also" pattern; relation = the verb
    (
        "{verb}",
        re.compile(
            r"(?P<subj>" + _NP + r")\s+also\s+(?P<verb>[a-z]+s?)\s+(?P<obj>" + _NP + r")",
            re.IGNORECASE,
        ),
    ),
]

# Punct that should be stripped from the end of a captured noun-phrase
_TRAILING_PUNCT = re.compile(r"[\s.!?,;:]+$")


def _strip(s: str) -> str:
    return _TRAILING_PUNCT.sub("", s).strip()


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    raw = _SENT_SPLIT.split(text.strip())
    return [s.strip() for s in raw if s.strip()]


class PatternExtractor:
    """Zero-dependency regex-based claim extractor.

    Confidence is fixed at 0.7 (pattern matching is less reliable than LLM).
    """

    CONFIDENCE: float = 0.7

    def extract(self, chunk: Chunk) -> list[Claim]:
        """Extract claims from a single Chunk."""
        if not chunk.text.strip():
            return []

        seen: set[tuple[str, str, str]] = set()
        claims: list[Claim] = []

        for sentence in _split_sentences(chunk.text):
            for label_template, pattern in _PATTERNS:
                m = pattern.search(sentence)
                if m is None:
                    continue

                gd = m.groupdict()
                subj = _strip(gd["subj"])
                obj = _strip(gd["obj"])

                # Build the relation label, filling in any named captures
                if label_template == "not_{verb}":
                    relation = f"not_{gd['verb'].lower()}"
                elif label_template == "more_{adj}_than":
                    relation = f"more_{gd['adj'].lower()}_than"
                elif label_template == "{verb}":
                    relation = gd["verb"].lower()
                else:
                    relation = label_template

                if not subj or not obj:
                    continue

                key = (subj.lower(), relation.lower(), obj.lower())
                if key in seen:
                    continue
                seen.add(key)

                claims.append(
                    Claim(
                        subject=subj,
                        relation=relation,
                        object=obj,
                        source_chunk_id=chunk.id,
                        confidence=self.CONFIDENCE,
                    )
                )

        return claims

    def extract_many(self, chunks: list[Chunk]) -> list[Claim]:
        """Extract claims from multiple Chunks."""
        result: list[Claim] = []
        for chunk in chunks:
            result.extend(self.extract(chunk))
        return result
