from src.reporting.coverage_report import generate_coverage_report


def test_generates_documentation_coverage_report():
    report = generate_coverage_report(
        "tests/fixtures/matcher_example.py",
        "tests/fixtures/matcher_example.md",
    )

    assert report["total_symbols"] == 1
    assert report["documented_count"] == 1
    assert report["undocumented_count"] == 0
    assert report["coverage_percentage"] == 100.0

    assert report["documented"][0]["name"] == "calculate_total"
    assert report["undocumented"] == []
