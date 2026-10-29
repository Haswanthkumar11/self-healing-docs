import ast
from pathlib import Path
from typing import Any


def analyze_python_file(file_path: str | Path) -> dict[str, Any]:
    """
    Extract classes, functions, signatures, docstrings,
    and source locations from a Python file.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Python file not found: {path}")

    if path.suffix.lower() != ".py":
        raise ValueError(f"Expected a Python file: {path}")

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    symbols: list[dict[str, Any]] = []

    def source_text(node: ast.AST | None) -> str | None:
        if node is None:
            return None
        return ast.get_source_segment(source, node)

    def format_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Build a readable signature from a function's AST."""

        args = node.args
        parameters: list[str] = []

        # Positional-only and regular positional parameters.
        positional = args.posonlyargs + args.args
        defaults_start = len(positional) - len(args.defaults)

        for index, argument in enumerate(positional):
            parameter = argument.arg

            if argument.annotation is not None:
                parameter += f": {source_text(argument.annotation)}"

            default_index = index - defaults_start
            if default_index >= 0:
                parameter += f"={source_text(args.defaults[default_index])}"

            parameters.append(parameter)

            # "/" marks the end of positional-only parameters.
            if (
                args.posonlyargs
                and index == len(args.posonlyargs) - 1
            ):
                parameters.append("/")

        # *args or a bare * for keyword-only parameters.
        if args.vararg is not None:
            vararg = f"*{args.vararg.arg}"

            if args.vararg.annotation is not None:
                vararg += f": {source_text(args.vararg.annotation)}"

            parameters.append(vararg)

        elif args.kwonlyargs:
            parameters.append("*")

        # Keyword-only parameters.
        for argument, default in zip(args.kwonlyargs, args.kw_defaults):
            parameter = argument.arg

            if argument.annotation is not None:
                parameter += f": {source_text(argument.annotation)}"

            if default is not None:
                parameter += f"={source_text(default)}"

            parameters.append(parameter)

        # **kwargs.
        if args.kwarg is not None:
            kwarg = f"**{args.kwarg.arg}"

            if args.kwarg.annotation is not None:
                kwarg += f": {source_text(args.kwarg.annotation)}"

            parameters.append(kwarg)

        return ", ".join(parameters)

    def visit_node(
        node: ast.AST,
        parent_name: str | None = None,
    ) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            qualified_name = (
                f"{parent_name}.{node.name}"
                if parent_name
                else node.name
            )

            symbols.append({
                "kind": (
                    "async_function"
                    if isinstance(node, ast.AsyncFunctionDef)
                    else "function"
                ),
                "name": node.name,
                "qualified_name": qualified_name,
                "line": node.lineno,
                "end_line": node.end_lineno,
                "signature": format_signature(node),
                "return_annotation": source_text(node.returns),
                "decorators": [
                    source_text(item) for item in node.decorator_list
                ],
                "docstring": ast.get_docstring(node),
            })

            for child in node.body:
                if isinstance(
                    child,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                        ast.ClassDef,
                    ),
                ):
                    visit_node(child, qualified_name)

        elif isinstance(node, ast.ClassDef):
            qualified_name = (
                f"{parent_name}.{node.name}"
                if parent_name
                else node.name
            )

            symbols.append({
                "kind": "class",
                "name": node.name,
                "qualified_name": qualified_name,
                "line": node.lineno,
                "end_line": node.end_lineno,
                "bases": [
                    source_text(base) for base in node.bases
                ],
                "decorators": [
                    source_text(item) for item in node.decorator_list
                ],
                "docstring": ast.get_docstring(node),
            })

            for child in node.body:
                if isinstance(
                    child,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                        ast.ClassDef,
                    ),
                ):
                    visit_node(child, qualified_name)

    for node in tree.body:
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ):
            visit_node(node)

    return {
        "file": str(path),
        "symbols": symbols,
    }
