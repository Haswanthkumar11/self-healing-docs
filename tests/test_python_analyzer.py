from pathlib import Path

import pytest

from src.analyzers.python_analyzer import analyze_python_file


FIXTURE = Path(__file__).parent / "fixtures" / "sample_module.py"


def test_extracts_function_signature_and_docstring():
    result = analyze_python_file(FIXTURE)

    function = next(
        item for item in result["symbols"]
        if item["qualified_name"] == "calculate_total"
    )

    assert function["kind"] == "function"
    assert function["signature"] == "price: float, quantity: int=1"
    assert function["return_annotation"] == "float"
    assert function["docstring"] == "Calculate the total price."
    assert function["line"] == 4


def test_extracts_async_function():
    result = analyze_python_file(FIXTURE)

    function = next(
        item for item in result["symbols"]
        if item["qualified_name"] == "fetch_record"
    )

    assert function["kind"] == "async_function"
    assert function["return_annotation"] == "dict"


def test_extracts_class_and_method():
    result = analyze_python_file(FIXTURE)

    calculator = next(
        item for item in result["symbols"]
        if item["qualified_name"] == "Calculator"
    )

    method = next(
        item for item in result["symbols"]
        if item["qualified_name"] == "Calculator.add"
    )

    assert calculator["kind"] == "class"
    assert calculator["docstring"] == "A simple calculator."
    assert method["signature"] == "self, a: int, b: int=0"
    assert method["return_annotation"] == "int"


def test_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        analyze_python_file("missing_module.py")


def test_rejects_non_python_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError, match="Expected a Python file"):
        analyze_python_file(file_path)