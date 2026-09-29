"""Detection of in-text citations (author-year, numeric and narrative styles)."""

import re

_YEAR = r"(?:1[6-9]|20)\d{2}[a-z]?|n\.d\.|in press|forthcoming"
_NAME = r"[A-Z][\w'’\-]+(?:\s+(?:van|von|de|der|da|del|di|le|la)\s+[A-Z][\w'’\-]+)?"

CITATION_PATTERNS = [
    # (Smith, 2020) (Smith et al., 2020; Jones & Lee, 2019a) (see WHO, 2021, p. 4)
    re.compile(r"\((?=[^()]*?\b(?:" + _YEAR + r")\b)[^()]{2,300}\)"),
    # [1] [2, 5] [3-7] [1–3, 9]
    re.compile(r"\[\s*\d+(?:\s*[,–—-]\s*\d+)*\s*\]"),
    # Smith et al. (2020) / Smith and Jones (2019) / Smith & Lee (2019, p. 7)
    re.compile(
        r"\b" + _NAME + r"(?:\s+et\s+al\.?|\s+(?:and|&)\s+" + _NAME + r")?\s+\((?:" + _YEAR
        + r")(?:[,;][^()]{0,40})?\)"
    ),
]

_CITATION_COMPACT = re.compile(r"\s+")


def find_citations(text):
    """Return a list of (start, end) spans of citations, merged and sorted."""
    spans = []
    for pattern in CITATION_PATTERNS:
        spans.extend((m.start(), m.end()) for m in pattern.finditer(text))
    spans.sort()
    merged = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def citation_strings(text):
    return [_CITATION_COMPACT.sub(" ", text[s:e]) for s, e in find_citations(text)]


def protect_citations(text):
    """Replace citations with placeholders. Returns (protected_text, mapping)."""
    citations = {}
    parts = []
    last = 0
    for start, end in find_citations(text):
        key = f"__CITATION_{len(citations)}__"
        citations[key] = text[start:end]
        parts.append(text[last:start])
        parts.append(key)
        last = end
    parts.append(text[last:])
    return "".join(parts), citations


def restore_citations(text, citations):
    for key, value in citations.items():
        text = text.replace(key, value)
    return text
