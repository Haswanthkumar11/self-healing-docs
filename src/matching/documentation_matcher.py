from pathlib import Path
from typing import Any

from src.analyzers.python_analyzer import analyze_python_file
from src.parsers.markdown_parser import parse_markdown_file


def match_symbols_to_documentation(
    python_file: str | Path,
    markdown_file: str | Path,
) -> list[dict[str, Any]]:
    """
    Match Python functions and classes to Markdown sections.

    A section is considered a candidate when its heading matches
    a Python symbol's name or qualified name.
    """
    analysis = analyze_python_file(python_file)
    documentation = parse_markdown_file(markdown_file)

    symbols = analysis["symbols"]
    sections = documentation["sections"]

    matches: list[dict[str, Any]] = []

    for symbol in symbols:
        symbol_name = symbol["name"].casefold()
        qualified_name = symbol["qualified_name"].casefold()

        for section in sections:
            heading = section["heading"].strip().casefold()

            if heading in {symbol_name, qualified_name}:
                matches.append({
                    "symbol_name": symbol["name"],
                    "qualified_name": symbol["qualified_name"],
                    "symbol_kind": symbol["kind"],
                    "symbol_line": symbol["line"],
                    "documentation_heading": section["heading"],
                    "documentation_heading_path": section["heading_path"],
                    "documentation_line": section["line"],
                    "documentation_content": section["content"],
                })

    return matches