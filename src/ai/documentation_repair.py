import difflib
import hashlib
from pathlib import Path
from typing import Any


def create_correction_proposal(
    finding: dict[str, Any],
    original_text: str,
    replacement_text: str,
    documentation_file: str | Path,
) -> dict[str, Any]:
    """Create a correction proposal tied to the current documentation file."""

    required_fields = {
        "symbol",
        "documentation_heading",
        "severity",
        "issue",
        "evidence",
        "suggested_correction",
    }

    if not isinstance(finding, dict):
        raise ValueError("Finding must be a dictionary.")

    missing_fields = required_fields - finding.keys()
    if missing_fields:
        raise ValueError(
            f"Finding is missing required fields: "
            f"{', '.join(sorted(missing_fields))}."
        )

    if not isinstance(original_text, str) or not original_text.strip():
        raise ValueError("Original text must not be empty.")

    if not isinstance(replacement_text, str) or not replacement_text.strip():
        raise ValueError("Replacement text must not be empty.")

    path = Path(documentation_file)
    if not path.is_file():
        raise FileNotFoundError(f"Documentation file not found: {path}")

    current_text = path.read_text(encoding="utf-8")

    if current_text.count(original_text) != 1:
        raise ValueError(
            "Original text must appear exactly once in the documentation file."
        )

    file_hash = hashlib.sha256(current_text.encode("utf-8")).hexdigest()

    diff = list(
        difflib.unified_diff(
            original_text.splitlines(),
            replacement_text.splitlines(),
            fromfile="original",
            tofile="proposed",
            lineterm="",
        )
    )

    return {
        "status": "pending_approval",
        "symbol": finding["symbol"],
        "documentation_heading": finding["documentation_heading"],
        "severity": finding["severity"],
        "issue": finding["issue"],
        "evidence": finding["evidence"],
        "documentation_file": str(path.resolve()),
        "original_text": original_text,
        "replacement_text": replacement_text,
        "diff": "\n".join(diff),
        "documentation_file_hash": file_hash,
        "approved": False,
    }


def apply_approved_correction(
    documentation_file: str | Path,
    proposal: dict[str, Any],
    approved: bool = False,
) -> dict[str, Any]:
    """Apply a correction only after approval and a stale-file check."""

    if approved is not True:
        raise PermissionError(
            "Correction not applied. Explicit approval is required."
        )

    if not isinstance(proposal, dict):
        raise ValueError("Proposal must be a dictionary.")

    if proposal.get("status") != "pending_approval":
        raise ValueError("Proposal is not pending approval.")

    path = Path(documentation_file)

    if not path.is_file():
        raise FileNotFoundError(f"Documentation file not found: {path}")

    expected_path = proposal.get("documentation_file")
    if not expected_path or path.resolve() != Path(expected_path).resolve():
        raise ValueError(
            "Documentation file does not match the file used for this proposal."
        )

    original_text = proposal.get("original_text")
    replacement_text = proposal.get("replacement_text")
    expected_hash = proposal.get("documentation_file_hash")

    if not isinstance(original_text, str) or not original_text:
        raise ValueError("Proposal has no valid original text.")

    if not isinstance(replacement_text, str) or not replacement_text.strip():
        raise ValueError("Proposal has no valid replacement text.")

    if not isinstance(expected_hash, str) or not expected_hash:
        raise ValueError("Proposal is missing the original documentation file hash.")

    current_text = path.read_text(encoding="utf-8")
    current_hash = hashlib.sha256(current_text.encode("utf-8")).hexdigest()

    if current_hash != expected_hash:
        raise ValueError(
            "Documentation changed since the proposal was created. "
            "Generate a new proposal before applying the correction."
        )

    occurrences = current_text.count(original_text)
    if occurrences != 1:
        raise ValueError(
            "Correction requires the original text to appear exactly once. "
            f"Found {occurrences} occurrences; no changes were made."
        )

    updated_text = current_text.replace(original_text, replacement_text, 1)
    path.write_text(updated_text, encoding="utf-8")

    proposal["status"] = "applied"
    proposal["approved"] = True

    return {
        "status": "applied",
        "documentation_file": str(path),
        "changed": True,
    }