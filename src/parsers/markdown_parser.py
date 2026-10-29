import re
from pathlib import Path
from typing import Any


HEADING_PATTERN = re.compile(
    r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$"
)


def parse_markdown_file(file_path: str | Path) -> dict[str, Any]:
    """
    Parse a Markdown file into sections based on its headings.

    Each section contains its heading, level, heading path,
    source line number, and content.

    Headings inside fenced code blocks are ignored.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Markdown file not found: {path}"
        )

    if path.suffix.lower() != ".md":
        raise ValueError(
            f"Expected a Markdown file: {path}"
        )

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    sections: list[dict[str, Any]] = []
    heading_stack: list[dict[str, Any]] = []
    current_section: dict[str, Any] | None = None
    content_lines: list[str] = []

    fence_character: str | None = None
    fence_length = 0

    def save_current_section() -> None:
        if current_section is not None:
            current_section["content"] = "\n".join(
                content_lines
            ).strip()
            sections.append(current_section)

    for line_number, line in enumerate(lines, start=1):
        stripped = line.lstrip()

        # If inside a fenced code block, look only for its closing fence.
        if fence_character is not None:
            closing_fence = re.fullmatch(
                r"(`{3,}|~{3,})[ \t]*",
                stripped,
            )

            if (
                closing_fence is not None
                and closing_fence.group(1)[0] == fence_character
                and len(closing_fence.group(1)) >= fence_length
            ):
                fence_character = None
                fence_length = 0

            if current_section is not None:
                content_lines.append(line)

            continue

        # Detect the start of a fenced code block.
        opening_fence = re.match(
            r"^(`{3,}|~{3,})(.*)$",
            stripped,
        )

        if opening_fence is not None:
            marker = opening_fence.group(1)
            info_string = opening_fence.group(2)

            # A backtick fence cannot have backticks in its info string.
            if marker[0] == "~" or "`" not in info_string:
                fence_character = marker[0]
                fence_length = len(marker)

                if current_section is not None:
                    content_lines.append(line)

                continue

        # Outside code blocks, identify Markdown headings.
        heading_match = HEADING_PATTERN.match(line)

        if heading_match is None:
            if current_section is not None:
                content_lines.append(line)
            continue

        save_current_section()
        content_lines = []

        level = len(heading_match.group(1))
        heading = heading_match.group(2).strip()

        # Remove headings at the same level or deeper from the path.
        while (
            heading_stack
            and heading_stack[-1]["level"] >= level
        ):
            heading_stack.pop()

        heading_stack.append({
            "level": level,
            "heading": heading,
        })

        current_section = {
            "heading": heading,
            "level": level,
            "line": line_number,
            "heading_path": [
                item["heading"]
                for item in heading_stack
            ],
        }

    save_current_section()

    return {
        "file": str(path),
        "sections": sections,
    }