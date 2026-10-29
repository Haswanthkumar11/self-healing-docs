import subprocess
from pathlib import Path

import pytest

from src.git_tools.change_detector import get_changed_files


def run_git(repository: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def create_test_repository(tmp_path: Path) -> tuple[Path, str]:
    repository = tmp_path / "repo"
    repository.mkdir()

    run_git(repository, "init")
    run_git(repository, "config", "user.name", "Test User")
    run_git(repository, "config", "user.email", "test@example.com")

    (repository / "app.py").write_text(
        "def greet():\n    return 'hello'\n",
        encoding="utf-8",
    )
    (repository / "README.md").write_text(
        "# Example\n",
        encoding="utf-8",
    )

    run_git(repository, "add", ".")
    run_git(repository, "commit", "-m", "Initial commit")

    base_ref = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    return repository, base_ref


def test_detects_modified_file(tmp_path: Path) -> None:
    repository, base_ref = create_test_repository(tmp_path)

    (repository / "app.py").write_text(
        "def greet(name='world'):\n    return f'hello {name}'\n",
        encoding="utf-8",
    )
    run_git(repository, "add", "app.py")
    run_git(repository, "commit", "-m", "Update greeting")

    changes = get_changed_files(repository, base_ref)

    assert changes == [
        {"status": "modified", "path": "app.py"}
    ]


def test_detects_added_file(tmp_path: Path) -> None:
    repository, base_ref = create_test_repository(tmp_path)

    (repository / "utils.py").write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )
    run_git(repository, "add", "utils.py")
    run_git(repository, "commit", "-m", "Add utility")

    changes = get_changed_files(repository, base_ref)

    assert changes == [
        {"status": "added", "path": "utils.py"}
    ]


def test_detects_deleted_file(tmp_path: Path) -> None:
    repository, base_ref = create_test_repository(tmp_path)

    (repository / "app.py").unlink()
    run_git(repository, "add", "-u")
    run_git(repository, "commit", "-m", "Delete application")

    changes = get_changed_files(repository, base_ref)

    assert changes == [
        {"status": "deleted", "path": "app.py"}
    ]


def test_returns_empty_list_when_nothing_changed(
    tmp_path: Path,
) -> None:
    repository, base_ref = create_test_repository(tmp_path)

    assert get_changed_files(repository, base_ref) == []


def test_rejects_nonexistent_repository(
    tmp_path: Path,
) -> None:
    with pytest.raises(NotADirectoryError):
        get_changed_files(tmp_path / "missing", "HEAD")


def test_rejects_invalid_git_reference(
    tmp_path: Path,
) -> None:
    repository, base_ref = create_test_repository(tmp_path)

    with pytest.raises(RuntimeError, match="Git command failed"):
        get_changed_files(repository, "reference-that-does-not-exist")