"""User-facing processing options."""

from dataclasses import asdict, dataclass, field, fields

REWRITE_STYLES = {
    "natural": "Natural, fluent prose that reads smoothly while keeping the author's voice.",
    "professional": "Polished, professional prose suitable for reports and business documents.",
    "academic": "Clear, precise academic prose with formal register and hedged claims kept as hedged.",
    "simple": "Plain language with shorter sentences and common words.",
    "concise": "Tighter prose with redundancy removed; keep every fact.",
    "formal": "Formal register; no contractions or colloquialisms.",
    "technical": "Precise technical prose; keep terminology exactly as given.",
    "business": "Direct, action-oriented business prose.",
}

REWRITE_LEVELS = {
    "light": "Light: polish wording only where a sentence is unclear; clear sentences stay as they are.",
    "thorough": "Thorough: rework most sentences for clarity and natural flow while keeping every fact.",
}

MODES = ("academic", "standard")


@dataclass
class ProcessingOptions:
    language: str = "en-US"
    mode: str = "academic"

    # LanguageTool categories
    grammar: bool = True
    spelling: bool = True
    punctuation: bool = True
    style: bool = True
    picky: bool = False

    # Optional rewrite stage
    rewrite: bool = False
    rewrite_style: str = "natural"
    rewrite_level: str = "light"

    # What to process
    process_body: bool = True
    process_tables: bool = True
    process_headers: bool = False
    process_footers: bool = False
    process_headings: bool = False
    process_captions: bool = True
    skip_numeric_cells: bool = True

    # What to protect
    protect_citations: bool = True
    protect_urls: bool = True
    protect_numbers: bool = True
    protect_terms: bool = True
    protect_equations: bool = True
    auto_detect_terms: bool = True
    skip_capitalized_spelling: bool = True
    protected_terms: list = field(default_factory=list)

    def __post_init__(self):
        if self.mode not in MODES:
            self.mode = "academic"
        if self.rewrite_style not in REWRITE_STYLES:
            self.rewrite_style = "natural"
        if self.rewrite_level not in REWRITE_LEVELS:
            self.rewrite_level = "light"
        if isinstance(self.protected_terms, str):
            self.protected_terms = [t.strip() for t in self.protected_terms.replace("\n", ",").split(",")]
        self.protected_terms = [t for t in (s.strip() for s in self.protected_terms) if t]

    @classmethod
    def from_dict(cls, data):
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in (data or {}).items() if k in known})

    @classmethod
    def for_mode(cls, mode, **overrides):
        if mode == "standard":
            base = dict(mode="standard", protect_numbers=False, auto_detect_terms=False,
                        skip_capitalized_spelling=False, process_headings=True)
        else:
            base = dict(mode="academic")
        base.update(overrides)
        return cls(**base)

    def to_dict(self):
        return asdict(self)

    @property
    def any_correction(self):
        return self.grammar or self.spelling or self.punctuation or self.style
