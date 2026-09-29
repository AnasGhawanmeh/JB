"""Split text into LanguageTool-sized chunks without cutting sentences.

Boundary preference: paragraph -> sentence -> word -> hard character cut.
Every function here is lossless: joining the returned pieces gives back the
original text exactly, so offsets can always be mapped back.
"""

import re
from dataclasses import dataclass, field

from utils.text_utils import sentence_spans


def split_text(text, max_chars=50000):
    """Split ``text`` into pieces of at most ``max_chars`` characters.

    Returns a list of strings whose concatenation equals ``text``.
    """
    return [piece for _, piece in split_with_offsets(text, max_chars)]


def split_with_offsets(text, max_chars=50000):
    """Like split_text, but returns (offset, piece) tuples."""
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if len(text) <= max_chars:
        return [(0, text)] if text else []

    units = _paragraph_units(text)
    pieces = []
    current_start, current_end = None, None

    def flush():
        nonlocal current_start, current_end
        if current_start is not None:
            pieces.append((current_start, text[current_start:current_end]))
        current_start = current_end = None

    for start, end in units:
        if end - start > max_chars:
            flush()
            for sub_start, sub_end in _split_long(text, start, end, max_chars):
                pieces.append((sub_start, text[sub_start:sub_end]))
            continue
        if current_start is None:
            current_start, current_end = start, end
        elif end - current_start <= max_chars:
            current_end = end
        else:
            flush()
            current_start, current_end = start, end
    flush()
    return pieces


def _paragraph_units(text):
    units = []
    start = 0
    for match in re.finditer(r"\n+", text):
        units.append((start, match.end()))
        start = match.end()
    if start < len(text):
        units.append((start, len(text)))
    return units


def _split_long(text, start, end, max_chars):
    """Split text[start:end] at sentence, then word, then character boundaries."""
    segment = text[start:end]
    sentences = [(start + s, start + e) for s, e in sentence_spans(segment)]
    result = []
    cur_s = cur_e = None
    for s, e in sentences:
        if e - s > max_chars:
            if cur_s is not None:
                result.append((cur_s, cur_e))
                cur_s = cur_e = None
            result.extend(_split_words(text, s, e, max_chars))
        elif cur_s is None:
            cur_s, cur_e = s, e
        elif e - cur_s <= max_chars:
            cur_e = e
        else:
            result.append((cur_s, cur_e))
            cur_s, cur_e = s, e
    if cur_s is not None:
        result.append((cur_s, cur_e))
    return result


def _split_words(text, start, end, max_chars):
    result = []
    pos = start
    while end - pos > max_chars:
        cut = text.rfind(" ", pos + 1, pos + max_chars)
        if cut <= pos:
            cut = pos + max_chars  # no whitespace: hard cut
        else:
            cut += 1
        result.append((pos, cut))
        pos = cut
    if pos < end:
        result.append((pos, end))
    return result


# --------------------------------------------------------------------------
# Batching many small paragraphs into few requests
# --------------------------------------------------------------------------

@dataclass
class BatchSegment:
    unit_index: int      # index of the source unit (paragraph)
    unit_offset: int     # offset of this piece inside the unit's text
    batch_offset: int    # offset of this piece inside the batch text
    length: int


@dataclass
class Batch:
    text: str = ""
    segments: list = field(default_factory=list)

    def locate(self, start, end):
        """Map a batch range to (segment, start_in_unit, end_in_unit) or None."""
        for seg in self.segments:
            seg_end = seg.batch_offset + seg.length
            if seg.batch_offset <= start and end <= seg_end:
                return seg, seg.unit_offset + start - seg.batch_offset, seg.unit_offset + end - seg.batch_offset
        return None


def batch_units(texts, max_chars=50000, separator="\n\n"):
    """Pack many unit texts into batches of at most ``max_chars`` characters.

    ``texts`` is a list of strings (``None`` or empty entries are skipped).
    Long texts are split with split_with_offsets. Units are separated by a
    blank line so LanguageTool treats them as separate paragraphs.
    """
    batches = []
    current = Batch()

    def close():
        nonlocal current
        if current.segments:
            batches.append(current)
        current = Batch()

    for index, text in enumerate(texts):
        if not text or not text.strip():
            continue
        for offset, piece in split_with_offsets(text, max_chars):
            needed = len(piece) + (len(separator) if current.segments else 0)
            if current.segments and len(current.text) + needed > max_chars:
                close()
            if current.segments:
                current.text += separator
            current.segments.append(BatchSegment(index, offset, len(current.text), len(piece)))
            current.text += piece
    close()
    return batches
