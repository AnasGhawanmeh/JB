"""Writing edits back into Word runs without destroying formatting.

Instead of ``paragraph.text = new_text`` (which collapses every run into one
and loses bold/italic/underline/links), each edit is applied to the run(s)
that hold the affected characters. A replacement inherits the formatting of
the first run it touches; characters removed from later runs are deleted from
those runs only.
"""

import difflib
import re
from dataclasses import dataclass

from core.document_reader import paragraph_segments, paragraph_text


@dataclass(frozen=True)
class Edit:
    start: int
    end: int
    replacement: str


def edit_is_applicable(segments, edit):
    """An edit may not touch locked segments (links, fields, images, math...)."""
    for seg in segments:
        if seg.editable:
            continue
        if seg.start == seg.end:  # zero-width barrier
            if edit.start < seg.start < edit.end:
                return False
            continue
        if edit.start == edit.end:
            if seg.start < edit.start < seg.end:
                return False
        elif edit.start < seg.end and edit.end > seg.start:
            return False
    return _target_segment(segments, edit) is not None


def _target_segment(segments, edit):
    """The editable segment that receives the replacement text."""
    if edit.start == edit.end:
        # Insertion: prefer the run that ends at the insertion point (inherits
        # the preceding formatting), else the run that contains/starts at it.
        for seg in segments:
            if seg.editable and seg.text and seg.start < edit.start <= seg.end:
                return seg
        for seg in segments:
            if seg.editable and seg.start == edit.start:
                return seg
        return None
    for seg in segments:
        if seg.editable and seg.start < edit.end and seg.end > edit.start:
            return seg
    return None


def apply_edits(segments, edits, atomic=False):
    """Apply non-overlapping edits (unit coordinates) to segments in place.

    Returns (applied, skipped) lists. With ``atomic=True`` either every edit is
    applied or none is. Call ``write_segments`` afterwards to update the runs.
    """
    ordered = sorted(edits, key=lambda e: (e.start, e.end), reverse=True)
    accepted, skipped = [], []
    boundary = None
    for edit in ordered:
        if boundary is not None and edit.end > boundary:
            skipped.append(edit)  # overlaps an edit already accepted
            continue
        if edit_is_applicable(segments, edit):
            accepted.append(edit)
            boundary = edit.start
        else:
            skipped.append(edit)
    if atomic and skipped:
        return [], list(edits)

    for edit in accepted:  # right-to-left, so earlier offsets stay valid
        target = _target_segment(segments, edit)
        for seg in segments:
            if not seg.editable:
                continue
            lo = max(edit.start, seg.start)
            hi = min(edit.end, seg.end)
            if seg is target:
                local_lo, local_hi = lo - seg.start, max(lo, hi) - seg.start
                seg.text = seg.text[:local_lo] + edit.replacement + seg.text[local_hi:]
                seg.modified = True
            elif hi > lo and edit.start < edit.end:
                seg.text = seg.text[:lo - seg.start] + seg.text[hi - seg.start:]
                seg.modified = True
        _reindex(segments)
    return accepted, skipped


def _reindex(segments):
    pos = 0
    for seg in segments:
        seg.start = pos
        pos += len(seg.text)


def write_segments(segments):
    """Push modified segment texts into their runs."""
    for seg in segments:
        if seg.modified and seg.run is not None:
            seg.run.text = seg.text
            seg.modified = False


def apply_edits_to_paragraph(paragraph, edits, atomic=False):
    segments = paragraph_segments(paragraph)
    applied, skipped = apply_edits(segments, edits, atomic=atomic)
    write_segments(segments)
    return applied, skipped, paragraph_text(segments)


# --------------------------------------------------------------------------
# Turning a rewritten string into minimal edits
# --------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"\s+|\w+|[^\w\s]", re.UNICODE)


def _tokens(text):
    return [(m.start(), m.group()) for m in _TOKEN_RE.finditer(text)]


def diff_edits(old, new):
    """Compute word-level edits that turn ``old`` into ``new``."""
    a = _tokens(old)
    b = _tokens(new)
    matcher = difflib.SequenceMatcher(None, [t for _, t in a], [t for _, t in b], autojunk=False)
    edits = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        start = a[i1][0] if i1 < len(a) else len(old)
        end = a[i2 - 1][0] + len(a[i2 - 1][1]) if i2 > i1 else start
        replacement = "".join(t for _, t in b[j1:j2])
        edits.append(Edit(start, end, replacement))
    return edits
