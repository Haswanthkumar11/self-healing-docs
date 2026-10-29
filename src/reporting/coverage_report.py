from pathlib import Path
from typing import Any

from src.analyzers.python_analyzer import analyze_python_file
from src.parsers.markdown_parser import parse_markdown_file


def generate_coverage_report(
    python_file: str | Path,
    markdown_file: str | Path,
) -> dict[str, Any]:
    """
    Report which Python functions and classes have matching
    Markdown headings and which do not.
    """
    analysis = analyze_python_file(python_file)
    documentation = parse_markdown_file(markdown_file)

    symbols = analysis["symbols"]
    sections = documentation["sections"]

    documented_names = {
        section["heading"].strip().casefold()
        for section in sections
    }

    documented: list[dict[str, Any]] = []
    undocumented: list[dict[str, Any]] = []

    for symbol in symbols:
        symbol_name = symbol["name"]
        qualified_name = symbol["qualified_name"]

        is_documented = (
            symbol_name.casefold() in documented_names
            or qualified_name.casefold() in documented_names
        )

        entry = {
            "name": symbol_name,
            "qualified_name": qualified_name,
            "kind": symbol["kind"],
            "line": symbol["line"],
        }

        if is_documented:
            documented.append(entry)
        else:
            undocumented.append(entry)

    total = len(symbols)
    documented_count = len(documented)

    coverage_percentage = (
        round(documented_count / total * 100, 2)
        if total
        else 100.0
    )

    return {
        "python_file": str(python_file),
        "markdown_file": str(markdown_file),
        "total_symbols": total,
        "documented_count": documented_count,
        "undocumented_count": len(undocumented),
        "coverage_percentage": coverage_percentage,
        "documented": documented,
        "undocumented": undocumented,
    }
