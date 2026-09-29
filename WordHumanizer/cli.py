"""Command-line interface.

Examples:
    python cli.py input/My_Research.docx
    python cli.py thesis.docx -o output/thesis_checked.docx --language en-GB --no-style
    python cli.py thesis.docx --rewrite --rewrite-style academic --terms "LEAP,SimaPro"
"""

import argparse
import json
import sys
from pathlib import Path

from config import get_settings
from core.language_tool_client import LanguageToolClient
from core.options import REWRITE_STYLES, ProcessingOptions
from core.pipeline import DocumentProcessor
from core.rewriting_engine import create_rewriting_engine
from utils.file_utils import (InvalidDocumentError, convert_doc_to_docx,
                              output_name, validate_docx)
from utils.logger import setup_logger


def build_parser():
    p = argparse.ArgumentParser(description="Proofread a Word document with LanguageTool, keeping its formatting.")
    p.add_argument("input", help=".docx (or .doc with LibreOffice installed)")
    p.add_argument("-o", "--output", help="output .docx (default: output/<name>_processed.docx)")
    p.add_argument("--language", help="LanguageTool language code, e.g. en-US, en-GB, de-DE")
    p.add_argument("--mode", choices=["academic", "standard"], default="academic")
    for group in ("grammar", "spelling", "punctuation", "style"):
        p.add_argument(f"--no-{group}", action="store_true", help=f"do not apply {group} corrections")
    p.add_argument("--picky", action="store_true", help="LanguageTool picky mode")
    p.add_argument("--rewrite", action="store_true", help="enable the rewriting stage (needs REWRITE_PROVIDER)")
    p.add_argument("--rewrite-style", choices=sorted(REWRITE_STYLES), default="natural")
    p.add_argument("--headings", action="store_true", help="also correct headings")
    p.add_argument("--headers", action="store_true", help="also process page headers")
    p.add_argument("--footers", action="store_true", help="also process page footers")
    p.add_argument("--no-tables", action="store_true", help="skip tables")
    p.add_argument("--terms", default="", help="comma-separated extra protected terms")
    p.add_argument("--report", help="write the report to this file (.txt or .json)")
    p.add_argument("--quiet", action="store_true")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = get_settings()
    setup_logger(settings.log_dir)

    source = Path(args.input)
    if not source.exists():
        print(f"File not found: {source}", file=sys.stderr)
        return 2
    try:
        if source.suffix.lower() == ".doc":
            source = convert_doc_to_docx(source, settings.temp_dir)
        validate_docx(source)
    except InvalidDocumentError as error:
        print(f"Invalid document: {error}", file=sys.stderr)
        return 2

    output = Path(args.output) if args.output else settings.output_dir / output_name(source.name)
    if output.resolve() == Path(args.input).resolve():
        print("Refusing to overwrite the original file; choose another output name.", file=sys.stderr)
        return 2

    options = ProcessingOptions.for_mode(
        args.mode,
        language=args.language or settings.language,
        grammar=not args.no_grammar, spelling=not args.no_spelling,
        punctuation=not args.no_punctuation, style=not args.no_style,
        picky=args.picky, rewrite=args.rewrite, rewrite_style=args.rewrite_style,
        process_tables=not args.no_tables, process_headers=args.headers,
        process_footers=args.footers,
        protected_terms=args.terms,
    )
    if args.headings:
        options.process_headings = True

    progress = _progress_printer(args.quiet)
    lt = LanguageToolClient.from_settings(settings, language=options.language, picky=options.picky)
    rewriter = create_rewriting_engine(settings) if options.rewrite else None
    processor = DocumentProcessor(lt, rewriter, options, settings.max_chars, progress)
    report = processor.process(source, output)
    progress.close()

    text = report.to_text()
    if args.report:
        path = Path(args.report)
        path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
                        if path.suffix == ".json" else text, encoding="utf-8")
    if not args.quiet:
        print(text if not args.report else text.split("\nChanges\n")[0])
        print(f"Saved: {output}")
    return 0 if report.ok else 1


class _progress_printer:
    def __init__(self, quiet):
        self.quiet = quiet
        self.bar = None
        if not quiet:
            try:
                from tqdm import tqdm
                self.bar = tqdm(total=100, bar_format="{l_bar}{bar}| {desc}")
            except ImportError:
                pass

    def __call__(self, fraction, message):
        if self.quiet:
            return
        if self.bar is not None:
            self.bar.n = int(fraction * 100)
            self.bar.set_description_str(message)
            self.bar.refresh()
        else:
            print(f"[{fraction:4.0%}] {message}", file=sys.stderr)

    def close(self):
        if self.bar is not None:
            self.bar.close()


if __name__ == "__main__":
    sys.exit(main())
