"""Deciding which LanguageTool suggestions to accept, per paragraph."""

import re

from core.document_reader import paragraph_segments, paragraph_text
from core.document_writer import Edit, apply_edits, write_segments
from core.protection import Span, overlaps_any
from core.structure_manager import Kind, Location

# Rules that are noisy on documents extracted from Word.
IGNORED_RULES = {
    "WHITESPACE_RULE",          # double spaces around fields/links are layout artefacts
    "EN_QUOTES",                # typographic quotes are a style choice
    "DASH_RULE",
    "PUNCTUATION_PARAGRAPH_END",  # table cells / list items often have no final period
    "UPPERCASE_SENTENCE_START",   # list items and cells frequently start lowercase
}


def locked_spans(segments):
    """Spans covering runs that must not be edited (links, fields, super/subscript...)."""
    return [Span(s.start, s.end, f"format:{s.reason}") for s in segments if not s.editable and s.text]


class MatchFilter:

    def __init__(self, options, protection):
        self.options = options
        self.protection = protection
        self.enabled_groups = {g for g in ("grammar", "spelling", "punctuation", "style")
                               if getattr(options, g)}
        self.terms = set(protection.terms)

    def accept(self, match, text, spans):
        """Return (accepted, reason)."""
        if match.replacement is None:
            return False, "no suggestion"
        if match.rule_id in IGNORED_RULES:
            return False, "ignored rule"
        if match.group not in self.enabled_groups:
            return False, f"{match.group} disabled"
        if match.start < 0 or match.end > len(text) or match.start > match.end:
            return False, "bad offsets"
        original = text[match.start:match.end]
        if original == match.replacement:
            return False, "no change"
        if overlaps_any(spans, match.start, match.end):
            return False, "protected"
        if match.group == "spelling":
            if original.lower() == match.replacement.lower():
                return False, "case-only suggestion"  # e.g. 'kt' -> 'KT'
            if not self._spelling_ok(original, text, match.start):
                return False, "likely term or name"
        return True, ""

    def _spelling_ok(self, word, text, start):
        word = word.strip()
        if not word or word in self.terms:
            return False
        if any(c.isdigit() for c in word):
            return False
        if len(word) > 1 and word.isupper():
            return False
        if re.search(r"[a-z][A-Z]", word):
            return False
        if self.options.skip_capitalized_spelling and word[0].isupper():
            before = text[:start].rstrip()
            sentence_start = not before or before[-1] in ".!?:;\"'“(["
            if not sentence_start:
                return False  # capitalised mid-sentence: probably a proper noun
        return True


def unit_policy(unit, options):
    """Return ('skip' | 'correct' | 'full', reason)."""
    loc = unit.location
    if loc == Location.BODY and not options.process_body:
        return "skip", "body disabled"
    if loc == Location.TABLE and not options.process_tables:
        return "skip", "tables disabled"
    if loc == Location.HEADER and not options.process_headers:
        return "skip", "headers disabled"
    if loc == Location.FOOTER and not options.process_footers:
        return "skip", "footers disabled"
    if unit.kind in (Kind.EMPTY,):
        return "skip", "empty"
    if unit.kind in (Kind.TOC, Kind.EQUATION, Kind.REFERENCE, Kind.QUOTE):
        return "skip", unit.kind.value
    if unit.numeric_cell and options.skip_numeric_cells:
        return "skip", "numeric cell"
    if unit.kind in (Kind.TITLE, Kind.HEADING):
        return ("correct", "") if options.process_headings else ("skip", "heading")
    if unit.kind == Kind.CAPTION:
        return ("correct", "") if options.process_captions else ("skip", "caption")
    if loc != Location.BODY or unit.contains_math:
        return "correct", ""
    return "full", ""


class ParagraphProcessor:
    """Correct a single paragraph in place (run-level, formatting preserved).

    The DocumentProcessor batches many paragraphs per request; this class is
    the simple path for one-off use and scripts.
    """

    def __init__(self, language_tool, options=None, protection=None):
        from core.options import ProcessingOptions
        from core.protection import ProtectionEngine
        self.language_tool = language_tool
        self.options = options or ProcessingOptions()
        self.protection = protection or ProtectionEngine(self.options)
        self.filter = MatchFilter(self.options, self.protection)

    def process(self, paragraph):
        segments = paragraph_segments(paragraph)
        text = paragraph_text(segments)
        if not text.strip():
            return text
        spans = self.protection.find_spans(text, locked_spans(segments))
        edits = [Edit(m.start, m.end, m.replacement)
                 for m in self.language_tool.check_matches(text)
                 if self.filter.accept(m, text, spans)[0]]
        apply_edits(segments, edits)
        write_segments(segments)
        return paragraph_text(segments)
