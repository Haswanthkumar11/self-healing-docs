import argparse
import json
import sys
from pathlib import Path

from src.reporting.impact_report import generate_impact_report
from src.ai.documentation_pipeline import (
    analyze_documentation,
    save_analysis_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze Git changes, identify affected documentation, "
            "and optionally audit documentation with AI."
        )
    )

    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the Git repository (default: current directory).",
    )

    parser.add_argument(
        "--base",
        required=True,
        help="Base Git reference to compare against, such as HEAD~1.",
    )

    parser.add_argument(
        "--target",
        default="HEAD",
        help="Target Git reference (default: HEAD).",
    )

    parser.add_argument(
        "--docs",
        default="docs",
        help="Documentation directory relative to the repository.",
    )

    parser.add_argument(
        "--output",
        help="Optional path for saving the Git impact report as JSON.",
    )

    parser.add_argument(
        "--audit-source",
        help=(
            "Python source file to audit against Markdown documentation. "
            "Path is relative to the repository unless absolute."
        ),
    )

    parser.add_argument(
        "--audit-doc",
        help=(
            "Markdown file to compare with --audit-source. "
            "Path is relative to the repository unless absolute."
        ),
    )

    parser.add_argument(
        "--audit-output",
        help="Optional path for saving the AI audit report as JSON.",
    )

    return parser


def resolve_path(repository: Path, supplied_path: str) -> Path:
    """Resolve a supplied path relative to the repository when appropriate."""
    path = Path(supplied_path)

    if not path.is_absolute():
        path = repository / path

    return path.resolve()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if bool(args.audit_source) != bool(args.audit_doc):
        parser.error(
            "--audit-source and --audit-doc must be supplied together."
        )

    if args.audit_output and not args.audit_source:
        parser.error(
            "--audit-output requires --audit-source and --audit-doc."
        )

    try:
        repository = Path(args.repo).resolve()

        # Generate the Git documentation impact report.
        report = generate_impact_report(
            repository_path=repository,
            base_ref=args.base,
            target_ref=args.target,
            documentation_root=args.docs,
        )

        output = json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )

        if args.output:
            output_path = resolve_path(repository, args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                output + "\n",
                encoding="utf-8",
            )
            print(f"Impact report saved to: {output_path}")

        print("=== Git Documentation Impact Report ===")
        print(output)

        # Optionally audit Python source against Markdown documentation.
        if args.audit_source:
            source_file = resolve_path(
                repository,
                args.audit_source,
            )
            documentation_file = resolve_path(
                repository,
                args.audit_doc,
            )

            print("\n=== AI Documentation Audit ===")
            print(f"Source file: {source_file}")
            print(f"Documentation file: {documentation_file}")
            print("Running Gemini audit; this may take some time...")

            audit_report = analyze_documentation(
                source_file=source_file,
                documentation_file=documentation_file,
            )

            audit_output = json.dumps(
                audit_report,
                indent=2,
                ensure_ascii=False,
            )

            if args.audit_output:
                audit_output_path = resolve_path(
                    repository,
                    args.audit_output,
                )

                save_analysis_report(
                    audit_report,
                    audit_output_path,
                )

                print(
                    f"AI audit report saved to: {audit_output_path}"
                )

            print(audit_output)

        return 0

    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    except Exception as exc:
        # Prevent unexpected API or third-party errors from producing
        # an unhandled traceback in normal CLI usage.
        print(
            f"Unexpected error ({type(exc).__name__}): {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
