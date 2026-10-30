import json
from unittest.mock import MagicMock

import pytest

from src.ai.discrepancy_detector import DocumentationDiscrepancyDetector


@pytest.fixture
def source_analysis():
    return {
        "file": "src/calculator.py",
        "symbols": [
            {
                "name": "add",
                "qualified_name": "add",
                "kind": "function",
                "signature": "a: int, b: int",
                "return_annotation": "int",
                "docstring": "Return the sum of two integers.",
                "line": 1,
            }
        ],
    }


@pytest.fixture
def documentation_sections():
    return [
        {
            "heading": "add",
            "heading_path": ["Calculator", "add"],
            "line": 10,
            "content": (
                "The add function accepts two integers "
                "and returns their product."
            ),
        }
    ]


@pytest.fixture
def mock_client():
    return MagicMock()


def test_detects_documentation_discrepancy(
    source_analysis,
    documentation_sections,
    mock_client,
):
    mock_client.generate.return_value = json.dumps({
        "findings": [
            {
                "symbol": "add",
                "documentation_heading": "add",
                "severity": "high",
                "issue": "Documentation incorrectly says product.",
                "evidence": "The function is described as returning a sum.",
                "suggested_correction": (
                    "The add function accepts two integers "
                    "and returns their sum."
                ),
            }
        ]
    })

    detector = DocumentationDiscrepancyDetector(mock_client)

    result = detector.detect(
        source_analysis,
        documentation_sections,
    )

    assert result["status"] == "completed"
    assert result["finding_count"] == 1
    assert result["findings"][0]["symbol"] == "add"
    assert result["findings"][0]["severity"] == "high"
    mock_client.generate.assert_called_once()


def test_returns_no_findings_for_empty_symbols(
    documentation_sections,
    mock_client,
):
    detector = DocumentationDiscrepancyDetector(mock_client)

    result = detector.detect(
        {"file": "src/calculator.py", "symbols": []},
        documentation_sections,
    )

    assert result == {
        "status": "completed",
        "findings": [],
        "finding_count": 0,
    }
    mock_client.generate.assert_not_called()


def test_rejects_invalid_json(
    source_analysis,
    documentation_sections,
    mock_client,
):
    mock_client.generate.return_value = "This is not JSON"

    detector = DocumentationDiscrepancyDetector(mock_client)

    with pytest.raises(ValueError, match="invalid JSON"):
        detector.detect(source_analysis, documentation_sections)


def test_rejects_invalid_severity(
    source_analysis,
    documentation_sections,
    mock_client,
):
    mock_client.generate.return_value = json.dumps({
        "findings": [
            {
                "symbol": "add",
                "documentation_heading": "add",
                "severity": "critical",
                "issue": "Incorrect description.",
                "evidence": "Evidence from the source.",
                "suggested_correction": "Correct the description.",
            }
        ]
    })

    detector = DocumentationDiscrepancyDetector(mock_client)

    with pytest.raises(ValueError, match="invalid severity"):
        detector.detect(source_analysis, documentation_sections)


def test_rejects_missing_finding_fields(
    source_analysis,
    documentation_sections,
    mock_client,
):
    mock_client.generate.return_value = json.dumps({
        "findings": [
            {
                "symbol": "add",
                "severity": "low",
            }
        ]
    })

    detector = DocumentationDiscrepancyDetector(mock_client)

    with pytest.raises(ValueError, match="missing fields"):
        detector.detect(source_analysis, documentation_sections)


def test_rejects_invalid_source_symbols(
    documentation_sections,
    mock_client,
):
    detector = DocumentationDiscrepancyDetector(mock_client)

    with pytest.raises(ValueError, match="list of symbols"):
        detector.detect(
            {"symbols": "not a list"},
            documentation_sections,
        )

    mock_client.generate.assert_not_called()