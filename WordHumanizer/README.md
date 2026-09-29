# Word Humanizer

A proofreading and editing application for Word documents. It sends the text of
a `.docx` file to [LanguageTool](https://languagetool.org) for grammar, spelling,
punctuation and style correction, can optionally rewrite paragraphs for
clarity, and writes the result to a **new** `.docx`. Formatting, citations,
numbers, technical terms and document structure are left as they were.

It is an editing assistant: it preserves the author's meaning and content, and
it is not designed to disguise how a text was produced. Always review the
changes (every one is listed in the report) before you submit a document.

```
WORD FILE → structure analysis → protection engine → batched LanguageTool
→ optional rewrite → LanguageTool verification → validation
→ run-level write-back → NEW WORD FILE + report
```

## Features

| Area | What it does |
| --- | --- |
| **Document** | Body paragraphs, headings, lists, captions, nested tables (merged cells de-duplicated), headers/footers (optional), content controls |
| **Formatting** | Edits are applied **run by run**, so bold/italic/underline, fonts, styles and paragraph layout survive. It never uses `paragraph.text = ...` |
| **Locked content** | Hyperlinks, field results (cross-references, Zotero/Mendeley/EndNote citations), tracked changes, images and objects, equations (OMML), hidden text and super/subscript runs (CO₂, footnote-style citations) are never edited |
| **Protection** | Citations (author-year, numeric `[1–3]`, narrative "Smith et al. (2024)"), URLs, DOIs, e-mails, numbers with units, inline equations, a built-in term list (LEAP, SimaPro, CO2, LCA, UNFCCC …), your own terms, and auto-detected acronyms / formulas / CamelCase names |
| **Classification** | Title, heading, normal, list, caption, quote, TOC and equation paragraphs; the *References / Bibliography* section is detected and skipped |
| **Academic mode** | Headings, references and quotes are not touched. Capitalised words in mid-sentence (names) are not spell-"corrected". Case-only suggestions (`kt` → `KT`) are ignored |
| **Large files** | Paragraphs are packed into batches of at most `MAX_CHARS` and split at paragraph, sentence and then word boundaries. One request covers many paragraphs. UTF-16 offsets are mapped correctly |
| **Reliability** | Retries with exponential backoff (connection errors, 429, 5xx), client-side rate limiting, a result cache, and per-paragraph error isolation, so a failure leaves that paragraph unchanged instead of crashing the run |
| **Rewrite (optional)** | Pluggable engine (Claude included). Protected content is replaced by `⟦P0⟧` placeholders first. The rewrite is re-checked by LanguageTool, and it is **rejected** if any number, citation, URL or term changed, a placeholder is lost, or the change would touch locked runs |
| **Validation** | The saved file is re-opened. Paragraph, table, image, equation, hyperlink and section counts are compared, and leftover placeholders are checked |
| **Report** | Counts by category, protected items, skipped reasons, every individual change with context, warnings, and validation results (text or JSON) |
| **Interfaces** | Web UI (FastAPI, drag and drop, progress bar, download), CLI, and a Python API |
| **Security** | Checks extension, ZIP signature, Word package parts, size limit and zip-bomb ratio, and rejects macro-enabled files. Uploads are deleted after processing, and the original file is never overwritten |

## Setup

Python 3.11 or 3.12.

```bash
cd WordHumanizer
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then edit .env
```

### LanguageTool: cloud or self-hosted

* **Public API** (default `https://api.languagetool.org/v2/check`): the free tier
  allows roughly 20 requests/min and 20 KB per request. Keep `MAX_CHARS=18000`
  and the rate limits in `.env`. Add `LANGUAGETOOL_USERNAME` and
  `LANGUAGETOOL_API_KEY` for a Premium account (up to 60,000 characters per
  request).
* **Self-hosted** (recommended for private documents and large theses): needs
  Java 17+ and Maven.

  ```bash
  tools/languagetool/start_languagetool.sh      # first run downloads ~250 MB
  # in .env:
  LANGUAGETOOL_URL=http://localhost:8081/v2/check
  LANGUAGETOOL_REQUESTS_PER_MINUTE=0
  LANGUAGETOOL_CHARS_PER_MINUTE=0
  MAX_CHARS=50000
  ```
  To add languages, edit `tools/languagetool/pom.xml` (for example `language-de` or `language-ar`).

### Optional rewriting stage

```env
REWRITE_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
REWRITE_MODEL=claude-opus-5-5
```

Styles: natural, professional, academic, simple, concise, formal, technical,
business. Only body paragraphs with at least 8 words are rewritten. Headings,
captions, table cells, references and quotes only get corrections.

## Usage

### Web interface

```bash
./run.sh          # Windows: run.bat
# open http://localhost:8000
```

Drop a `.docx` file, choose the language, mode and options, and press
**Process document**. When it finishes, download the processed file and the
report.

API: `POST /api/jobs` (multipart `file` + JSON `options`),
`GET /api/jobs/{id}`, `GET /api/jobs/{id}/download`,
`GET /api/jobs/{id}/report?format=txt|json`, `DELETE /api/jobs/{id}`.
Interactive documentation is at `/docs`.

### Command line

```bash
python cli.py input/My_Research.docx                      # → output/My_Research_processed.docx
python cli.py thesis.docx -o out.docx --language en-GB --picky --report out_report.txt
python cli.py thesis.docx --no-style --headings --terms "Zarqa, JUST, BRT"
python cli.py thesis.docx --rewrite --rewrite-style academic
```

The exit code is `0` on success, `1` if validation failed or some paragraphs
had errors, and `2` for invalid input.

### Python

```python
from core.options import ProcessingOptions
from core.pipeline import process_document

report = process_document("input/paper.docx", "output/paper_processed.docx",
                          ProcessingOptions(language="en-GB", protected_terms=["LEAP"]))
print(report.to_text())
```

`.doc` files are converted with LibreOffice (`soffice`) if it is installed.
Otherwise, save them as `.docx` in Word.

## Project layout

```
app.py                      FastAPI web app          cli.py      command line
config.py                   settings from .env       static/     web UI
core/
  document_reader.py        paragraphs → run segments (editable / locked)
  document_writer.py        run-level edits, diff of rewrites → minimal edits
  structure_manager.py      body/tables/headers walk + paragraph classification
  protection.py             protected spans, placeholder masking
  citation_detector.py      citation patterns
  chunker.py                lossless splitting and batching
  language_tool_client.py   HTTP client, retries, rate limit, cache
  paragraph_processor.py    suggestion filtering + processing policy
  rewriting_engine.py       rewriting interface + Claude implementation
  validation.py             rewrite checks, output document checks
  pipeline.py               the processing engine
  report.py, jobs.py, options.py
utils/                      logging, file validation, text helpers
tests/                      pytest suite (offline, fake LanguageTool)
tools/languagetool/         self-hosted LanguageTool helper
```

## Tests

```bash
python -m pytest
```

The suite runs offline with a fake LanguageTool. It covers chunking, citation
and number protection, run-level formatting preservation, locked hyperlinks,
the full pipeline, rewrite rejection rules, the HTTP client (retries, UTF-16
offsets, rate limiting) and the web API.

## Known limitations

* LanguageTool finds many, but not all, grammar errors. Picky mode finds more.
  Automatic corrections always take LanguageTool's first suggestion, so review
  the report.
* Footnotes, endnotes, comments and text boxes are not processed yet
  (python-docx does not expose them). They are left unchanged.
* A correction is skipped if it would span a locked run (for example text
  that continues into a hyperlink). The report counts these as
  `locked formatting/overlap`.
* A rewrite replaces text inside the existing runs. Wording that moves
  between differently formatted runs takes the formatting of the first run it
  touches.

## Packaging as a Windows .exe (optional)

```bash
pip install pyinstaller
pyinstaller --onefile --name WordHumanizer cli.py
```

The executable reads `.env` and writes `output/` and `logs/` next to itself.
