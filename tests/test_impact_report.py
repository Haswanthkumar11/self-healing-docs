import subprocess
from pathlib import Path

from src.reporting.impact_report import generate_impact_report


def run_git(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def create_repository(tmp_path: Path) -> tuple[Path, str]:
    repository = tmp_path / "repo"
    source_dir = repository / "src"
    docs_dir = repository / "docs"

    source_dir.mkdir(parents=True)
    docs_dir.mkdir()

    run_git(repository, "init")
    run_git(repository, "config", "user.name", "Test User")
    run_git(repository, "config", "user.email", "test@example.com")

    (source_dir / "calculator.py").write_text(
        "def calculate_total(price: float, quantity: int = 1) -> float:\n"
        "    return price * quantity\n",
        encoding="utf-8",
    )

    (docs_dir / "calculator.md").write_text(
        "# Calculator\n\n"
        "## calculate_total\n\n"
        "Calculates the total price from price and quantity.\n",
        encoding="utf-8",
    )

    (repository / "README.md").write_text(
        "# Test repository\n",
        encoding="utf-8",
    )

    run_git(repository, "add", ".")
    run_git(repository, "commit", "-m", "Initial commit")

    base_ref = run_git(repository, "rev-parse", "HEAD")

    return repository, base_ref


def test_reports_documentation_for_modified_python_file(
    tmp_path: Path,
) -> None:
    repository, base_ref = create_repository(tmp_path)

    source_file = repository / "src" / "calculator.py"
    source_file.write_text(
        "def calculate_total(price: float, quantity: int = 1) -> float:\n"
        "    return price * quantity\n\n"
        "def apply_discount(total: float, rate: float) -> float:\n"
        "    return total * (1 - rate)\n",
        encoding="utf-8",
    )

    run_git(repository, "add", "src/calculator.py")
    run_git(repository, "commit", "-m", "Add discount function")

    report = generate_impact_report(
        repository,
        base_ref,
        documentation_root="docs",
    )

    assert report["changed_file_count"] == 1
    assert report["python_files_analyzed"] == 1
    assert len(report["file_reports"]) == 1

    file_report = report["file_reports"][0]

    assert file_report["source_file"] == "src/calculator.py"
    assert file_report["change_status"] == "modified"
    assert len(file_report["matches"]) == 1
    assert file_report["matches"][0]["symbol_name"] == "calculate_total"

    assert [
        item["name"]
        for item in file_report["unmatched_symbols"]
    ] == ["apply_discount"]

    assert report["summary"]["documentation_matches"] == 1
    assert report["summary"]["unmatched_symbols"] == 1
    assert report["analysis_errors"] == []


def test_ignores_changes_to_non_python_files(
    tmp_path: Path,
) -> None:
    repository, base_ref = create_repository(tmp_path)

    (repository / "README.md").write_text(
        "# Updated test repository\n",
        encoding="utf-8",
    )

    run_git(repository, "add", "README.md")
    run_git(repository, "commit", "-m", "Update README")

    report = generate_impact_report(
        repository,
        base_ref,
        documentation_root="docs",
    )

    assert report["changed_file_count"] == 1
    assert report["python_files_analyzed"] == 0
    assert report["file_reports"] == []
    assert report["ignored_changes"] == [
        {"path": "README.md", "status": "modified"}
    ]


def test_reports_deleted_python_files(
    tmp_path: Path,
) -> None:
    repository, base_ref = create_repository(tmp_path)

    (repository / "src" / "calculator.py").unlink()

    run_git(repository, "add", "-u")
    run_git(repository, "commit", "-m", "Delete calculator")

    report = generate_impact_report(
        repository,
        base_ref,
        documentation_root="docs",
    )

    assert report["deleted_python_files"] == ["src/calculator.py"]
    assert report["python_files_analyzed"] == 0
    assert report["summary"]["deleted_python_files"] == 1
