import json
from pathlib import Path
from typing import Any

from src.ai.discrepancy_detector import DocumentationDiscrepancyDetector
from src.analyzers.python_analyzer import analyze_python_file
from src.parsers.markdown_parser import parse_markdown_file


def analyze_documentation(
    source_file: str | Path,
    documentation_file: str | Path,
    detector: DocumentationDiscrepancyDetector | None = None,
) -> dict[str, Any]:
    """Analyze a Python file and its Markdown documentation for discrepancies."""

    source_path = Path(source_file)
    documentation_path = Path(documentation_file)

    source_analysis = analyze_python_file(source_path)
    documentation = parse_markdown_file(documentation_path)

    active_detector = detector or DocumentationDiscrepancyDetector()

    result = active_detector.detect(
        source_analysis=source_analysis,
        documentation_sections=documentation["sections"],
    )

    return {
        "source_file": str(source_path),
        "documentation_file": str(documentation_path),
        "source_symbol_count": len(source_analysis["symbols"]),
        "documentation_section_count": len(documentation["sections"]),
        "status": result["status"],
        "finding_count": result["finding_count"],
        "findings": result["findings"],
    }


def save_analysis_report(
    report: dict[str, Any],
    output_file: str | Path,
) -> Path:
    """Save an analysis report as JSON."""

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return output_path