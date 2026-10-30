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

def test_matches_python_symbol_to_documentation_alias(tmp_path):
    python_file = tmp_path / "change_detector.py"
    markdown_file = tmp_path / "git-guide.md"

    python_file.write_text(
        "def get_changed_files():\n"
        '    """Detect changed Git files."""\n'
        "    return []\n",
        encoding="utf-8",
    )

    markdown_file.write_text(
        "# Git Change Detector\n\n"
        "Identifies files changed between Git references.\n",
        encoding="utf-8",
    )

    matches = match_symbols_to_documentation(
        python_file,
        markdown_file,
    )

    assert len(matches) == 1
    assert matches[0]["symbol_name"] == "get_changed_files"
    assert matches[0]["documentation_heading"] == "Git Change Detector"

