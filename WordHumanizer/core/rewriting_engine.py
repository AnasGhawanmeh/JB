"""Optional rewriting stage.

The engine is an interface so the rest of the application does not depend on
a particular provider. Rewrites are only ever *proposals*: the pipeline
restores protected content, re-checks the result with LanguageTool, validates
numbers/citations/terms and discards the rewrite if anything changed.

The purpose of this stage is editing for clarity and readability while
preserving the author's meaning - it is not designed to disguise the origin
of a text.
"""

from core.options import REWRITE_LEVELS, REWRITE_STYLES
from utils.logger import get_logger

log = get_logger("rewriter")


class RewriteError(RuntimeError):
    pass


class RewritingEngine:
    name = "base"
    available = False

    def rewrite(self, text, style="natural", language="en-US", level="light"):
        raise NotImplementedError


class NoOpRewritingEngine(RewritingEngine):
    """Used when no provider is configured: returns the text unchanged."""
    name = "none"
    available = False

    def rewrite(self, text, style="natural", language="en-US", level="light"):
        return text


SYSTEM_PROMPT = """You are a careful copy editor improving one paragraph of a document written by its author.

Improve clarity, flow and readability in the requested style while keeping the author's meaning, claims, \
level of certainty and voice. Keep the paragraph in the same language ({language}).

{level_instructions}

Hard rules:
- Tokens of the form ⟦P0⟧, ⟦P1⟧, ... stand for citations, numbers, units, URLs, equations and technical \
terms. Copy every token exactly once, unchanged. Never add new tokens. You may move a token only if the \
sentence structure requires it.
- Do not add, remove or change facts, numbers, dates, names, units or citations.
- Do not add commentary, headings, quotation marks, or explanations.

Output only the edited paragraph text."""

LEVEL_INSTRUCTIONS = {
    "light": "Depth: light. Change only what is unclear, awkward or wordy. If the paragraph is already "
             "clear, return it with minimal or no changes.",
    "thorough": "Depth: thorough. Rework most sentences, not just the unclear ones: restructure long or stiff "
                "sentences, split or combine sentences where that reads better, vary sentence length and "
                "openings, replace generic filler, stock phrases and repetitive transitions with direct, "
                "specific wording, and prefer active voice where it fits the field's conventions. The result "
                "should read as a carefully revised version of the same paragraph, with the same content, "
                "the same order of ideas and a similar length.",
}


class ClaudeRewritingEngine(RewritingEngine):
    """Rewriting with Claude through the official Anthropic SDK."""
    name = "claude"

    def __init__(self, model="claude-opus-5-5", client=None):
        self.model = model
        if client is None:
            import anthropic  # optional dependency
            client = anthropic.Anthropic()
        self.client = client
        self.available = True

    def rewrite(self, text, style="natural", language="en-US", level="light"):
        style_text = REWRITE_STYLES.get(style, REWRITE_STYLES["natural"])
        level = level if level in REWRITE_LEVELS else "light"
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium" if level == "thorough" else "low"},
            # Server-side fallback if the primary model declines the request.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=SYSTEM_PROMPT.format(language=language, level_instructions=LEVEL_INSTRUCTIONS[level]),
            messages=[{
                "role": "user",
                "content": f"Style: {style} - {style_text}\n\nParagraph:\n{text}",
            }],
        )
        if response.stop_reason == "refusal":
            raise RewriteError("The model declined to rewrite this paragraph.")
        if response.stop_reason == "max_tokens":
            raise RewriteError("The rewrite was cut off.")
        output = "".join(block.text for block in response.content if block.type == "text").strip()
        if not output:
            raise RewriteError("The model returned no text.")
        return output


def create_rewriting_engine(settings):
    provider = (settings.rewrite_provider or "none").lower()
    if provider == "claude":
        try:
            return ClaudeRewritingEngine(model=settings.rewrite_model)
        except Exception as error:  # noqa: BLE001 - missing SDK or credentials
            log.warning("Claude rewriting unavailable: %s", error)
            return NoOpRewritingEngine()
    return NoOpRewritingEngine()
