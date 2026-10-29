from pathlib import Path

import pytest

from src.mapping.change_mapper import (
    map_changed_file_to_documentation,
)


def test_maps_changed_python_file_to_matching_documentation(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repo"
    source_dir = repository / "src"
    docs_dir = repository / "docs"

    source_dir.mkdir(parents=True)
    docs_dir.mkdir(parents=True)

    source_file = source_dir / "calculator.py"
    source_file.write_text(
        "def calculate_total(price: float, quantity: int = 1) -> float:\n"
        "    return price * quantity\n",
        encoding="utf-8",
    )

    documentation_file = docs_dir / "calculator.md"
    documentation_file.write_text(
        "# Calculator\n\n"
        "## calculate_total\n\n"
        "Calculates the total price using price and quantity.\n",
        encoding="utf-8",
    )

    result = map_changed_file_to_documentation(
        repository,
        "src/calculator.py",
        "docs",
    )

    assert result["source_file"] == "src/calculator.py"
    assert result["symbols_found"] == 1
    assert len(result["matches"]) == 1
    assert (
        result["matches"][0]["documentation_heading"]
        == "calculate_total"
    )
    assert result["unmatched_symbols"] == []


def test_reports_symbol_without_matching_documentation(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repo"
    source_dir = repository / "src"
    docs_dir = repository / "docs"

    source_dir.mkdir(parents=True)
    docs_dir.mkdir(parents=True)

    source_file = source_dir / "calculator.py"
    source_file.write_text(
        "def calculate_total(price, quantity):\n"
        "    return price * quantity\n",
        encoding="utf-8",
    )

    (docs_dir / "calculator.md").write_text(
        "# Calculator\n\n"
        "## Installation\n\n"
        "Install the package before using it.\n",
        encoding="utf-8",
    )

    result = map_changed_file_to_documentation(
        repository,
        "src/calculator.py",
        "docs",
    )

    assert result["matches"] == []
    assert len(result["unmatched_symbols"]) == 1
    assert result["unmatched_symbols"][0]["name"] == "calculate_total"


def test_rejects_non_python_file(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    docs_dir = repository / "docs"

    docs_dir.mkdir(parents=True)
    markdown_file = repository / "README.md"
    markdown_file.write_text("# Example\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Expected a Python source file"):
        map_changed_file_to_documentation(
            repository,
            markdown_file,
            docs_dir,
        )


def test_rejects_source_file_outside_repository(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repo"
    docs_dir = repository / "docs"

    docs_dir.mkdir(parents=True)

    outside_file = tmp_path / "outside.py"
    outside_file.write_text(
        "def example():\n    return True\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="inside the repository"):
        map_changed_file_to_documentation(
            repository,
            outside_file,
            docs_dir,
        )


def test_rejects_missing_documentation_directory(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repo"
    source_dir = repository / "src"

    source_dir.mkdir(parents=True)

    source_file = source_dir / "calculator.py"
    source_file.write_text(
        "def calculate_total(price, quantity):\n"
        "    return price * quantity\n",
        encoding="utf-8",
    )

    with pytest.raises(NotADirectoryError, match="Documentation directory"):
        map_changed_file_to_documentation(
            repository,
            source_file,
            repository / "missing_docs",
        )