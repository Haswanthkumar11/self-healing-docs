from pathlib import Path
from typing import Any

from src.git_tools.change_detector import get_changed_files
from src.mapping.change_mapper import map_changed_file_to_documentation


def generate_impact_report(
    repository_path: str | Path,
    base_ref: str,
    target_ref: str = "HEAD",
    documentation_root: str | Path = "docs",
) -> dict[str, Any]:
    """
    Generate a documentation impact report for changed Python files.

    Added and modified Python files outside test directories are
    analyzed for matching Markdown documentation. Deleted Python
    files are reported separately because their source is unavailable.
    """
    repository = Path(repository_path).resolve()

    if not repository.is_dir():
        raise NotADirectoryError(
            f"Repository directory does not exist: {repository}"
        )

    changes = get_changed_files(
        repository,
        base_ref,
        target_ref,
    )

    python_changes: list[dict[str, Any]] = []
    deleted_python_files: list[str] = []
    ignored_changes: list[dict[str, str]] = []

    for change in changes:
        path = change["path"]
        relative_path = Path(path)

        # Ignore test files when analyzing documentation coverage.
        # Git still reports these files in changed_file_count.
        if (
            relative_path.suffix.lower() == ".py"
            and "tests" in relative_path.parts
        ):
            ignored_changes.append({
                "path": path,
                "status": change["status"],
            })
            continue

        if relative_path.suffix.lower() != ".py":
            ignored_changes.append({
                "path": path,
                "status": change["status"],
            })
            continue

        if change["status"] == "deleted":
            deleted_python_files.append(path)
        elif change["status"] in {"added", "modified"}:
            python_changes.append(change)
        else:
            ignored_changes.append({
                "path": path,
                "status": change["status"],
            })

    file_reports: list[dict[str, Any]] = []
    analysis_errors: list[dict[str, str]] = []

    for change in python_changes:
        try:
            mapping = map_changed_file_to_documentation(
                repository,
                change["path"],
                documentation_root,
            )

            file_reports.append({
                "source_file": change["path"],
                "change_status": change["status"],
                "documentation_files_considered": (
                    mapping["documentation_files_considered"]
                ),
                "matches": mapping["matches"],
                "unmatched_symbols": mapping["unmatched_symbols"],
            })
        except (
            FileNotFoundError,
            NotADirectoryError,
            ValueError,
        ) as exc:
            analysis_errors.append({
                "source_file": change["path"],
                "error": str(exc),
            })

    total_matches = sum(
        len(report["matches"])
        for report in file_reports
    )

    total_unmatched_symbols = sum(
        len(report["unmatched_symbols"])
        for report in file_reports
    )

    return {
        "base_ref": base_ref,
        "target_ref": target_ref,
        "changed_file_count": len(changes),
        "python_files_analyzed": len(file_reports),
        "deleted_python_files": deleted_python_files,
        "ignored_changes": ignored_changes,
        "file_reports": file_reports,
        "analysis_errors": analysis_errors,
        "summary": {
            "documentation_matches": total_matches,
            "unmatched_symbols": total_unmatched_symbols,
            "deleted_python_files": len(deleted_python_files),
            "analysis_errors": len(analysis_errors),
        },
    }