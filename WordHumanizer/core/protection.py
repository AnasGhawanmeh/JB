"""Protection engine: finds text that must never be modified.

Protected spans are used in two ways:

* LanguageTool matches that overlap a protected span are discarded.
* Before AI rewriting, protected spans are replaced by opaque placeholders
  (``⟦P0⟧``, ``⟦P1⟧`` ...) and restored afterwards; a rewrite that loses,
  duplicates or invents a placeholder is rejected.
"""

import re
from collections import Counter
from dataclasses import dataclass

from core.citation_detector import find_citations

DEFAULT_PROTECTED_TERMS = [
    "LEAP", "SimaPro", "CO2", "CO₂", "CH4", "CH₄", "N2O", "N₂O", "BC", "LCA", "GIS",
    "WHO", "UNFCCC", "IPCC", "GHG", "PM2.5", "PM10", "NOx", "SO2", "GWP",
]

URL_RE = re.compile(r"\b(?:https?://|ftp://|www\.)[^\s<>\"'()\[\]{}]+(?:\([^\s()]*\))?[^\s<>\"'()\[\]{}.,;:!?]*")
DOI_RE = re.compile(r"\b(?:doi:\s*)?10\.\d{4,9}/[^\s\"<>]+[^\s\"<>.,;:)\]]", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")

_UNITS = (
    r"%|‰|°C|°F|°|K|kg|g|mg|µg|μg|t|tonnes?|tons?|Mt|Gt|kt|km|m|cm|mm|µm|μm|nm|km2|km²|m2|m²|m3|m³|"
    r"ha|L|l|mL|ml|kWh|MWh|GWh|TWh|Wh|kW|MW|GW|W|kV|V|A|Hz|kHz|MHz|GHz|J|kJ|MJ|GJ|TJ|PJ|"
    r"ppm|ppb|ppt|mol|mmol|s|sec|min|h|hr|hrs|yr|yrs|years?|days?|months?|vehicles?|"
    r"USD|JOD|EUR|\$|€|£|km/h|m/s|g/km|kg/km|tCO2e?|tCO₂e?|kgCO2e?|kgCO₂e?|µg/m3|µg/m³|μg/m3|μg/m³|mg/m3|mg/m³"
)
NUMBER_RE = re.compile(
    r"(?<![\w.])[-+−]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
    r"(?:\s*(?:×|x|\*)\s*10\s*\^?\s*[-−]?\d+)?"
    r"(?:\s*(?:" + _UNITS + r")(?![A-Za-z]))?"
)
NUMERIC_VALUE_RE = re.compile(r"\d+(?:[.,]\d+)*")

# Acronyms (WHO, UNFCCC, LCAs), chemical formulas (CO2, CH4, PM2.5) and
# camel-case product names (SimaPro, iPhone).
ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,}(?:[.\-][A-Z0-9]+)*s?\b")
FORMULA_RE = re.compile(r"\b(?=[A-Za-z0-9.₀-₉]*[0-9₀-₉])(?:[A-Z][a-z]?[0-9₀-₉.]*){1,}[a-z]?\b")
CAMEL_RE = re.compile(r"\b[a-z]+[A-Z][A-Za-z0-9]*\b|\b[A-Z][a-z]+[A-Z][A-Za-z0-9]*\b")
EQUATION_RE = re.compile(
    r"(?:[A-Za-zα-ωΑ-Ω0-9_₀-₉()\[\]]+\s*)(?:=|≈|≤|≥|≠|∝)\s*[^.;:\n]*?(?=[.;:\n]\s|[.;:]?$)"
)

PLACEHOLDER_RE = re.compile(r"⟦P(\d+)⟧")


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    kind: str

    def overlaps(self, start, end):
        if start == end:  # insertion: protected if strictly inside
            return self.start < start < self.end
        return start < self.end and end > self.start


