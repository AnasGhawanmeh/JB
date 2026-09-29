"""The document processing engine.

Word file → structure analysis → protection → batched LanguageTool correction
→ optional rewriting (+ LanguageTool verification + validation) → run-level
write-back → save → re-open and validate → report.
"""

import time
from collections import Counter
from dataclasses import dataclass, field, replace
from pathlib import Path

from docx import Document

from core.chunker import batch_units
from core.document_reader import paragraph_segments, paragraph_text
from core.document_writer import (Edit, apply_edits, diff_edits,
                                  write_segments)
from core.language_tool_client import LanguageToolError, apply_matches
from core.options import ProcessingOptions
from core.paragraph_processor import MatchFilter, locked_spans, unit_policy
from core.protection import ProtectionEngine
from core.report import Report
from core.rewriting_engine import NoOpRewritingEngine, RewriteError
from core.structure_manager import analyze_document
from core.validation import document_stats, validate_document, validate_rewrite
from utils.logger import get_logger
from utils.text_utils import snippet, word_count

log = get_logger("pipeline")

MIN_WORDS_TO_REWRITE = {"light": 8, "thorough": 5}


@dataclass
class WorkItem:
    unit: object
    policy: str
    text: str = ""
    spans: list = field(default_factory=list)
    edits: list = field(default_factory=list)
    failed: bool = False


class ProcessingCancelled(Exception):
    pass


