"""Processing report."""

from collections import Counter
from dataclasses import asdict, dataclass, field

MAX_CHANGES_IN_REPORT = 5000


@dataclass
class Report:
    file: str = ""
    output: str = ""
    language: str = ""
    mode: str = ""
    options: dict = field(default_factory=dict)
    duration_seconds: float = 0.0

    paragraphs_total: int = 0
    processed: int = 0
    skipped: int = 0
    skipped_reasons: Counter = field(default_factory=Counter)
    kinds: Counter = field(default_factory=Counter)

    corrections: int = 0
    corrections_by_group: Counter = field(default_factory=Counter)
    suggestions_rejected: Counter = field(default_factory=Counter)
    rewritten: int = 0
    rewrites_rejected: int = 0

    protected: Counter = field(default_factory=Counter)
    document: dict = field(default_factory=dict)
    languagetool_requests: int = 0

    changes: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    checks: list = field(default_factory=list)

    def add_change(self, **change):
        if len(self.changes) < MAX_CHANGES_IN_REPORT:
            self.changes.append(change)

    @property
    def ok(self):
        return all(passed for _, passed, _ in self.checks) and not self.errors

    def to_dict(self):
        data = asdict(self)
        for key in ("skipped_reasons", "kinds", "corrections_by_group", "suggestions_rejected", "protected"):
            data[key] = dict(getattr(self, key))
        data["checks"] = [{"check": c, "passed": p, "detail": d} for c, p, d in self.checks]
        data["ok"] = self.ok
        return data

    def to_text(self):
        minutes, seconds = divmod(int(round(self.duration_seconds)), 60)
        doc = self.document
        lines = [
            "Processing Report",
            "-----------------",
            f"File:                 {self.file}",
            f"Output:               {self.output}",
            f"Language:             {self.language}",
            f"Mode:                 {self.mode}",
            "",
            f"Paragraphs:           {self.paragraphs_total}",
            f"Processed:            {self.processed}",
            f"Skipped:              {self.skipped}",
        ]
        for reason, count in sorted(self.skipped_reasons.items()):
            lines.append(f"  - {reason:<18} {count}")
        lines += [
            "",
            f"Corrections applied:  {self.corrections}",
        ]
        for group in ("grammar", "spelling", "punctuation", "style"):
            lines.append(f"  - {group:<18} {self.corrections_by_group.get(group, 0)}")
        lines += [
            f"Rewritten paragraphs: {self.rewritten}",
            f"Rewrites rejected:    {self.rewrites_rejected}",
            "",
            f"Protected citations:  {self.protected.get('citation', 0)}",
            f"Protected URLs:       {self.protected.get('url', 0) + self.protected.get('doi', 0) + self.protected.get('email', 0)}",
            f"Protected numbers:    {self.protected.get('number', 0)}",
            f"Protected terms:      {self.protected.get('term', 0)}",
            f"Protected equations:  {self.protected.get('equation', 0)}",
            f"Locked runs:          {sum(v for k, v in self.protected.items() if k.startswith('format:'))}",
            "",
            f"Tables:               {doc.get('tables', 0)}",
            f"Images:               {doc.get('images', 0)}",
            f"LanguageTool calls:   {self.languagetool_requests}",
            f"Processing time:      {minutes:02d}:{seconds:02d}",
            "",
            "Validation",
        ]
        for check, passed, detail in self.checks:
            lines.append(f"  {'✓' if passed else '✗'} {check}{(' — ' + detail) if detail else ''}")
        if self.warnings:
            lines += ["", f"Warnings ({len(self.warnings)})"]
            lines += [f"  ⚠ {w}" for w in self.warnings[:200]]
        if self.errors:
            lines += ["", f"Errors ({len(self.errors)})"]
            lines += [f"  ✗ {e}" for e in self.errors[:200]]
        if self.changes:
            lines += ["", "Changes"]
            for c in self.changes:
                if c["type"] == "rewrite":
                    lines.append(f"  [{c['location']}] rewrite:\n      - {c['before']}\n      + {c['after']}")
                else:
                    lines.append(f"  [{c['location']}] {c['group']}: {c['before']!r} → {c['after']!r}"
                                 f"  ({c['message']})")
        return "\n".join(lines) + "\n"
