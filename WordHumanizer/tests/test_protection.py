from core.citation_detector import find_citations, protect_citations, restore_citations
from core.options import ProcessingOptions
from core.protection import ProtectionEngine
from core.validation import validate_rewrite


def kinds(text, **opts):
    engine = ProtectionEngine(ProcessingOptions(**opts))
    return {(text[s.start:s.end], s.kind) for s in engine.find_spans(text)}


def test_citation_styles():
    text = ("Emissions rose (Smith et al., 2024; Lee & Park, 2019a). Jones and Brown (2020) agree [3, 5-7]. "
            "WHO (2021) also reports it.")
    found = [text[s:e] for s, e in find_citations(text)]
    assert "(Smith et al., 2024; Lee & Park, 2019a)" in found
    assert "Jones and Brown (2020)" in found
    assert "[3, 5-7]" in found
    assert "WHO (2021)" in found


def test_protect_and_restore_citations():
    text = "Jordan's transport emits a lot (Smith et al., 2024)."
    protected, mapping = protect_citations(text)
    assert "__CITATION_0__" in protected and "Smith" not in protected
    assert restore_citations(protected, mapping) == text


def test_urls_emails_numbers_terms():
    text = "See https://doi.org/10.1000/xyz123 or mail a.b@example.com: 5.2 million tonnes of CO2 in LEAP, 3.5%."
    found = kinds(text)
    assert ("https://doi.org/10.1000/xyz123", "url") in found
    assert ("a.b@example.com", "email") in found
    assert ("3.5%", "number") in found
    assert ("LEAP", "term") in found
    assert any(t.startswith("CO2") for t, _ in found)


def test_user_terms_and_disabled_protection():
    found = kinds("We used Zarqa data.", protected_terms=["Zarqa"])
    assert ("Zarqa", "term") in found
    assert kinds("Value is 25 kg.", protect_numbers=False, protect_equations=False) == set()


def test_mask_unmask_roundtrip_and_problems():
    engine = ProtectionEngine(ProcessingOptions())
    text = "In 2023, CO2 emissions reached 5.2 Mt (Smith, 2024)."
    masked, mapping = engine.mask(text, engine.find_spans(text))
    assert "2023" not in masked and "⟦P0⟧" in masked
    restored, problems = engine.unmask(masked, mapping)
    assert restored == text and problems == []
    _, problems = engine.unmask(masked.replace("⟦P0⟧", ""), mapping)
    assert problems
    _, problems = engine.unmask(masked + " ⟦P99⟧", mapping)
    assert any("unknown" in p for p in problems)


def test_validate_rewrite_flags_changed_numbers():
    engine = ProtectionEngine(ProcessingOptions())
    original = "Jordan's transportation sector emitted 5.2 million tonnes of CO2 in 2023 (Smith, 2024)."
    good = "In 2023, Jordan's transportation sector emitted 5.2 million tonnes of CO2 (Smith, 2024)."
    bad = "Jordan's transportation sector emitted 6.7 million tonnes of CO2 in 2023 (Smith, 2024)."
    assert validate_rewrite(original, good, engine) == []
    problems = validate_rewrite(original, bad, engine)
    assert any("Numerical" in p for p in problems)
    assert any("Citation" in p for p in validate_rewrite(original, good.replace(" (Smith, 2024)", ""), engine))
