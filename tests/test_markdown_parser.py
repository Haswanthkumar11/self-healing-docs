import pytest

from src.parsers.markdown_parser import parse_markdown_file


FIXTURE = "tests/fixtures/sample_docs.md"


def test_extracts_markdown_headings():
    result = parse_markdown_file(FIXTURE)

    headings = [
        section["heading"]
        for section in result["sections"]
    ]

    assert headings == [
        "Authentication",
        "Token Validation",
        "Database",
        "Example Code",
    ]


def test_extracts_nested_heading_path():
    result = parse_markdown_file(FIXTURE)

    token_section = next(
        section
        for section in result["sections"]
        if section["heading"] == "Token Validation"
    )

    assert token_section["heading_path"] == [
        "Authentication",
        "Token Validation",
    ]


def test_preserves_section_content():
    result = parse_markdown_file(FIXTURE)

    auth_section = result["sections"][0]

    assert "Users authenticate with their credentials." in (
        auth_section["content"]
    )


def test_ignores_headings_inside_fenced_code_blocks():
    result = parse_markdown_file(FIXTURE)

    headings = [
        section["heading"]
        for section in result["sections"]
    ]

    assert "# This is a code comment, not a Markdown heading." not in (
        headings
    )


def test_records_heading_line_numbers():
    result = parse_markdown_file(FIXTURE)

    auth_section = result["sections"][0]

    assert auth_section["line"] == 1


def test_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        parse_markdown_file("tests/fixtures/missing.md")


def test_rejects_non_markdown_file():
    with pytest.raises(ValueError, match="Expected a Markdown file"):
        parse_markdown_file("src/config.py")