"""Small text helpers shared across the engine."""

import re

_ABBREVIATIONS = {
    "e.g", "i.e", "etc", "et al", "al", "fig", "figs", "eq", "eqs", "no", "vol", "pp", "p",
    "dr", "mr", "mrs", "ms", "prof", "vs", "approx", "ca", "cf", "resp", "dept", "univ",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
    "inc", "ltd", "co", "corp", "st", "u.s", "u.k",
}

_SENTENCE_END = re.compile(r"[.!?]+[\"')\]]*\s+")


def utf16_offset_map(text):
    """Map UTF-16 code-unit offsets (LanguageTool/Java) to Python str indices.

    Returns a list where ``result[utf16_offset] == python_index``. Offsets that fall
    inside a surrogate pair map to the index of that character.
    """
    mapping = []
    for index, char in enumerate(text):
        units = 2 if ord(char) > 0xFFFF else 1
        mapping.extend([index] * units)
    mapping.append(len(text))
    return mapping


def needs_utf16_mapping(text):
    return any(ord(c) > 0xFFFF for c in text)


def sentence_spans(text):
    """Return (start, end) spans of sentences; spans cover the whole text."""
    spans = []
    start = 0
    for match in _SENTENCE_END.finditer(text):
        end = match.end()
        before = text[start:match.start() + 1].rstrip(".!?")
        last_word = re.split(r"\s+", before.strip())[-1].lower() if before.strip() else ""
        if last_word.rstrip(".") in _ABBREVIATIONS or re.fullmatch(r"[a-z]", last_word):
            continue
        # Don't split before a lowercase continuation ("approx. five").
        if end < len(text) and text[end].islower():
            continue
        spans.append((start, end))
        start = end
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def letter_ratio(text):
    stripped = re.sub(r"\s", "", text)
    if not stripped:
        return 0.0
    return sum(c.isalpha() for c in stripped) / len(stripped)


def word_count(text):
    return len(re.findall(r"\w+", text))


def snippet(text, start, end, context=30):
    left = max(0, start - context)
    right = min(len(text), end + context)
    prefix = "…" if left > 0 else ""
    suffix = "…" if right < len(text) else ""
    return prefix + text[left:right].replace("\n", " ") + suffix