class DocumentProcessor:

    def __init__(self, language_tool, rewriter=None, options=None, max_chars=18000,
                 progress=None, cancelled=None):
        self.lt = language_tool
        self.rewriter = rewriter or NoOpRewritingEngine()
        self.options = options or ProcessingOptions()
        self.max_chars = max_chars
        self.protection = ProtectionEngine(self.options)
        self.filter = MatchFilter(self.options, self.protection)
        self._progress = progress or (lambda fraction, message: None)
        self._cancelled = cancelled or (lambda: False)

    # ------------------------------------------------------------------ API
    def process(self, input_path, output_path):
        started = time.monotonic()
        o = self.options
        report = Report(file=Path(input_path).name, output=Path(output_path).name,
                        language=o.language, mode=o.mode, options=o.to_dict())
        requests_before = getattr(self.lt, "request_count", 0)

        self._progress(0.02, "Reading document")
        document = Document(input_path)
        original_stats = document_stats(document)
        report.document = original_stats

        self._progress(0.05, "Analysing structure")
        units = analyze_document(document)
        report.paragraphs_total = len(units)
        items = self._plan(units, report)

        if o.any_correction and items:
            self._correct(items, report)

        if o.rewrite:
            if getattr(self.rewriter, "available", False):
                self._rewrite([i for i in items if i.policy == "full" and not i.failed], report)
            else:
                report.warnings.append("Rewrite requested but no rewriting provider is configured "
                                       "(set REWRITE_PROVIDER); only corrections were applied.")

        report.processed = sum(1 for i in items if not i.failed)

        self._progress(0.95, "Saving document")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        document.save(output_path)

        self._progress(0.97, "Validating output")
        report.checks, _ = validate_document(original_stats, output_path)
        report.languagetool_requests = getattr(self.lt, "request_count", 0) - requests_before
        report.duration_seconds = time.monotonic() - started
        self._progress(1.0, "Done")
        log.info("Processed %s: %s corrections, %s rewrites", report.file, report.corrections, report.rewritten)
        return report

    # --------------------------------------------------------------- stages
    def _plan(self, units, report):
        items = []
        for unit in units:
            report.kinds[unit.kind.value] += 1
            policy, reason = unit_policy(unit, self.options)
            if policy == "skip":
                report.skipped += 1
                report.skipped_reasons[reason] += 1
                continue
            try:
                segments = paragraph_segments(unit.paragraph)
                text = paragraph_text(segments)
                spans = self.protection.find_spans(text, locked_spans(segments))
            except Exception as error:  # noqa: BLE001 - never crash on one paragraph
                log.exception("Cannot read %s", unit.label)
                report.errors.append(f"{unit.label}: could not be read ({error}); left unchanged")
                report.skipped += 1
                report.skipped_reasons["read error"] += 1
                continue
            for span in spans:
                report.protected[span.kind] += 1
            items.append(WorkItem(unit, policy, text, spans))
        return items

    def _correct(self, items, report):
        batches = batch_units([i.text for i in items], self.max_chars)
        total = max(1, len(batches))
        for number, batch in enumerate(batches, start=1):
            self._check_cancel()
            self._progress(0.08 + 0.52 * (number - 1) / total,
                           f"Checking grammar and spelling ({number}/{len(batches)})")
            try:
                matches = self.lt.check_matches(batch.text)
            except LanguageToolError as error:
                units = sorted({seg.unit_index for seg in batch.segments})
                report.errors.append(f"LanguageTool request failed ({error}); "
                                     f"{len(units)} paragraph(s) left uncorrected")
                for index in units:
                    items[index].failed = True
                continue
            for match in matches:
                located = batch.locate(match.start, match.end)
                if located is None:
                    continue
                seg, start, end = located
                item = items[seg.unit_index]
                match = replace(match, start=start, end=end)  # cached objects stay intact
                accepted, reason = self.filter.accept(match, item.text, item.spans)
                if accepted:
                    item.edits.append((match, Edit(start, end, match.replacement)))
                else:
                    report.suggestions_rejected[reason] += 1

        self._progress(0.6, "Applying corrections")
        for item in items:
            if item.failed or not item.edits:
                continue
            try:
                segments = paragraph_segments(item.unit.paragraph)
                applied, skipped = apply_edits(segments, [e for _, e in item.edits])
                write_segments(segments)
            except Exception as error:  # noqa: BLE001
                log.exception("Cannot apply corrections to %s", item.unit.label)
                report.errors.append(f"{item.unit.label}: corrections failed ({error}); left unchanged")
                item.failed = True
                continue
            applied_set = set(applied)
            for match, edit in item.edits:
                if edit not in applied_set:
                    report.suggestions_rejected["locked formatting/overlap"] += 1
                    continue
                report.corrections += 1
                report.corrections_by_group[match.group] += 1
                report.add_change(
                    type="correction", location=item.unit.label, group=match.group,
                    rule=match.rule_id, message=match.message,
                    before=item.text[edit.start:edit.end], after=edit.replacement,
                    context=snippet(item.text, edit.start, edit.end),
                )
            item.text = paragraph_text(segments)

    def _rewrite(self, items, report):
        min_words = MIN_WORDS_TO_REWRITE.get(self.options.rewrite_level, 8)
        candidates = [i for i in items if word_count(i.text) >= min_words]
        total = max(1, len(candidates))
        for number, item in enumerate(candidates, start=1):
            self._check_cancel()
            self._progress(0.6 + 0.35 * (number - 1) / total, f"Rewriting ({number}/{len(candidates)})")
            try:
                self._rewrite_one(item, report)
            except (RewriteError, LanguageToolError) as error:
                report.rewrites_rejected += 1
                report.warnings.append(f"{item.unit.label}: rewrite skipped ({error})")
            except Exception as error:  # noqa: BLE001
                log.exception("Rewrite failed for %s", item.unit.label)
                report.rewrites_rejected += 1
                report.warnings.append(f"{item.unit.label}: rewrite failed ({error}); kept corrected text")

    def _rewrite_one(self, item, report):
        o = self.options
        segments = paragraph_segments(item.unit.paragraph)
        text = paragraph_text(segments)
        spans = self.protection.find_spans(text, locked_spans(segments))
        masked, mapping = self.protection.mask(text, spans)

        proposal = self.rewriter.rewrite(masked, style=o.rewrite_style, language=o.language,
                                         level=o.rewrite_level)
        restored, problems = self.protection.unmask(proposal, mapping)
        if not problems:
            # Verification pass: LanguageTool re-checks the rewritten paragraph.
            new_spans = self.protection.find_spans(restored)
            matches = [m for m in self.lt.check_matches(restored)
                       if self.filter.accept(m, restored, new_spans)[0]]
            restored = apply_matches(restored, matches)
            problems = validate_rewrite(text, restored, self.protection)
        if problems:
            report.rewrites_rejected += 1
            report.warnings.append(f"{item.unit.label}: rewrite rejected — {'; '.join(problems[:3])}")
            return
        if restored == text:
            return
        applied, skipped = apply_edits(segments, diff_edits(text, restored), atomic=True)
        if skipped:
            report.rewrites_rejected += 1
            report.warnings.append(f"{item.unit.label}: rewrite rejected — it would alter locked "
                                   "content (links, fields, super/subscript)")
            return
        write_segments(segments)
        report.rewritten += 1
        report.add_change(type="rewrite", location=item.unit.label, before=text, after=restored)
        item.text = restored

    def _check_cancel(self):
        if self._cancelled():
            raise ProcessingCancelled()


def process_document(input_file, output_file, options=None, settings=None, progress=None):
    """Convenience entry point that builds the clients from settings."""
    from config import get_settings
    from core.language_tool_client import LanguageToolClient
    from core.rewriting_engine import create_rewriting_engine

    settings = settings or get_settings()
    options = options or ProcessingOptions(language=settings.language)
    lt = LanguageToolClient.from_settings(settings, language=options.language, picky=options.picky)
    rewriter = create_rewriting_engine(settings) if options.rewrite else None
    processor = DocumentProcessor(lt, rewriter, options, settings.max_chars, progress)
    return processor.process(input_file, output_file)
