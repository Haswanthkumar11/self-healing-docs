import json
from unittest.mock import MagicMock, patch

from src.ai.documentation_pipeline import (
    analyze_documentation,
    save_analysis_report,
)


def test_pipeline_analyzes_source_and_documentation(tmp_path):
    source_file = tmp_path / "example.py"
    documentation_file = tmp_path / "example.md"

    source_file.write_text(
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n",
        encoding="utf-8",
    )
    documentation_file.write_text(
        "# add\n\nReturns the sum of two integers.\n",
        encoding="utf-8",
    )

    mock_detector = MagicMock()
    mock_detector.detect.return_value = {
        "status": "completed",
        "findings": [],
        "finding_count": 0,
    }

    result = analyze_documentation(
        source_file,
        documentation_file,
        detector=mock_detector,
    )

    assert result["source_symbol_count"] == 1
    assert result["documentation_section_count"] == 1
    assert result["status"] == "completed"
    assert result["finding_count"] == 0
    assert result["findings"] == []

    mock_detector.detect.assert_called_once()


def test_pipeline_returns_detector_findings(tmp_path):
    source_file = tmp_path / "example.py"
    documentation_file = tmp_path / "example.md"

    source_file.write_text(
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n",
        encoding="utf-8",
    )
    documentation_file.write_text(
        "# add\n\nReturns the product of two integers.\n",
        encoding="utf-8",
    )

    mock_detector = MagicMock()
    mock_detector.detect.return_value = {
        "status": "completed",
        "findings": [
            {
                "symbol": "add",
                "documentation_heading": "add",
                "severity": "high",
                "issue": "Documentation describes multiplication.",
                "evidence": "The source uses addition.",
                "suggested_correction": "Describe the sum operation.",
            }
        ],
        "finding_count": 1,
    }

    result = analyze_documentation(
        source_file,
        documentation_file,
        detector=mock_detector,
    )

    assert result["finding_count"] == 1
    assert result["findings"][0]["symbol"] == "add"
    assert result["findings"][0]["severity"] == "high"


def test_pipeline_rejects_missing_source_file(tmp_path):
    documentation_file = tmp_path / "example.md"
    documentation_file.write_text("# Example\n", encoding="utf-8")

    try:
        analyze_documentation(
            tmp_path / "missing.py",
            documentation_file,
            detector=MagicMock(),
        )
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_save_analysis_report_writes_valid_json(tmp_path):
    report = {
        "source_file": "example.py",
        "documentation_file": "example.md",
        "status": "completed",
        "finding_count": 0,
        "findings": [],
    }

    output_file = tmp_path / "reports" / "analysis.json"

    saved_path = save_analysis_report(report, output_file)

    assert saved_path.is_file()
    assert json.loads(saved_path.read_text(encoding="utf-8")) == report


def test_pipeline_uses_injected_detector_without_creating_gemini_client(
    tmp_path,
):
    source_file = tmp_path / "example.py"
    documentation_file = tmp_path / "example.md"

    source_file.write_text(
        "def example() -> str:\n"
        "    return 'hello'\n",
        encoding="utf-8",
    )
    documentation_file.write_text(
        "# example\n\nReturns a greeting.\n",
        encoding="utf-8",
    )

    mock_detector = MagicMock()
    mock_detector.detect.return_value = {
        "status": "completed",
        "findings": [],
        "finding_count": 0,
    }

    with patch(
        "src.ai.documentation_pipeline.DocumentationDiscrepancyDetector"
    ) as detector_class:
        analyze_documentation(
            source_file,
            documentation_file,
            detector=mock_detector,
        )

    detector_class.assert_not_called()
    mock_detector.detect.assert_called_once()