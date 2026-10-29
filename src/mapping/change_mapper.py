from pathlib import Path
from typing import Any

from src.analyzers.python_analyzer import analyze_python_file
from src.matching.documentation_matcher import (
    match_symbols_to_documentation,
)


def map_changed_file_to_documentation(
    repository_path: str | Path,
    changed_file: str | Path,
    documentation_root: str | Path,
) -> dict[str, Any]:
    """
    Find candidate Markdown documentation for a changed Python file.

    Matching is based on Python symbol names and Markdown headings.
    This function identifies candidates; it does not determine
    whether the documentation is actually outdated.
    """
    repository = Path(repository_path).resolve()
    changed_path = Path(changed_file)

    if not changed_path.is_absolute():
        changed_path = repository / changed_path

    changed_path = changed_path.resolve()

    docs_root = Path(documentation_root)
    if not docs_root.is_absolute():
        docs_root = repository / docs_root

    docs_root = docs_root.resolve()

    if not repository.is_dir():
        raise NotADirectoryError(
            f"Repository directory does not exist: {repository}"
        )

    if not changed_path.is_file():
        raise FileNotFoundError(
            f"Changed source file does not exist: {changed_path}"
        )

    if changed_path.suffix.lower() != ".py":
        raise ValueError(
            f"Expected a Python source file: {changed_path}"
        )

    if not changed_path.is_relative_to(repository):
        raise ValueError(
            "Changed source file must be inside the repository."
        )

    if not docs_root.is_dir():
        raise NotADirectoryError(
            f"Documentation directory does not exist: {docs_root}"
        )

    analysis = analyze_python_file(changed_path)

    relative_source = changed_path.relative_to(repository)
    source_stem = changed_path.stem.casefold()

    markdown_files = sorted(
        path for path in docs_root.rglob("*.md")
        if path.is_file()
    )

    # First look for a Markdown file with the same filename stem.
    # If one exists, prioritize it. Otherwise, examine all Markdown
    # files because documentation may use a different filename.
    same_name_docs = [
        path for path in markdown_files
        if path.stem.casefold() == source_stem
    ]

    candidate_docs = same_name_docs or markdown_files

    documentation_matches: list[dict[str, Any]] = []

    for markdown_file in candidate_docs:
        matches = match_symbols_to_documentation(
            changed_path,
            markdown_file,
        )

        for match in matches:
            documentation_matches.append({
                **match,
                "source_file": relative_source.as_posix(),
                "documentation_file": (
                    markdown_file.relative_to(repository).as_posix()
                    if markdown_file.is_relative_to(repository)
                    else str(markdown_file)
                ),
            })

    return {
        "source_file": relative_source.as_posix(),
        "symbols_found": len(analysis["symbols"]),
        "documentation_files_considered": [
            str(path.relative_to(repository))
            if path.is_relative_to(repository)
            else str(path)
            for path in candidate_docs
        ],
        "matches": documentation_matches,
        "unmatched_symbols": [
            {
                "name": symbol["name"],
                "qualified_name": symbol["qualified_name"],
                "kind": symbol["kind"],
                "line": symbol["line"],
            }
            for symbol in analysis["symbols"]
            if not any(
                match["qualified_name"] == symbol["qualified_name"]
                for match in documentation_matches
            )
        ],
    }