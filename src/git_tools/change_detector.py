import subprocess
from pathlib import Path
from typing import Any


def get_changed_files(
    repository_path: str | Path,
    base_ref: str,
    target_ref: str = "HEAD",
) -> list[dict[str, Any]]:
    """
    Return files changed between two Git references.

    Each result contains the change status and affected file paths.
    Supports added, modified, deleted, copied, and renamed files.
    """
    repository = Path(repository_path).resolve()

    if not repository.is_dir():
        raise NotADirectoryError(
            f"Repository directory does not exist: {repository}"
        )

    def run_git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(repository), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        if result.returncode != 0:
            message = result.stderr.strip() or "Unknown Git error"
            raise RuntimeError(f"Git command failed: {message}")

        return result.stdout

    # Verify that the directory belongs to a Git repository.
    run_git("rev-parse", "--git-dir")

    # Compare two references using a NUL-delimited format.
    output = run_git(
        "diff",
        "--name-status",
        "-z",
        "--find-renames",
        base_ref,
        target_ref,
        "--",
    )

    fields = output.split("\0")
    changes: list[dict[str, Any]] = []
    index = 0

    while index < len(fields):
        status = fields[index]
        index += 1

        if not status:
            continue

        if status.startswith(("R", "C")):
            if index + 1 >= len(fields):
                raise RuntimeError(
                    "Unexpected Git output for a rename or copy."
                )

            old_path = fields[index]
            new_path = fields[index + 1]
            index += 2

            changes.append({
                "status": "renamed" if status.startswith("R") else "copied",
                "old_path": old_path,
                "path": new_path,
            })
        else:
            if index >= len(fields):
                raise RuntimeError(
                    "Unexpected Git output for a file change."
                )

            path = fields[index]
            index += 1

            status_code = status[0]

            status_map = {
                "A": "added",
                "M": "modified",
                "D": "deleted",
                "T": "type_changed",
                "U": "unmerged",
            }

            changes.append({
                "status": status_map.get(status_code, "unknown"),
                "path": path,
            })

    return changes