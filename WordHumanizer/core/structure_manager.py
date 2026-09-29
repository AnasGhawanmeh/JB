"""Document structure analysis: find every text paragraph and classify it."""

import re
from dataclasses import dataclass
from enum import Enum

from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from core.document_reader import has_math, paragraph_segments, paragraph_text
from utils.text_utils import letter_ratio


class Kind(str, Enum):
    TITLE = "title"
    HEADING = "heading"
    NORMAL = "normal"
    CAPTION = "caption"
    REFERENCE = "reference"
    LIST = "list"
    QUOTE = "quote"
    TOC = "toc"
    EQUATION = "equation"
    EMPTY = "empty"


class Location(str, Enum):
    BODY = "body"
    TABLE = "table"
    HEADER = "header"
    FOOTER = "footer"


@dataclass
class TextUnit:
    index: int
    paragraph: Paragraph
    kind: Kind
    location: Location
    label: str
    heading_level: int = 0
    numeric_cell: bool = False
    contains_math: bool = False

    @property
    def text(self):
        return paragraph_text(paragraph_segments(self.paragraph))


REFERENCES_HEADING = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\.?\s*)?(references?|bibliography|works cited|literature cited|"
    r"reference list|sources|citations)\s*:?\s*$",
    re.IGNORECASE,
)
CAPTION_RE = re.compile(r"^\s*(figure|fig\.|table|chart|graph|equation|eq\.|map|plate|box)\s+"
                        r"[A-Z]?\d+(?:[.\-]\d+)*\s*[.:\-–—]", re.IGNORECASE)


def _style_name(paragraph):
    try:
        return (paragraph.style.name or "") if paragraph.style is not None else ""
    except (KeyError, AttributeError):
        return ""


def _outline_level(paragraph):
    ppr = paragraph._p.pPr
    if ppr is None:
        return None
    lvl = ppr.find(qn("w:outlineLvl"))
    if lvl is None:
        return None
    try:
        value = int(lvl.get(qn("w:val")))
    except (TypeError, ValueError):
        return None
    return value + 1 if value < 9 else None


def _is_numbered(paragraph):
    ppr = paragraph._p.pPr
    return ppr is not None and ppr.find(qn("w:numPr")) is not None


def classify(paragraph):
    """Return (Kind, heading_level) for a paragraph, ignoring context."""
    text = paragraph_text(paragraph_segments(paragraph))
    style = _style_name(paragraph)
    lowered = style.lower()
    math = has_math(paragraph)

    if not text.strip():
        return (Kind.EQUATION if math else Kind.EMPTY), 0
    if lowered in ("title", "subtitle"):
        return Kind.TITLE, 0
    match = re.match(r"heading\s*(\d)", lowered)
    if match:
        return Kind.HEADING, int(match.group(1))
    level = _outline_level(paragraph)
    if level:
        return Kind.HEADING, level
    if lowered.startswith("toc") or lowered.startswith("table of"):
        return Kind.TOC, 0
    if lowered == "caption" or CAPTION_RE.match(text) and len(text) < 400:
        return Kind.CAPTION, 0
    if "bibliograph" in lowered or lowered.startswith("reference"):
        return Kind.REFERENCE, 0
    if "quote" in lowered:
        return Kind.QUOTE, 0
    if "list" in lowered or _is_numbered(paragraph):
        return Kind.LIST, 0
    if math and letter_ratio(text) < 0.5:
        return Kind.EQUATION, 0
    return Kind.NORMAL, 0


def _is_references_title(paragraph, kind):
    text = paragraph.text.strip()
    if not REFERENCES_HEADING.match(text):
        return False
    if kind in (Kind.HEADING, Kind.TITLE):
        return True
    # "References" typed as a short bold normal paragraph
    runs = [r for r in paragraph.runs if r.text.strip()]
    return bool(runs) and all(r.bold for r in runs)


def iter_block_items(container):
    """Yield Paragraph and Table objects of a body/cell/header in document order."""
    element = container._element if hasattr(container, "_element") else container
    body = getattr(element, "body", None)
    parent_elm = body if body is not None else element
    for child in parent_elm.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, container)
        elif child.tag == qn("w:tbl"):
            yield Table(child, container)
        elif child.tag == qn("w:sdt"):
            content = child.find(qn("w:sdtContent"))
            if content is not None:
                for sub in content.iterchildren():
                    if sub.tag == qn("w:p"):
                        yield Paragraph(sub, container)
                    elif sub.tag == qn("w:tbl"):
                        yield Table(sub, container)


def analyze_document(document):
    """Return a list of TextUnits for every paragraph in the document."""
    units = []
    counters = {"table": 0}

    def add(paragraph, location, label, cell_numeric=False):
        kind, level = classify(paragraph)
        units.append(TextUnit(len(units), paragraph, kind, location, label, level,
                              numeric_cell=cell_numeric, contains_math=has_math(paragraph)))

    def walk(container, location, prefix):
        para_no = 0
        for block in iter_block_items(container):
            if isinstance(block, Paragraph):
                para_no += 1
                add(block, location, f"{prefix}¶{para_no}")
            else:
                walk_table(block, location, prefix)

    def walk_table(table, location, prefix):
        counters["table"] += 1
        table_no = counters["table"]
        seen = set()
        for r, row in enumerate(table.rows, start=1):
            for c, cell in enumerate(row.cells, start=1):
                if id(cell._tc) in seen:  # merged cells repeat
                    continue
                seen.add(id(cell._tc))
                cell_text = cell.text
                numeric = bool(cell_text.strip()) and letter_ratio(cell_text) < 0.5
                cell_prefix = f"{prefix}Table {table_no} r{r}c{c} "
                para_no = 0
                for block in iter_block_items(cell):
                    if isinstance(block, Paragraph):
                        para_no += 1
                        add(block, Location.TABLE if location == Location.BODY else location,
                            f"{cell_prefix}¶{para_no}", numeric)
                    else:
                        walk_table(block, location, cell_prefix)

    walk(document, Location.BODY, "")

    seen_parts = set()
    for s_no, section in enumerate(document.sections, start=1):
        for attr, location in (("header", Location.HEADER), ("first_page_header", Location.HEADER),
                               ("even_page_header", Location.HEADER), ("footer", Location.FOOTER),
                               ("first_page_footer", Location.FOOTER), ("even_page_footer", Location.FOOTER)):
            part = getattr(section, attr)
            if part.is_linked_to_previous:
                continue
            key = id(part._element)
            if key in seen_parts:
                continue
            seen_parts.add(key)
            walk(part, location, f"Section {s_no} {attr.replace('_', ' ')} ")

    _mark_reference_sections(units)
    return units


def _mark_reference_sections(units):
    in_refs = False
    refs_level = 0
    for unit in units:
        if unit.location != Location.BODY:
            continue
        if _is_references_title(unit.paragraph, unit.kind):
            in_refs = True
            refs_level = unit.heading_level or 1
            continue
        if in_refs:
            if unit.kind in (Kind.HEADING, Kind.TITLE) and (unit.heading_level or 1) <= refs_level:
                in_refs = False
            elif unit.kind in (Kind.NORMAL, Kind.LIST, Kind.QUOTE):
                unit.kind = Kind.REFERENCE
