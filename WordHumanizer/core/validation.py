"""Validation of rewritten text and of the final document."""

from docx import Document

from core.protection import PLACEHOLDER_RE
from core.structure_manager import analyze_document


def compare_inventories(before, after):
    """Return warnings for protected items that changed between two inventories."""
    labels = {
        "citations": "Citation",
        "urls": "URL/DOI/e-mail",
        "numbers": "Numerical value",
        "terms": "Technical term",
    }
    problems = []
    for key, label in labels.items():
        missing = before[key] - after[key]
        added = after[key] - before[key]
        for item in missing:
            problems.append(f"{label} removed or changed: {item!r}")
        for item in added:
            problems.append(f"{label} added: {item!r}")
    return problems


def validate_rewrite(original, rewritten, protection, min_ratio=0.5, max_ratio=1.8):
    """Check that a rewrite kept the meaning-critical content of ``original``."""
    problems = []
    if not rewritten.strip():
        return ["Rewrite is empty."]
    ratio = len(rewritten) / max(1, len(original))
    if not (min_ratio <= ratio <= max_ratio):
        problems.append(f"Rewrite length changed too much ({ratio:.0%} of original).")
    if PLACEHOLDER_RE.search(rewritten):
        problems.append("Rewrite still contains placeholders.")
    problems += compare_inventories(protection.inventory(original), protection.inventory(rewritten))
    return problems


def validate(original, processed):
    """Minimal text check kept for compatibility with simple scripts."""
    problems = []
    if len(processed) == 0:
        problems.append("Processed document is empty.")
    return problems


def document_stats(document):
    body = document.element.body
    return {
        "paragraphs": len(body.xpath(".//w:p")),
        "tables": len(body.xpath(".//w:tbl")),
        "images": len(body.xpath(".//w:drawing | .//w:pict")),
        "equations": len(body.xpath(".//m:oMath")),
        "hyperlinks": len(body.xpath(".//w:hyperlink")),
        "sections": len(document.sections),
    }


def validate_document(original_stats, output_path):
    """Re-open the saved file and compare its structure with the original."""
    checks = []
    try:
        document = Document(output_path)
    except Exception as error:  # noqa: BLE001 - any failure means an unreadable file
        return [("File opens", False, str(error))], {}
    checks.append(("File opens", True, ""))
    stats = document_stats(document)
    for key, label in (("paragraphs", "Paragraph count"), ("tables", "Table count"),
                       ("images", "Images preserved"), ("equations", "Equations preserved"),
                       ("hyperlinks", "Hyperlinks preserved"), ("sections", "Sections preserved")):
        ok = stats[key] == original_stats.get(key)
        detail = "" if ok else f"{original_stats.get(key)} → {stats[key]}"
        checks.append((label, ok, detail))
    leftovers = sum(1 for u in analyze_document(document) if PLACEHOLDER_RE.search(u.paragraph.text))
    checks.append(("No placeholder left", leftovers == 0, f"{leftovers} paragraph(s)" if leftovers else ""))
    return checks, stats
