from src.matching.documentation_matcher import (
    match_symbols_to_documentation,
)


def test_matches_python_symbol_to_documentation_heading():
    matches = match_symbols_to_documentation(
        "tests/fixtures/matcher_example.py",
        "tests/fixtures/matcher_example.md",
    )

    assert len(matches) == 1

    match = matches[0]

    assert match["symbol_name"] == "calculate_total"
    assert match["documentation_heading"] == "calculate_total"
    assert match["symbol_kind"] == "function"
    assert "multiplying the price" in match["documentation_content"]


def test_returns_no_match_when_documentation_heading_is_missing():
    matches = match_symbols_to_documentation(
        "tests/fixtures/matcher_example.py",
        "tests/fixtures/sample_docs.md",
    )

    assert matches == []