class ProtectionEngine:

    def __init__(self, options):
        self.options = options
        terms = list(options.protected_terms)
        if options.protect_terms:
            terms += DEFAULT_PROTECTED_TERMS
        self.terms = sorted(set(terms), key=len, reverse=True)
        self._term_re = (
            re.compile(r"(?<![\w])(?:" + "|".join(re.escape(t) for t in self.terms) + r")(?![\w])")
            if self.terms else None
        )

    # ------------------------------------------------------------------ spans
    def find_spans(self, text, extra_spans=()):
        o = self.options
        spans = list(extra_spans)
        if o.protect_citations:
            spans += [Span(s, e, "citation") for s, e in find_citations(text)]
        if o.protect_urls:
            spans += [Span(m.start(), m.end(), "url") for m in URL_RE.finditer(text)]
            spans += [Span(m.start(), m.end(), "doi") for m in DOI_RE.finditer(text)]
            spans += [Span(m.start(), m.end(), "email") for m in EMAIL_RE.finditer(text)]
        if o.protect_numbers:
            spans += [Span(m.start(), m.end(), "number") for m in NUMBER_RE.finditer(text)
                      if any(c.isdigit() for c in m.group())]
        if o.protect_equations:
            spans += [Span(m.start(), m.end(), "equation") for m in EQUATION_RE.finditer(text)
                      if m.end() - m.start() >= 3]
        if self._term_re is not None:
            spans += [Span(m.start(), m.end(), "term") for m in self._term_re.finditer(text)]
        if o.auto_detect_terms:
            for pattern in (ACRONYM_RE, FORMULA_RE, CAMEL_RE):
                spans += [Span(m.start(), m.end(), "term") for m in pattern.finditer(text)
                          if len(m.group()) > 1]
        return merge_spans(spans)

    # ---------------------------------------------------------------- masking
    @staticmethod
    def mask(text, spans):
        """Replace spans by placeholders. Returns (masked_text, {placeholder: original})."""
        mapping = {}
        parts = []
        last = 0
        for span in sorted(spans, key=lambda s: s.start):
            if span.end <= span.start:
                continue
            key = f"⟦P{len(mapping)}⟧"
            mapping[key] = text[span.start:span.end]
            parts.append(text[last:span.start])
            parts.append(key)
            last = span.end
        parts.append(text[last:])
        return "".join(parts), mapping

    @staticmethod
    def unmask(text, mapping):
        """Restore placeholders. Returns (text, problems)."""
        problems = []
        found = Counter(f"⟦P{n}⟧" for n in PLACEHOLDER_RE.findall(text))
        for key in mapping:
            if found[key] == 0:
                problems.append(f"protected content lost: {mapping[key]!r}")
            elif found[key] > 1:
                problems.append(f"protected content duplicated: {mapping[key]!r}")
        for key in found:
            if key not in mapping:
                problems.append(f"unknown placeholder {key}")
        restored = PLACEHOLDER_RE.sub(lambda m: mapping.get(m.group(0), m.group(0)), text)
        return restored, problems

    # ------------------------------------------------------------- inventory
    def inventory(self, text):
        """Counts of protected items, used for validation and the report."""
        return {
            "citations": Counter(re.sub(r"\s+", " ", text[s:e]) for s, e in find_citations(text)),
            "urls": Counter(m.group() for m in URL_RE.finditer(text))
                    + Counter(m.group() for m in DOI_RE.finditer(text))
                    + Counter(m.group() for m in EMAIL_RE.finditer(text)),
            "numbers": Counter(normalize_number(m.group()) for m in NUMERIC_VALUE_RE.finditer(text)),
            "terms": Counter(m.group() for m in self._term_re.finditer(text)) if self._term_re else Counter(),
        }


def normalize_number(value):
    return value.replace(",", "")


def merge_spans(spans):
    """Merge overlapping/adjacent spans; the kind of the first span wins."""
    ordered = sorted((s for s in spans if s.end > s.start), key=lambda s: (s.start, -s.end))
    merged = []
    for span in ordered:
        if merged and span.start < merged[-1].end:
            last = merged[-1]
            if span.end > last.end:
                merged[-1] = Span(last.start, span.end, last.kind)
        else:
            merged.append(span)
    return merged


def overlaps_any(spans, start, end):
    return any(s.overlaps(start, end) for s in spans)
