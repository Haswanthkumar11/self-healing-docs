import pytest

from src.ai.documentation_repair import (
    create_correction_proposal,
    apply_approved_correction,
)


@pytest.fixture
def sample_finding():
    return {
        "symbol": "calculate_total",
        "documentation_heading": "Pricing",
        "severity": "medium",
        "issue": "Documentation describes an outdated calculation.",
        "evidence": "The function accepts a discount parameter.",
        "suggested_correction": "Document the discount parameter.",
    }


@pytest.fixture
def documentation_file(tmp_path):
    path = tmp_path / "guide.md"
    path.write_text(
        "# Pricing\n\nCalculates the total price.\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def sample_proposal(sample_finding, documentation_file):
    return create_correction_proposal(
        finding=sample_finding,
        original_text="Calculates the total price.",
        replacement_text=(
            "Calculates the total price after applying a discount."
        ),
        documentation_file=documentation_file,
    )


def test_creates_pending_correction_proposal(sample_proposal):
    assert sample_proposal["status"] == "pending_approval"
    assert sample_proposal["approved"] is False
    assert sample_proposal["documentation_file_hash"]
    assert "original" in sample_proposal["diff"]
    assert "proposed" in sample_proposal["diff"]


def test_rejects_empty_original_text(sample_finding, documentation_file):
    with pytest.raises(ValueError, match="Original text"):
        create_correction_proposal(
            sample_finding,
            "  ",
            "Updated documentation.",
            documentation_file,
        )


def test_rejects_empty_replacement_text(sample_finding, documentation_file):
    with pytest.raises(ValueError, match="Replacement text"):
        create_correction_proposal(
            sample_finding,
            "Calculates the total price.",
            "  ",
            documentation_file,
        )


def test_rejects_missing_documentation_file(sample_finding, tmp_path):
    with pytest.raises(FileNotFoundError, match="Documentation file not found"):
        create_correction_proposal(
            sample_finding,
            "Original documentation.",
            "Updated documentation.",
            tmp_path / "missing.md",
        )


def test_rejects_original_text_that_is_missing_or_duplicated(
    sample_finding, documentation_file
):
    with pytest.raises(ValueError, match="exactly once"):
        create_correction_proposal(
            sample_finding,
            "Text that does not exist.",
            "Updated documentation.",
            documentation_file,
        )


def test_correction_requires_explicit_approval(
    sample_proposal, documentation_file
):
    with pytest.raises(PermissionError, match="approval is required"):
        apply_approved_correction(documentation_file, sample_proposal)

    assert "Calculates the total price." in documentation_file.read_text(
        encoding="utf-8"
    )


def test_applies_approved_correction(sample_proposal, documentation_file):
    result = apply_approved_correction(
        documentation_file,
        sample_proposal,
        approved=True,
    )

    updated_text = documentation_file.read_text(encoding="utf-8")

    assert result["status"] == "applied"
    assert result["changed"] is True
    assert (
        "Calculates the total price after applying a discount."
        in updated_text
    )
    assert sample_proposal["approved"] is True


def test_rejects_documentation_changed_after_proposal_creation(
    sample_proposal, documentation_file
):
    documentation_file.write_text(
        "# Pricing\n\nThe pricing rules have changed.\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Documentation changed"):
        apply_approved_correction(
            documentation_file,
            sample_proposal,
            approved=True,
        )


def test_rejects_a_different_documentation_file(
    sample_proposal, tmp_path
):
    other_file = tmp_path / "other.md"
    other_file.write_text(
        "# Pricing\n\nCalculates the total price.\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="does not match"):
        apply_approved_correction(
            other_file,
            sample_proposal,
            approved=True,
        )


def test_rejects_reapplying_an_applied_proposal(
    sample_proposal, documentation_file
):
    apply_approved_correction(
        documentation_file,
        sample_proposal,
        approved=True,
    )

    with pytest.raises(ValueError, match="not pending approval"):
        apply_approved_correction(
            documentation_file,
            sample_proposal,
            approved=True,
        )


def test_rejects_incomplete_finding(documentation_file):
    with pytest.raises(ValueError, match="missing required fields"):
        create_correction_proposal(
            finding={"symbol": "calculate_total"},
            original_text="Calculates the total price.",
            replacement_text="Updated documentation.",
            documentation_file=documentation_file,
        )